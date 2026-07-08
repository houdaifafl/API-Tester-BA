import React, { useState, useRef, useEffect } from 'react';
import { FaChevronDown, FaCheck, FaComment, FaPlus } from 'react-icons/fa';
import './AuthorizationTab.css';

const AUTH_OPTIONS = [
  { value: 'none',   label: 'No Auth' },
  { value: 'bearer', label: 'Bearer Token' },
  { value: 'basic',  label: 'Basic Auth' },
];

const DEFAULT_AUTH = { type: 'bearer', token: '', username: '', password: '' };

export default function AuthorizationTab({ initialAuth, onAuthChange, comments = [], onCommentClick }) {
  const [auth, setAuth] = useState(initialAuth ?? DEFAULT_AUTH);
  const [dropdownOpen, setDropdownOpen] = useState(false);
  const dropdownRef = useRef(null);
  const onAuthChangeRef = useRef(onAuthChange);

  useEffect(() => { onAuthChangeRef.current = onAuthChange; });

  useEffect(() => {
    const handleClickOutside = (e) => {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target)) {
        setDropdownOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const update = (patch) => {
    const next = { ...auth, ...patch };
    setAuth(next);
    onAuthChangeRef.current?.(next);
  };

  const selectedLabel = AUTH_OPTIONS.find(o => o.value === auth.type)?.label ?? '';

  const renderAuthField = (label, fieldKey, inputType, placeholder, value, onChange) => {
    const fieldComments = comments.filter(c => c.target_key === fieldKey);
    const count = fieldComments.length;

    return (
      <div className="auth-field-container">
        <div className="auth-field-header">
          <label className="auth-field-label">{label}</label>
          <div className="auth-field-comment-trigger">
            {count > 0 ? (
              <button
                type="button"
                className="row-comment-btn has-comments"
                onClick={() => onCommentClick?.(fieldKey)}
                title={`${count} comments. Click to view.`}
              >
                <FaComment />
                <span className="row-comment-count">{count}</span>
              </button>
            ) : (
              <button
                type="button"
                className="row-comment-btn add-comment"
                onClick={() => onCommentClick?.(fieldKey)}
                title="Add comment"
              >
                <FaPlus />
              </button>
            )}
          </div>
        </div>
        <input
          id={`comment-target-auth-${fieldKey}`}
          className="auth-field-input"
          type={inputType}
          placeholder={placeholder}
          value={value}
          onChange={onChange}
        />
      </div>
    );
  };

  const tabLevelComments = comments.filter(c => !c.target_key);
  const tabLevelCount = tabLevelComments.length;

  return (
    <div id="comment-target-auth" className="auth-tab">
      {/* ── Left panel ── */}
      <div className="auth-left">
        <div className="tab-header-row" style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '10px' }}>
          <p className="auth-label" style={{ margin: 0 }}>Auth Type</p>
          <div className="tab-comment-trigger" style={{ userSelect: 'none' }}>
            {tabLevelCount > 0 ? (
              <button
                type="button"
                className="row-comment-btn has-comments"
                onClick={() => onCommentClick?.(null)}
                title={`${tabLevelCount} comments on auth. Click to view.`}
              >
                <FaComment />
                <span className="row-comment-count">{tabLevelCount}</span>
              </button>
            ) : (
              <button
                type="button"
                className="row-comment-btn add-comment"
                onClick={() => onCommentClick?.(null)}
                title="Add comment to Auth tab"
              >
                <FaPlus />
              </button>
            )}
          </div>
        </div>
        <div className="auth-dropdown" ref={dropdownRef}>
          <button
            className="auth-dropdown-toggle"
            onClick={() => setDropdownOpen(o => !o)}
          >
            {selectedLabel}
            <FaChevronDown className={`auth-dropdown-caret ${dropdownOpen ? 'open' : ''}`} />
          </button>
          {dropdownOpen && (
            <ul className="auth-dropdown-menu">
              {AUTH_OPTIONS.map(opt => (
                <li
                  key={opt.value}
                  className={`auth-dropdown-item ${auth.type === opt.value ? 'selected' : ''}`}
                  onClick={() => { update({ type: opt.value }); setDropdownOpen(false); }}
                >
                  {opt.label}
                  {auth.type === opt.value && <FaCheck className="auth-check-icon" />}
                </li>
              ))}
            </ul>
          )}
        </div>
      </div>

      <div className="auth-divider" />

      {/* ── Right panel ── */}
      <div className="auth-right">
        {auth.type === 'none' && (
          <div className="auth-no-auth">
            <p className="auth-no-auth-title">No Auth</p>
            <p className="auth-no-auth-desc">This request does not use any authorization.</p>
          </div>
        )}

        {auth.type === 'bearer' && (
          <div className="auth-fields">
            {renderAuthField('Token', 'token', 'text', 'Token', auth.token, e => update({ token: e.target.value }))}
          </div>
        )}

        {auth.type === 'basic' && (
          <div className="auth-fields">
            {renderAuthField('Username', 'username', 'text', 'Username', auth.username, e => update({ username: e.target.value }))}
            {renderAuthField('Password', 'password', 'password', 'Password', auth.password, e => update({ password: e.target.value }))}
          </div>
        )}
      </div>
    </div>
  );
}
