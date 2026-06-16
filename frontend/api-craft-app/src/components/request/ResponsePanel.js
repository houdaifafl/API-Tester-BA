import React, { useState, useRef, useEffect } from 'react';

const MIN_HEIGHT     = 60;
const MAX_HEIGHT     = 500;
const DEFAULT_HEIGHT = 200;

function statusClass(code) {
  if (code >= 200 && code < 300) return 'resp-status-ok';
  if (code >= 300 && code < 400) return 'resp-status-redirect';
  if (code >= 400 && code < 500) return 'resp-status-client-err';
  return 'resp-status-server-err';
}

function formatData(data) {
  if (data === null || data === undefined) return '';
  if (typeof data === 'string') return data;
  return JSON.stringify(data, null, 2);
}

export default function ResponsePanel({ initialHeight, onHeightChange, response, loading }) {
  const [height, setHeight]     = useState(initialHeight ?? DEFAULT_HEIGHT);
  const isResizing              = useRef(false);
  const startY                  = useRef(0);
  const startHeight             = useRef(0);
  const onHeightChangeRef       = useRef(onHeightChange);

  useEffect(() => { onHeightChangeRef.current = onHeightChange; });

  const handleResizeStart = (e) => {
    isResizing.current    = true;
    startY.current        = e.clientY;
    startHeight.current   = height;
    document.body.style.cursor     = 'row-resize';
    document.body.style.userSelect = 'none';
    e.preventDefault();
  };

  useEffect(() => {
    const handleMouseMove = (e) => {
      if (!isResizing.current) return;
      const delta     = startY.current - e.clientY;
      const newHeight = Math.min(Math.max(startHeight.current + delta, MIN_HEIGHT), MAX_HEIGHT);
      setHeight(newHeight);
      onHeightChangeRef.current?.(newHeight);
    };
    const handleMouseUp = () => {
      if (!isResizing.current) return;
      isResizing.current             = false;
      document.body.style.cursor     = '';
      document.body.style.userSelect = '';
    };
    document.addEventListener('mousemove', handleMouseMove);
    document.addEventListener('mouseup',   handleMouseUp);
    return () => {
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseup',   handleMouseUp);
    };
  }, []);

  const renderBody = () => {
    if (loading) {
      return <div className="resp-empty">Sending request…</div>;
    }
    if (!response) {
      return <div className="resp-empty">Enter a URL and click Send to get a response.</div>;
    }
    if (response.error) {
      return (
        <div className="resp-error-wrap">
          <span className="resp-error-label">Error</span>
          <pre className="resp-pre">{response.error}</pre>
        </div>
      );
    }
    return (
      <>
        <div className="resp-meta">
          <span className={`resp-status ${statusClass(response.status)}`}>
            {response.status}
          </span>
          <span className="resp-time">{response.response_time} ms</span>
        </div>
        <div className="resp-data">
          <pre className="resp-pre">{formatData(response.data)}</pre>
        </div>
      </>
    );
  };

  return (
    <div className="response-panel" style={{ height }}>
      <div className="response-resize-handle" onMouseDown={handleResizeStart} />
      <div className="response-header">
        <span className="response-title">Response</span>
      </div>
      <div className="response-body">
        {renderBody()}
      </div>
    </div>
  );
}
