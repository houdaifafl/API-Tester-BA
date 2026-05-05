import React, { useEffect, useRef } from 'react';
import './RequestContextMenu.css';

export default function RequestContextMenu({ anchorRect, onRename, onDelete, onClose }) {
  const ref = useRef(null);

  useEffect(() => {
    const handleMouseDown = (e) => {
      if (ref.current && !ref.current.contains(e.target)) onClose();
    };
    document.addEventListener('mousedown', handleMouseDown);
    return () => document.removeEventListener('mousedown', handleMouseDown);
  }, [onClose]);

  return (
    <div
      className="req-ctx-menu"
      ref={ref}
      style={{ top: anchorRect.top, left: anchorRect.right + 6 }}
    >
      <button
        className="req-ctx-item"
        onClick={() => { onRename(); onClose(); }}
      >
        Rename
      </button>
      {onDelete && (
        <>
          <div className="req-ctx-divider" />
          <button
            className="req-ctx-item req-ctx-delete"
            onClick={() => { onDelete(); onClose(); }}
          >
            Delete
          </button>
        </>
      )}
    </div>
  );
}
