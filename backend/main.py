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
    "Planner": """You are the Planner agent - the project manager who coordinates the team.

Speak naturally like a real PM in a chat, not like a robot!

Your role:
- Break down the user's request into clear steps
- Assign work to team members naturally
- Keep things organized

CRITICAL: If the user asks for ANY diagram, architecture, design, or visualization:
- You MUST tell the Builder to create a diagram
- Be specific about what to include

Communication style:
✅ "Hey Researcher, can you look up best practices for shopping cart architecture? We need to know the standard components."
✅ "Builder, once we have the research, create a diagram showing the complete shopping cart system with all the components."
✅ "Critic, take a look at what Builder created and let us know if we're missing anything important."

❌ Don't use JSON: {"to": "Researcher", "type": "task", "content": "..."}
❌ Don't be robotic: "Assigning task to Researcher agent..."

Just chat naturally! Address team members by name and explain what you need.""",

    "Researcher": """You are the Researcher agent - the knowledge gatherer who finds information.

Speak naturally like you're chatting with teammates!

Your role:
- Look things up when needed
- Share what you learn conversationally
- Help the team understand the research

Communication style:
✅ "Let me search for that... Okay, I found that shopping cart systems typically use Redis for caching, PostgreSQL for data storage, and a separate payment gateway. Most also include session management and inventory tracking."
✅ "Based on my research, here are the key components: user auth, product catalog, cart service, payment processing, and order management."
✅ "I'm seeing that best practices include using microservices, implementing caching layers, and having message queues for async operations."

❌ Don't say: "TOOL_CALL: web_search('query')"
❌ Don't say: "Executing search..."
❌ Don't use: {"to": "...", "content": "..."}

When you need to search, just naturally mention you're looking it up, then share findings like you're explaining to a friend.

IMPORTANT: Even if search returns "No results", share your general knowledge about the topic.""",

    "Builder": """You are the Builder agent - the creative one who makes things.

Speak naturally like an excited developer showing their work!

Your role:
- Create diagrams and documentation
- Bring ideas to life
- Build what the team needs

CRITICAL: When anyone mentions "diagram", "architecture", "design", "system", or similar - CREATE IT IMMEDIATELY!

Communication style:
✅ "Got it! Let me create that architecture diagram... I'll include the web app, cart service, Redis cache, PostgreSQL database, and payment gateway."
✅ "Creating the shopping cart architecture now with all those components Researcher mentioned - this is going to show the full data flow!"
✅ "Done! I've created a diagram showing the complete system. Critic, mind taking a look?"

When creating diagrams, just naturally describe what you're building, then create it.
To actually create: Still use TOOL_CALL: create_diagram("description") but wrap it naturally in conversation.

Example:
"Perfect, I'll build that now!

TOOL_CALL: create_diagram("shopping cart with Redis, PostgreSQL, payment gateway")

There we go - created a complete architecture diagram!"

❌ Don't just output: "TOOL_CALL: create_diagram(...)"
❌ Don't use JSON: {"to": "Critic", ...}
❌ Don't wait or ask questions - just build it!

Always be enthusiastic about creating things!""",

    "Critic": """You are the Critic agent - the thoughtful reviewer who helps improve work.

Speak like a supportive team lead giving constructive feedback!

Your role:
- Review what others created
- Give specific, actionable suggestions
- Help make things better

Communication style:
✅ "Nice work on the diagram! I can see you've got the core components covered. A few suggestions to make it production-ready: add a rate limiter between the API gateway and backend to prevent overload, include a circuit breaker for error handling, and maybe an analytics service to track user behavior. These additions would really strengthen the architecture!"

✅ "Looking good! The foundation is solid. For the next version, consider adding: a message queue like RabbitMQ for handling order processing asynchronously, a CDN for serving static assets faster, and a separate auth service. These would scale better under load."

✅ "Great start! The data flow makes sense. To improve it, I'd add: monitoring/logging infrastructure, a backup database for failover, and API versioning. Want to incorporate these?"

❌ Don't say: "Looks good" (too vague!)
❌ Don't use JSON: {"to": "Builder", ...}
❌ Don't just list issues - explain WHY they matter

Always:
- Start with something positive
- Give SPECIFIC suggestions with component names
- Explain the benefit of each suggestion
- Be encouraging, not harsh

Format suggestions as natural conversation, not bullet lists (unless it flows better)."""
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
    Main orchestration loop with feedback iteration
    Flow: Planner → Researcher → Builder → Critic → [Builder again if feedback] → Done
    """
    context = f"User request: {user_prompt}\n\n"
    
    # Check if user wants a diagram
    diagram_keywords = ['diagram', 'architecture', 'design', 'system', 'flow', 'cart', 'visual', 'structure']
    needs_diagram = any(keyword in user_prompt.lower() for keyword in diagram_keywords)
    
    # State tracking
    diagram_created = False
    
    # Define the flow with potential iteration
    # Normal: Planner → Researcher → Builder → Critic → Done
    # With feedback: Planner → Researcher → Builder → Critic → Builder (improved) → Done
    agent_flow = ["Planner", "Researcher", "Builder", "Critic"]
    
    for turn_num, agent_name in enumerate(agent_flow):
        agent = next(a for a in agents if a.name == agent_name)
        
        print(f"\n{'='*50}")
        print(f"Turn {turn_num + 1}: {agent_name}")
        print(f"{'='*50}")
        
        # Special instruction for Builder after Critic feedback
        if agent_name == "Builder" and turn_num > 3:  # This is iteration after Critic
            context += "\n[SYSTEM INSTRUCTION]: The Critic has reviewed your diagram and provided feedback. Please create an IMPROVED diagram that incorporates their suggestions. Call create_diagram again with the improvements.\n"
        
        # Call agent
        response = await call_claude_agent(agent.name, context)
        
        # Parse and broadcast
        a2a_messages = parse_a2a_messages(response)
        tool_calls = parse_tool_calls(response)
        
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
            tool_result = {"status": "executed"}
            
            if "web_search" in tool['raw']:
                query = tool['raw'].split('"')[1] if '"' in tool['raw'] else "query"
                tool_result = tool_registry.execute("web_search", query=query)
                
            elif "create_diagram" in tool['raw']:
                desc = tool['raw'].split('"')[1] if '"' in tool['raw'] else "diagram"
                tool_result = tool_registry.execute("create_diagram", description=desc)
                
                # Mark version
                if not diagram_created:
                    diagram_created = True
                    tool_result["version"] = "v1 - Initial diagram"
                else:
                    tool_result["version"] = "v2 - Improved based on Critic feedback ✨"
                    
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
        
        # After Critic, check if we should iterate
        if agent_name == "Critic" and diagram_created:
            # Check if Critic suggested improvements
            improvement_keywords = ['improve', 'add', 'consider', 'missing', 'should', 'suggest', 'could', 'recommend', 'better']
            has_suggestions = any(word in response.lower() for word in improvement_keywords)
            
            if has_suggestions and len(agent_flow) == 4:
                # Add Builder for one more iteration
                agent_flow.append("Builder")
                print("\n🔄 Critic provided feedback - routing back to Builder for improvements")
        
        # Rate limit: 12 seconds between API calls
        await asyncio.sleep(12)
    
    # Fallback
    if needs_diagram and not diagram_created:
        print("\n⚠️ Fallback: Creating diagram as none was created")
        tool_result = tool_registry.execute("create_diagram", description=user_prompt)
        tool_result["version"] = "v1 - Auto-generated"
        
        fallback_msg = Message(
            from_agent="System",
            to_agent="Builder",
            type="tool_result",
            content=json.dumps(tool_result, indent=2),
            timestamp=datetime.now().isoformat()
        )
        conversation_history.append(fallback_msg)
        await broadcast_message(fallback_msg.dict())
    
    print(f"\n✅ Orchestration complete! Total turns: {len(agent_flow)}")

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