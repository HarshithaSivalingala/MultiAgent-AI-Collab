import { useEffect, useRef, useState } from 'react';
import mermaid from 'mermaid';

// Initialize mermaid with dark theme
mermaid.initialize({ 
  startOnLoad: false,
  theme: 'dark',
  themeVariables: {
    darkMode: true,
    background: '#000000',
    primaryColor: '#C0C0C0',
    primaryTextColor: '#E0E0E0',
    primaryBorderColor: '#808080',
    lineColor: '#A0A0A0',
    secondaryColor: '#909090',
    tertiaryColor: '#B0B0B0',
    fontSize: '14px'
  }
});

function DiagramItem({ code, description }) {
  const diagramRef = useRef(null);
  const containerRef = useRef(null);
  const [zoom, setZoom] = useState(0.7); // Start at 70% to fit most diagrams
  const [position, setPosition] = useState({ x: 0, y: 0 });
  const [isDragging, setIsDragging] = useState(false);
  const [dragStart, setDragStart] = useState({ x: 0, y: 0 });

  useEffect(() => {
    if (diagramRef.current) {
      const id = `mermaid-${Math.random().toString(36).substr(2, 9)}`;
      mermaid.render(id, code).then(({ svg }) => {
        diagramRef.current.innerHTML = svg;
        
        // Auto-fit after rendering
        setTimeout(() => {
          autoFitDiagram();
        }, 100);
      }).catch(error => {
        console.error('Mermaid error:', error);
        diagramRef.current.innerHTML = '<p class="text-red-400">Failed to render diagram</p>';
      });
    }
  }, [code]);

  const autoFitDiagram = () => {
    if (diagramRef.current && containerRef.current) {
      const svgElement = diagramRef.current.querySelector('svg');
      if (svgElement) {
        const svgWidth = svgElement.width.baseVal.value || svgElement.getBBox().width;
        const svgHeight = svgElement.height.baseVal.value || svgElement.getBBox().height;
        const containerWidth = containerRef.current.offsetWidth - 48; // Minus padding
        const containerHeight = containerRef.current.offsetHeight - 48;
        
        // Calculate zoom to fit
        const scaleX = containerWidth / svgWidth;
        const scaleY = containerHeight / svgHeight;
        const fitZoom = Math.min(scaleX, scaleY, 1) * 0.9; // 90% to add padding
        
        setZoom(Math.max(0.3, Math.min(fitZoom, 1))); // Between 30% and 100%
        setPosition({ x: 0, y: 0 });
      }
    }
  };

  const handleZoomIn = () => {
    setZoom(prev => Math.min(prev + 0.15, 3)); // Max 3x zoom
  };

  const handleZoomOut = () => {
    setZoom(prev => Math.max(prev - 0.15, 0.3)); // Min 0.3x zoom
  };

  const handleResetZoom = () => {
    setZoom(1);
    setPosition({ x: 0, y: 0 });
  };

  const handleFitToScreen = () => {
    autoFitDiagram();
  };

  const handleMouseDown = (e) => {
    if (e.button === 0) { // Left click only
      setIsDragging(true);
      setDragStart({
        x: e.clientX - position.x,
        y: e.clientY - position.y
      });
    }
  };

  const handleMouseMove = (e) => {
    if (isDragging) {
      setPosition({
        x: e.clientX - dragStart.x,
        y: e.clientY - dragStart.y
      });
    }
  };

  const handleMouseUp = () => {
    setIsDragging(false);
  };

  const handleWheel = (e) => {
    e.preventDefault();
    const delta = e.deltaY > 0 ? -0.1 : 0.1;
    setZoom(prev => Math.max(0.3, Math.min(3, prev + delta)));
  };

  return (
    <div className="group relative bg-gray-900/50 rounded-2xl p-6 border border-gray-800 backdrop-blur-sm hover:border-gray-700 transition-all duration-300 animate-fadeIn"
      style={{ boxShadow: '0 8px 32px rgba(192, 192, 192, 0.05)' }}>
      
      {/* Silver top accent */}
      <div className="absolute top-0 left-0 right-0 h-[1px] bg-gradient-to-r from-transparent via-gray-500 to-transparent opacity-50"></div>
      
      <div className="relative">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-gray-800/50 border border-gray-700">
              <span className="text-2xl">📊</span>
            </div>
            <div>
              <h3 className="font-semibold text-lg text-gray-200 tracking-tight">
                System Architecture
              </h3>
              {description && (
                <p className="text-sm text-gray-500 mt-0.5 font-light">{description}</p>
              )}
            </div>
          </div>

          {/* Zoom Controls */}
          <div className="flex items-center gap-2 bg-gray-900/80 rounded-lg p-1 border border-gray-700">
            <button
              onClick={handleZoomOut}
              className="p-2 rounded hover:bg-gray-800 transition-colors group/btn"
              title="Zoom Out"
            >
              <svg className="w-4 h-4 text-gray-400 group-hover/btn:text-gray-200" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0zM13 10H7" />
              </svg>
            </button>
            
            <span className="text-xs text-gray-400 font-mono w-12 text-center">
              {Math.round(zoom * 100)}%
            </span>
            
            <button
              onClick={handleZoomIn}
              className="p-2 rounded hover:bg-gray-800 transition-colors group/btn"
              title="Zoom In"
            >
              <svg className="w-4 h-4 text-gray-400 group-hover/btn:text-gray-200" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0zM10 7v3m0 0v3m0-3h3m-3 0H7" />
              </svg>
            </button>
            
            <div className="w-px h-6 bg-gray-700"></div>
            
            <button
              onClick={handleFitToScreen}
              className="p-2 rounded hover:bg-gray-800 transition-colors group/btn bg-gray-800/50"
              title="Fit to Screen (Auto-fit)"
            >
              <svg className="w-4 h-4 text-gray-300 group-hover/btn:text-gray-100" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 8V4m0 0h4M4 4l5 5m11-1V4m0 0h-4m4 0l-5 5M4 16v4m0 0h4m-4 0l5-5m11 5l-5-5m5 5v-4m0 4h-4" />
              </svg>
            </button>
            
            <button
              onClick={handleResetZoom}
              className="p-2 rounded hover:bg-gray-800 transition-colors group/btn"
              title="Reset (100%)"
            >
              <svg className="w-4 h-4 text-gray-400 group-hover/btn:text-gray-200" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
              </svg>
            </button>
          </div>
        </div>
        
        <div 
          ref={containerRef}
          onMouseDown={handleMouseDown}
          onMouseMove={handleMouseMove}
          onMouseUp={handleMouseUp}
          onMouseLeave={handleMouseUp}
          onWheel={handleWheel}
          className={`bg-black/40 rounded-xl p-6 border border-gray-800/50 backdrop-blur-sm relative flex items-center justify-center ${isDragging ? 'cursor-grabbing' : 'cursor-grab'}`}
          style={{ 
            height: '650px',
            overflow: 'hidden'
          }}
        >
          <div
            ref={diagramRef}
            style={{
              transform: `scale(${zoom}) translate(${position.x / zoom}px, ${position.y / zoom}px)`,
              transformOrigin: 'center center',
              transition: isDragging ? 'none' : 'transform 0.2s ease-out',
              maxWidth: 'none',
              maxHeight: 'none'
            }}
            className="inline-block"
          />
          
          {/* Helper text */}
          <div className="absolute bottom-3 left-1/2 transform -translate-x-1/2 text-xs text-gray-600 bg-gray-900/90 px-3 py-1.5 rounded-lg border border-gray-800 font-light backdrop-blur-sm">
            💡 Scroll to zoom • Drag to pan • Click ⛶ to fit entire diagram
          </div>
        </div>
      </div>

      {/* Silver bottom glow */}
      <div className="absolute bottom-0 left-0 right-0 h-[1px] bg-gradient-to-r from-transparent via-gray-600 to-transparent opacity-30"></div>
    </div>
  );
}

function NoteItem({ content }) {
  return (
    <div className="group relative bg-gray-900/50 rounded-2xl p-6 border border-gray-800 backdrop-blur-sm hover:border-gray-700 transition-all duration-300 hover:scale-[1.01] animate-fadeIn"
      style={{ boxShadow: '0 8px 32px rgba(192, 192, 192, 0.05)' }}>
      
      {/* Silver top accent */}
      <div className="absolute top-0 left-0 right-0 h-[1px] bg-gradient-to-r from-transparent via-gray-500 to-transparent opacity-50"></div>
      
      <div className="relative">
        <div className="flex items-center gap-3 mb-4">
          <div className="p-2 rounded-lg bg-gray-800/50 border border-gray-700">
            <span className="text-2xl">📝</span>
          </div>
          <h3 className="font-semibold text-lg text-gray-200 tracking-tight">
            Note
          </h3>
        </div>
        
        <div className="text-sm text-gray-300 leading-relaxed whitespace-pre-wrap bg-black/30 rounded-xl p-4 border border-gray-800/30 font-light">
          {content}
        </div>
      </div>

      {/* Silver bottom glow */}
      <div className="absolute bottom-0 left-0 right-0 h-[1px] bg-gradient-to-r from-transparent via-gray-600 to-transparent opacity-30"></div>
    </div>
  );
}

export default function SharedCanvas({ items }) {
  return (
    <div className="h-full flex flex-col bg-black">
      {/* Header */}
      <div className="px-6 py-4 border-b border-gray-800 bg-gray-900/30 backdrop-blur-sm">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-lg font-semibold tracking-tight text-gray-200">
              Shared Workspace
            </h2>
            <p className="text-xs text-gray-500 mt-0.5 font-light">Collaborative outputs from the team</p>
          </div>
          {items.length > 0 && (
            <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-gray-700/10 border border-gray-700/30">
              <span className="text-xs text-gray-400 font-medium">{items.length} item{items.length !== 1 ? 's' : ''}</span>
            </div>
          )}
        </div>
      </div>

      {/* Canvas Content */}
      <div className="flex-1 overflow-y-auto p-6 space-y-6 scrollbar-thin">
        {items.length === 0 && (
          <div className="flex flex-col items-center justify-center h-full text-gray-600">
            <div className="relative mb-4">
              <div className="text-6xl opacity-20">🎨</div>
              <div className="absolute inset-0 blur-2xl bg-gray-500/10"></div>
            </div>
            <p className="text-sm font-light">Waiting for content...</p>
            <p className="text-xs mt-2 text-gray-700 text-center max-w-md font-light">
              Diagrams and outputs will appear here as agents create them
            </p>
          </div>
        )}

        {items.map((item, idx) => (
          <div key={idx}>
            {item.type === 'diagram' && (
              <DiagramItem code={item.code} description={item.description} />
            )}
            {item.type === 'note' && (
              <NoteItem content={item.content} />
            )}
          </div>
        ))}
      </div>
    </div>
  );
}