import { useState, useEffect, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { getWorkspaces, getWorkspaceById } from '../services/workspaceService';
import { useAuth } from '../contexts/AuthContext';

export default function useWorkspace() {
  const { user } = useAuth();
  const { userId } = user;
  const { workspaceId: workspaceIdParam } = useParams();
  const navigate = useNavigate();

  const [workspaces, setWorkspaces]             = useState([]);
  const [activeWorkspace, setActiveWorkspace]   = useState(null);
  const [workspaceError, setWorkspaceError]     = useState(null);
  const [workspaceLoading, setWorkspaceLoading] = useState(true);

  // Load all workspaces for the user once
  useEffect(() => {
    if (!userId) return;
    getWorkspaces(userId)
      .then(data => setWorkspaces(data))
      .catch(() => {});
  }, [userId]);

  // Validate workspace ownership on every URL param change — no fallback allowed
  useEffect(() => {
    if (!userId || !workspaceIdParam) return;
    setActiveWorkspace(null);
    setWorkspaceError(null);
    setWorkspaceLoading(true);
    if (!/^\d+$/.test(workspaceIdParam)) {
      setWorkspaceError('invalid');
      setWorkspaceLoading(false);
      return;
    }
    getWorkspaceById(workspaceIdParam, userId)
      .then(data => { setActiveWorkspace(data); setWorkspaceLoading(false); })
      .catch(err => {
        const error = err.status === 404 ? 'not_found' : err.status === 400 ? 'invalid' : 'forbidden';
        setWorkspaceError(error);
        setWorkspaceLoading(false);
      });
  }, [workspaceIdParam, userId]);

  const handleSwitch = useCallback((ws) => {
    navigate(`/workspace/${ws.id}`);
  }, [navigate]);

  const handleWorkspaceCreated = useCallback((ws) => {
    setWorkspaces(prev => [...prev, ws]);
    navigate(`/workspace/${ws.id}`);
  }, [navigate]);

  const handleWorkspaceDeleted = useCallback((wsId) => {
    const updated = workspaces.filter(w => w.id !== wsId);
    setWorkspaces(updated);
    if (parseInt(workspaceIdParam, 10) === wsId) {
      const fallback = updated.find(w => w.is_default) || updated[0] || null;
      if (fallback) navigate(`/workspace/${fallback.id}`);
    }
  }, [workspaces, workspaceIdParam, navigate]);

  return {
    workspaces,
    activeWorkspace,
    workspaceError,
    workspaceLoading,
    workspaceIdParam,
    handleSwitch,
    handleWorkspaceCreated,
    handleWorkspaceDeleted,
  };
}
