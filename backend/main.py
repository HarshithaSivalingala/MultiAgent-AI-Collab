from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import json
import asyncio
from datetime import datetime

from claude_integration import call_agent
from tools import tool_registry

app = FastAPI()

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================
# AGENT SYSTEM PROMPTS
# ============================================

AGENT_PROMPTS = {
    "Planner": """You are the Planner agent. Your role:
- Break down user requests into clear tasks
- Assign work to other agents
- Coordinate the overall strategy

When you need other agents, send A2A messages in this format:
{"to": "Researcher", "type": "task", "content": "your message"}

Keep responses short and actionable.""",

    "Researcher": """You are the Researcher agent. Your role:
- Find information and best practices
- Use web-search tool when needed
- Provide factual, researched answers

To use tools, output:
TOOL_CALL: web_search("your query")

To message agents:
{"to": "Builder", "type": "info", "content": "your message"}""",

    "Builder": """You are the Builder agent. Your role:
- Create diagrams, code, or documentation
- Use create_diagram or write_note tools
- Execute the planned solution

To use tools:
TOOL_CALL: create_diagram("description")
TOOL_CALL: write_note("content")

To message agents:
{"to": "Critic", "type": "review_request", "content": "your message"}""",

    "Critic": """You are the Critic agent. Your role:
- Review work from other agents
- Identify problems or improvements
- Validate the final solution

Keep feedback constructive. Message format:
{"to": "Builder", "type": "feedback", "content": "your message"}"""
}

# ============================================
# DATA MODELS
# ============================================

class Message(BaseModel):
    from_agent: str
    to_agent: Optional[str] = None
    type: str  # "task", "info", "feedback", "tool_result"
    content: str
    timestamp: str

class AgentState(BaseModel):
    name: str
    role: str
    active: bool = True

# ============================================
# GLOBAL STATE
# ============================================

conversation_history: List[Message] = []
agents = [
    AgentState(name="Planner", role="strategist"),
    AgentState(name="Researcher", role="fact-finder"),
    AgentState(name="Builder", role="executor"),
    AgentState(name="Critic", role="reviewer")
]
active_connections: List[WebSocket] = []

# ============================================
# ORCHESTRATOR LOGIC
# ============================================

async def call_claude_agent(agent_name: str, context: str) -> str:
    """
    Calls Claude API as a specific agent
    Uses real API if key is configured, otherwise uses mock responses
    """
    system_prompt = AGENT_PROMPTS[agent_name]
    response = await call_agent(agent_name, system_prompt, context)
    return response

def parse_a2a_messages(response: str) -> List[dict]:
    """Extract A2A messages from agent response"""
    messages = []
    lines = response.split('\n')
    
    for line in lines:
        line = line.strip()
        if line.startswith('{') and '"to"' in line:
            try:
                msg = json.loads(line)
                if 'to' in msg and 'content' in msg:
                    messages.append(msg)
            except:
                pass
    
    return messages

def parse_tool_calls(response: str) -> List[dict]:
    """Extract tool calls from agent response"""
    tools = []
    lines = response.split('\n')
    
    for line in lines:
        if 'TOOL_CALL:' in line:
            tool_str = line.split('TOOL_CALL:')[1].strip()
            tools.append({"raw": tool_str})
    
    return tools

async def broadcast_message(message: dict):
    """Send message to all connected WebSocket clients"""
    for connection in active_connections:
        try:
            await connection.send_json(message)
        except:
            active_connections.remove(connection)

# ============================================
# API ENDPOINTS
# ============================================

@app.get("/")
async def root():
    return {"status": "AI Team Room Backend Running"}

@app.get("/agents")
async def get_agents():
    return {"agents": agents}

@app.post("/start")
async def start_collaboration(request: dict):
    """
    Start the agent collaboration loop
    Input: {"prompt": "Design a URL shortener"}
    """
    user_prompt = request.get("prompt", "")
    
    # Clear history
    conversation_history.clear()
    
    # Add user message
    user_msg = Message(
        from_agent="User",
        to_agent="Planner",
        type="request",
        content=user_prompt,
        timestamp=datetime.now().isoformat()
    )
    conversation_history.append(user_msg)
    await broadcast_message(user_msg.dict())
    
    # Start orchestration loop
    asyncio.create_task(orchestrate_agents(user_prompt))
    
    return {"status": "started", "prompt": user_prompt}

async def orchestrate_agents(user_prompt: str):
    """
    Main orchestration loop - runs agents in turns
    """
    max_turns = 8
    current_turn = 0
    
    # Build context from history
    context = f"User request: {user_prompt}\n\n"
    
    while current_turn < max_turns:
        agent = agents[current_turn % len(agents)]
        
        # Call agent
        response = await call_claude_agent(agent.name, context)
        
        # Parse A2A messages
        a2a_messages = parse_a2a_messages(response)
        
        # Parse tool calls
        tool_calls = parse_tool_calls(response)
        
        # Create agent message
        agent_msg = Message(
            from_agent=agent.name,
            to_agent=a2a_messages[0]["to"] if a2a_messages else None,
            type="response",
            content=response,
            timestamp=datetime.now().isoformat()
        )
        conversation_history.append(agent_msg)
        await broadcast_message(agent_msg.dict())
        
        # Handle tool calls
        for tool in tool_calls:
            # Parse tool call (simple parsing for hackathon)
            tool_result = {"status": "executed", "output": "mock result"}
            
            # Try to execute real tool
            if "web_search" in tool['raw']:
                query = tool['raw'].split('"')[1] if '"' in tool['raw'] else "query"
                tool_result = tool_registry.execute("web_search", query=query)
            elif "create_diagram" in tool['raw']:
                desc = tool['raw'].split('"')[1] if '"' in tool['raw'] else "diagram"
                tool_result = tool_registry.execute("create_diagram", description=desc)
            elif "write_note" in tool['raw']:
                content = tool['raw'].split('"')[1] if '"' in tool['raw'] else "note"
                tool_result = tool_registry.execute("write_note", content=content)
            
            tool_msg = Message(
                from_agent="System",
                to_agent=agent.name,
                type="tool_result",
                content=json.dumps(tool_result, indent=2),
                timestamp=datetime.now().isoformat()
            )
            conversation_history.append(tool_msg)
            await broadcast_message(tool_msg.dict())
        
        # Update context
        context += f"\n{agent.name}: {response}\n"
        
        current_turn += 1
        await asyncio.sleep(2)  # Pause between turns

# ============================================
# WEBSOCKET
# ============================================

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    active_connections.append(websocket)
    
    # Send current history
    for msg in conversation_history:
        await websocket.send_json(msg.dict())
    
    try:
        while True:
            await websocket.receive_text()
    except:
        active_connections.remove(websocket)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)