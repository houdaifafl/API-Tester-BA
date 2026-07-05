import React, { useEffect, useState, useRef } from 'react';
import { FaBell } from 'react-icons/fa';
import { getUserNotifications, markNotificationsRead } from '../../services/adminService';
import './NotificationBell.css';

export default function NotificationBell() {
  const [notifications, setNotifications] = useState([]);
  const [isOpen, setIsOpen] = useState(false);
  const containerRef = useRef(null);

  const fetchNotifs = async () => {
    try {
      const data = await getUserNotifications();
      setNotifications(data);
    } catch {}
  };

  useEffect(() => {
    fetchNotifs();
    // Poll notifications every 10 seconds for real-time updates
    const interval = setInterval(fetchNotifs, 10000);

    const handleOutsideClick = (e) => {
      if (containerRef.current && !containerRef.current.contains(e.target)) {
        setIsOpen(false);
      }
    };
    document.addEventListener('mousedown', handleOutsideClick);

    return () => {
      clearInterval(interval);
      document.removeEventListener('mousedown', handleOutsideClick);
    };
  }, []);

  const handleToggle = async () => {
    const nextState = !isOpen;
    setIsOpen(nextState);
    if (nextState && unreadCount > 0) {
      try {
        await markNotificationsRead();
        // Update local status as read
        setNotifications(prev => prev.map(n => ({ ...n, is_read: true })));
      } catch {}
    }
  };

  const unreadCount = notifications.filter(n => !n.is_read).length;

  return (
    <div className="notif-container" ref={containerRef}>
      <button className="notif-bell-btn" onClick={handleToggle} title="Notifications">
        <FaBell />
        {unreadCount > 0 && <span className="notif-badge">{unreadCount}</span>}
      </button>

      {isOpen && (
        <div className="notif-dropdown">
          <div className="notif-header">Notifications</div>
          <ul className="notif-list">
            {notifications.length === 0 ? (
              <li className="notif-empty">No notifications</li>
            ) : (
              notifications.map(notif => (
                <li key={notif.id} className={`notif-item ${!notif.is_read ? 'notif-item--unread' : ''}`}>
                  <span className="notif-message">{notif.message}</span>
                  <span className="notif-time">
                    {new Date(notif.created_at).toLocaleDateString()} at {new Date(notif.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                  </span>
                </li>
              ))
            )}
          </ul>
        </div>
      )}
    </div>
  );
}
