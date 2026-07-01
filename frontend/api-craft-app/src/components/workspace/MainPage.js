import React, { useState, useRef, useEffect, useCallback } from 'react';
import TopBar from './TopBar';
import Sidebar from './Sidebar';
import MainPanel from './MainPanel';
import useWorkspace from '../../hooks/useWorkspace';
import useCollections from '../../hooks/useCollections';
import useWorkspaceTabs from '../../hooks/useWorkspaceTabs';
import useHistory from '../../hooks/useHistory';
import './MainPage.css';

const MIN_SIDEBAR_WIDTH = 150;

export default function MainPage() {
  const [sidebarWidth, setSidebarWidth] = useState(() => window.innerWidth * 0.17);
  const isResizing = useRef(false);

  const {
    workspaces,
    activeWorkspace,
    workspaceError,
    workspaceLoading,
    workspaceIdParam,
    handleSwitch,
    handleWorkspaceCreated,
    handleWorkspaceDeleted,
  } = useWorkspace();

  const {
    openTabs,
    activeTabId,
    requestStates,
    responseHeights,
    handleRequestOpen,
    handleHistoryOpen,
    handleTabChange,
    handleTabClose,
    updateTabMethod,
    updateTabLabel,
    updateTabCollectionName,
    removeTabsByRequestIds,
  } = useWorkspaceTabs(workspaceIdParam);

  const activeWorkspaceId = activeWorkspace?.id ?? null;

  const {
    history,
    addHistoryItem,
  } = useHistory(activeWorkspaceId);

  const {
    collections,
    handleSaveRequest,
    handleRequestMethodChange,
    handleRequestRename,
    handleRequestDelete,
    handleRequestAdd,
    handleCollectionAdd,
    handleCollectionRename,
    handleCollectionDelete,
  } = useCollections({
    activeWorkspaceId,
    handleRequestOpen,
    updateTabMethod,
    updateTabLabel,
    updateTabCollectionName,
    removeTabsByRequestIds,
  });

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
  const activeHistoryId = activeTab.type === 'history' ? activeTab.historyId : null;

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
          history={history}
          onHistoryOpen={handleHistoryOpen}
          activeHistoryId={activeHistoryId}
        />
        <MainPanel
          activeTab={activeTab}
          responseHeights={responseHeights}
          requestStates={requestStates}
          onMethodChange={handleRequestMethodChange}
          onSaveRequest={handleSaveRequest}
          onExecute={addHistoryItem}
        />
      </div>
    </div>
  );
}

