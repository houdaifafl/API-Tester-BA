import React, { useState, useRef, useEffect, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import TopBar from './TopBar';
import Sidebar from './Sidebar';
import MainPanel from './MainPanel';
import { getWorkspaces, getWorkspaceById } from '../../services/workspaceService';
import { getCollections, addCollection, renameCollection, deleteCollection, createRequest, renameRequest, deleteRequest, updateRequestMethod } from '../../services/collectionService';
import { useAuth } from '../../contexts/AuthContext';
import './MainPage.css';

const MIN_SIDEBAR_WIDTH = 150;

const OVERVIEW_TAB = {
  id: 'overview',
  type: 'overview',
  label: 'Overview',
  method: null,
  requestId: null,
  collectionName: null,
};

export default function MainPage() {
  const { user } = useAuth();
  const { userId } = user;
  const { workspaceId: workspaceIdParam } = useParams();
  const navigate = useNavigate();

  const [sidebarWidth, setSidebarWidth]       = useState(() => window.innerWidth * 0.17);
  const [workspaces, setWorkspaces]           = useState([]);
  const [activeWorkspace, setActiveWorkspace] = useState(null);
  const [workspaceError, setWorkspaceError]   = useState(null);
  const [workspaceLoading, setWorkspaceLoading] = useState(true);
  const [collections, setCollections]         = useState([]);
  const [openTabs, setOpenTabs]               = useState([OVERVIEW_TAB]);
  const [activeTabId, setActiveTabId]         = useState('overview');
  const isResizing     = useRef(false);
  const responseHeights = useRef({});
  const requestStates  = useRef({});
  const collectionsRef = useRef([]);

  // Keep collectionsRef in sync so async callbacks can read current state
  useEffect(() => { collectionsRef.current = collections; }, [collections]);

  // Load all workspaces for the user once
  useEffect(() => {
    if (!userId) return;
    getWorkspaces(userId)
      .then(data => setWorkspaces(data))
      .catch(() => {});
  }, [userId]);

  // Validate workspace ownership on every URL param change — no fallback allowed
  useEffect(() => {
    if (!userId || !workspaceIdParam) return;
    setActiveWorkspace(null);
    setWorkspaceError(null);
    setWorkspaceLoading(true);
    if (!/^\d+$/.test(workspaceIdParam)) {
      setWorkspaceError('invalid');
      setWorkspaceLoading(false);
      return;
    }
    getWorkspaceById(workspaceIdParam, userId)
      .then(data => { setActiveWorkspace(data); setWorkspaceLoading(false); })
      .catch(err => {
        const error = err.status === 404 ? 'not_found' : err.status === 400 ? 'invalid' : 'forbidden';
        setWorkspaceError(error);
        setWorkspaceLoading(false);
      });
  }, [workspaceIdParam, userId]);

  // Reload collections whenever the active workspace changes
  const activeWorkspaceId = activeWorkspace?.id ?? null;
  useEffect(() => {
    if (!activeWorkspaceId) { setCollections([]); return; }
    getCollections(activeWorkspaceId)
      .then(data => {
        // Attach collectionName to each request so tabs and breadcrumbs work
        setCollections(data.map(col => ({
          ...col,
          requests: col.requests.map(r => ({ ...r, collectionName: col.name })),
        })));
      })
      .catch(() => {});
  }, [activeWorkspaceId]);

  const handleSwitch = useCallback((ws) => {
    navigate(`/workspace/${ws.id}`);
  }, [navigate]);

  const handleWorkspaceCreated = useCallback((ws) => {
    setWorkspaces(prev => [...prev, ws]);
    navigate(`/workspace/${ws.id}`);
  }, [navigate]);

  const handleWorkspaceDeleted = useCallback((wsId) => {
    const updated = workspaces.filter(w => w.id !== wsId);
    setWorkspaces(updated);
    if (parseInt(workspaceIdParam, 10) === wsId) {
      const fallback = updated.find(w => w.is_default) || updated[0] || null;
      if (fallback) navigate(`/workspace/${fallback.id}`);
    }
  }, [workspaces, workspaceIdParam, navigate]);

  const handleRequestOpen = useCallback((request) => {
    const tabId = `req-${request.id}`;
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

  const handleRequestMethodChange = useCallback(async (id, newMethod) => {
    setCollections(prev => prev.map(col => ({
      ...col,
      requests: col.requests.map(r => r.id === id ? { ...r, method: newMethod } : r),
    })));
    setOpenTabs(prev => prev.map(t => t.requestId === id ? { ...t, method: newMethod } : t));
    try {
      await updateRequestMethod(id, newMethod);
    } catch {}
  }, []);

  const handleRequestRename = useCallback(async (id, newName) => {
    setCollections(prev => prev.map(col => ({
      ...col,
      requests: col.requests.map(r => r.id === id ? { ...r, name: newName } : r),
    })));
    setOpenTabs(prev => prev.map(t => t.requestId === id ? { ...t, label: newName } : t));
    try {
      await renameRequest(id, newName);
    } catch {}
  }, []);

  const handleRequestDelete = useCallback(async (id) => {
    try {
      await deleteRequest(id);
    } catch {}
    setCollections(prev => prev.map(col => ({
      ...col,
      requests: col.requests.filter(r => r.id !== id),
    })));
    const tabId = `req-${id}`;
    delete responseHeights.current[id];
    delete requestStates.current[id];
    setOpenTabs(prev => prev.filter(t => t.id !== tabId));
    setActiveTabId(prev => (prev === tabId ? 'overview' : prev));
  }, []);

  const handleRequestAdd = useCallback(async (collectionId) => {
    try {
      const newReq = await createRequest(collectionId);
      const col = collectionsRef.current.find(c => c.id === collectionId);
      const reqWithMeta = { ...newReq, collectionName: col ? col.name : '' };
      setCollections(prev => prev.map(c =>
        c.id === collectionId
          ? { ...c, requests: [...c.requests, reqWithMeta] }
          : c
      ));
      handleRequestOpen(reqWithMeta);
    } catch {}
  }, [handleRequestOpen]);

  const handleCollectionAdd = useCallback(async () => {
    if (!activeWorkspaceId) return;
    try {
      const newCol = await addCollection(activeWorkspaceId);
      setCollections(prev => [...prev, { ...newCol, requests: [] }]);
    } catch {}
  }, [activeWorkspaceId]);

  const handleCollectionRename = useCallback(async (id, newName) => {
    setCollections(prev => prev.map(c => c.id === id ? { ...c, name: newName } : c));
    setOpenTabs(prev => prev.map(t =>
      t.collectionName === (collectionsRef.current.find(c => c.id === id)?.name)
        ? { ...t, collectionName: newName }
        : t
    ));
    try {
      await renameCollection(id, newName);
    } catch {}
  }, []);

  const handleCollectionDelete = useCallback(async (id) => {
    try {
      await deleteCollection(id);
    } catch {}
    const col = collectionsRef.current.find(c => c.id === id);
    const requestIds = new Set((col?.requests ?? []).map(r => r.id));
    setCollections(prev => prev.filter(c => c.id !== id));
    setOpenTabs(prev => prev.filter(t => !t.requestId || !requestIds.has(t.requestId)));
    setActiveTabId(prev => {
      const tabId = prev;
      const tab = openTabs.find(t => t.id === tabId);
      if (tab?.requestId && requestIds.has(tab.requestId)) return 'overview';
      return prev;
    });
    requestIds.forEach(rid => {
      delete responseHeights.current[rid];
      delete requestStates.current[rid];
    });
  }, [openTabs]);

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

  const startResize = useCallback((e) => {
    isResizing.current = true;
    document.body.style.userSelect = 'none';
    document.body.style.cursor = 'col-resize';
    e.preventDefault();
  }, []);

  useEffect(() => {
    const handleMouseMove = (e) => {
      if (!isResizing.current) return;
      const maxWidth = window.innerWidth * 0.17;
      setSidebarWidth(Math.min(Math.max(e.clientX, MIN_SIDEBAR_WIDTH), maxWidth));
    };
    const handleMouseUp = () => {
      isResizing.current = false;
      document.body.style.userSelect = '';
      document.body.style.cursor = '';
    };
    document.addEventListener('mousemove', handleMouseMove);
    document.addEventListener('mouseup', handleMouseUp);
    return () => {
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseup', handleMouseUp);
    };
  }, []);

  const activeTab = openTabs.find(t => t.id === activeTabId) ?? OVERVIEW_TAB;
  const activeRequestId = activeTab.type === 'request' ? activeTab.requestId : null;

  if (workspaceLoading || workspaceError) {
    return (
      <div className="workspace-error">
        {workspaceError && (
          <p className="workspace-error-message">
            {workspaceError === 'invalid'   ? 'Invalid workspace ID.'  :
             workspaceError === 'not_found' ? 'Workspace not found.'   :
                                             'Access denied.'}
          </p>
        )}
      </div>
    );
  }

  return (
    <div className="workspace">
      <TopBar
        sidebarWidth={sidebarWidth}
        workspaces={workspaces}
        activeWorkspace={activeWorkspace}
        onSwitch={handleSwitch}
        onWorkspaceCreated={handleWorkspaceCreated}
        onWorkspaceDeleted={handleWorkspaceDeleted}
        openTabs={openTabs}
        activeTabId={activeTabId}
        onTabChange={handleTabChange}
        onTabClose={handleTabClose}
      />
      <div className="workspace-body">
        <Sidebar
          sidebarWidth={sidebarWidth}
          onResizeStart={startResize}
          activeRequestId={activeRequestId}
          onRequestOpen={handleRequestOpen}
          collections={collections}
          onRequestAdd={handleRequestAdd}
          onRequestRename={handleRequestRename}
          onRequestDelete={handleRequestDelete}
          onCollectionAdd={handleCollectionAdd}
          onCollectionRename={handleCollectionRename}
          onCollectionDelete={handleCollectionDelete}
        />
        <MainPanel
          activeTab={activeTab}
          responseHeights={responseHeights}
          requestStates={requestStates}
          onMethodChange={handleRequestMethodChange}
        />
      </div>
    </div>
  );
}
