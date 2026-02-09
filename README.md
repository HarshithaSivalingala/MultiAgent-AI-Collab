# 🤖 AI Team Room

> **Pioneering MCP and A2A Communication for Multi-Agent AI Systems**

A research project demonstrating **Model Context Protocol (MCP)** and **Agent-to-Agent (A2A) Communication** patterns. Watch specialized AI agents collaborate through structured messaging and tool orchestration to solve complex design problems.

![Python](https://img.shields.io/badge/python-3.9+-blue.svg)
![React](https://img.shields.io/badge/react-18.0+-61dafb.svg)

---

## 🎯 Core Innovation

I like to challenge AI systems rather than take their outputs at face value. Instead of simply accepting responses, I cross-question them to understand the reasoning, assumptions, and steps behind their predictions. While learning about A2A and MCP tools, this mindset led to the idea of creating an AI Team Room, a space where multiple AI agents can reason together, explain their approaches, and collaborate transparently.
This project implements two cutting-edge AI collaboration patterns:

1. Model Context Protocol (MCP) - A standardized protocol allowing AI agents to interact with external tools and data sources
2. Agent-to-Agent (A2A) Communication - A messaging protocol enabling direct AI-to-AI collaboration

---

## 🏗️ Architecture Deep Dive

### **MCP Implementation**

```python
# Tool Definition (MCP)
class ToolRegistry:
    def execute(self, tool_name: str, **params):
        # Route to appropriate tool
        if tool_name == "web_search":
            return self.web_search(params['query'])
        elif tool_name == "create_diagram":
            return self.create_diagram(params['description'])
```

**Tool Call Flow:**
```
Agent → TOOL_CALL: web_search("shopping cart architecture")
                ↓
         Tool Registry (MCP Layer)
                ↓
         Web Search Tool
                ↓
         Structured Result
                ↓
         Back to Agent
```

### **A2A Communication Protocol**

```json
{
  "from_agent": "Planner",
  "to_agent": "Researcher",
  "type": "task",
  "content": "Research best practices for shopping cart systems",
  "timestamp": "2024-02-09T10:30:00Z"
}
```
---

## 🧠 The Agent Team

| Agent | Role | MCP Tools Used | A2A Patterns |
|-------|------|----------------|--------------|
| 🧭 **Planner** | Orchestrator | None | Sends tasks to all |
| 🧠 **Researcher** | Information Gatherer | `web_search` | Receives tasks, sends info |
| 🧑‍💻 **Builder** | Creator | `create_diagram`, `write_note` | Receives info, sends review requests |
| 🔍 **Critic** | Quality Assurance | None | Receives reviews, sends feedback |

---

## 🚀 Quick Start

### **Prerequisites**

- Python 3.9+
- Node.js 16+
- Google Gemini API key

### **Installation**

```bash
# Backend
cd backend
pip install fastapi uvicorn websockets google-generativeai requests --break-system-packages
export GEMINI_API_KEY="your-key"
uvicorn main:app --reload

# Frontend
cd frontend
npm install
npm run dev
```

---

## 📊 MCP + A2A in Action

### **Example: Shopping Cart Design**

**Step 1: A2A Task Assignment**
```
Planner → Researcher: "Research shopping cart architectures"
```

**Step 2: MCP Tool Call**
```
Researcher → MCP: web_search("shopping cart best practices")
MCP → Researcher: {results: [...]}
```

**Step 3: A2A Information Sharing**
```
Researcher → Builder: "Use Redis cache, PostgreSQL, Payment API..."
```

**Step 4: MCP Diagram Creation**
```
Builder → MCP: create_diagram("shopping cart with Redis, PostgreSQL...")
MCP → Builder: {diagram_code: "graph LR..."}
```

**Step 5: A2A Review**
```
Builder → Critic: "Please review"
Critic → Builder: "Add rate limiter, circuit breaker, analytics"
```

**Step 6: MCP Improved Diagram**
```
Builder → MCP: create_diagram("shopping cart with improvements...")
MCP → Builder: {diagram_code: "graph LR...", version: "v2"}
```

---


## 📁 Project Structure

```
ai-team-room/
├── backend/
│   ├── main.py              # A2A orchestration logic
│   ├── tools.py             # MCP tool registry
│   ├── claude_integration.py  # LLM API wrapper
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── AgentChat.jsx    # A2A message display
│   │   │   ├── SharedCanvas.jsx # MCP output rendering
│   │   │   └── ToolLog.jsx      # MCP tool call log
│   │   └── App.jsx
│   └── package.json
└── README.md
```
---

## 📚RESOURCES:

## References & Resources

- **Official Spec (Model Context Protocol):** https://modelcontextprotocol.io/
- **Python SDK:** https://github.com/modelcontextprotocol/python-sdk
- **Anthropic MCP Guide:** https://docs.anthropic.com/en/docs/mcp
- **Research Paper:** https://arxiv.org/abs/2402.01680
- **AutoGen Framework:** https://github.com/microsoft/autogen
- **FastAPI:** https://fastapi.tiangolo.com/
- **Google Gemini API:** https://ai.google.dev/docs
- **Mermaid.js:** https://mermaid.js.org/
- **UV Package Manager:** https://docs.astral.sh/uv/


---
If this helped you, it did its job ✨
