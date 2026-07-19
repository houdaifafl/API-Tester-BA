import React, { useEffect, useState, useCallback } from 'react';
import { FaTimes, FaUserTimes, FaTrash, FaCheck, FaSpinner } from 'react-icons/fa';
import { getWorkspaceById, renameWorkspace, updateMemberRole, removeMember } from '../../services/workspaceService';
import { cancelInvitation } from '../../services/invitationService';
import './WorkspaceSettingsModal.css';

export default function WorkspaceSettingsModal({ workspace, onClose, onWorkspaceUpdated, workspaceRole }) {
  const [name, setName] = useState(workspace ? workspace.name : '');
  const [renaming, setRenaming] = useState(false);
  const [renameSuccess, setRenameSuccess] = useState(false);
  
  const [collaborators, setCollaborators] = useState({ members: [], invitations: [] });
  const [loadingCollabs, setLoadingCollabs] = useState(true);
  const [collabError, setCollabError] = useState(null);

  const fetchCollaborators = useCallback(async () => {
    setLoadingCollabs(true);
    setCollabError(null);
    try {
      // In our design: GET /api/workspaces/{id}/collaborators
      const res = await fetch(`/api/workspaces/${workspace.id}/collaborators`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}` // simple standard retrieval matching authFetch
        }
      });
      if (!res.ok) throw new Error('Failed to fetch collaborators');
      const data = await res.json();
      setCollaborators(data);
    } catch (err) {
      setCollabError(err.message || 'Error loading collaborators');
    } finally {
      setLoadingCollabs(false);
    }
  }, [workspace.id]);

  useEffect(() => {
    if (workspace) {
      setName(workspace.name);
      fetchCollaborators();
    }
  }, [workspace, fetchCollaborators]);

  const handleRename = async (e) => {
    e.preventDefault();
    if (!name.trim() || name.trim() === workspace.name) return;
    setRenaming(true);
    setRenameSuccess(false);
    try {
      await renameWorkspace(workspace.id, name.trim());
      setRenameSuccess(true);
      if (onWorkspaceUpdated) {
        onWorkspaceUpdated({ ...workspace, name: name.trim() });
      }
    } catch (err) {
      alert(err.message || 'Failed to rename workspace');
    } finally {
      setRenaming(false);
    }
  };

  const handleRoleChange = async (memberUserId, newRole) => {
    try {
      await updateMemberRole(workspace.id, memberUserId, newRole);
      fetchCollaborators();
    } catch (err) {
      alert(err.message || 'Failed to update member role');
    }
  };

  const handleRemoveMember = async (memberUserId) => {
    if (!window.confirm('Are you sure you want to remove this collaborator?')) return;
    try {
      await removeMember(workspace.id, memberUserId);
      fetchCollaborators();
    } catch (err) {
      alert(err.message || 'Failed to remove collaborator');
    }
  };

  const handleCancelInvite = async (inviteId) => {
    if (!window.confirm('Are you sure you want to cancel this invitation?')) return;
    try {
      await cancelInvitation(inviteId);
      fetchCollaborators();
    } catch (err) {
      alert(err.message || 'Failed to cancel invitation');
    }
  };

  const isOwner = workspaceRole === 'owner';

  return (
    <div className="wsm-overlay" onClick={onClose}>
      <div className="wsm-modal" onClick={e => e.stopPropagation()}>
        <div className="wsm-header">
          <h2>Workspace Settings</h2>
          <button className="wsm-close-btn" onClick={onClose} aria-label="Close settings">
            <FaTimes />
          </button>
        </div>

        <div className="wsm-body">
          {/* Workspace Renaming */}
          <section className="wsm-section">
            <h3>Workspace Name</h3>
            <form onSubmit={handleRename} className="wsm-rename-form">
              <input
                type="text"
                className="wsm-input"
                value={name}
                onChange={e => setName(e.target.value)}
                disabled={!isOwner || renaming}
                placeholder="Enter workspace name"
                required
                maxLength={100}
              />
              {isOwner && (
                <button
                  type="submit"
                  className="wsm-btn wsm-btn--primary"
                  disabled={renaming || !name.trim() || name.trim() === workspace.name}
                >
                  {renaming ? 'Saving...' : 'Rename'}
                </button>
              )}
            </form>
            {renameSuccess && (
              <div className="wsm-success-msg">
                <FaCheck /> Workspace name updated!
              </div>
            )}
          </section>

          {/* Collaborator Management */}
          <section className="wsm-section">
            <h3>Collaborators & Members</h3>
            {loadingCollabs ? (
              <div className="wsm-loading">
                <FaSpinner className="wsm-spinner" /> Loading members...
              </div>
            ) : collabError ? (
              <div className="wsm-error">{collabError}</div>
            ) : (
              <div className="wsm-collaborators-list">
                {/* Active Members */}
                <div className="wsm-collab-group">
                  <h4>Active Members</h4>
                  {collaborators.members.length === 0 ? (
                    <p className="wsm-empty-text">No other members in this workspace.</p>
                  ) : (
                    <ul className="wsm-list">
                      {collaborators.members.map(member => (
                        <li key={member.user_id} className="wsm-item">
                          <div className="wsm-item-details">
                            <span className="wsm-username">@{member.username}</span>
                            <span className="wsm-email">{member.email}</span>
                          </div>
                          <div className="wsm-item-actions">
                            <select
                              className="wsm-select"
                              value={member.role}
                              onChange={e => handleRoleChange(member.user_id, e.target.value)}
                              disabled={!isOwner}
                            >
                              <option value="editor">Editor</option>
                              <option value="viewer">Viewer</option>
                            </select>
                            {isOwner && (
                              <button
                                className="wsm-action-btn wsm-action-btn--delete"
                                onClick={() => handleRemoveMember(member.user_id)}
                                title="Remove member"
                              >
                                <FaUserTimes />
                              </button>
                            )}
                          </div>
                        </li>
                      ))}
                    </ul>
                  )}
                </div>

                {/* Pending Invitations */}
                <div className="wsm-collab-group">
                  <h4>Pending Invitations</h4>
                  {collaborators.invitations.length === 0 ? (
                    <p className="wsm-empty-text">No pending invitations.</p>
                  ) : (
                    <ul className="wsm-list">
                      {collaborators.invitations.map(invite => (
                        <li key={invite.id} className="wsm-item">
                          <div className="wsm-item-details">
                            <span className="wsm-username">@{invite.username}</span>
                            <span className="wsm-email">{invite.email}</span>
                            <span className="wsm-role-badge">{invite.role}</span>
                          </div>
                          <div className="wsm-item-actions">
                            {isOwner && (
                              <button
                                className="wsm-action-btn wsm-action-btn--delete"
                                onClick={() => handleCancelInvite(invite.id)}
                                title="Cancel invitation"
                              >
                                <FaTrash />
                              </button>
                            )}
                          </div>
                        </li>
                      ))}
                    </ul>
                  )}
                </div>
              </div>
            )}
          </section>
        </div>
      </div>
    </div>
  );
}
