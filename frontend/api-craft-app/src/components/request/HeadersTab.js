import React, { useState, useCallback, useRef, useEffect } from 'react';
import { FaComment, FaPlus } from 'react-icons/fa';
import KeyValueTable from '../shared/KeyValueTable';
import './ParamsTab.css';

const createRow = () => ({ id: Date.now() + Math.random(), key: '', value: '', description: '' });

export default function HeadersTab({ initialHeaders, onHeadersChange, comments = [], onCommentClick }) {
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

  const tabLevelComments = comments.filter(c => !c.target_key);
  const tabLevelCount = tabLevelComments.length;

  return (
    <div id="comment-target-headers" className="params-tab">
      <div className="tab-header-row" style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '10px' }}>
        <p className="params-title" style={{ margin: 0 }}>Headers</p>
        <div className="tab-comment-trigger" style={{ userSelect: 'none' }}>
          {tabLevelCount > 0 ? (
            <button
              type="button"
              className="row-comment-btn has-comments"
              onClick={() => onCommentClick?.(null)}
              title={`${tabLevelCount} comments on headers. Click to view.`}
            >
              <FaComment />
              <span className="row-comment-count">{tabLevelCount}</span>
            </button>
          ) : (
            <button
              type="button"
              className="row-comment-btn add-comment"
              onClick={() => onCommentClick?.(null)}
              title="Add comment to Headers tab"
            >
              <FaPlus />
            </button>
          )}
        </div>
      </div>
      <KeyValueTable
        rows={headers}
        onRowChange={handleChange}
        onRowDelete={handleDelete}
        comments={comments}
        onCommentClick={onCommentClick}
        tab="headers"
      />
    </div>
  );
}
