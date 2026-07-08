import React, { useState, useRef, useEffect, useCallback } from 'react';
import TopBar from './TopBar';
import Sidebar from './Sidebar';
import MainPanel from './MainPanel';
import AlertModal from '../shared/AlertModal';
import useWorkspace from '../../hooks/useWorkspace';
import useCollections from '../../hooks/useCollections';
import useWorkspaceTabs from '../../hooks/useWorkspaceTabs';
import useHistory from '../../hooks/useHistory';
import useInvitations from '../../hooks/useInvitations';
import useComments from '../../hooks/useComments';
import WorkspaceChat from './WorkspaceChat';
import { useAuth } from '../../contexts/AuthContext';
import './MainPage.css';

const MIN_SIDEBAR_WIDTH = 150;

export default function MainPage() {
  const [sidebarWidth, setSidebarWidth] = useState(() => window.innerWidth * 0.17);
  const isResizing = useRef(false);
  const [alertMessage, setAlertMessage] = useState(null);

  useEffect(() => {
    const handleAlert = (e) => {
      setAlertMessage(e.detail.message);
    };
    window.addEventListener('show-unauthorized-alert', handleAlert);
    return () => window.removeEventListener('show-unauthorized-alert', handleAlert);
  }, []);

  const {
    workspaces,
    activeWorkspace,
    workspaceRole,
    workspaceError,
    workspaceLoading,
    workspaceIdParam,
    handleSwitch,
    handleWorkspaceCreated,
    handleWorkspaceDeleted,
    reloadWorkspaces,
  } = useWorkspace();

  const {
    pendingInvitations,
    handleAccept,
    handleDecline,
  } = useInvitations(reloadWorkspaces);

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

  const { user } = useAuth();
  const currentUserId = user?.userId ?? null;

  const commentsState = useComments(activeWorkspaceId, activeRequestId);

  const handleBadgeNavigate = useCallback((comment) => {
    if (comment.target_tab === 'collection') {
      const event = new CustomEvent('navigate-to-collection-context', {
        detail: {
          collectionId: parseInt(comment.target_key)
        }
      });
      window.dispatchEvent(event);
      return;
    }

    const event = new CustomEvent('navigate-to-comment-context', {
      detail: {
        requestId: comment.request_id,
        tab: comment.target_tab,
        key: comment.target_key
      }
    });

    const req = collections.flatMap(c => c.requests || []).find(r => r.id === comment.request_id);
    if (req) {
      handleRequestOpen(req);
      setTimeout(() => {
        window.dispatchEvent(event);
      }, 100);
    }
  }, [collections, handleRequestOpen]);

  const handleCommentClick = useCallback((tab, key = null, collectionId = null) => {
    if (collectionId) {
      const count = commentsState.comments.filter(c => 
        c.target_tab === 'collection' &&
        c.target_key === String(collectionId)
      ).length;

      if (count > 0) {
        commentsState.openCommentsForElement(null, 'collection', String(collectionId));
      } else {
        commentsState.openCommentsForCollectionDraft(collectionId);
      }
      return;
    }

    if (activeRequestId) {
      const count = commentsState.comments.filter(c => 
        c.request_id === activeRequestId &&
        c.target_tab === tab &&
        (!key || c.target_key === key)
      ).length;

      if (count > 0) {
        commentsState.openCommentsForElement(activeRequestId, tab, key);
      } else {
        commentsState.openCommentsForDraft(activeRequestId, tab, key);
      }
    }
  }, [activeRequestId, commentsState]);

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
        pendingInvitations={pendingInvitations}
        onAcceptInvitation={handleAccept}
        onDeclineInvitation={handleDecline}
        workspaceRole={workspaceRole}
        isChatOpen={commentsState.isChatOpen}
        onChatToggle={commentsState.toggleChat}
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
          workspaceRole={workspaceRole}
          comments={commentsState.comments}
          onCommentClick={handleCommentClick}
        />
        <MainPanel
          activeTab={activeTab}
          responseHeights={responseHeights}
          requestStates={requestStates}
          onMethodChange={handleRequestMethodChange}
          onSaveRequest={handleSaveRequest}
          onExecute={addHistoryItem}
          workspaceRole={workspaceRole}
          comments={commentsState.comments}
          onCommentClick={handleCommentClick}
        />
        {commentsState.isChatOpen && (
          <WorkspaceChat
            workspaceId={activeWorkspaceId}
            currentUserId={currentUserId}
            workspaceRole={workspaceRole}
            collections={collections}
            activeRequestId={activeRequestId}
            commentsState={commentsState}
            onBadgeNavigate={handleBadgeNavigate}
          />
        )}
      </div>
      <AlertModal message={alertMessage} onClose={() => setAlertMessage(null)} />
    </div>
  );
}
