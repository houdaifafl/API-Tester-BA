import React, { useEffect, useState } from 'react';
import { 
  getAdminWorkspaces, deleteWorkspaceByAdmin, 
  getWorkspaceCollectionsByAdmin, deleteCollectionByAdmin, 
  logSensitiveView 
} from '../../services/adminService';
import { FaLock, FaTrashAlt, FaFolder, FaChevronDown, FaChevronRight } from 'react-icons/fa';

export default function AdminWorkspacesTab() {
  const [workspaces, setWorkspaces] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedWs, setSelectedWs] = useState(null);
  const [collections, setCollections] = useState([]);
  const [activeReqId, setActiveReqId] = useState(null);
  const [confirmDeleteWs, setConfirmDeleteWs] = useState(null);
  const [confirmDeleteCol, setConfirmDeleteCol] = useState(null);
  const [collapsedCols, setCollapsedCols] = useState(new Set());

  const fetchWorkspaces = async () => {
    try {
      const data = await getAdminWorkspaces();
      setWorkspaces(data);
    } catch {}
  };

  useEffect(() => {
    fetchWorkspaces();
  }, []);

  const handleSelectWorkspace = async (ws) => {
    setSelectedWs(ws);
    setCollections([]);
    setActiveReqId(null);
    try {
      const cols = await getWorkspaceCollectionsByAdmin(ws.id);
      setCollections(cols);
    } catch {}
  };

  const handleToggleCol = (colId, e) => {
    e.stopPropagation();
    setCollapsedCols(prev => {
      const next = new Set(prev);
      if (next.has(colId)) next.delete(colId);
      else next.add(colId);
      return next;
    });
  };

  const handleViewRequestDetails = async (wsId, req) => {
    setActiveReqId(prev => (prev === req.id ? null : req.id));
    // Log the sensitive view action to audit logs
    try {
      await logSensitiveView(wsId, `Viewed request details (id: ${req.id}, name: "${req.name}", url: "${req.url}")`);
    } catch {}
  };

  const handleDeleteWorkspaceClick = (e, ws) => {
    e.stopPropagation();
    setConfirmDeleteWs(ws);
  };

  const handleConfirmDeleteWorkspace = async () => {
    if (!confirmDeleteWs) return;
    try {
      await deleteWorkspaceByAdmin(confirmDeleteWs.id);
      if (selectedWs?.id === confirmDeleteWs.id) {
        setSelectedWs(null);
        setCollections([]);
      }
      setConfirmDeleteWs(null);
      fetchWorkspaces();
    } catch {}
  };

  const handleDeleteCollectionClick = (e, col) => {
    e.stopPropagation();
    setConfirmDeleteCol(col);
  };

  const handleConfirmDeleteCollection = async () => {
    if (!confirmDeleteCol || !selectedWs) return;
    try {
      await deleteCollectionByAdmin(confirmDeleteCol.id);
      setConfirmDeleteCol(null);
      // Reload collections
      const cols = await getWorkspaceCollectionsByAdmin(selectedWs.id);
      setCollections(cols);
    } catch {}
  };

  const filteredWorkspaces = workspaces.filter(w => 
    w.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    w.owner_username.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="admin-tab" style={{ display: 'flex', gap: '20px', height: 'calc(100vh - 120px)', overflow: 'hidden' }}>
      {/* Left List Pane */}
      <div style={{ flex: '0 0 350px', display: 'flex', flexDirection: 'column', borderRight: '1px solid rgba(0,0,0,0.08)', paddingRight: '20px', height: '100%', overflowY: 'auto' }}>
        <div className="admin-tab-header" style={{ marginBottom: '12px' }}>
          <h2 className="admin-tab-title">Workspaces</h2>
        </div>
        <input 
          type="text" 
          placeholder="Search workspaces..." 
          className="admin-search-input"
          style={{ width: '100%', marginBottom: '16px' }}
          value={searchTerm}
          onChange={e => setSearchTerm(e.target.value)}
        />
        
        <div className="admin-table-container" style={{ flex: 1, overflowY: 'auto' }}>
          <ul style={{ listStyle: 'none', margin: 0, padding: 0 }}>
            {filteredWorkspaces.length === 0 ? (
              <li style={{ padding: '16px', textAlign: 'center', color: '#888', fontSize: '12.5px' }}>No workspaces found</li>
            ) : (
              filteredWorkspaces.map(w => (
                <li 
                  key={w.id} 
                  onClick={() => handleSelectWorkspace(w)}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    padding: '10px 12px',
                    cursor: 'pointer',
                    background: selectedWs?.id === w.id ? 'rgba(0,0,0,0.04)' : 'transparent',
                    borderBottom: '1px solid rgba(0,0,0,0.05)',
                    fontSize: '12.5px'
                  }}
                >
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '2px', minWidth: 0 }}>
                    <span style={{ fontWeight: 600, color: '#1a1a1a', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>{w.name}</span>
                    <span style={{ fontSize: '10px', color: '#888' }}>Owner: {w.owner_username}</span>
                  </div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <span style={{ fontSize: '10px', color: '#666', background: 'rgba(0,0,0,0.05)', padding: '2px 6px', borderRadius: '4px' }}>
                      {w.collections_count} cols
                    </span>
                    <button 
                      className="admin-btn admin-btn--danger" 
                      style={{ padding: '3px 6px' }}
                      onClick={(e) => handleDeleteWorkspaceClick(e, w)}
                      title="Delete Workspace"
                    >
                      <FaTrashAlt style={{ fontSize: '10px' }} />
                    </button>
                  </div>
                </li>
              ))
            )}
          </ul>
        </div>
      </div>

      {/* Right Details Pane */}
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column', height: '100%', overflowY: 'auto' }}>
        {!selectedWs ? (
          <div style={{ display: 'flex', flex: 1, alignItems: 'center', justifyContent: 'center', color: '#888', fontSize: '13px' }}>
            Select a workspace to inspect its collections and requests.
          </div>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
            {/* Workspace Title & Stats */}
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderBottom: '1px solid rgba(0,0,0,0.08)', paddingBottom: '12px' }}>
              <div>
                <h3 style={{ margin: 0, fontSize: '16px', fontWeight: 700, color: '#1a1a1a' }}>{selectedWs.name}</h3>
                <span style={{ fontSize: '11px', color: '#666' }}>Owner: {selectedWs.owner_username} | Members count: {selectedWs.members_count}</span>
              </div>
            </div>

            {/* Privacy Alert Warning Banner */}
            <div style={{
              background: 'rgba(217, 119, 6, 0.08)',
              border: '1px solid rgba(217, 119, 6, 0.25)',
              borderRadius: '6px',
              padding: '10px 14px',
              display: 'flex',
              alignItems: 'center',
              gap: '10px',
              fontSize: '11.5px',
              color: '#d97706'
            }}>
              <FaLock />
              <span>
                <strong>Privacy Notice:</strong> Inspecting saved request configurations containing headers, bodies, or tokens is recorded immutably in the administrative audit logs.
              </span>
            </div>

            {/* Collections List */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
              <h4 style={{ margin: 0, fontSize: '13px', fontWeight: 700, color: '#555' }}>Collections & Requests</h4>
              
              {collections.length === 0 ? (
                <div style={{ fontStyle: 'italic', color: '#888', fontSize: '12.5px', padding: '8px' }}>No collections found in this workspace</div>
              ) : (
                collections.map(col => {
                  const isCollapsed = collapsedCols.has(col.id);
                  return (
                    <div 
                      key={col.id} 
                      style={{ 
                        border: '1px solid rgba(0,0,0,0.06)', 
                        borderRadius: '6px', 
                        background: '#ffffff',
                        overflow: 'hidden'
                      }}
                    >
                      {/* Collection Header Row */}
                      <div 
                        onClick={(e) => handleToggleCol(col.id, e)}
                        style={{
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'space-between',
                          padding: '10px 12px',
                          background: '#f9f9f9',
                          cursor: 'pointer',
                          borderBottom: isCollapsed ? 'none' : '1px solid rgba(0,0,0,0.06)'
                        }}
                      >
                        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '12.5px', fontWeight: 600 }}>
                          {isCollapsed ? <FaChevronRight style={{ fontSize: '10px', color: '#666' }} /> : <FaChevronDown style={{ fontSize: '10px', color: '#666' }} />}
                          <FaFolder style={{ color: '#555' }} />
                          <span>{col.name}</span>
                          {col.is_default && <span style={{ fontSize: '9px', background: 'rgba(0,0,0,0.05)', padding: '1px 4px', borderRadius: '3px' }}>Default</span>}
                        </div>
                        <button 
                          className="admin-btn admin-btn--danger"
                          style={{ padding: '3px 6px' }}
                          onClick={(e) => handleDeleteCollectionClick(e, col)}
                          title="Delete Collection"
                        >
                          <FaTrashAlt style={{ fontSize: '10px' }} />
                        </button>
                      </div>

                      {/* Requests Grid (if expanded) */}
                      {!isCollapsed && (
                        <div style={{ padding: '4px 0' }}>
                          {col.requests.length === 0 ? (
                            <div style={{ fontStyle: 'italic', color: '#888', fontSize: '11.5px', padding: '10px 32px' }}>Empty Collection</div>
                          ) : (
                            col.requests.map(req => {
                              const isDetailsOpen = activeReqId === req.id;
                              return (
                                <div key={req.id} style={{ borderBottom: '1px solid rgba(0,0,0,0.03)' }}>
                                  <div 
                                    onClick={() => handleViewRequestDetails(selectedWs.id, req)}
                                    style={{
                                      display: 'flex',
                                      alignItems: 'center',
                                      justifyContent: 'space-between',
                                      padding: '8px 16px 8px 32px',
                                      cursor: 'pointer',
                                      fontSize: '12px'
                                    }}
                                  >
                                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px', minWidth: 0 }}>
                                      <span style={{ fontWeight: 700, color: '#2980b9', minWidth: '40px' }}>{req.method}</span>
                                      <span style={{ fontWeight: 500, color: '#333' }}>{req.name}</span>
                                      <span style={{ color: '#888', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis', fontSize: '11.5px' }}>{req.url}</span>
                                    </div>
                                    <span style={{ fontSize: '10px', color: '#999' }}>{isDetailsOpen ? 'Hide configurations' : 'Click to inspect config'}</span>
                                  </div>

                                  {/* Request configuration JSON display */}
                                  {isDetailsOpen && (
                                    <div style={{
                                      background: '#fafafa',
                                      padding: '12px 16px 12px 32px',
                                      borderTop: '1px solid rgba(0,0,0,0.03)',
                                      fontFamily: 'monospace',
                                      fontSize: '11px',
                                      color: '#444'
                                    }}>
                                      <pre style={{ margin: 0, overflowX: 'auto' }}>
                                        {JSON.stringify({
                                          url: req.url,
                                          params: req.params,
                                          headers: req.headers,
                                          body: req.body,
                                          auth: req.auth
                                        }, null, 2)}
                                      </pre>
                                    </div>
                                  )}
                                </div>
                              );
                            })
                          )}
                        </div>
                      )}
                    </div>
                  );
                })
              )}
            </div>
          </div>
        )}
      </div>

      {/* Delete Workspace Confirmation Modal */}
      {confirmDeleteWs && (
        <div className="admin-modal-overlay">
          <div className="admin-modal">
            <h3 className="admin-modal-title">Confirm Delete Workspace</h3>
            <p className="admin-modal-body">
              Are you sure you want to permanently delete workspace <strong>{confirmDeleteWs.name}</strong>?<br/>
              This will cascade and delete all collections, requests, and execute history inside it. This action cannot be undone.
            </p>
            <div className="admin-modal-actions">
              <button className="admin-btn" onClick={() => setConfirmDeleteWs(null)}>Cancel</button>
              <button className="admin-btn admin-btn--danger" onClick={handleConfirmDeleteWorkspace}>Delete workspace</button>
            </div>
          </div>
        </div>
      )}

      {/* Delete Collection Confirmation Modal */}
      {confirmDeleteCol && (
        <div className="admin-modal-overlay">
          <div className="admin-modal">
            <h3 className="admin-modal-title">Confirm Delete Collection</h3>
            <p className="admin-modal-body">
              Are you sure you want to permanently delete collection <strong>{confirmDeleteCol.name}</strong>?<br/>
              This will delete all requests saved inside it. This action cannot be undone.
            </p>
            <div className="admin-modal-actions">
              <button className="admin-btn" onClick={() => setConfirmDeleteCol(null)}>Cancel</button>
              <button className="admin-btn admin-btn--danger" onClick={handleConfirmDeleteCollection}>Delete collection</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
