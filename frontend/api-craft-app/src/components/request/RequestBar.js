import React, { useState, useEffect } from 'react';

const METHOD_COLORS = {
  GET: '#49cc90',
  POST: '#f6851b',
  PUT: '#e6a817',
  DELETE: '#e74c3c',
  PATCH: '#9b59b6',
};

const METHODS = ['GET', 'POST', 'PUT', 'DELETE', 'PATCH'];

export default function RequestBar({ method: initialMethod = 'GET' }) {
  const [method, setMethod] = useState(initialMethod);

  useEffect(() => {
    setMethod(initialMethod);
  }, [initialMethod]);

  return (
    <div className="req-bar">
      <select
        className="req-method-select"
        value={method}
        onChange={e => setMethod(e.target.value)}
        style={{ color: METHOD_COLORS[method] }}
      >
        {METHODS.map(m => (
          <option key={m} value={m}>{m}</option>
        ))}
      </select>
      <input
        className="req-url-input"
        placeholder="Enter URL or paste text"
      />
      <button className="req-send-btn">Send</button>
    </div>
  );
}
