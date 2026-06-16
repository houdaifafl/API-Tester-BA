import React, { useState, useRef, useEffect, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import TopBar from './TopBar';
import Sidebar from './Sidebar';
import MainPanel from './MainPanel';
import { getWorkspaces, getWorkspaceById } from '../../services/workspaceService';
import { getCollections, addCollection, renameCollection, deleteCollection } from '../../services/collectionService';
import { createRequest, renameRequest, deleteRequest, updateRequestMethod, saveRequest } from '../../services/requestService';
import { useAuth } from '../../contexts/AuthContext';
import useWorkspaceTabs from '../../hooks/useWorkspaceTabs';
import './MainPage.css';

const MIN_SIDEBAR_WIDTH = 150;

export default function MainPage() {
  const { user } = useAuth();
  const { userId } = user;
  const { workspaceId: workspaceIdParam } = useParams();
  const navigate = useNavigate();

  const [sidebarWidth, setSidebarWidth]         = useState(() => window.innerWidth * 0.17);
  const [workspaces, setWorkspaces]             = useState([]);
  const [activeWorkspace, setActiveWorkspace]   = useState(null);
  const [workspaceError, setWorkspaceError]     = useState(null);
  const [workspaceLoading, setWorkspaceLoading] = useState(true);
  const [collections, setCollections]           = useState([]);
  const collectionsRef = useRef([]);
  const isResizing     = useRef(false);

  const {
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
  } = useWorkspaceTabs(workspaceIdParam);

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

  const handleSaveRequest = useCallback(async (requestId, data) => {
    await saveRequest(requestId, data);
    setCollections(prev => prev.map(col => ({
      ...col,
      requests: col.requests.map(r => r.id === requestId ? { ...r, ...data } : r),
    })));
  }, []);

  const handleRequestMethodChange = useCallback(async (id, newMethod) => {
    setCollections(prev => prev.map(col => ({
      ...col,
      requests: col.requests.map(r => r.id === id ? { ...r, method: newMethod } : r),
    })));
    updateTabMethod(id, newMethod);
    try { await updateRequestMethod(id, newMethod); } catch {}
  }, [updateTabMethod]);

  const handleRequestRename = useCallback(async (id, newName) => {
    setCollections(prev => prev.map(col => ({
      ...col,
      requests: col.requests.map(r => r.id === id ? { ...r, name: newName } : r),
    })));
    updateTabLabel(id, newName);
    try { await renameRequest(id, newName); } catch {}
  }, [updateTabLabel]);

  const handleRequestDelete = useCallback(async (id) => {
    try { await deleteRequest(id); } catch {}
    setCollections(prev => prev.map(col => ({
      ...col,
      requests: col.requests.filter(r => r.id !== id),
    })));
    removeTabsByRequestIds([id]);
  }, [removeTabsByRequestIds]);

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
    const oldName = collectionsRef.current.find(c => c.id === id)?.name;
    setCollections(prev => prev.map(c => c.id === id ? { ...c, name: newName } : c));
    if (oldName) updateTabCollectionName(oldName, newName);
    try { await renameCollection(id, newName); } catch {}
  }, [updateTabCollectionName]);

  const handleCollectionDelete = useCallback(async (id) => {
    try { await deleteCollection(id); } catch {}
    const col = collectionsRef.current.find(c => c.id === id);
    const requestIds = (col?.requests ?? []).map(r => r.id);
    setCollections(prev => prev.filter(c => c.id !== id));
    removeTabsByRequestIds(requestIds);
  }, [removeTabsByRequestIds]);

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

  const activeTab = openTabs.find(t => t.id === activeTabId)
    ?? { id: 'overview', type: 'overview', label: 'Overview', method: null, requestId: null, collectionName: null };
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
          onSaveRequest={handleSaveRequest}
        />
      </div>
    </div>
  );
}
