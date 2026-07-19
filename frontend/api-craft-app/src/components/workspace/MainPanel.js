import React from 'react';
import RequestBuilder from '../request/RequestBuilder';
import OverviewPanel from './OverviewPanel';
import AnalyticsDashboard from './AnalyticsDashboard';

export default function MainPanel({ activeTab, responseHeights, requestStates, onMethodChange, onSaveRequest, onExecute, workspaceRole, comments = [], onCommentClick, workspaceId }) {
  if (activeTab.type === 'request' || activeTab.type === 'history') {
    const tabId = activeTab.id;
    const savedState = requestStates.current[tabId];
    const handleStateChange = (patch) => {
      requestStates.current[tabId] = { ...requestStates.current[tabId], ...patch };
    };

    return (
      <main className="main-panel">
        <RequestBuilder
          key={tabId}
          request={activeTab}
          initialResponseHeight={responseHeights.current[tabId]}
          onResponseHeightChange={(h) => { responseHeights.current[tabId] = h; }}
          savedState={savedState}
          onStateChange={handleStateChange}
          onMethodChange={onMethodChange}
          onSaveRequest={onSaveRequest}
          onExecute={onExecute}
          workspaceRole={workspaceRole}
          comments={comments}
          onCommentClick={onCommentClick}
        />
      </main>
    );
  }

  if (activeTab.type === 'analytics') {
    return (
      <main className="main-panel">
        <AnalyticsDashboard workspaceId={workspaceId} />
      </main>
    );
  }

  return (
    <main className="main-panel">
      <OverviewPanel workspaceId={workspaceId} workspaceRole={workspaceRole} />
    </main>
  );
}

