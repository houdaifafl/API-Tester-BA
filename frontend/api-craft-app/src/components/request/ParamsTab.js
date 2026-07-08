import React, { useState, useCallback, useRef, useEffect } from 'react';
import { FaComment, FaPlus } from 'react-icons/fa';
import KeyValueTable from '../shared/KeyValueTable';
import './ParamsTab.css';

const createRow = () => ({ id: Date.now() + Math.random(), key: '', value: '', description: '' });

export default function ParamsTab({ initialParams, onParamsChange, comments = [], onCommentClick }) {
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

  const tabLevelComments = comments.filter(c => !c.target_key);
  const tabLevelCount = tabLevelComments.length;

  return (
    <div id="comment-target-params" className="params-tab">
      <div className="tab-header-row" style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '10px' }}>
        <p className="params-title" style={{ margin: 0 }}>Query Params</p>
        <div className="tab-comment-trigger" style={{ userSelect: 'none' }}>
          {tabLevelCount > 0 ? (
            <button
              type="button"
              className="row-comment-btn has-comments"
              onClick={() => onCommentClick?.(null)}
              title={`${tabLevelCount} comments on params. Click to view.`}
            >
              <FaComment />
              <span className="row-comment-count">{tabLevelCount}</span>
            </button>
          ) : (
            <button
              type="button"
              className="row-comment-btn add-comment"
              onClick={() => onCommentClick?.(null)}
              title="Add comment to Params tab"
            >
              <FaPlus />
            </button>
          )}
        </div>
      </div>
      <KeyValueTable
        rows={params}
        onRowChange={handleChange}
        onRowDelete={handleDelete}
        comments={comments}
        onCommentClick={onCommentClick}
        tab="params"
      />
    </div>
  );
}
