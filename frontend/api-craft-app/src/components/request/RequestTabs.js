import React from 'react';
import { FaComment } from 'react-icons/fa';

const TABS = ['Docs', 'Params', 'Authorization', 'Headers', 'Body'];

const TAB_KEYS = {
  'Params': 'params',
  'Headers': 'headers',
  'Authorization': 'auth',
  'Body': 'body'
};

export default function RequestTabs({ activeTab, onTabChange, comments = [] }) {
  const getTabCommentCount = (tabName) => {
    const dbTab = TAB_KEYS[tabName];
    if (!dbTab) return 0;
    return comments.filter(c => c.target_tab === dbTab).length;
  };

  return (
    <div className="req-tabs">
      {TABS.map(tab => {
        const count = getTabCommentCount(tab);
        return (
          <button
            key={tab}
            className={`req-tab ${activeTab === tab ? 'active' : ''}`}
            onClick={() => onTabChange(tab)}
            style={{ display: 'inline-flex', alignItems: 'center', gap: '6px' }}
          >
            <span>{tab}</span>
            {count > 0 && (
              <span className="tab-comment-badge" title={`${count} active comments`}>
                <FaComment style={{ fontSize: '0.65rem', marginRight: '2px' }} />
                {count}
              </span>
            )}
          </button>
        );
      })}
    </div>
  );
}
