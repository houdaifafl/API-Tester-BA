import React, { useState, useRef, useEffect, useCallback } from 'react';
import { FaCube, FaHistory, FaPlus, FaChevronDown, FaChevronRight, FaEllipsisH } from 'react-icons/fa';
import RequestContextMenu from './RequestContextMenu';
import './Sidebar.css';

export default function Sidebar({
  sidebarWidth,
  onResizeStart,
  activeRequestId,
  onRequestOpen,
  collections,
  onRequestAdd,
  onRequestRename,
  onRequestDelete,
  onCollectionAdd,
  onCollectionRename,
  onCollectionDelete,
}) {
  const [collectionsOpen, setCollectionsOpen]   = useState(true);
  const [collapsedCols, setCollapsedCols]       = useState(new Set());
  const [searchQuery, setSearchQuery]           = useState('');

  // Context menu state — { kind: 'request'|'collection', id, rect }
  const [menuState, setMenuState]               = useState(null);

  // Rename state — { kind: 'request'|'collection', id, value }
  const [renaming, setRenaming]                 = useState(null);
  const renameInputRef = useRef(null);

  const renamingId = renaming?.id;
  useEffect(() => {
    if (renamingId && renameInputRef.current) {
      renameInputRef.current.focus();
      renameInputRef.current.select();
    }
  }, [renamingId]);

  const toggleCollection = useCallback((colId) => {
    setCollapsedCols(prev => {
      const next = new Set(prev);
      if (next.has(colId)) next.delete(colId); else next.add(colId);
      return next;
    });
  }, []);

  const openRequestMenu = useCallback((e, req) => {
    e.stopPropagation();
    setMenuState({ kind: 'request', id: req.id, rect: e.currentTarget.getBoundingClientRect() });
  }, []);

  const openCollectionMenu = useCallback((e, col) => {
    e.stopPropagation();
    setMenuState({ kind: 'collection', id: col.id, isDefault: col.is_default, rect: e.currentTarget.getBoundingClientRect() });
  }, []);

  const closeMenu = useCallback(() => setMenuState(null), []);

  const startRename = useCallback((kind, id, currentName) => {
    setRenaming({ kind, id, value: currentName });
  }, []);

  const commitRename = useCallback((value) => {
    if (!renaming) return;
    const trimmed = value.trim();
    if (trimmed) {
      if (renaming.kind === 'request') onRequestRename(renaming.id, trimmed);
      else onCollectionRename(renaming.id, trimmed);
    }
    setRenaming(null);
  }, [renaming, onRequestRename, onCollectionRename]);

  const cancelRename = useCallback(() => setRenaming(null), []);

  const allRequests = collections.flatMap(c => c.requests);

  const query = searchQuery.trim().toLowerCase();
  const filteredCollections = query
    ? collections.reduce((acc, col) => {
        const colMatches = col.name.toLowerCase().includes(query);
        const matchingRequests = col.requests.filter(r =>
          r.name.toLowerCase().includes(query)
        );
        if (colMatches) {
          acc.push({ ...col });
        } else if (matchingRequests.length > 0) {
          acc.push({ ...col, requests: matchingRequests });
        }
        return acc;
      }, [])
    : collections;

  return (
    <aside className="sidebar" style={{ width: sidebarWidth }}>
      <div className="ws-toolbar">
        <button className="ws-icon-btn active" title="Collections">
          <FaCube />
        </button>
        <button className="ws-icon-btn" title="History">
          <FaHistory />
        </button>
      </div>

      <div className="ws-search-row">
        <input
          className="ws-search"
          placeholder="Search"
          aria-label="Search"
          value={searchQuery}
          onChange={e => setSearchQuery(e.target.value)}
        />
        <button
          className="ws-search-add"
          title="Add collection"
          onClick={onCollectionAdd}
        >
          <FaPlus />
        </button>
      </div>

      <nav className="ws-nav">
        <div
          className="ws-section-header"
          onClick={() => setCollectionsOpen(o => !o)}
        >
          {collectionsOpen
            ? <FaChevronDown className="ws-section-caret" />
            : <FaChevronRight className="ws-section-caret" />}
          Collections
        </div>

        {collectionsOpen && (
          <ul className="ws-collection-list">
            {filteredCollections.length === 0 && query && (
              <li className="ws-no-results">No results found</li>
            )}
            {filteredCollections.map(col => {
              const expanded = query ? true : !collapsedCols.has(col.id);
              const isRenamingCol = renaming?.kind === 'collection' && renaming.id === col.id;

              return (
                <li key={col.id}>
                  <div
                    className="ws-collection-row"
                    onClick={() => { if (!isRenamingCol) toggleCollection(col.id); }}
                  >
                    {expanded
                      ? <FaChevronDown className="ws-item-caret" />
                      : <FaChevronRight className="ws-item-caret" />}

                    {isRenamingCol ? (
                      <input
                        ref={renameInputRef}
                        className="ws-rename-input"
                        value={renaming.value}
                        onChange={e => setRenaming(r => ({ ...r, value: e.target.value }))}
                        onKeyDown={e => {
                          if (e.key === 'Enter')  commitRename(renaming.value);
                          if (e.key === 'Escape') cancelRename();
                        }}
                        onBlur={() => commitRename(renaming.value)}
                        onClick={e => e.stopPropagation()}
                      />
                    ) : (
                      <span className="ws-collection-name">{col.name}</span>
                    )}

                    {!isRenamingCol && (
                      <>
                        <button
                          className="ws-item-add-btn"
                          title="Add request"
                          onClick={e => { e.stopPropagation(); onRequestAdd(col.id); }}
                        >
                          <FaPlus />
                        </button>
                        <button
                          className="ws-req-menu-btn"
                          title="More actions"
                          onClick={e => openCollectionMenu(e, col)}
                        >
                          <FaEllipsisH />
                        </button>
                      </>
                    )}
                  </div>

                  {expanded && (
                    <ul className="ws-request-list">
                      {col.requests.map(req => {
                        const isRenamingReq = renaming?.kind === 'request' && renaming.id === req.id;
                        return (
                          <li
                            key={req.id}
                            className={`ws-request-item ${activeRequestId === req.id ? 'active' : ''}`}
                            onClick={() => { if (!isRenamingReq) onRequestOpen(req); }}
                          >
                            <span className={`ws-method-badge ws-method-${req.method.toLowerCase()}`}>
                              {req.method}
                            </span>

                            {isRenamingReq ? (
                              <input
                                ref={renameInputRef}
                                className="ws-rename-input"
                                value={renaming.value}
                                onChange={e => setRenaming(r => ({ ...r, value: e.target.value }))}
                                onKeyDown={e => {
                                  if (e.key === 'Enter')  commitRename(renaming.value);
                                  if (e.key === 'Escape') cancelRename();
                                }}
                                onBlur={() => commitRename(renaming.value)}
                                onClick={e => e.stopPropagation()}
                              />
                            ) : (
                              <span className="ws-request-name">{req.name}</span>
                            )}

                            {!isRenamingReq && (
                              <button
                                className="ws-req-menu-btn"
                                onClick={e => openRequestMenu(e, req)}
                                title="More actions"
                              >
                                <FaEllipsisH />
                              </button>
                            )}
                          </li>
                        );
                      })}
                    </ul>
                  )}
                </li>
              );
            })}
          </ul>
        )}
      </nav>

      <div className="ws-brand">APICraft</div>

      <div className="sidebar-resize-handle" onMouseDown={onResizeStart} />

      {menuState?.kind === 'request' && (
        <RequestContextMenu
          anchorRect={menuState.rect}
          onRename={() => {
            const req = allRequests.find(r => r.id === menuState.id);
            if (req) startRename('request', req.id, req.name);
          }}
          onDelete={() => onRequestDelete(menuState.id)}
          onClose={closeMenu}
        />
      )}

      {menuState?.kind === 'collection' && (
        <RequestContextMenu
          anchorRect={menuState.rect}
          onRename={() => {
            const col = collections.find(c => c.id === menuState.id);
            if (col) startRename('collection', col.id, col.name);
          }}
          onDelete={menuState.isDefault ? null : () => onCollectionDelete(menuState.id)}
          onClose={closeMenu}
        />
      )}
    </aside>
  );
}
