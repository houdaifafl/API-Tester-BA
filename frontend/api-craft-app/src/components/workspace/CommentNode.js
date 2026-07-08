import React, { useState } from 'react';
import { FaReply, FaEdit, FaTrash, FaCheck, FaTimes } from 'react-icons/fa';

function formatRelativeTime(isoString) {
  try {
    const date = new Date(isoString);
    const now = new Date();
    const diffMs = now - date;
    const diffSec = Math.floor(diffMs / 1000);
    const diffMin = Math.floor(diffSec / 60);
    const diffHr = Math.floor(diffMin / 60);
    const diffDays = Math.floor(diffHr / 24);

    if (diffSec < 10) return 'just now';
    if (diffSec < 60) return `${diffSec}s ago`;
    if (diffMin < 60) return `${diffMin}m ago`;
    if (diffHr < 24) return `${diffHr}h ago`;
    if (diffDays === 1) return 'yesterday';
    return date.toLocaleDateString();
  } catch {
    return '';
  }
}

// Deterministic palette — maps a username to a consistent distinct color
const USER_COLOR_PALETTE = [
  '#ffc107', // amber
  '#4fc3f7', // sky blue
  '#81c784', // soft green
  '#f48fb1', // rose pink
  '#ce93d8', // lavender
  '#ff8a65', // coral orange
  '#80cbc4', // teal
  '#fff176', // light yellow
  '#80deea', // cyan
  '#ffab91', // peach
];

function getUserColor(username) {
  if (!username) return USER_COLOR_PALETTE[0];
  let hash = 0;
  for (let i = 0; i < username.length; i++) {
    hash = username.charCodeAt(i) + ((hash << 5) - hash);
  }
  const index = Math.abs(hash) % USER_COLOR_PALETTE.length;
  return USER_COLOR_PALETTE[index];
}

export default function CommentNode({
  comment,
  isReply = false,
  currentUserId,
  workspaceRole,
  onReplyClick,
  onEdit,
  onDelete,
  onBadgeClick,
  collectionName = ''
}) {
  const [editing, setEditing] = useState(false);
  const [editVal, setEditVal] = useState(comment.content);

  const isCreator = comment.user_id === currentUserId;
  const isWsOwner = workspaceRole === 'owner';

  // Edit own comment is allowed
  const canEdit = isCreator;
  // Delete own comment OR delete other comments if workspace owner
  const canDelete = isCreator || isWsOwner;

  const handleSaveEdit = async () => {
    if (!editVal.trim()) return;
    try {
      await onEdit(comment.id, editVal);
      setEditing(false);
    } catch (err) {
      alert(err.message);
    }
  };

  const handleCancelEdit = () => {
    setEditVal(comment.content);
    setEditing(false);
  };

  const renderBadge = () => {
    if (isReply || (!comment.request_id && comment.target_tab !== 'collection')) return null;
    let badgeText = '';
    if (comment.target_tab === 'collection') {
      badgeText = collectionName || 'Collection';
    } else {
      badgeText = comment.request_name || 'Request';
      if (collectionName) {
        badgeText = `${collectionName} > ${badgeText}`;
      }
      if (comment.target_tab) {
        const tabNames = { params: 'Params', headers: 'Headers', body: 'Body', auth: 'Auth' };
        badgeText += ` > ${tabNames[comment.target_tab] || comment.target_tab}`;
        if (comment.target_key) {
          badgeText += ` > ${comment.target_key}`;
        }
      }
    }
    return (
      <span
        className="comment-badge"
        onClick={() => onBadgeClick?.(comment)}
        title="Click to jump to request context"
      >
        {badgeText}
      </span>
    );
  };

  return (
    <div className={`comment-node ${isReply ? 'comment-reply' : 'comment-parent'}`}>
      <div className="comment-header">
        <span className="comment-author" style={{ color: getUserColor(comment.username) }}>
          {comment.username}
        </span>
        <span className="comment-time">{formatRelativeTime(comment.created_at)}</span>
      </div>

      {editing ? (
        <div className="comment-edit-form">
          <textarea
            className="comment-edit-input"
            value={editVal}
            onChange={e => setEditVal(e.target.value)}
            spellCheck={false}
          />
          <div className="comment-edit-actions">
            <button className="comment-action-btn ok" onClick={handleSaveEdit} title="Save changes">
              <FaCheck />
            </button>
            <button className="comment-action-btn cancel" onClick={handleCancelEdit} title="Cancel">
              <FaTimes />
            </button>
          </div>
        </div>
      ) : (
        <div className="comment-body">
          {renderBadge()}
          <p className="comment-text">{comment.content}</p>
        </div>
      )}

      {!editing && (
        <div className="comment-actions">
          {!isReply && onReplyClick && (
            <button className="comment-action-btn" onClick={() => onReplyClick(comment)} title="Reply">
              <FaReply />
              <span>Reply</span>
            </button>
          )}
          {canEdit && (
            <button className="comment-action-btn" onClick={() => setEditing(true)} title="Edit comment">
              <FaEdit />
              <span>Edit</span>
            </button>
          )}
          {canDelete && (
            <button className="comment-action-btn delete" onClick={() => onDelete(comment.id)} title="Delete comment">
              <FaTrash />
              <span>Delete</span>
            </button>
          )}
        </div>
      )}
    </div>
  );
}
