"""
Real Claude API integration (supports Anthropic, OpenRouter, and Gemini)
"""
import os
import aiohttp
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Detect which API to use
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

USE_GEMINI = bool(GEMINI_API_KEY)
USE_OPENROUTER = bool(OPENROUTER_API_KEY) and not USE_GEMINI

async def call_claude_api(system_prompt: str, user_message: str, context: str) -> str:
    """
    Call AI API with agent-specific system prompt
    Supports Gemini, OpenRouter, and Anthropic APIs
    """
    
    # Build the prompt
    full_prompt = f"""{context}

Your turn to respond. Remember:
- Send A2A messages in JSON format: {{"to": "AgentName", "type": "task", "content": "message"}}
- Use tools with: TOOL_CALL: tool_name("params")
- Keep responses focused and actionable
"""
    
    try:
        if USE_GEMINI:
            return await call_gemini_api(system_prompt, full_prompt)
        elif USE_OPENROUTER:
            return await call_openrouter_api(system_prompt, full_prompt)
        else:
            return await call_anthropic_api(system_prompt, full_prompt)
    except Exception as e:
        return f"[API Error: {str(e)}]"

async def call_gemini_api(system_prompt: str, user_prompt: str) -> str:
    """Call Google Gemini API - WORKING VERSION"""
    import google.generativeai as genai
    
    genai.configure(api_key=GEMINI_API_KEY)
    
    # Combine system prompt with user prompt
    full_prompt = f"""{system_prompt}

{user_prompt}"""
    
    # Use the FULL model path - this is the fix!
    model = genai.GenerativeModel('models/gemini-2.5-flash')
    response = model.generate_content(full_prompt)
    
    return response.text

async def call_openrouter_api(system_prompt: str, user_prompt: str) -> str:
    """Call OpenRouter API"""
    async with aiohttp.ClientSession() as session:
        async with session.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": "anthropic/claude-3.5-sonnet",
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                "max_tokens": 1000
            }
        ) as response:
            data = await response.json()
            return data["choices"][0]["message"]["content"]

async def call_anthropic_api(system_prompt: str, user_prompt: str) -> str:
    """Call Anthropic API directly"""
    from anthropic import Anthropic
    client = Anthropic(api_key=ANTHROPIC_API_KEY)
    
    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1000,
        system=system_prompt,
        messages=[{"role": "user", "content": user_prompt}]
    )
    
    return message.content[0].text

# ============================================
# MOCK MODE (for testing without API key)
# ============================================

MOCK_MODE = not (GEMINI_API_KEY or OPENROUTER_API_KEY or ANTHROPIC_API_KEY)

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