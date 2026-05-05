import React, { useState, useCallback, useRef, useEffect } from 'react';
import { FaTimes } from 'react-icons/fa';
import './ParamsTab.css';

const createRow = () => ({ id: Date.now() + Math.random(), key: '', value: '', description: '' });

export default function ParamsTab({ initialParams, onParamsChange }) {
  const [params, setParams] = useState(() => initialParams ?? [createRow()]);

  const onParamsChangeRef = useRef(onParamsChange);
  useEffect(() => { onParamsChangeRef.current = onParamsChange; });

  const handleChange = useCallback((id, field, value) => {
    setParams(prev => {
      const updated = prev.map(p => p.id === id ? { ...p, [field]: value } : p);
      const last = updated[updated.length - 1];
      const isLast = last.id === id;
      const hasContent = last.key || last.value || last.description;
      const next = isLast && hasContent ? [...updated, createRow()] : updated;
      onParamsChangeRef.current?.(next);
      return next;
    });
  }, []);

  const handleDelete = useCallback((id) => {
    setParams(prev => {
      if (prev.length === 1) return prev;
      const next = prev.filter(p => p.id !== id);
      onParamsChangeRef.current?.(next);
      return next;
    });
  }, []);

  return (
    <div className="params-tab">
      <p className="params-title">Query Params</p>
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
          {params.map(row => (
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
                {params.length > 1 && (
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
