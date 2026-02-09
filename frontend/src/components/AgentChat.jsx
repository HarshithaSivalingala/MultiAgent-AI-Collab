import { useEffect, useRef } from 'react';

const AGENT_COLORS = {
  'Planner': {
    accent: '#C0C0C0', // Silver
    bg: 'rgba(192, 192, 192, 0.05)',
    border: 'rgba(192, 192, 192, 0.2)',
    shadow: '0 4px 20px rgba(192, 192, 192, 0.1)'
  },
  'Researcher': {
    accent: '#A8A8A8', // Light gray
    bg: 'rgba(168, 168, 168, 0.05)',
    border: 'rgba(168, 168, 168, 0.2)',
    shadow: '0 4px 20px rgba(168, 168, 168, 0.1)'
  },
  'Builder': {
    accent: '#D3D3D3', // Lighter silver
    bg: 'rgba(211, 211, 211, 0.05)',
    border: 'rgba(211, 211, 211, 0.2)',
    shadow: '0 4px 20px rgba(211, 211, 211, 0.1)'
  },
  'Critic': {
    accent: '#B0B0B0', // Medium gray
    bg: 'rgba(176, 176, 176, 0.05)',
    border: 'rgba(176, 176, 176, 0.2)',
    shadow: '0 4px 20px rgba(176, 176, 176, 0.1)'
  },
  'User': {
    accent: '#909090',
    bg: 'rgba(144, 144, 144, 0.05)',
    border: 'rgba(144, 144, 144, 0.2)',
    shadow: '0 4px 20px rgba(144, 144, 144, 0.1)'
  },
  'System': {
    accent: '#808080',
    bg: 'rgba(128, 128, 128, 0.05)',
    border: 'rgba(128, 128, 128, 0.2)',
    shadow: '0 4px 20px rgba(128, 128, 128, 0.1)'
  }
};

const AGENT_ICONS = {
  'Planner': '🧭',
  'Researcher': '🧠',
  'Builder': '🧑‍💻',
  'Critic': '🔍',
  'User': '👤',
  'System': '⚙️'
};

export default function AgentChat({ messages, isRunning }) {
  const scrollRef = useRef(null);

  useEffect(() => {
    scrollRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const getAgentStyle = (agentName) => {
    return AGENT_COLORS[agentName] || AGENT_COLORS['System'];
  };

  return (
    <div className="h-full flex flex-col bg-black">
      {/* Header */}
      <div className="px-6 py-4 border-b border-gray-800 bg-gray-900/30 backdrop-blur-sm">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-lg font-semibold tracking-tight text-gray-200">
              Agent Collaboration
            </h2>
            <p className="text-xs text-gray-500 mt-0.5 font-light">Live multi-agent conversation</p>
          </div>
          {isRunning && (
            <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-green-500/10 border border-green-500/20">
              <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse shadow-lg shadow-green-400/50"></div>
              <span className="text-xs text-green-400 font-medium">Active</span>
            </div>
          )}
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-6 space-y-4 scrollbar-thin">
        {messages.length === 0 && (
          <div className="flex flex-col items-center justify-center h-full text-gray-600">
            <div className="relative mb-4">
              <div className="text-6xl opacity-20">💬</div>
              <div className="absolute inset-0 blur-2xl bg-gray-500/10"></div>
            </div>
            <p className="text-sm font-light">Waiting for agents to start...</p>
            <p className="text-xs mt-2 text-gray-700">Enter a prompt and click "Start Team"</p>
          </div>
        )}

        {messages.map((msg, idx) => {
          const style = getAgentStyle(msg.from_agent);
          
          return (
            <div
              key={idx}
              className="relative rounded-xl p-4 transition-all duration-300 hover:scale-[1.01] animate-fadeIn border"
              style={{
                background: style.bg,
                borderColor: style.border,
                boxShadow: style.shadow,
                animationDelay: `${idx * 0.05}s`
              }}
            >
              {/* Silver line accent */}
              <div 
                className="absolute left-0 top-0 bottom-0 w-1 rounded-l-xl"
                style={{ backgroundColor: style.accent }}
              ></div>

              {/* Agent Header */}
              <div className="flex items-center justify-between mb-3 pl-3">
                <div className="flex items-center gap-3">
                  <div className="text-2xl filter drop-shadow-lg">
                    {AGENT_ICONS[msg.from_agent] || '🤖'}
                  </div>
                  <div>
                    <span className="font-semibold text-gray-200">
                      {msg.from_agent}
                    </span>
                    {msg.to_agent && (
                      <div className="flex items-center gap-1.5 mt-0.5">
                        <span className="text-gray-600 text-xs">→</span>
                        <span className="text-xs text-gray-500">
                          {AGENT_ICONS[msg.to_agent]} {msg.to_agent}
                        </span>
                      </div>
                    )}
                  </div>
                </div>
                <div className="flex flex-col items-end gap-1">
                  <span className="text-xs text-gray-600 font-mono font-light">
                    {new Date(msg.timestamp).toLocaleTimeString()}
                  </span>
                  <span className="text-xs px-2 py-0.5 rounded-md bg-gray-800/50 text-gray-500 border border-gray-700/50 font-light">
                    {msg.type}
                  </span>
                </div>
              </div>

              {/* Message Content */}
              <div className="text-sm text-gray-300 leading-relaxed whitespace-pre-wrap font-mono bg-black/30 rounded-lg p-3 border border-gray-800/50 ml-3 font-light">
                {msg.content}
              </div>
            </div>
          );
        })}

        <div ref={scrollRef} />
      </div>
    </div>
  );
}