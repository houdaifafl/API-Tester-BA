import React from 'react';
import RequestBuilder from '../request/RequestBuilder';
import OverviewPanel from './OverviewPanel';

export default function MainPanel({ activeTab, responseHeights, requestStates, onMethodChange, onSaveRequest }) {
  if (activeTab.type === 'request') {
    const rid = activeTab.requestId;
    const savedState = requestStates.current[rid];
    const handleStateChange = (patch) => {
      requestStates.current[rid] = { ...requestStates.current[rid], ...patch };
    };

    return (
      <main className="main-panel">
        <RequestBuilder
          key={rid}
          request={activeTab}
          initialResponseHeight={responseHeights.current[rid]}
          onResponseHeightChange={(h) => { responseHeights.current[rid] = h; }}
          savedState={savedState}
          onStateChange={handleStateChange}
          onMethodChange={onMethodChange}
          onSaveRequest={onSaveRequest}
        />
      </main>
    );
  }

  return (
    <main className="main-panel">
      <OverviewPanel />
    </main>
  );
}
