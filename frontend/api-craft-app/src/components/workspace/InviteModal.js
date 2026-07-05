import React, { useState, useCallback } from 'react';
import { FaTimes } from 'react-icons/fa';
import { inviteUserToWorkspace } from '../../services/invitationService';
import './InviteModal.css';

export default function InviteModal({ workspace, onClose }) {
  const [username, setUsername] = useState('');
  const [role, setRole] = useState('editor');
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState(null);
  const [error, setError] = useState(null);

  const handleSubmit = useCallback(async (e) => {
    e.preventDefault();
    if (!username.trim()) return;

    setLoading(true);
    setMessage(null);
    setError(null);

    try {
      await inviteUserToWorkspace(workspace.id, username.trim(), role);
      setMessage(`Successfully invited ${username} as ${role}!`);
      setUsername('');
    } catch (err) {
      setError(err.message || 'Failed to send invitation');
    } finally {
      setLoading(false);
    }
  }, [workspace, username, role]);

  return (
    <div className="invite-modal" onClick={onClose}>
      <div className="invite-modal__content" onClick={(e) => e.stopPropagation()}>
        <div className="invite-modal__header">
          <h3 className="invite-modal__title">Invite members</h3>
          <button className="invite-modal__close-btn" onClick={onClose} aria-label="Close modal">
            <FaTimes />
          </button>
        </div>
        <form className="invite-modal__form" onSubmit={handleSubmit}>
          <div className="invite-modal__body">
            <p className="invite-modal__subtitle">
              Invite another user to collaborate on <strong>{workspace.name}</strong>.
            </p>
            <div className="invite-modal__input-group">
              <label htmlFor="invite-username" className="invite-modal__label">
                Username
              </label>
              <input
                id="invite-username"
                type="text"
                className="invite-modal__input"
                placeholder="Enter username"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                disabled={loading}
                autoFocus
              />
            </div>
            <div className="invite-modal__input-group">
              <label htmlFor="invite-role" className="invite-modal__label">
                Role
              </label>
              <select
                id="invite-role"
                className="invite-modal__input"
                value={role}
                onChange={(e) => setRole(e.target.value)}
                disabled={loading}
                style={{ background: '#2d2d2d', color: '#fff', cursor: 'pointer' }}
              >
                <option value="editor">Editor</option>
                <option value="viewer">Viewer</option>
              </select>
            </div>
            {message && <div className="invite-modal__feedback invite-modal__feedback--success">{message}</div>}
            {error && <div className="invite-modal__feedback invite-modal__feedback--error">{error}</div>}
          </div>
          <div className="invite-modal__footer">
            <button
              type="button"
              className="invite-modal__btn invite-modal__btn--cancel"
              onClick={onClose}
              disabled={loading}
            >
              Cancel
            </button>
            <button
              type="submit"
              className="invite-modal__btn invite-modal__btn--submit"
              disabled={loading || !username.trim()}
            >
              {loading ? 'Sending...' : 'Send Invitation'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
