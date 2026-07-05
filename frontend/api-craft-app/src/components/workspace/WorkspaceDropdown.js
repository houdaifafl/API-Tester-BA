import React, { useCallback, useEffect, useRef, useState } from 'react';
import { FaCog, FaUserFriends, FaPlus, FaMinus, FaSignOutAlt } from 'react-icons/fa';
import { createWorkspace, deleteWorkspace, leaveWorkspace } from '../../services/workspaceService';
import { useAuth } from '../../contexts/AuthContext';
import './WorkspaceDropdown.css';

export default function WorkspaceDropdown({
  workspaces,
  activeWorkspace,
  onSwitch,
  onWorkspaceCreated,
  onWorkspaceDeleted,
  onClose,
  pendingInvitations = [],
  onAcceptInvitation,
  onDeclineInvitation,
  onInviteClick,
  workspaceRole = 'viewer',
}) {
  const { user } = useAuth();
  const { email, userId } = user;

  const [creating, setCreating] = useState(false);
  const [newName, setNewName] = useState('');
  const [leavingId, setLeavingId] = useState(null);
  const ref = useRef(null);

  useEffect(() => {
    const handleOutsideClick = (e) => {
      if (ref.current && !ref.current.contains(e.target)) onClose();
    };
    document.addEventListener('mousedown', handleOutsideClick);
    return () => document.removeEventListener('mousedown', handleOutsideClick);
  }, [onClose]);

  const handleCreate = async () => {
    if (!newName.trim()) return;
    try {
      const ws = await createWorkspace(userId, newName.trim());
      setNewName('');
      setCreating(false);
      onWorkspaceCreated(ws);
    } catch {}
  };

  const handleDelete = async (e, ws) => {
    e.stopPropagation();
    try {
      await deleteWorkspace(ws.id, userId);
      onWorkspaceDeleted(ws.id);
    } catch {}
  };

  const handleLeave = useCallback(async (e, ws) => {
    e.stopPropagation();
    if (leavingId !== ws.id) {
      setLeavingId(ws.id);
      return;
    }
    try {
      await leaveWorkspace(ws.id);
      onWorkspaceDeleted(ws.id);
    } catch {
      // silently reset — button should not have been visible for owners
    } finally {
      setLeavingId(null);
    }
  }, [leavingId, onWorkspaceDeleted]);

  const currentName = activeWorkspace ? activeWorkspace.name : '';

  return (
    <div className="wsd-container" ref={ref}>

      {/* Current workspace */}
      <div className="wsd-current">
        <div className="wsd-avatar">{currentName.charAt(0).toUpperCase()}</div>
        <span className="wsd-current-name">{currentName}</span>
      </div>

      {/* Action buttons */}
      <div className="wsd-actions">
        <button
          className="wsd-action-btn"
          onClick={() => {
            if (workspaceRole !== 'owner') {
              window.dispatchEvent(new CustomEvent('show-unauthorized-alert', {
                detail: { message: "Action forbidden: Only workspace owners can modify settings." }
              }));
            }
          }}
        >
          <FaCog className="wsd-action-icon" /> Settings
        </button>
        <button
          className="wsd-action-btn"
          onClick={(e) => {
            if (workspaceRole !== 'owner') {
              window.dispatchEvent(new CustomEvent('show-unauthorized-alert', {
                detail: { message: "Action forbidden: Only workspace owners can invite members." }
              }));
            } else {
              onInviteClick(e);
            }
          }}
        >
          <FaUserFriends className="wsd-action-icon" /> Invite members
        </button>
      </div>

      <hr className="wsd-divider" />

      {/* Email */}
      <div className="wsd-email">{email}</div>

      {/* Workspace list */}
      <ul className="wsd-list">
        {workspaces.map(ws => (
          <li key={ws.id} className="wsd-item" onClick={() => onSwitch(ws)}>
            <div className="wsd-item-avatar">{ws.name.charAt(0).toUpperCase()}</div>
            <span className="wsd-item-name">{ws.name}</span>
            {!ws.is_default && ws.is_owner && (
              <button
                className="wsd-delete-btn"
                onClick={(e) => handleDelete(e, ws)}
                title="Delete workspace"
              >
                <FaMinus />
              </button>
            )}
            {!ws.is_owner && (
              <button
                className={`wsd-leave-btn${leavingId === ws.id ? ' wsd-leave-btn--confirm' : ''}`}
                onClick={(e) => handleLeave(e, ws)}
                title={leavingId === ws.id ? 'Click again to confirm' : 'Leave workspace'}
              >
                {leavingId === ws.id ? 'Confirm?' : <FaSignOutAlt />}
              </button>
            )}
          </li>
        ))}
      </ul>

      {/* New workspace */}
      {creating ? (
        <div className="wsd-new-input-row">
          <input
            autoFocus
            className="wsd-new-input"
            placeholder="Workspace name"
            value={newName}
            onChange={e => setNewName(e.target.value)}
            onKeyDown={e => {
              if (e.key === 'Enter') handleCreate();
              if (e.key === 'Escape') setCreating(false);
            }}
          />
          <button className="wsd-new-confirm" onClick={handleCreate}>Add</button>
        </div>
      ) : (
        <button className="wsd-new-btn" onClick={() => setCreating(true)}>
          <FaPlus className="wsd-new-icon" /> New workspace
        </button>
      )}

      {/* Pending Workspace Invitations */}
      {pendingInvitations.length > 0 && (
        <>
          <hr className="wsd-divider" />
          <div className="wsd-section-title">Pending Invitations</div>
          <ul className="wsd-invitations-list">
            {pendingInvitations.map(inv => (
              <li key={inv.id} className="wsd-invitation-item">
                <div className="wsd-invitation-details">
                  <span className="wsd-invitation-ws-name" title={inv.workspace_name}>
                    {inv.workspace_name}
                  </span>
                  <span className="wsd-invitation-sender">
                    invited by {inv.inviter_username}
                  </span>
                </div>
                <div className="wsd-invitation-actions">
                  <button
                    className="wsd-invitation-btn wsd-invitation-btn--accept"
                    onClick={(e) => {
                      e.stopPropagation();
                      onAcceptInvitation(inv.id);
                    }}
                  >
                    Accept
                  </button>
                  <button
                    className="wsd-invitation-btn wsd-invitation-btn--decline"
                    onClick={(e) => {
                      e.stopPropagation();
                      onDeclineInvitation(inv.id);
                    }}
                  >
                    Decline
                  </button>
                </div>
              </li>
            ))}
          </ul>
        </>
      )}

    </div>
  );
}
