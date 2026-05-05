import React, { useState, useCallback } from 'react';
import { FaChevronDown, FaPlus, FaBinoculars, FaTimes, FaSignOutAlt } from 'react-icons/fa';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import WorkspaceDropdown from './WorkspaceDropdown';
import './TopBar.css';

const METHOD_COLORS = {
  GET: '#49cc90',
  POST: '#f6851b',
  PUT: '#e6a817',
  DELETE: '#e74c3c',
  PATCH: '#9b59b6',
};

export default function TopBar({
  sidebarWidth,
  workspaces,
  activeWorkspace,
  onSwitch,
  onWorkspaceCreated,
  onWorkspaceDeleted,
  openTabs,
  activeTabId,
  onTabChange,
  onTabClose,
}) {
  const { logout } = useAuth();
  const navigate = useNavigate();
  const [dropdownOpen, setDropdownOpen] = useState(false);

  const handleLogout = useCallback(() => {
    logout();
    navigate('/login');
  }, [logout, navigate]);

  const handleSwitch = useCallback((ws) => {
    onSwitch(ws);
    setDropdownOpen(false);
  }, [onSwitch]);

  const handleWorkspaceCreated = useCallback((ws) => {
    onWorkspaceCreated(ws);
    setDropdownOpen(false);
  }, [onWorkspaceCreated]);

  const headerName = activeWorkspace ? activeWorkspace.name : '';

  return (
    <div className="top-bar">
      <div className="top-bar-sidebar-space" style={{ width: sidebarWidth }}>
        <div className="ws-header" onClick={() => setDropdownOpen(o => !o)}>
          <div className="ws-avatar">{headerName.charAt(0).toUpperCase()}</div>
          <span className="ws-name">{headerName}</span>
          <FaChevronDown className="ws-caret" />
        </div>
        {dropdownOpen && (
          <WorkspaceDropdown
            workspaces={workspaces}
            activeWorkspace={activeWorkspace}
            onSwitch={handleSwitch}
            onWorkspaceCreated={handleWorkspaceCreated}
            onWorkspaceDeleted={onWorkspaceDeleted}
            onClose={() => setDropdownOpen(false)}
          />
        )}
      </div>

      <div className="top-bar-tabs">
        {openTabs.map(tab => (
          <button
            key={tab.id}
            className={`top-tab ${activeTabId === tab.id ? 'top-tab-active' : 'top-tab-inactive'}`}
            onClick={() => onTabChange(tab.id)}
          >
            {tab.type === 'overview' && <FaBinoculars className="top-tab-icon" />}
            {tab.type === 'request' && (
              <span
                className="top-tab-method"
                style={{ color: METHOD_COLORS[tab.method] ?? '#888' }}
              >
                {tab.method}
              </span>
            )}
            <span className="top-tab-label">{tab.label}</span>
            {tab.type === 'request' && (
              <span
                className="top-tab-close"
                onClick={e => { e.stopPropagation(); onTabClose(tab.id); }}
                title="Close"
              >
                <FaTimes />
              </span>
            )}
          </button>
        ))}
        <button className="top-tab-add" title="New tab">
          <FaPlus />
        </button>
      </div>

      <button className="top-bar-signout" title="Sign out" onClick={handleLogout}>
        <FaSignOutAlt />
      </button>
    </div>
  );
}
