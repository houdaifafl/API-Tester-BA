import React, { useState } from 'react';
import { FaCube, FaHistory, FaPlus, FaChevronDown, FaChevronRight } from 'react-icons/fa';

export default function Sidebar({ sidebarWidth, onResizeStart }) {
  const [collectionsOpen, setCollectionsOpen] = useState(true);

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
        <input className="ws-search" placeholder="" aria-label="Search" />
        <button className="ws-search-add" title="Add">
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
            <li className="ws-collection-item">
              <FaChevronRight className="ws-item-caret" />
              My Collection
            </li>
          </ul>
        )}
      </nav>

      <div className="ws-brand">APICraft</div>

      <div className="sidebar-resize-handle" onMouseDown={onResizeStart} />
    </aside>
  );
}
