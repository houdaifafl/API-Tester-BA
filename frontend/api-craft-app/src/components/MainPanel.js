import React, { useState } from 'react';
import { FaFileAlt, FaBell } from 'react-icons/fa';

export default function MainPanel() {
  const [activeTab, setActiveTab] = useState('updates');

  return (
    <main className="main-panel">
      <div className="panel-tab-bar">
        <button
          className={`panel-tab ${activeTab === 'docs' ? 'active' : ''}`}
          onClick={() => setActiveTab('docs')}
        >
          <FaFileAlt className="panel-tab-icon" />
          Docs
        </button>
        <button
          className={`panel-tab ${activeTab === 'updates' ? 'active' : ''}`}
          onClick={() => setActiveTab('updates')}
        >
          <FaBell className="panel-tab-icon" />
          Updates
        </button>
      </div>

      <div className="panel-body">
        {activeTab === 'docs' && (
          <p className="panel-empty">Documentation will appear here.</p>
        )}
        {activeTab === 'updates' && (
          <p className="panel-empty">Keep users informed about all new features</p>
        )}
      </div>
    </main>
  );
}
