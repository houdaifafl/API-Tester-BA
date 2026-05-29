import React from 'react';
import { FaTimes } from 'react-icons/fa';
import './KeyValueTable.css';

export default function KeyValueTable({ rows, onRowChange, onRowDelete, showTypeSelector = false }) {
  return (
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
        {rows.map(row => (
          <tr key={row.id} className="params-row">
            <td>
              <div className={showTypeSelector ? 'kv-key-cell' : undefined}>
                <input
                  className="params-input"
                  placeholder="Key"
                  value={row.key}
                  onChange={e => onRowChange(row.id, 'key', e.target.value)}
                />
                {showTypeSelector && (
                  <select
                    className="kv-value-type"
                    value={row.valueType}
                    onChange={e => onRowChange(row.id, 'valueType', e.target.value)}
                  >
                    <option value="text">Text</option>
                    <option value="file">File</option>
                  </select>
                )}
              </div>
            </td>
            <td>
              {showTypeSelector && row.valueType === 'file' ? (
                <span className="kv-file-placeholder">Select file</span>
              ) : (
                <input
                  className="params-input"
                  placeholder="Value"
                  value={row.value}
                  onChange={e => onRowChange(row.id, 'value', e.target.value)}
                />
              )}
            </td>
            <td>
              <input
                className="params-input"
                placeholder="Description"
                value={row.description}
                onChange={e => onRowChange(row.id, 'description', e.target.value)}
              />
            </td>
            <td className="params-delete-cell">
              {rows.length > 1 && (
                <button
                  className="params-delete-btn"
                  onClick={() => onRowDelete(row.id)}
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
  );
}
