import React, { useEffect, useState } from 'react';
import { getAuditLogs } from '../../services/adminService';

export default function AdminAuditLogTab() {
  const [logs, setLogs] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');

  const fetchLogs = async () => {
    try {
      const data = await getAuditLogs();
      setLogs(data);
    } catch {}
  };

  useEffect(() => {
    fetchLogs();
  }, []);

  const filteredLogs = logs.filter(l => 
    l.admin_username.toLowerCase().includes(searchTerm.toLowerCase()) ||
    l.action.toLowerCase().includes(searchTerm.toLowerCase()) ||
    l.target_type.toLowerCase().includes(searchTerm.toLowerCase()) ||
    (l.target_snapshot && JSON.stringify(l.target_snapshot).toLowerCase().includes(searchTerm.toLowerCase()))
  );

  return (
    <div className="admin-tab">
      <div className="admin-tab-header">
        <h2 className="admin-tab-title">Administrative Audit Logs</h2>
        <input 
          type="text" 
          placeholder="Filter logs by admin, action, target..." 
          className="admin-search-input"
          value={searchTerm}
          onChange={e => setSearchTerm(e.target.value)}
        />
      </div>

      <div className="admin-table-container">
        <table className="admin-table">
          <thead>
            <tr>
              <th>Timestamp</th>
              <th>Admin</th>
              <th>Action</th>
              <th>Target Type</th>
              <th>Target ID</th>
              <th>Details / Snapshot</th>
            </tr>
          </thead>
          <tbody>
            {filteredLogs.length === 0 ? (
              <tr>
                <td colSpan="6" style={{ textAlign: 'center', color: '#888' }}>No logs recorded</td>
              </tr>
            ) : (
              filteredLogs.map(l => (
                <tr key={l.id}>
                  <td style={{ color: '#666', fontSize: '11px' }}>
                    {new Date(l.created_at).toLocaleString()}
                  </td>
                  <td style={{ fontWeight: 600 }}>{l.admin_username}</td>
                  <td>
                    <span style={{ 
                      fontSize: '11.5px',
                      fontFamily: 'monospace', 
                      background: 'rgba(0,0,0,0.05)', 
                      padding: '2px 6px', 
                      borderRadius: '4px' 
                    }}>
                      {l.action}
                    </span>
                  </td>
                  <td>{l.target_type}</td>
                  <td>{l.target_id || '-'}</td>
                  <td>
                    <span style={{ fontSize: '11.5px', color: '#555' }}>
                      {l.target_snapshot ? JSON.stringify(l.target_snapshot) : '-'}
                    </span>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
