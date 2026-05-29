import React, { useState, useCallback, useRef, useEffect } from 'react';
import KeyValueTable from '../shared/KeyValueTable';
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
      <KeyValueTable
        rows={headers}
        onRowChange={handleChange}
        onRowDelete={handleDelete}
      />
    </div>
  );
}
