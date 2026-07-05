import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { FaUserCircle, FaSignOutAlt, FaUsers, FaFolder, FaHistory } from 'react-icons/fa';
import { useAuth } from '../../contexts/AuthContext';
import AdminUsersTab from './AdminUsersTab';
import AdminWorkspacesTab from './AdminWorkspacesTab';
import AdminAuditLogTab from './AdminAuditLogTab';
import './AdminDashboard.css';

export default function AdminDashboard() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState('users');

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <div className="admin-layout">
      {/* Top Header */}
      <header className="admin-header">
        <div className="admin-header-left">
          <span className="admin-logo">APICraft</span>
          <span className="admin-badge">Super Admin</span>
        </div>
        
        <div className="admin-header-right">
          <div className="admin-user-info">
            <FaUserCircle className="admin-user-avatar" />
            <div className="admin-user-details">
              <span className="admin-username">{user.username}</span>
              <span className="admin-email">{user.email}</span>
            </div>
          </div>
          <button className="admin-logout-btn" onClick={handleLogout} title="Sign Out">
            <FaSignOutAlt />
            <span>Sign Out</span>
          </button>
        </div>
      </header>

      <div className="admin-main">
        {/* Sidebar Nav */}
        <aside className="admin-sidebar">
          <ul className="admin-nav">
            <li 
              className={`admin-nav-item ${activeTab === 'users' ? 'active' : ''}`}
              onClick={() => setActiveTab('users')}
            >
              <FaUsers />
              <span>Users</span>
            </li>
            <li 
              className={`admin-nav-item ${activeTab === 'workspaces' ? 'active' : ''}`}
              onClick={() => setActiveTab('workspaces')}
            >
              <FaFolder />
              <span>Workspaces</span>
            </li>
            <li 
              className={`admin-nav-item ${activeTab === 'audit-log' ? 'active' : ''}`}
              onClick={() => setActiveTab('audit-log')}
            >
              <FaHistory />
              <span>Audit Log</span>
            </li>
          </ul>
        </aside>

        {/* Content Area */}
        <section className="admin-content">
          {activeTab === 'users' && <AdminUsersTab />}
          {activeTab === 'workspaces' && <AdminWorkspacesTab />}
          {activeTab === 'audit-log' && <AdminAuditLogTab />}
        </section>
      </div>
    </div>
  );
}
