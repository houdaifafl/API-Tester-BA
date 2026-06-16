import React, { useState, useRef, useEffect } from 'react';
import { FaChevronDown, FaCheck } from 'react-icons/fa';
import './AuthorizationTab.css';

const AUTH_OPTIONS = [
  { value: 'none',   label: 'No Auth' },
  { value: 'bearer', label: 'Bearer Token' },
  { value: 'basic',  label: 'Basic Auth' },
];

const DEFAULT_AUTH = { type: 'bearer', token: '', username: '', password: '' };

export default function AuthorizationTab({ initialAuth, onAuthChange }) {
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

  return (
    <div className="auth-tab">
      {/* ── Left panel ── */}
      <div className="auth-left">
        <p className="auth-label">Auth Type</p>
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
            <div>
              <label className="auth-field-label">Token</label>
              <input
                className="auth-field-input"
                type="text"
                placeholder="Token"
                value={auth.token}
                onChange={e => update({ token: e.target.value })}
              />
            </div>
          </div>
        )}

        {auth.type === 'basic' && (
          <div className="auth-fields">
            <div>
              <label className="auth-field-label">Username</label>
              <input
                className="auth-field-input"
                type="text"
                placeholder="Username"
                value={auth.username}
                onChange={e => update({ username: e.target.value })}
              />
            </div>
            <div>
              <label className="auth-field-label">Password</label>
              <input
                className="auth-field-input"
                type="password"
                placeholder="Password"
                value={auth.password}
                onChange={e => update({ password: e.target.value })}
              />
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
