import React, { useState, useCallback, useRef, useEffect } from 'react';
import { FaTimes } from 'react-icons/fa';
import './ParamsTab.css';

const createRow = () => ({ id: Date.now() + Math.random(), key: '', value: '', description: '' });

export default function HeadersTab({ initialHeaders, onHeadersChange }) {
  const [headers, setHeaders] = useState(() => initialHeaders ?? [createRow()]);

  const onHeadersChangeRef = useRef(onHeadersChange);
  useEffect(() => { onHeadersChangeRef.current = onHeadersChange; });

  const handleChange = useCallback((id, field, value) => {
    setHeaders(prev => {
      const updated = prev.map(r => r.id === id ? { ...r, [field]: value } : r);
      const last = updated[updated.length - 1];
      const isLast = last.id === id;
      const hasContent = last.key || last.value || last.description;
      const next = isLast && hasContent ? [...updated, createRow()] : updated;
      onHeadersChangeRef.current?.(next);
      return next;
    });
  }, []);

  const handleDelete = useCallback((id) => {
    setHeaders(prev => {
      if (prev.length === 1) return prev;
      const next = prev.filter(r => r.id !== id);
      onHeadersChangeRef.current?.(next);
      return next;
    });
  }, []);

  return (
    <div className="params-tab">
      <p className="params-title">Headers</p>
      <table className="params-table">
        <thead>
          <tr>
            <th>Key</th>
            <th>Value</th>
            <th>Description</th>
            <th />
          </tr>
        </thead>
        <tbody>
          {headers.map(row => (
            <tr key={row.id} className="params-row">
              <td>
                <input
                  className="params-input"
                  placeholder="Key"
                  value={row.key}
                  onChange={e => handleChange(row.id, 'key', e.target.value)}
                />
              </td>
              <td>
                <input
                  className="params-input"
                  placeholder="Value"
                  value={row.value}
                  onChange={e => handleChange(row.id, 'value', e.target.value)}
                />
              </td>
              <td>
                <input
                  className="params-input"
                  placeholder="Description"
                  value={row.description}
                  onChange={e => handleChange(row.id, 'description', e.target.value)}
                />
              </td>
              <td className="params-delete-cell">
                {headers.length > 1 && (
                  <button
                    className="params-delete-btn"
                    onClick={() => handleDelete(row.id)}
                    title="Remove row"
                  >
                    <FaTimes />
                  </button>
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
