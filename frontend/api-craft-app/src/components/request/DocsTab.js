import React, { useState } from 'react';

export default function DocsTab({ value: initialValue, onChange }) {
  const [text, setText] = useState(initialValue ?? '');

  const handleChange = (e) => {
    setText(e.target.value);
    onChange?.(e.target.value);
  };

  return (
    <div className="docs-content">
      <textarea
        className="docs-textarea"
        placeholder="Document this request..."
        value={text}
        onChange={handleChange}
        spellCheck={false}
      />
    </div>
  );
}
