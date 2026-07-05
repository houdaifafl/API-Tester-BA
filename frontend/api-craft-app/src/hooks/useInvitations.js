import { useState, useEffect, useCallback } from 'react';
import { getPendingInvitations, acceptInvitation, declineInvitation } from '../services/invitationService';
import { useAuth } from '../contexts/AuthContext';

export default function useInvitations(onWorkspaceAccepted) {
  const { user } = useAuth();
  const [pendingInvitations, setPendingInvitations] = useState([]);

  const refreshInvitations = useCallback(async () => {
    if (!user || !user.userId) return;
    try {
      const data = await getPendingInvitations();
      setPendingInvitations(data);
    } catch (err) {
      console.error('Failed to fetch pending invitations:', err);
    }
  }, [user]);

  const handleAccept = useCallback(async (id) => {
    try {
      await acceptInvitation(id);
      setPendingInvitations(prev => prev.filter(inv => inv.id !== id));
      if (onWorkspaceAccepted) {
        await onWorkspaceAccepted();
      }
    } catch (err) {
      console.error('Failed to accept invitation:', err);
      throw err;
    }
  }, [onWorkspaceAccepted]);

  const handleDecline = useCallback(async (id) => {
    try {
      await declineInvitation(id);
      setPendingInvitations(prev => prev.filter(inv => inv.id !== id));
    } catch (err) {
      console.error('Failed to decline invitation:', err);
      throw err;
    }
  }, []);

  useEffect(() => {
    refreshInvitations();

    // Poll for new invitations every 5 seconds
    const interval = setInterval(() => {
      refreshInvitations();
    }, 5000);

    return () => clearInterval(interval);
  }, [refreshInvitations]);

  return {
    pendingInvitations,
    handleAccept,
    handleDecline,
    refreshInvitations,
  };
}
