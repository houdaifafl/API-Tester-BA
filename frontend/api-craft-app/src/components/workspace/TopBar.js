import React, { useState, useRef, useEffect, useCallback } from 'react';
import { FaChevronDown, FaPlus, FaBinoculars, FaTimes, FaUserCircle, FaSignOutAlt } from 'react-icons/fa';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import WorkspaceDropdown from './WorkspaceDropdown';
import SignOutModal from './SignOutModal';
import InviteModal from './InviteModal';
import NotificationBell from '../admin/NotificationBell';
import { METHOD_COLORS } from '../../constants';
import './TopBar.css';

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
  pendingInvitations = [],
  onAcceptInvitation,
  onDeclineInvitation,
  workspaceRole = 'viewer',
}) {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [dropdownOpen, setDropdownOpen] = useState(false);
  const [accountOpen, setAccountOpen] = useState(false);
  const [confirmOpen, setConfirmOpen] = useState(false);
  const [inviteOpen, setInviteOpen] = useState(false);
  const accountRef = useRef(null);

  useEffect(() => {
    if (!accountOpen) return;
    const handler = (e) => {
      if (accountRef.current && !accountRef.current.contains(e.target)) {
        setAccountOpen(false);
      }
    };
    document.addEventListener('mousedown', handler);
    return () => document.removeEventListener('mousedown', handler);
  }, [accountOpen]);

  const handleSignOutClick = useCallback(() => {
    setAccountOpen(false);
    setConfirmOpen(true);
  }, []);

  const handleConfirmLogout = useCallback(() => {
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

  const handleInviteTrigger = useCallback(() => {
    setInviteOpen(true);
    setDropdownOpen(false);
  }, []);

  const headerName = activeWorkspace ? activeWorkspace.name : '';

  return (
    <>
      <div className="top-bar">
        <div className="top-bar-sidebar-space" style={{ width: sidebarWidth }}>
          <div className="ws-header" onClick={() => setDropdownOpen(o => !o)}>
            <div className="ws-avatar">{headerName.charAt(0).toUpperCase()}</div>
            <span className="ws-name">{headerName}</span>
            {workspaceRole === 'viewer' && (
              <span className="ws-readonly-badge" style={{ fontSize: '0.65rem', padding: '1px 4px', background: '#3d3d3d', borderRadius: '3px', color: '#ffc107', marginLeft: '6px', whiteSpace: 'nowrap' }}>
                🔒 Read-only
              </span>
            )}
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
              pendingInvitations={pendingInvitations}
              onAcceptInvitation={onAcceptInvitation}
              onDeclineInvitation={onDeclineInvitation}
              onInviteClick={handleInviteTrigger}
              workspaceRole={workspaceRole}
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

        <div className="top-bar-profile" ref={accountRef} style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <NotificationBell />
          <button
            className="profile-btn"
            title="Account"
            onClick={() => setAccountOpen(o => !o)}
          >
            <FaUserCircle />
          </button>
          {accountOpen && (
            <div className="account-dropdown">
              <div className="account-info">
                <span className="account-name">{user.username}</span>
                <span className="account-email">{user.email}</span>
              </div>
              <div className="account-divider" />
              <button className="account-signout" onClick={handleSignOutClick}>
                <FaSignOutAlt />
                <span>Sign out</span>
              </button>
            </div>
          )}
        </div>
      </div>

      {confirmOpen && (
        <SignOutModal
          onCancel={() => setConfirmOpen(false)}
          onConfirm={handleConfirmLogout}
        />
      )}

      {inviteOpen && activeWorkspace && (
        <InviteModal
          workspace={activeWorkspace}
          onClose={() => setInviteOpen(false)}
        />
      )}
    </>
  );
}
