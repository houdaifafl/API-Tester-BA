import React, { useState, useRef, useEffect, useCallback } from 'react';
import { FaChevronDown } from 'react-icons/fa';

const METHOD_COLORS = {
  GET:    '#49cc90',
  POST:   '#e74c3c',
  PUT:    '#4a90e2',
  DELETE: '#795548',
};

const METHODS = ['GET', 'POST', 'PUT', 'DELETE'];

export default function RequestBar({ method: initialMethod = 'GET', onMethodChange }) {
  const [method, setMethod] = useState(initialMethod);
  const [dropdownOpen, setDropdownOpen] = useState(false);
  const wrapperRef = useRef(null);

  useEffect(() => {
    setMethod(initialMethod);
  }, [initialMethod]);

  useEffect(() => {
    if (!dropdownOpen) return;
    const handler = (e) => {
      if (wrapperRef.current && !wrapperRef.current.contains(e.target)) {
        setDropdownOpen(false);
      }
    };
    document.addEventListener('mousedown', handler);
    return () => document.removeEventListener('mousedown', handler);
  }, [dropdownOpen]);

  const handleSelect = useCallback((m) => {
    setMethod(m);
    setDropdownOpen(false);
    onMethodChange?.(m);
  }, [onMethodChange]);

  return (
    <div className="req-bar">
      <div className="req-method-wrapper" ref={wrapperRef}>
        <button
          className="req-method-btn"
          style={{ color: METHOD_COLORS[method] }}
          onClick={() => setDropdownOpen(o => !o)}
        >
          {method}
          <FaChevronDown className="req-method-caret" />
        </button>
        {dropdownOpen && (
          <div className="req-method-dropdown">
            {METHODS.map(m => (
              <button
                key={m}
                className={`req-method-option${m === method ? ' req-method-option-active' : ''}`}
                onClick={() => handleSelect(m)}
              >
                <span style={{ color: METHOD_COLORS[m] }}>{m}</span>
              </button>
            ))}
          </div>
        )}
      </div>
      <input
        className="req-url-input"
        placeholder="Enter URL or paste text"
      />
      <button className="req-send-btn">Send</button>
    </div>
  );
}
