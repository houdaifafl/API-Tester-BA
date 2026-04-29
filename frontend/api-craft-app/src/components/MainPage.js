import React, { useState, useRef, useEffect, useCallback } from 'react';
import { FaCube, FaHistory, FaPlus, FaChevronDown, FaChevronRight, FaFileAlt, FaBell, FaBinoculars } from 'react-icons/fa';
import './mainpage.css';

const MIN_SIDEBAR_WIDTH = 150;

export default function MainPage() {
  const rawName = localStorage.getItem('firstName') || 'User';
  const displayName = rawName.charAt(0).toUpperCase() + rawName.slice(1).toLowerCase();

  const [activeTab, setActiveTab] = useState('updates');
  const [collectionsOpen, setCollectionsOpen] = useState(true);
  const [sidebarWidth, setSidebarWidth] = useState(() => window.innerWidth * 0.17);
  const isResizing = useRef(false);

  const startResize = useCallback((e) => {
    isResizing.current = true;
    document.body.style.userSelect = 'none';
    document.body.style.cursor = 'col-resize';
    e.preventDefault();
  }, []);

  useEffect(() => {
    const handleMouseMove = (e) => {
      if (!isResizing.current) return;
      const maxWidth = window.innerWidth * 0.17;
      setSidebarWidth(Math.min(Math.max(e.clientX, MIN_SIDEBAR_WIDTH), maxWidth));
    };

    const handleMouseUp = () => {
      isResizing.current = false;
      document.body.style.userSelect = '';
      document.body.style.cursor = '';
    };

    document.addEventListener('mousemove', handleMouseMove);
    document.addEventListener('mouseup', handleMouseUp);

    return () => {
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseup', handleMouseUp);
    };
  }, []);

  return (
    <div className="workspace">

      {/* ── Top tab bar ── */}
      <div className="top-bar">
        <div className="top-bar-sidebar-space" style={{ width: sidebarWidth }}>
          <div className="ws-header">
            <div className="ws-avatar">
              {displayName.charAt(0)}
            </div>
            <span className="ws-name">{displayName}'s Space</span>
            <FaChevronDown className="ws-caret" />
          </div>
        </div>
        <div className="top-bar-tabs">
          <div className="top-tab">
            <FaBinoculars className="top-tab-icon" />
            Overview
          </div>
          <button className="top-tab-add" title="New tab">
            <FaPlus />
          </button>
        </div>
      </div>

      {/* ── Body ── */}
      <div className="workspace-body">

        {/* ── Sidebar ── */}
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

          {/* ── Drag handle ── */}
          <div className="sidebar-resize-handle" onMouseDown={startResize} />
        </aside>

        {/* ── Main panel ── */}
        <main className="main-panel">
          <div className="panel-tab-bar">
            <button
              className={`panel-tab ${activeTab === 'docs' ? 'active' : ''}`}
              onClick={() => setActiveTab('docs')}
            >
              <FaFileAlt className="panel-tab-icon" />
              Docs
            </button>
            <button
              className={`panel-tab ${activeTab === 'updates' ? 'active' : ''}`}
              onClick={() => setActiveTab('updates')}
            >
              <FaBell className="panel-tab-icon" />
              Updates
            </button>
          </div>

          <div className="panel-body">
            {activeTab === 'docs' && (
              <p className="panel-empty">Documentation will appear here.</p>
            )}
            {activeTab === 'updates' && (
              <p className="panel-empty">Keep users informed about all new features</p>
            )}
          </div>
        </main>

      </div>
    </div>
  );
}
