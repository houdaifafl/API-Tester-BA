import React, { useEffect, useState } from 'react';
import { getActivities } from '../../services/activityService';
import { FaHistory, FaPlus, FaTrash, FaEdit, FaChevronDown, FaChevronUp, FaPlay, FaUserCheck, FaUserTimes, FaKey } from 'react-icons/fa';
import './ActivityLogTab.css';

export default function ActivityLogTab({ workspaceId, workspaceRole }) {
  const [activities, setActivities] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [expandedIds, setExpandedIds] = useState(new Set());

  useEffect(() => {
    let active = true;
    const fetchLogs = async () => {
      setLoading(true);
      setError(null);
      try {
        const logs = await getActivities(workspaceId);
        if (active) setActivities(logs);
      } catch (err) {
        if (active) setError(err.message || 'Failed to load activities');
      } finally {
        if (active) setLoading(false);
      }
    };
    fetchLogs();
    return () => { active = false; };
  }, [workspaceId]);

  const toggleExpand = (id) => {
    const next = new Set(expandedIds);
    if (next.has(id)) next.delete(id);
    else next.add(id);
    setExpandedIds(next);
  };

  const getActionIcon = (category, action) => {
    if (action === 'create') return <FaPlus className="act-icon act-icon--create" />;
    if (action === 'delete') return <FaTrash className="act-icon act-icon--delete" />;
    if (action === 'execute') return <FaPlay className="act-icon act-icon--execute" />;
    if (action === 'invite') return <FaKey className="act-icon act-icon--invite" />;
    if (action === 'join') return <FaUserCheck className="act-icon act-icon--join" />;
    if (action === 'leave' || action === 'decline' || action === 'revoke') return <FaUserTimes className="act-icon act-icon--leave" />;
    return <FaEdit className="act-icon act-icon--edit" />;
  };

  const getEventText = (act) => {
    const userSpan = <strong className="act-user">@{act.user_username}</strong>;
    const targetSpan = <strong className="act-target">"{act.target_name}"</strong>;

    if (act.event_category === 'workspace') {
      if (act.action === 'create') return <>{userSpan} created the workspace {targetSpan}</>;
      if (act.action === 'rename') return <>{userSpan} renamed the workspace to {targetSpan}</>;
      if (act.action === 'delete') return <>{userSpan} deleted the workspace {targetSpan}</>;
    }
    if (act.event_category === 'collection') {
      if (act.action === 'create') return <>{userSpan} created collection {targetSpan}</>;
      if (act.action === 'rename') return <>{userSpan} renamed collection to {targetSpan}</>;
      if (act.action === 'delete') return <>{userSpan} deleted collection {targetSpan}</>;
    }
    if (act.event_category === 'request') {
      if (act.action === 'create') return <>{userSpan} created request {targetSpan}</>;
      if (act.action === 'rename') return <>{userSpan} renamed request to {targetSpan}</>;
      if (act.action === 'update') return <>{userSpan} updated request parameters on {targetSpan}</>;
      if (act.action === 'delete') return <>{userSpan} deleted request {targetSpan}</>;
    }
    if (act.event_category === 'membership') {
      if (act.action === 'invite') return <>{userSpan} invited collaborator <span className="act-email">{act.target_name}</span></>;
      if (act.action === 'join') return <>{userSpan} joined the workspace</>;
      if (act.action === 'decline') return <>{userSpan} declined invitation to the workspace</>;
      if (act.action === 'revoke') return <>{userSpan} cancelled invitation to <span className="act-email">{act.target_name}</span></>;
      if (act.action === 'role_change') return <>{userSpan} updated collaborator role for {targetSpan}</>;
      if (act.action === 'leave') return <>{userSpan} removed collaborator/left workspace {targetSpan}</>;
    }
    if (act.event_category === 'execution') {
      return <>{userSpan} executed request {targetSpan}</>;
    }
    return <>{userSpan} performed {act.action} on {act.target_type} {targetSpan}</>;
  };

  const formatTimestamp = (isoString) => {
    const d = new Date(isoString);
    return d.toLocaleString(undefined, {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const renderDiffState = (field, val, isBefore) => {
    if (val === null || val === undefined) return null;
    let displayVal = val;
    if (typeof val === 'object') {
      displayVal = JSON.stringify(val, null, 2);
    }
    return (
      <div className={`act-diff-line ${isBefore ? 'act-diff-line--before' : 'act-diff-line--after'}`} key={field + (isBefore ? '-b' : '-a')}>
        <span className="act-diff-sign">{isBefore ? '-' : '+'}</span>
        <span className="act-diff-field">{field}:</span>
        <pre className="act-diff-val">{displayVal}</pre>
      </div>
    );
  };

  const renderDiffs = (act) => {
    const before = act.before_state || {};
    const after = act.after_state || {};
    const fields = Array.from(new Set([...Object.keys(before), ...Object.keys(after)]));

    if (fields.length === 0) return null;

    return (
      <div className="act-diff-viewer">
        {fields.map(field => (
          <React.Fragment key={field}>
            {renderDiffState(field, before[field], true)}
            {renderDiffState(field, after[field], false)}
          </React.Fragment>
        ))}
      </div>
    );
  };

  if (loading) {
    return <div className="act-status-msg">Loading activity logs...</div>;
  }

  if (error) {
    return <div className="act-status-msg act-status-msg--error">{error}</div>;
  }

  if (activities.length === 0) {
    return (
      <div className="act-empty-state">
        <FaHistory className="act-empty-icon" />
        <p>No activity logs found for this workspace.</p>
      </div>
    );
  }

  return (
    <div className="act-timeline-container">
      <div className="act-timeline">
        {activities.map(act => {
          const isExpanded = expandedIds.has(act.id);
          const hasDiff = (act.before_state && Object.keys(act.before_state).length > 0) ||
                          (act.after_state && Object.keys(act.after_state).length > 0);

          return (
            <div className="act-timeline-item" key={act.id}>
              <div className="act-timeline-line"></div>
              <div className="act-timeline-badge">
                {getActionIcon(act.event_category, act.action)}
              </div>
              <div className="act-timeline-content">
                <div className="act-timeline-header">
                  <span className="act-timeline-text">{getEventText(act)}</span>
                  <span className="act-timeline-time">{formatTimestamp(act.created_at)}</span>
                </div>
                {hasDiff && (
                  <div className="act-timeline-actions">
                    <button className="act-expand-btn" onClick={() => toggleExpand(act.id)}>
                      {isExpanded ? (
                        <><FaChevronUp /> Hide Diffs</>
                      ) : (
                        <><FaChevronDown /> Show Diffs</>
                      )}
                    </button>
                  </div>
                )}
                {isExpanded && hasDiff && renderDiffs(act)}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
