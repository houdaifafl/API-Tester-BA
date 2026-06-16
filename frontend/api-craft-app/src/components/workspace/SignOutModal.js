import './SignOutModal.css';

export default function SignOutModal({ onCancel, onConfirm }) {
  return (
    <div className="signout-overlay" onClick={onCancel}>
      <div className="signout-modal" onClick={e => e.stopPropagation()}>
        <p className="signout-modal-message">Are you sure you want to sign out?</p>
        <div className="signout-modal-actions">
          <button className="signout-btn-cancel" onClick={onCancel}>Cancel</button>
          <button className="signout-btn-confirm" onClick={onConfirm}>Sign out</button>
        </div>
      </div>
    </div>
  );
}
