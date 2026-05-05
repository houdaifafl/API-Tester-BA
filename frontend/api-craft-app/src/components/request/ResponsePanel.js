import React, { useState, useRef, useEffect } from 'react';
import { FaHistory, FaChevronDown } from 'react-icons/fa';

const MIN_HEIGHT = 60;
const MAX_HEIGHT = 400;
const DEFAULT_HEIGHT = 120;

export default function ResponsePanel({ initialHeight, onHeightChange }) {
  const [height, setHeight] = useState(initialHeight ?? DEFAULT_HEIGHT);
  const isResizing = useRef(false);
  const startY = useRef(0);
  const startHeight = useRef(0);
  const onHeightChangeRef = useRef(onHeightChange);

  useEffect(() => {
    onHeightChangeRef.current = onHeightChange;
  });

  const handleResizeStart = (e) => {
    isResizing.current = true;
    startY.current = e.clientY;
    startHeight.current = height;
    document.body.style.cursor = 'row-resize';
    document.body.style.userSelect = 'none';
    e.preventDefault();
  };

  useEffect(() => {
    const handleMouseMove = (e) => {
      if (!isResizing.current) return;
      const delta = startY.current - e.clientY;
      const newHeight = Math.min(Math.max(startHeight.current + delta, MIN_HEIGHT), MAX_HEIGHT);
      setHeight(newHeight);
      onHeightChangeRef.current?.(newHeight);
    };
    const handleMouseUp = () => {
      if (!isResizing.current) return;
      isResizing.current = false;
      document.body.style.cursor = '';
      document.body.style.userSelect = '';
    };
    document.addEventListener('mousemove', handleMouseMove);
    document.addEventListener('mouseup', handleMouseUp);
    return () => {
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseup', handleMouseUp);
    };
  }, []);

  return (
    <div className="response-panel" style={{ height }}>
      <div className="response-resize-handle" onMouseDown={handleResizeStart} />
      <div className="response-header">
        <span className="response-title">Response</span>
        <button className="history-btn">
          <FaHistory className="history-icon" />
          History
          <FaChevronDown className="history-caret" />
        </button>
      </div>
      <div className="response-body" />
    </div>
  );
}
