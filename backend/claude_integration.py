"""
Real Claude API integration
Replace mock responses with actual API calls
"""
import os
from anthropic import Anthropic
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

async def call_claude_api(system_prompt: str, user_message: str, context: str) -> str:
    """
    Call Claude API with agent-specific system prompt
    
    Args:
        system_prompt: Agent's role and instructions
        user_message: Current user request
        context: Full conversation history
    
    Returns:
        Agent's response as string
    """
    
    # Build the prompt
    full_prompt = f"""{context}

Your turn to respond. Remember:
- Send A2A messages in JSON format: {{"to": "AgentName", "type": "task", "content": "message"}}
- Use tools with: TOOL_CALL: tool_name("params")
- Keep responses focused and actionable
"""
    
    try:
        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1000,
            system=system_prompt,
            messages=[
                {"role": "user", "content": full_prompt}
            ]
        )
        
        return message.content[0].text
    
    except Exception as e:
        return f"[API Error: {str(e)}]"

# ============================================
# MOCK MODE (for testing without API key)
# ============================================

MOCK_MODE = not os.getenv("ANTHROPIC_API_KEY") or os.getenv("ANTHROPIC_API_KEY") == "your_key_here"

async def call_agent(agent_name: str, system_prompt: str, context: str) -> str:
    """
    Wrapper that uses real API or mock responses
    """
    if MOCK_MODE:
        return await mock_agent_response(agent_name, context)
    else:
        return await call_claude_api(system_prompt, "", context)

async def mock_agent_response(agent_name: str, context: str) -> str:
    """Mock responses for testing without API"""
    
    import asyncio
    await asyncio.sleep(1)  # Simulate API delay
    
    mock_responses = {
        "Planner": '{"to": "Researcher", "type": "task", "content": "Research best practices for URL shortener architecture"}\n\nI\'ll coordinate our team to build this solution.',
        
        "Researcher": 'TOOL_CALL: web_search("URL shortener best practices")\n\nBased on research:\n- Use base62 encoding for short keys\n- Redis for caching\n- PostgreSQL for persistence\n\n{"to": "Builder", "type": "info", "content": "Key findings: base62 encoding, Redis cache, PostgreSQL storage"}',
        
        "Builder": 'TOOL_CALL: create_diagram("URL Shortener System Architecture")\n\nI\'ve created the system diagram showing:\n- API Gateway\n- Redis Cache Layer\n- PostgreSQL Database\n\n{"to": "Critic", "type": "review_request", "content": "Please review the architecture diagram"}',
        
        "Critic": 'The design looks solid! Suggestions:\n- Add rate limiting\n- Consider analytics layer\n- Add monitoring\n\n{"to": "Planner", "type": "feedback", "content": "Architecture approved with minor suggestions for improvements"}'
    }
    
    return mock_responses.get(agent_name, f"{agent_name}: Working on it...")