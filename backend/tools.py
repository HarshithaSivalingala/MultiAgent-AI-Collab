"""
MCP Tools - A collection of tools that MCP agents can use to perform tasks
"""
import json
from typing import Dict, Any

# ============================================
# TOOL REGISTRY
# ============================================

class ToolRegistry:
    def __init__(self):
        self.tools = {
            "web_search": self.web_search,
            "create_diagram": self.create_diagram,
            "write_note": self.write_note
        }
        self.tool_log = []
    
    def execute(self, tool_name: str, **kwargs) -> Dict[str, Any]:
        """Execute a tool and log the result"""
        if tool_name not in self.tools:
            return {"error": f"Tool {tool_name} not found"}
        
        result = self.tools[tool_name](**kwargs)
        
        # Log tool usage
        self.tool_log.append({
            "tool": tool_name,
            "input": kwargs,
            "output": result,
            "timestamp": "now"
        })
        
        return result
    
    # ============================================
    # TOOL IMPLEMENTATIONS
    # ============================================
    
    def web_search(self, query: str) -> Dict[str, Any]:
        """
        Mock web search - returns fake but realistic results
        In production: wire up to real search API
        """
        mock_results = {
            "url shortener": [
                "Use base62 encoding for short codes",
                "Redis for fast lookups, PostgreSQL for persistence",
                "Typical pattern: API -> Cache -> Database"
            ],
            "system design": [
                "Consider scalability, reliability, maintainability",
                "Use load balancers and caching layers",
                "Microservices for complex systems"
            ]
        }
        
        # Simple keyword matching
        for keyword, results in mock_results.items():
            if keyword.lower() in query.lower():
                return {
                    "query": query,
                    "results": results,
                    "source": "mock_search"
                }
        
        return {
            "query": query,
            "results": ["No specific results found"],
            "source": "mock_search"
        }
    
    def create_diagram(self, description: str) -> Dict[str, Any]:
        """
        Generate Mermaid diagram code
        In production: could use AI to generate from description
        """
        # Simple pattern matching for common diagrams
        if "url shortener" in description.lower():
            mermaid = """graph LR
    A[Client] --> B[API Gateway]
    B --> C[URL Service]
    C --> D[Redis Cache]
    C --> E[PostgreSQL]
    D -.-> E
"""
        elif "system" in description.lower():
            mermaid = """graph TB
    A[User Request] --> B[Load Balancer]
    B --> C[App Server 1]
    B --> D[App Server 2]
    C --> E[Database]
    D --> E
"""
        else:
            mermaid = """graph LR
    A[Start] --> B[Process]
    B --> C[End]
"""
        
        return {
            "description": description,
            "diagram_type": "mermaid",
            "code": mermaid,
            "status": "generated"
        }
    
    def write_note(self, content: str) -> Dict[str, Any]:
        """
        Save a note to the shared workspace
        """
        return {
            "content": content,
            "type": "note",
            "status": "saved",
            "word_count": len(content.split())
        }

# ============================================
# TOOL SCHEMAS (for MCP)
# ============================================

TOOL_SCHEMAS = {
    "web_search": {
        "name": "web_search",
        "description": "Search the web for information",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search query"
                }
            },
            "required": ["query"]
        }
    },
    "create_diagram": {
        "name": "create_diagram",
        "description": "Create a system diagram in Mermaid format",
        "input_schema": {
            "type": "object",
            "properties": {
                "description": {
                    "type": "string",
                    "description": "Description of what to diagram"
                }
            },
            "required": ["description"]
        }
    },
    "write_note": {
        "name": "write_note",
        "description": "Write a note to the shared workspace",
        "input_schema": {
            "type": "object",
            "properties": {
                "content": {
                    "type": "string",
                    "description": "Note content"
                }
            },
            "required": ["content"]
        }
    }
}

# Global instance
tool_registry = ToolRegistry()