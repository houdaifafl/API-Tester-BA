import React, { useState, useCallback, useRef, useEffect } from 'react';
import { FaComment, FaPlus } from 'react-icons/fa';
import KeyValueTable from '../shared/KeyValueTable';
import './BodyTab.css';

const createFormRow  = () => ({ id: Date.now() + Math.random(), key: '', value: '', description: '', valueType: 'text' });
const createPlainRow = () => ({ id: Date.now() + Math.random(), key: '', value: '', description: '' });

const DEFAULT_BODY = {
  bodyType:   'none',
  formData:   [createFormRow()],
  urlEncoded: [createPlainRow()],
  rawType:    'JSON',
  rawContent: '',
};

const RAW_FORMATS = ['Text', 'JavaScript', 'JSON', 'HTML', 'XML'];

export default function BodyTab({ initialBody, onBodyChange, comments = [], onCommentClick }) {
  const [body, setBody] = useState(() => initialBody ?? DEFAULT_BODY);
  const onBodyChangeRef = useRef(onBodyChange);
  useEffect(() => { onBodyChangeRef.current = onBodyChange; });

  const patch = useCallback((updates) => {
    setBody(prev => {
      const next = { ...prev, ...updates };
      onBodyChangeRef.current?.(next);
      return next;
    });
  }, []);

  const handleTableChange = useCallback((tableKey, id, field, value) => {
    setBody(prev => {
      const isFormData = tableKey === 'formData';
      const table = prev[tableKey];
      const updated = table.map(r => r.id === id ? { ...r, [field]: value } : r);
      const last = updated[updated.length - 1];
      const isLast = last.id === id;
      const hasContent = last.key || last.value || last.description;
      const newRow = isFormData ? createFormRow() : createPlainRow();
      const next = isLast && hasContent ? [...updated, newRow] : updated;
      const result = { ...prev, [tableKey]: next };
      onBodyChangeRef.current?.(result);
      return result;
    });
  }, []);

  const handleTableDelete = useCallback((tableKey, id) => {
    setBody(prev => {
      const table = prev[tableKey];
      if (table.length === 1) return prev;
      const next = table.filter(r => r.id !== id);
      const result = { ...prev, [tableKey]: next };
      onBodyChangeRef.current?.(result);
      return result;
    });
  }, []);

  const tabLevelComments = comments.filter(c => !c.target_key);
  const tabLevelCount = tabLevelComments.length;

  return (
    <div id="comment-target-body" className="body-tab">

      <div className="body-type-row" style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', width: '100%' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          {['none', 'form-data', 'x-www-form-urlencoded', 'raw'].map(type => (
            <label key={type} className="body-radio-label">
              <input
                type="radio"
                className="body-radio"
                name="bodyType"
                value={type}
                checked={body.bodyType === type}
                onChange={() => patch({ bodyType: type })}
              />
              {type}
            </label>
          ))}

          {body.bodyType === 'raw' && (
            <select
              className="body-raw-format-select"
              value={body.rawType}
              onChange={e => patch({ rawType: e.target.value })}
            >
              {RAW_FORMATS.map(f => <option key={f} value={f}>{f}</option>)}
            </select>
          )}
        </div>

        <div className="tab-comment-trigger" style={{ marginRight: '8px', userSelect: 'none' }}>
          {tabLevelCount > 0 ? (
            <button
              type="button"
              className="row-comment-btn has-comments"
              onClick={() => onCommentClick?.(null)}
              title={`${tabLevelCount} comments on body. Click to view.`}
            >
              <FaComment />
              <span className="row-comment-count">{tabLevelCount}</span>
            </button>
          ) : (
            <button
              type="button"
              className="row-comment-btn add-comment"
              onClick={() => onCommentClick?.(null)}
              title="Add comment to Body tab"
            >
              <FaPlus />
            </button>
          )}
        </div>
      </div>

      {body.bodyType === 'none' && (
        <div className="body-none">
          This request does not have a body.
        </div>
      )}

      {body.bodyType === 'form-data' && (
        <div className="body-table-wrap">
          <KeyValueTable
            rows={body.formData}
            showTypeSelector
            onRowChange={(id, field, val) => handleTableChange('formData', id, field, val)}
            onRowDelete={(id) => handleTableDelete('formData', id)}
            comments={comments}
            onCommentClick={onCommentClick}
            tab="body"
          />
        </div>
      )}

      {body.bodyType === 'x-www-form-urlencoded' && (
        <div className="body-table-wrap">
          <KeyValueTable
            rows={body.urlEncoded}
            onRowChange={(id, field, val) => handleTableChange('urlEncoded', id, field, val)}
            onRowDelete={(id) => handleTableDelete('urlEncoded', id)}
            comments={comments}
            onCommentClick={onCommentClick}
            tab="body"
          />
        </div>
      )}

      {body.bodyType === 'raw' && (
        <div className="body-raw-wrap">
          <textarea
            className="body-raw-editor"
            value={body.rawContent}
            onChange={e => patch({ rawContent: e.target.value })}
            spellCheck={false}
            placeholder="Enter request body"
          />
        </div>
      )}

    </div>
  );
}
