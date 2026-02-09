import { useState, useEffect, useRef } from 'react';
import AgentChat from './components/AgentChat';
import SharedCanvas from './components/SharedCanvas';
import ToolLog from './components/ToolLog';

function App() {
  const [messages, setMessages] = useState([]);
  const [toolCalls, setToolCalls] = useState([]);
  const [canvasItems, setCanvasItems] = useState([]);
  const [isConnected, setIsConnected] = useState(false);
  const [userPrompt, setUserPrompt] = useState('');
  const [isRunning, setIsRunning] = useState(false);
  const wsRef = useRef(null);

  // WebSocket connection
  useEffect(() => {
    const ws = new WebSocket('ws://localhost:8000/ws');
    
    ws.onopen = () => {
      console.log('✅ Connected to backend');
      setIsConnected(true);
    };
    
    ws.onmessage = (event) => {
      const message = JSON.parse(event.data);
      console.log('📨 Received:', message);
      
      // Add to messages
      setMessages(prev => [...prev, message]);
      
      // Handle tool results
      if (message.type === 'tool_result') {
        setToolCalls(prev => [...prev, message]);
        
        // Parse tool result for canvas
        try {
          const result = JSON.parse(message.content);
          
          // Add diagram to canvas
          if (result.diagram_type === 'mermaid') {
            setCanvasItems(prev => [...prev, {
              type: 'diagram',
              code: result.code,
              description: result.description
            }]);
          }
          
          // Add note to canvas
          if (result.type === 'note') {
            setCanvasItems(prev => [...prev, {
              type: 'note',
              content: result.content
            }]);
          }
        } catch (e) {
          // Not JSON, ignore
        }
      }
    };
    
    ws.onclose = () => {
      console.log('❌ Disconnected from backend');
      setIsConnected(false);
    };
    
    wsRef.current = ws;
    
    return () => ws.close();
  }, []);

  const startCollaboration = async () => {
    if (!userPrompt.trim()) return;
    
    // Clear previous state
    setMessages([]);
    setToolCalls([]);
    setCanvasItems([]);
    setIsRunning(true);
    
    try {
      const response = await fetch('http://localhost:8000/start', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ prompt: userPrompt })
      });
      
      const data = await response.json();
      console.log('🚀 Started:', data);
      
      // Stop running after 90 seconds
      setTimeout(() => setIsRunning(false), 90000);
    } catch (error) {
      console.error('❌ Error:', error);
      setIsRunning(false);
    }
  };

  return (
    <div className="h-screen bg-black text-white flex flex-col overflow-hidden relative">
      {/* Premium gradient overlay */}
      <div className="absolute inset-0 bg-gradient-to-br from-gray-900/50 via-black to-gray-900/50 pointer-events-none"></div>
      
      {/* Subtle grid pattern */}
      <div className="absolute inset-0 opacity-[0.03]" style={{
        backgroundImage: 'linear-gradient(rgba(255,255,255,0.05) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.05) 1px, transparent 1px)',
        backgroundSize: '50px 50px'
      }}></div>

      {/* Header */}
      <header className="relative z-10 border-b border-gray-800 bg-black/80 backdrop-blur-xl">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className="relative">
                <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-gray-700 to-gray-900 flex items-center justify-center shadow-2xl border border-gray-700">
                  <span className="text-2xl">🤖</span>
                </div>
                {isRunning && (
                  <div className="absolute -top-1 -right-1 w-4 h-4">
                    <div className="w-4 h-4 bg-green-400 rounded-full animate-ping absolute"></div>
                    <div className="w-4 h-4 bg-green-400 rounded-full"></div>
                  </div>
                )}
              </div>
              <div>
                <h1 className="text-2xl font-bold tracking-tight">
                  <span className="bg-gradient-to-r from-gray-200 via-gray-400 to-gray-200 bg-clip-text text-transparent">
                    AI Team Room
                  </span>
                </h1>
                <p className="text-sm text-gray-500 font-light">Multi-Agent Collaborative Workspace</p>
              </div>
            </div>
            
            <div className="flex items-center gap-3">
              <div className={`flex items-center gap-2 px-4 py-2 rounded-lg border ${isConnected ? 'bg-green-500/5 border-green-500/20' : 'bg-red-500/5 border-red-500/20'} backdrop-blur-sm`}>
                <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-green-400 shadow-lg shadow-green-400/50' : 'bg-red-400 shadow-lg shadow-red-400/50'} ${isConnected && 'animate-pulse'}`} />
                <span className={`text-xs font-medium ${isConnected ? 'text-green-400' : 'text-red-400'}`}>
                  {isConnected ? 'Online' : 'Offline'}
                </span>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Input Section */}
      <div className="relative z-10 border-b border-gray-800 bg-black/60 backdrop-blur-xl">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex gap-3">
            <div className="relative flex-1 group">
              <input
                type="text"
                value={userPrompt}
                onChange={(e) => setUserPrompt(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && !isRunning && startCollaboration()}
                placeholder="Describe what you want the AI team to create..."
                disabled={isRunning}
                className="w-full bg-gray-900/50 border border-gray-800 rounded-xl px-6 py-4 focus:outline-none focus:border-gray-600 focus:bg-gray-900/80 transition-all placeholder:text-gray-600 text-gray-100 disabled:opacity-50 shadow-inner font-light"
              />
              <div className="absolute inset-0 rounded-xl bg-gradient-to-r from-gray-700/0 via-gray-600/5 to-gray-700/0 opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none"></div>
            </div>
            <button
              onClick={startCollaboration}
              disabled={!userPrompt.trim() || !isConnected || isRunning}
              className="relative px-8 py-4 rounded-xl font-medium transition-all disabled:opacity-40 disabled:cursor-not-allowed overflow-hidden group bg-gradient-to-r from-gray-800 to-gray-900 border border-gray-700 hover:border-gray-600 shadow-2xl"
            >
              <div className="absolute inset-0 bg-gradient-to-r from-gray-700 to-gray-800 opacity-0 group-hover:opacity-100 transition-opacity"></div>
              <span className="relative flex items-center gap-2 text-gray-200">
                {isRunning ? (
                  <>
                    <div className="w-4 h-4 border-2 border-gray-500 border-t-gray-300 rounded-full animate-spin"></div>
                    Processing...
                  </>
                ) : (
                  <>
                    <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                    </svg>
                    Start Team
                  </>
                )}
              </span>
            </button>
          </div>
        </div>
      </div>

      {/* Main Workspace */}
      <div className="relative z-10 flex-1 flex overflow-hidden">
        {/* Left: Agent Chat */}
        <div className="w-1/2 border-r border-gray-800 relative">
          <AgentChat messages={messages} isRunning={isRunning} />
        </div>

        {/* Right: Shared Canvas */}
        <div className="w-1/2 relative">
          <SharedCanvas items={canvasItems} />
        </div>
      </div>

      {/* Bottom: Tool Log */}
      <div className="h-44 border-t border-gray-800 relative z-10 bg-black/60 backdrop-blur-xl">
        <ToolLog toolCalls={toolCalls} />
      </div>
    </div>
  );
}

export default App;