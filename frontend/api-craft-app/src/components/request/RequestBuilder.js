import React, { useState, useRef } from 'react';
import { FaSave } from 'react-icons/fa';
import RequestBar from './RequestBar';
import RequestTabs from './RequestTabs';
import DocsTab from './DocsTab';
import ParamsTab from './ParamsTab';
import AuthorizationTab from './AuthorizationTab';
import HeadersTab from './HeadersTab';
import BodyTab from './BodyTab';
import ResponsePanel from './ResponsePanel';
import './RequestBuilder.css';

export default function RequestBuilder({ request, initialResponseHeight, onResponseHeightChange, savedState, onStateChange, onMethodChange }) {
  const [activeTab, setActiveTab] = useState(savedState?.activeSubTab ?? 'Docs');

  // Live cache for sub-tab state — always holds the latest values so remounting
  // a sub-tab after switching always restores what the user last typed.
  const tabState = useRef({
    params:       savedState?.params    ?? null,
    auth:         savedState?.auth      ?? null,
    headers:      savedState?.headers   ?? null,
    body:         savedState?.body      ?? null,
  });

  const handleSubTabChange = (tab) => {
    setActiveTab(tab);
    onStateChange?.({ activeSubTab: tab });
  };

  const handleParamsChange = (params) => {
    tabState.current.params = params;
    onStateChange?.({ params });
  };

  const handleAuthChange = (auth) => {
    tabState.current.auth = auth;
    onStateChange?.({ auth });
  };

  const handleHeadersChange = (headers) => {
    tabState.current.headers = headers;
    onStateChange?.({ headers });
  };

  const handleBodyChange = (body) => {
    tabState.current.body = body;
    onStateChange?.({ body });
  };

  return (
    <div className="request-builder">
      <div className="req-breadcrumb-row">
        <div className="req-breadcrumb">
          <span className="breadcrumb-collection">{request.collectionName}</span>
          <span className="breadcrumb-sep">›</span>
          <span className="breadcrumb-request">{request.label}</span>
        </div>
        <button className="req-save-btn">
          <FaSave className="save-icon" />
          Save
        </button>
      </div>

      <RequestBar
        method={request.method}
        onMethodChange={(m) => onMethodChange?.(request.requestId, m)}
      />
      <RequestTabs activeTab={activeTab} onTabChange={handleSubTabChange} />

      <div className="req-content">
        {activeTab === 'Docs' && <DocsTab method={request.method} />}
        {activeTab === 'Params' && (
          <ParamsTab
            initialParams={tabState.current.params}
            onParamsChange={handleParamsChange}
          />
        )}
        {activeTab === 'Authorization' && (
          <AuthorizationTab
            initialAuth={tabState.current.auth}
            onAuthChange={handleAuthChange}
          />
        )}
        {activeTab === 'Headers' && (
          <HeadersTab
            initialHeaders={tabState.current.headers}
            onHeadersChange={handleHeadersChange}
          />
        )}
        {activeTab === 'Body' && (
          <BodyTab
            initialBody={tabState.current.body}
            onBodyChange={handleBodyChange}
          />
        )}
      </div>

      <ResponsePanel
        initialHeight={initialResponseHeight}
        onHeightChange={onResponseHeightChange}
      />
    </div>
  );
}
