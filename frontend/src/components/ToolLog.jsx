const TOOL_ICONS = {
    'web_search': '🔍',
    'create_diagram': '📊',
    'write_note': '📝',
    'default': '⚙️'
  };
  
  const TOOL_COLORS = {
    'web_search': {
      bg: 'rgba(192, 192, 192, 0.05)',
      border: 'rgba(192, 192, 192, 0.2)',
      text: '#C0C0C0'
    },
    'create_diagram': {
      bg: 'rgba(168, 168, 168, 0.05)',
      border: 'rgba(168, 168, 168, 0.2)',
      text: '#A8A8A8'
    },
    'write_note': {
      bg: 'rgba(211, 211, 211, 0.05)',
      border: 'rgba(211, 211, 211, 0.2)',
      text: '#D3D3D3'
    },
    'unknown': {
      bg: 'rgba(128, 128, 128, 0.05)',
      border: 'rgba(128, 128, 128, 0.2)',
      text: '#808080'
    }
  };
  
  export default function ToolLog({ toolCalls }) {
    const getToolName = (content) => {
      try {
        const result = JSON.parse(content);
        if (result.query) return 'web_search';
        if (result.diagram_type) return 'create_diagram';
        if (result.type === 'note') return 'write_note';
      } catch (e) {
        // Not JSON
      }
      return 'unknown';
    };
  
    const getToolIcon = (toolName) => {
      return TOOL_ICONS[toolName] || TOOL_ICONS['default'];
    };
  
    const getToolStyle = (toolName) => {
      return TOOL_COLORS[toolName] || TOOL_COLORS['unknown'];
    };
  
    return (
      <div className="h-full flex flex-col bg-black">
        {/* Header */}
        <div className="px-6 py-3 border-b border-gray-800 bg-gray-900/30 backdrop-blur-sm">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-sm font-semibold text-gray-200 tracking-tight">
                Tool Execution Log
              </h2>
              <p className="text-xs text-gray-500 mt-0.5 font-light">MCP tools executed by agents</p>
            </div>
            {toolCalls.length > 0 && (
              <div className="flex items-center gap-2 px-3 py-1 rounded-lg bg-gray-700/10 border border-gray-700/30">
                <span className="text-xs text-gray-400 font-medium">
                  {toolCalls.length} call{toolCalls.length !== 1 ? 's' : ''}
                </span>
              </div>
            )}
          </div>
        </div>
  
        {/* Tool Log */}
        <div className="flex-1 overflow-y-auto p-4 scrollbar-thin">
          {toolCalls.length === 0 && (
            <div className="flex flex-col items-center justify-center h-full text-gray-600">
              <div className="text-3xl mb-2 opacity-20">🛠️</div>
              <p className="text-sm font-light">No tools executed yet</p>
            </div>
          )}
  
          <div className="space-y-2">
            {toolCalls.map((call, idx) => {
              const toolName = getToolName(call.content);
              const icon = getToolIcon(toolName);
              const style = getToolStyle(toolName);
              
              return (
                <div
                  key={idx}
                  className="relative rounded-xl p-3 backdrop-blur-sm hover:scale-[1.01] transition-all duration-200 animate-fadeIn border"
                  style={{
                    background: style.bg,
                    borderColor: style.border,
                    boxShadow: '0 4px 16px rgba(128, 128, 128, 0.05)',
                    animationDelay: `${idx * 0.05}s`
                  }}
                >
                  {/* Silver accent line */}
                  <div 
                    className="absolute left-0 top-0 bottom-0 w-[2px] rounded-l-xl"
                    style={{ backgroundColor: style.text }}
                  ></div>
  
                  <div className="flex items-center justify-between mb-2 pl-2">
                    <div className="flex items-center gap-2.5">
                      <div className="text-lg filter drop-shadow-lg">
                        {icon}
                      </div>
                      <div className="flex items-center gap-2">
                        <span className="font-semibold text-sm text-gray-200">
                          {toolName}
                        </span>
                        <span className="text-gray-600 text-xs">by</span>
                        <span className="text-gray-400 text-xs font-medium">
                          {call.to_agent}
                        </span>
                      </div>
                    </div>
                    <span className="text-xs text-gray-600 font-mono font-light">
                      {new Date(call.timestamp).toLocaleTimeString()}
                    </span>
                  </div>
                  
                  <div className="bg-black/40 rounded-lg p-2 font-mono text-xs text-gray-400 overflow-x-auto max-h-16 overflow-y-auto border border-gray-800/30 scrollbar-thin ml-2 font-light">
                    {call.content}
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>
    );
  }