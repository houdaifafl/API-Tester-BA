import React from 'react';
import { FaTimes, FaComment, FaPlus } from 'react-icons/fa';
import './KeyValueTable.css';

export default function KeyValueTable({
  rows,
  onRowChange,
  onRowDelete,
  showTypeSelector = false,
  comments = [],
  onCommentClick,
  tab = 'params'
}) {
  return (
    <table className="params-table">
      <thead>
        <tr>
          <th>Key</th>
          <th>Value</th>
          <th>Description</th>
          <th style={{ width: '45px' }} />
          <th style={{ width: '30px' }} />
        </tr>
      </thead>
      <tbody>
        {rows.map(row => {
          const trimmedKey = row.key ? row.key.trim() : '';
          const keyCount = trimmedKey ? comments.filter(c => c.target_key === trimmedKey).length : 0;

          return (
            <tr key={row.id} className="params-row">
              <td>
                <div className={showTypeSelector ? 'kv-key-cell' : undefined}>
                  <input
                    id={trimmedKey ? `comment-target-${tab}-${trimmedKey}` : undefined}
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
              <td className="params-comment-cell" style={{ textAlign: 'center', verticalAlign: 'middle' }}>
                {trimmedKey && (
                  keyCount > 0 ? (
                    <button
                      type="button"
                      className="row-comment-btn has-comments"
                      onClick={() => onCommentClick?.(trimmedKey)}
                      title={`${keyCount} comments. Click to view.`}
                    >
                      <FaComment />
                      <span className="row-comment-count">{keyCount}</span>
                    </button>
                  ) : (
                    <button
                      type="button"
                      className="row-comment-btn add-comment"
                      onClick={() => onCommentClick?.(trimmedKey)}
                      title="Add comment"
                    >
                      <FaPlus />
                    </button>
                  )
                )}
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
          );
        })}
      </tbody>
    </table>
  );
}
