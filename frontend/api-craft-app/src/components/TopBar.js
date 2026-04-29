import React, { useState, useCallback } from 'react';
import { FaChevronDown, FaPlus, FaBinoculars } from 'react-icons/fa';
import WorkspaceDropdown from './WorkspaceDropdown';

export default function TopBar({ sidebarWidth, workspaces, activeWorkspace, onSwitch, onWorkspaceCreated }) {
  const [dropdownOpen, setDropdownOpen] = useState(false);

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
            onClose={() => setDropdownOpen(false)}
          />
        )}
      </div>
      <div className="top-bar-tabs">
        <div className="top-tab">
          <FaBinoculars className="top-tab-icon" />
          Overview
        </div>
        <button className="top-tab-add" title="New tab">
          <FaPlus />
        </button>
      </div>
    </div>
  );
}
