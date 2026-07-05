import React, { useEffect, useState } from 'react';
import { getAdminUsers, suspendUser, reactivateUser, promoteUser, demoteUser, deleteUser } from '../../services/adminService';
import { useAuth } from '../../contexts/AuthContext';

export default function AdminUsersTab() {
  const { user: currentUser } = useAuth();
  const [users, setUsers] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [deleteConfirmUser, setDeleteConfirmUser] = useState(null);

  const fetchUsers = async () => {
    try {
      const data = await getAdminUsers();
      setUsers(data);
    } catch {}
  };

  useEffect(() => {
    fetchUsers();
  }, []);

  const handleSuspend = async (userId) => {
    try {
      await suspendUser(userId);
      fetchUsers();
    } catch {}
  };

  const handleReactivate = async (userId) => {
    try {
      await reactivateUser(userId);
      fetchUsers();
    } catch {}
  };

  const handlePromote = async (userId) => {
    try {
      await promoteUser(userId);
      fetchUsers();
    } catch {}
  };

  const handleDemote = async (userId) => {
    try {
      await demoteUser(userId);
      fetchUsers();
    } catch {}
  };

  const handleDeleteClick = (user) => {
    setDeleteConfirmUser(user);
  };

  const handleConfirmDelete = async () => {
    if (!deleteConfirmUser) return;
    try {
      await deleteUser(deleteConfirmUser.id);
      setDeleteConfirmUser(null);
      fetchUsers();
    } catch {}
  };

  const filteredUsers = users.filter(u => 
    u.username.toLowerCase().includes(searchTerm.toLowerCase()) ||
    u.email.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="admin-tab">
      <div className="admin-tab-header">
        <h2 className="admin-tab-title">User Management</h2>
        <input 
          type="text" 
          placeholder="Search by username or email..." 
          className="admin-search-input"
          value={searchTerm}
          onChange={e => setSearchTerm(e.target.value)}
        />
      </div>

      <div className="admin-table-container">
        <table className="admin-table">
          <thead>
            <tr>
              <th>Username</th>
              <th>Email</th>
              <th>Status</th>
              <th>Workspaces</th>
              <th>Admin Privileges</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {filteredUsers.length === 0 ? (
              <tr>
                <td colSpan="6" style={{ textAlign: 'center', color: '#888' }}>No users found</td>
              </tr>
            ) : (
              filteredUsers.map(u => (
                <tr key={u.id}>
                  <td style={{ fontWeight: 600 }}>{u.username}</td>
                  <td>{u.email}</td>
                  <td>
                    <span style={{ 
                      color: u.is_suspended ? '#c0392b' : '#28a745', 
                      fontWeight: 600 
                    }}>
                      {u.is_suspended ? 'Suspended' : 'Active'}
                    </span>
                  </td>
                  <td>{u.workspaces_count}</td>
                  <td>{u.is_admin ? 'Yes' : 'No'}</td>
                  <td>
                    <div style={{ display: 'flex', gap: '6px' }}>
                      {u.id !== currentUser.userId && (
                        <>
                          {u.is_suspended ? (
                            <button className="admin-btn admin-btn--success" onClick={() => handleReactivate(u.id)}>
                              Reactivate
                            </button>
                          ) : (
                            <button className="admin-btn admin-btn--warn" onClick={() => handleSuspend(u.id)}>
                              Suspend
                            </button>
                          )}
                          
                          {u.is_admin ? (
                            <button className="admin-btn" onClick={() => handleDemote(u.id)}>
                              Demote
                            </button>
                          ) : (
                            <button className="admin-btn admin-btn--success" onClick={() => handlePromote(u.id)}>
                              Promote
                            </button>
                          )}
                          
                          <button className="admin-btn admin-btn--danger" onClick={() => handleDeleteClick(u)}>
                            Delete
                          </button>
                        </>
                      )}
                    </div>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {deleteConfirmUser && (
        <div className="admin-modal-overlay">
          <div className="admin-modal">
            <h3 className="admin-modal-title">Confirm Deletion</h3>
            <p className="admin-modal-body">
              Are you sure you want to permanently delete user <strong>{deleteConfirmUser.username}</strong>?<br/>
              This will cascade and delete all workspaces, collections, requests, and logs owned by this user. This action cannot be undone.
            </p>
            <div className="admin-modal-actions">
              <button className="admin-btn" onClick={() => setDeleteConfirmUser(null)}>Cancel</button>
              <button className="admin-btn admin-btn--danger" onClick={handleConfirmDelete}>Delete permanently</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
