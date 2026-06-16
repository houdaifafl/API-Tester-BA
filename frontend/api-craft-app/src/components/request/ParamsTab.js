import React, { useState, useCallback, useRef, useEffect } from 'react';
import KeyValueTable from '../shared/KeyValueTable';
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
      <KeyValueTable
        rows={params}
        onRowChange={handleChange}
        onRowDelete={handleDelete}
      />
    </div>
  );
}
