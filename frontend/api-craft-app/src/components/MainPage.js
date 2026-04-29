import React, { useState, useRef, useEffect, useCallback } from 'react';
import TopBar from './TopBar';
import Sidebar from './Sidebar';
import MainPanel from './MainPanel';
import { getWorkspaces } from '../services/workspaceService';
import { useAuth } from '../contexts/AuthContext';
import './MainPage.css';

const MIN_SIDEBAR_WIDTH = 150;

export default function MainPage() {
  const { user } = useAuth();
  const { userId } = user;

  const [sidebarWidth, setSidebarWidth] = useState(() => window.innerWidth * 0.17);
  const [workspaces, setWorkspaces] = useState([]);
  const [activeWorkspace, setActiveWorkspace] = useState(null);
  const isResizing = useRef(false);

  useEffect(() => {
    if (!userId) return;
    getWorkspaces(userId)
      .then(data => {
        setWorkspaces(data);
        if (data.length > 0) setActiveWorkspace(data[0]);
      })
      .catch(() => {});
  }, [userId]);

  const handleSwitch = useCallback((ws) => {
    setActiveWorkspace(ws);
  }, []);

  const handleWorkspaceCreated = useCallback((ws) => {
    setWorkspaces(prev => [...prev, ws]);
    setActiveWorkspace(ws);
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

  return (
    <div className="workspace">
      <TopBar
        sidebarWidth={sidebarWidth}
        workspaces={workspaces}
        activeWorkspace={activeWorkspace}
        onSwitch={handleSwitch}
        onWorkspaceCreated={handleWorkspaceCreated}
      />
      <div className="workspace-body">
        <Sidebar sidebarWidth={sidebarWidth} onResizeStart={startResize} />
        <MainPanel />
      </div>
    </div>
  );
}
