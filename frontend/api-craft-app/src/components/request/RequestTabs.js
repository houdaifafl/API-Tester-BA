import React from 'react';

const TABS = ['Docs', 'Params', 'Authorization', 'Headers', 'Body'];

export default function RequestTabs({ activeTab, onTabChange }) {
  return (
    <div className="req-tabs">
      {TABS.map(tab => (
        <button
          key={tab}
          className={`req-tab ${activeTab === tab ? 'active' : ''}`}
          onClick={() => onTabChange(tab)}
        >
          {tab}
        </button>
      ))}
    </div>
  );
}
