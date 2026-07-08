import React, { useState, useRef, useCallback, useEffect } from 'react';
import { FaSave } from 'react-icons/fa';
import RequestBar from './RequestBar';
import RequestTabs from './RequestTabs';
import DocsTab from './DocsTab';
import ParamsTab from './ParamsTab';
import AuthorizationTab from './AuthorizationTab';
import HeadersTab from './HeadersTab';
import BodyTab from './BodyTab';
import ResponsePanel from './ResponsePanel';
import { executeRequest } from '../../services/requestService';
import './RequestBuilder.css';

const DEFAULT_DOCS = {
  GET:  `This is a GET request and it is used to "get" data from an endpoint. There is no request body for a GET request, but you can use query parameters to help specify the resource you want data on (e.g., in this request, we have id=1).\n\nA successful GET response will have a 200 OK status, and should include some kind of response body - for example, HTML web content or JSON data.`,
  POST: `This is a POST request, submitting data to an API via the request body. This request submits JSON data, and the data is reflected in the response.\n\nA successful POST request typically returns a 200 OK or 201 Created response code.`,
};

function initDocs(savedState, requestName) {
  if (savedState?.docs !== undefined) return savedState.docs;
  if (requestName === 'Get data')  return DEFAULT_DOCS.GET;
  if (requestName === 'Post data') return DEFAULT_DOCS.POST;
  return '';
}

function buildParams(rows) {
  const out = {};
  (rows || []).forEach(r => { if (r.key.trim()) out[r.key.trim()] = r.value; });
  return out;
}

function buildHeaders(rows, auth) {
  const out = {};
  (rows || []).forEach(h => { if (h.key.trim()) out[h.key.trim()] = h.value; });
  if (auth?.type === 'bearer' && auth.token) {
    out['Authorization'] = `Bearer ${auth.token}`;
  } else if (auth?.type === 'basic') {
    out['Authorization'] = `Basic ${btoa(`${auth.username || ''}:${auth.password || ''}`)}`;
  }
  return out;
}

function buildBody(bodyState) {
  if (!bodyState || bodyState.bodyType === 'none') return null;
  if (bodyState.bodyType === 'raw') {
    if (!bodyState.rawContent) return null;
    if (bodyState.rawType === 'JSON') {
      try { return JSON.parse(bodyState.rawContent); } catch { return bodyState.rawContent; }
    }
    return bodyState.rawContent;
  }
  const rows = bodyState.bodyType === 'form-data' ? bodyState.formData : bodyState.urlEncoded;
  const out = {};
  (rows || []).forEach(r => { if (r.key) out[r.key] = r.value; });
  return Object.keys(out).length ? out : null;
}

export default function RequestBuilder({ request, initialResponseHeight, onResponseHeightChange, savedState, onStateChange, onMethodChange, onSaveRequest, onExecute, workspaceRole = 'viewer', comments = [], onCommentClick }) {
  const [activeTab, setActiveTab] = useState(savedState?.activeSubTab ?? 'Docs');
  const [url, setUrl]             = useState(savedState?.url ?? '');
  const [response, setResponse]   = useState(savedState?.response ?? null);
  const [loading, setLoading]     = useState(false);
  const [saving, setSaving]       = useState(false);
  const [method, setMethod]       = useState(request.method);

  const tabState = useRef({
    params:  savedState?.params  ?? null,
    auth:    savedState?.auth    ?? null,
    headers: savedState?.headers ?? null,
    body:    savedState?.body    ?? null,
    docs:    initDocs(savedState, request.label),
  });

  const handleSubTabChange = useCallback((tab) => {
    setActiveTab(tab);
    onStateChange?.({ activeSubTab: tab });
  }, [onStateChange]);

  const handleUrlChange = (val) => {
    setUrl(val);
    onStateChange?.({ url: val });
  };

  const handleParamsChange  = (params)  => { tabState.current.params  = params;  onStateChange?.({ params });  };
  const handleAuthChange    = (auth)    => { tabState.current.auth    = auth;    onStateChange?.({ auth });    };
  const handleHeadersChange = (headers) => { tabState.current.headers = headers; onStateChange?.({ headers }); };
  const handleBodyChange    = (body)    => { tabState.current.body    = body;    onStateChange?.({ body });    };
  const handleDocsChange    = (docs)    => { tabState.current.docs    = docs;    onStateChange?.({ docs });    };

  const handleMethodChange = useCallback((m) => {
    setMethod(m);
    if (request.type !== 'history') {
      onMethodChange?.(request.requestId, m);
    }
  }, [request.type, request.requestId, onMethodChange]);

  const handleSave = useCallback(async () => {
    setSaving(true);
    try {
      await onSaveRequest?.(request.requestId, {
        url,
        params:  tabState.current.params,
        headers: tabState.current.headers,
        body:    tabState.current.body,
        auth:    tabState.current.auth,
      });
    } finally {
      setSaving(false);
    }
  }, [url, request.requestId, onSaveRequest]);

  const handleSend = useCallback(async () => {
    if (!url.trim()) return;
    setLoading(true);
    setResponse(null);
    try {
      const result = await executeRequest({
        method,
        url:     url.trim(),
        params:  buildParams(tabState.current.params),
        headers: buildHeaders(tabState.current.headers, tabState.current.auth),
        body:    buildBody(tabState.current.body),
      });
      setResponse(result);
      onStateChange?.({ response: result });

      if (onExecute) {
        await onExecute({
          method,
          url: url.trim(),
          params: tabState.current.params,
          headers: tabState.current.headers,
          body: tabState.current.body,
          auth: tabState.current.auth,
          status: result.status,
          response_time: result.response_time,
          data: result.data,
        });
      }
    } catch (err) {
      const errorInstance = err instanceof Error ? err : new Error(err.error || 'Request failed');
      const errResponse = { error: errorInstance.message };
      setResponse(errResponse);
      onStateChange?.({ response: errResponse });
    } finally {
      setLoading(false);
    }
  }, [url, method, onStateChange, onExecute]);

  useEffect(() => {
    const handleNavigate = (e) => {
      const { requestId: targetReqId, tab: targetTab, key: targetKey } = e.detail;
      if (targetReqId !== request.requestId) return;

      const tabMap = {
        params: 'Params',
        headers: 'Headers',
        body: 'Body',
        auth: 'Authorization'
      };
      const uiTab = tabMap[targetTab];
      if (uiTab) {
        handleSubTabChange(uiTab);
        
        setTimeout(() => {
          const id = targetKey 
            ? `comment-target-${targetTab}-${targetKey}` 
            : `comment-target-${targetTab}`;
          const element = document.getElementById(id);
          if (element) {
            element.scrollIntoView({ behavior: 'smooth', block: 'center' });
            element.classList.add('comment-highlight-glow');
            setTimeout(() => {
              element.classList.remove('comment-highlight-glow');
            }, 3000);
          }
        }, 120);
      }
    };
    window.addEventListener('navigate-to-comment-context', handleNavigate);
    return () => window.removeEventListener('navigate-to-comment-context', handleNavigate);
  }, [request.requestId, handleSubTabChange]);

  const reqComments = comments.filter(c => c.request_id === request.requestId);

  return (
    <div className="request-builder">
      <div className="req-breadcrumb-row">
        <div className="req-breadcrumb">
          <span className="breadcrumb-collection">{request.collectionName}</span>
          <span className="breadcrumb-sep">›</span>
          <span className="breadcrumb-request">{request.label}</span>
        </div>
        {request.type !== 'history' && (
          <button
            className="req-save-btn"
            onClick={() => {
              if (workspaceRole === 'viewer') {
                window.dispatchEvent(new CustomEvent('show-unauthorized-alert', {
                  detail: { message: "Action forbidden: Viewers cannot save request changes." }
                }));
              } else {
                handleSave();
              }
            }}
            disabled={saving}
          >
            <FaSave className="save-icon" />
            {saving ? 'Saving…' : 'Save'}
          </button>
        )}
      </div>

      <RequestBar
        method={method}
        onMethodChange={handleMethodChange}
        url={url}
        onUrlChange={handleUrlChange}
        onSend={handleSend}
        loading={loading}
      />
      <RequestTabs activeTab={activeTab} onTabChange={handleSubTabChange} comments={reqComments} />

      <div className="req-content">
        {activeTab === 'Docs' && (
          <DocsTab value={tabState.current.docs} onChange={handleDocsChange} />
        )}
        {activeTab === 'Params' && (
          <ParamsTab
            initialParams={tabState.current.params}
            onParamsChange={handleParamsChange}
            comments={reqComments.filter(c => c.target_tab === 'params')}
            onCommentClick={(key) => onCommentClick?.('params', key)}
          />
        )}
        {activeTab === 'Authorization' && (
          <AuthorizationTab
            initialAuth={tabState.current.auth}
            onAuthChange={handleAuthChange}
            comments={reqComments.filter(c => c.target_tab === 'auth')}
            onCommentClick={(key) => onCommentClick?.('auth', key)}
          />
        )}
        {activeTab === 'Headers' && (
          <HeadersTab
            initialHeaders={tabState.current.headers}
            onHeadersChange={handleHeadersChange}
            comments={reqComments.filter(c => c.target_tab === 'headers')}
            onCommentClick={(key) => onCommentClick?.('headers', key)}
          />
        )}
        {activeTab === 'Body' && (
          <BodyTab
            initialBody={tabState.current.body}
            onBodyChange={handleBodyChange}
            comments={reqComments.filter(c => c.target_tab === 'body')}
            onCommentClick={(key) => onCommentClick?.('body', key)}
          />
        )}
      </div>

      <ResponsePanel
        initialHeight={initialResponseHeight}
        onHeightChange={onResponseHeightChange}
        response={response}
        loading={loading}
      />
    </div>
  );
}
