import { useState, useRef, useEffect, useCallback } from 'react';

const OVERVIEW_TAB = {
  id: 'overview',
  type: 'overview',
  label: 'Overview',
  method: null,
  requestId: null,
  collectionName: null,
};

export default function useWorkspaceTabs(workspaceIdParam) {
  const [openTabs, setOpenTabs]   = useState([OVERVIEW_TAB]);
  const [activeTabId, setActiveTabId] = useState('overview');

  const responseHeights    = useRef({});
  const requestStates      = useRef({});
  const openTabsRef        = useRef([OVERVIEW_TAB]);
  const activeTabIdRef     = useRef('overview');
  const workspaceTabsCache = useRef({});
  const prevWorkspaceIdRef = useRef(null);

  useEffect(() => { openTabsRef.current    = openTabs;    }, [openTabs]);
  useEffect(() => { activeTabIdRef.current = activeTabId; }, [activeTabId]);

  // Save tabs for the outgoing workspace; restore (or reset) for the incoming one
  useEffect(() => {
    if (!workspaceIdParam) return;
    const prev = prevWorkspaceIdRef.current;
    if (prev !== null && prev !== workspaceIdParam) {
      const requestStatesSnapshot = {};
      Object.entries(requestStates.current).forEach(([k, v]) => {
        const { response: _r, ...rest } = v || {};
        requestStatesSnapshot[k] = rest;
      });
      workspaceTabsCache.current[prev] = {
        openTabs:       openTabsRef.current,
        activeTabId:    activeTabIdRef.current,
        requestStates:  requestStatesSnapshot,
        responseHeights: { ...responseHeights.current },
      };
      const saved = workspaceTabsCache.current[workspaceIdParam];
      if (saved) {
        setOpenTabs(saved.openTabs);
        setActiveTabId(saved.activeTabId);
        requestStates.current   = { ...saved.requestStates };
        responseHeights.current = { ...saved.responseHeights };
      } else {
        setOpenTabs([OVERVIEW_TAB]);
        setActiveTabId('overview');
        requestStates.current   = {};
        responseHeights.current = {};
      }
    }
    prevWorkspaceIdRef.current = workspaceIdParam;
  }, [workspaceIdParam]);

  const handleRequestOpen = useCallback((request) => {
    const tabId = `req-${request.id}`;
    if (!requestStates.current[request.id]) {
      requestStates.current[request.id] = {
        url:     request.url     ?? '',
        params:  request.params  ?? null,
        headers: request.headers ?? null,
        body:    request.body    ?? null,
        auth:    request.auth    ?? null,
      };
    }
    setOpenTabs(prev => {
      if (prev.find(t => t.id === tabId)) return prev;
      return [...prev, {
        id: tabId,
        type: 'request',
        label: request.name,
        method: request.method,
        requestId: request.id,
        collectionName: request.collectionName,
      }];
    });
    setActiveTabId(tabId);
  }, []);

  const handleTabChange = useCallback((tabId) => {
    setActiveTabId(tabId);
  }, []);

  const handleTabClose = useCallback((tabId) => {
    setOpenTabs(prev => {
      const tab = prev.find(t => t.id === tabId);
      if (tab?.requestId) {
        delete responseHeights.current[tab.requestId];
        delete requestStates.current[tab.requestId];
      }
      return prev.filter(t => t.id !== tabId);
    });
    setActiveTabId(prev => (prev === tabId ? 'overview' : prev));
  }, []);

  // Called by MainPage when a request's HTTP method is changed
  const updateTabMethod = useCallback((requestId, method) => {
    setOpenTabs(prev => prev.map(t => t.requestId === requestId ? { ...t, method } : t));
  }, []);

  // Called by MainPage when a request is renamed
  const updateTabLabel = useCallback((requestId, name) => {
    setOpenTabs(prev => prev.map(t => t.requestId === requestId ? { ...t, label: name } : t));
  }, []);

  // Called by MainPage when a collection is renamed
  const updateTabCollectionName = useCallback((oldName, newName) => {
    setOpenTabs(prev => prev.map(t =>
      t.collectionName === oldName ? { ...t, collectionName: newName } : t
    ));
  }, []);

  // Called by MainPage when one or more requests are deleted
  const removeTabsByRequestIds = useCallback((ids) => {
    const idSet = new Set(ids);
    setOpenTabs(prev => prev.filter(t => !t.requestId || !idSet.has(t.requestId)));
    setActiveTabId(prev => {
      const match = prev.match(/^req-(\d+)$/);
      if (match && idSet.has(parseInt(match[1], 10))) return 'overview';
      return prev;
    });
    ids.forEach(id => {
      delete responseHeights.current[id];
      delete requestStates.current[id];
    });
  }, []);

  return {
    openTabs,
    activeTabId,
    requestStates,
    responseHeights,
    handleRequestOpen,
    handleTabChange,
    handleTabClose,
    updateTabMethod,
    updateTabLabel,
    updateTabCollectionName,
    removeTabsByRequestIds,
  };
}
