import React, { useEffect, useRef, useState } from 'react';
import { FaCog, FaUserFriends, FaPlus, FaMinus } from 'react-icons/fa';
import { createWorkspace, deleteWorkspace } from '../../services/workspaceService';
import { useAuth } from '../../contexts/AuthContext';
import './WorkspaceDropdown.css';

export default function WorkspaceDropdown({ workspaces, activeWorkspace, onSwitch, onWorkspaceCreated, onWorkspaceDeleted, onClose }) {
  const { user } = useAuth();
  const { email, userId } = user;

  const [creating, setCreating] = useState(false);
  const [newName, setNewName] = useState('');
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
        <button className="wsd-action-btn"><FaCog className="wsd-action-icon" /> Settings</button>
        <button className="wsd-action-btn"><FaUserFriends className="wsd-action-icon" /> Invite members</button>
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
            {!ws.is_default && (
              <button className="wsd-delete-btn" onClick={(e) => handleDelete(e, ws)} title="Delete workspace">
                <FaMinus />
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

    </div>
  );
}
