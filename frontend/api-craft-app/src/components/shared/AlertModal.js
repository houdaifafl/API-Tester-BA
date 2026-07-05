import React from 'react';
import { FaExclamationTriangle } from 'react-icons/fa';
import './AlertModal.css';

export default function AlertModal({ message, onClose }) {
  if (!message) return null;

  return (
    <div className="alert-modal-overlay" onClick={onClose}>
      <div className="alert-modal-content" onClick={e => e.stopPropagation()}>
        <div className="alert-modal-header">
          <FaExclamationTriangle className="alert-modal-icon" />
          <h3 className="alert-modal-title">Permission Required</h3>
        </div>
        <p className="alert-modal-message">{message}</p>
        <div className="alert-modal-actions">
          <button className="alert-modal-btn" onClick={onClose}>
            OK
          </button>
        </div>
      </div>
    </div>
  );
}
