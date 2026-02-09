"""
MCP Tools - Simple implementations for hackathon
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
        Generate Mermaid diagram code with basic and improved versions
        """
        desc_lower = description.lower()
        
        # Check if this is an improved/v2 version request
        is_improved = any(word in desc_lower for word in ['improved', 'better', 'enhanced', 'v2', 'rate limit', 'circuit breaker', 'analytics'])
        
        # Shopping cart / E-commerce
        if any(word in desc_lower for word in ['shopping', 'cart', 'ecommerce', 'e-commerce', 'store']):
            if is_improved:
                # IMPROVED VERSION - Production ready with all enhancements
                mermaid = """graph TB
    A[User/Browser] --> B[CDN]
    B --> C[Load Balancer]
    C --> D[Rate Limiter]
    D --> E[API Gateway]
    E --> F[Circuit Breaker]
    
    F --> G[Web Application]
    F --> H[Shopping Cart Service]
    F --> I[Product Catalog Service]
    F --> J[User Authentication]
    
    G --> K[Session Manager]
    H --> L[Cart Database]
    H --> M[Redis Cache]
    I --> N[Product Database]
    I --> M
    J --> O[User Database]
    
    H --> P[Payment Gateway]
    P --> Q[Payment Processor]
    
    H --> R[Message Queue]
    R --> S[Order Processing Service]
    S --> T[Inventory Management]
    S --> U[Shipping Service]
    S --> V[Notification Service]
    
    G --> W[Analytics Service]
    H --> W
    I --> W
    W --> X[Analytics Database]
    
    Y[Monitoring & Logging] -.-> E
    Y -.-> G
    Y -.-> H
    Y -.-> I
"""
            else:
                # BASIC VERSION - Simple initial design
                mermaid = """graph TB
    A[User/Browser] --> B[Web Application]
    
    B --> C[Shopping Cart Service]
    B --> D[Product Catalog Service]
    B --> E[User Authentication]
    
    C --> F[Cart Database]
    D --> G[Product Database]
    E --> H[User Database]
    
    C --> I[Payment Gateway]
    I --> J[Order Processing]
    
    J --> K[Inventory Management]
    J --> L[Shipping Service]
"""
        
        # URL shortener
        elif any(word in desc_lower for word in ['url', 'shortener', 'link']):
            if is_improved:
                # IMPROVED VERSION
                mermaid = """graph LR
    A[Client] --> B[CDN]
    B --> C[Load Balancer]
    C --> D[Rate Limiter]
    D --> E[API Gateway]
    
    E --> F[URL Service]
    F --> G[Redis Cache]
    F --> H[PostgreSQL]
    
    F --> I[Analytics Service]
    I --> J[Analytics DB]
    
    E --> K[Authentication Service]
    K --> L[User DB]
    
    M[Monitoring] -.-> E
    M -.-> F
"""
            else:
                # BASIC VERSION
                mermaid = """graph LR
    A[Client] --> B[API Gateway]
    
    B --> C[URL Service]
    C --> D[Redis Cache]
    C --> E[PostgreSQL]
    
    D -.-> E
    
    C --> F[Analytics Service]
    F --> G[Analytics DB]
"""
        
        # General system architecture
        elif any(word in desc_lower for word in ['system', 'architecture', 'microservice']):
            if is_improved:
                # IMPROVED VERSION
                mermaid = """graph TB
    A[User Request] --> B[Load Balancer]
    B --> C[Rate Limiter]
    C --> D[API Gateway]
    
    D --> E[Circuit Breaker]
    
    E --> F[App Server 1]
    E --> G[App Server 2]
    E --> H[App Server 3]
    
    F --> I[Service Layer]
    G --> I
    H --> I
    
    I --> J[Cache Layer - Redis]
    I --> K[Database Cluster]
    I --> L[Message Queue]
    
    L --> M[Worker Nodes]
    M --> N[Background Jobs]
    
    I --> O[Analytics Service]
    O --> P[Analytics DB]
    
    Q[Monitoring & Logging] -.-> D
    Q -.-> I
    Q -.-> K
"""
            else:
                # BASIC VERSION
                mermaid = """graph TB
    A[User Request] --> B[Load Balancer]
    
    B --> C[App Server 1]
    B --> D[App Server 2]
    
    C --> E[Service Layer]
    D --> E
    
    E --> F[Database Cluster]
    E --> G[Cache Layer]
    E --> H[Message Queue]
    
    H --> I[Worker Nodes]
"""
        
        # API design
        elif 'api' in desc_lower:
            if is_improved:
                # IMPROVED VERSION
                mermaid = """graph LR
    A[Client] --> B[Load Balancer]
    B --> C[Rate Limiter]
    C --> D[API Gateway]
    
    D --> E[Authentication]
    D --> F[Authorization]
    
    E --> G[Business Logic]
    F --> G
    
    G --> H[Database]
    G --> I[Cache - Redis]
    G --> J[External APIs]
    
    K[Circuit Breaker] --> G
    
    L[Monitoring] -.-> D
    L -.-> G
    
    M[API Versioning] --> D
"""
            else:
                # BASIC VERSION
                mermaid = """graph LR
    A[Client] --> B[API Gateway]
    
    B --> C[Auth Service]
    B --> D[Business Logic]
    
    D --> E[Database]
    D --> F[External APIs]
    
    B --> G[Rate Limiter]
"""
        
        # Default: Generic flow
        else:
            if is_improved:
                # IMPROVED VERSION
                mermaid = """graph TB
    A[User Input] --> B[Load Balancer]
    B --> C[Rate Limiter]
    C --> D[Processing Layer]
    
    D --> E[Business Logic]
    E --> F[Data Layer]
    
    F --> G[Primary Database]
    F --> H[Cache - Redis]
    F --> I[Backup Database]
    
    E --> J[External Services]
    E --> K[Message Queue]
    
    K --> L[Background Workers]
    
    D --> M[Response Handler]
    M --> N[User Output]
    
    O[Monitoring] -.-> D
    O -.-> E
    O -.-> F
"""
            else:
                # BASIC VERSION
                mermaid = """graph TB
    A[User Input] --> B[Processing Layer]
    
    B --> C[Business Logic]
    C --> D[Data Layer]
    
    D --> E[Database]
    C --> F[External Services]
    
    B --> G[Response Handler]
    G --> H[User Output]
"""
        
        version_label = "v2 - Production Ready" if is_improved else "v1 - Basic Architecture"
        
        return {
            "description": description,
            "diagram_type": "mermaid",
            "code": mermaid,
            "status": "generated",
            "version": version_label
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