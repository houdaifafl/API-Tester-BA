import React, { useState } from 'react';
import { FaFileAlt, FaBell, FaHistory } from 'react-icons/fa';
import ActivityLogTab from './ActivityLogTab';
import './OverviewPanel.css';

export default function OverviewPanel({ workspaceId, workspaceRole }) {
  const [activeTab, setActiveTab] = useState('docs');

  return (
    <>
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
        <button
          className={`panel-tab ${activeTab === 'activities' ? 'active' : ''}`}
          onClick={() => setActiveTab('activities')}
        >
          <FaHistory className="panel-tab-icon" />
          Activity Log
        </button>
      </div>

      <div className="panel-body">
        {activeTab === 'docs' && (
          <div className="overview-docs">
            <p>This tool enables you to create and send HTTP requests to any API endpoint.</p>
            <p>
              You can choose the request method, enter a URL, and optionally configure
              headers or request data. After sending a request, the system displays the
              response, including status, execution time, and returned content.
            </p>
            <p>This helps you test, debug, and understand how APIs behave in different scenarios.</p>
          </div>
        )}
        {activeTab === 'updates' && (
          <div className="overview-docs">
            <p>Keep users informed about all new features</p>
          </div>
        )}
        {activeTab === 'activities' && (
          <ActivityLogTab workspaceId={workspaceId} workspaceRole={workspaceRole} />
        )}
      </div>
    </>
  );
}
