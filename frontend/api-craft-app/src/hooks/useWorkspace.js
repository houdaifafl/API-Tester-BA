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

  const reloadWorkspaces = useCallback(() => {
    if (!userId) return Promise.resolve([]);
    return getWorkspaces(userId)
      .then(data => {
        setWorkspaces(data);
        return data;
      })
      .catch(() => []);
  }, [userId]);

  // Load all workspaces for the user once
  useEffect(() => {
    reloadWorkspaces();
  }, [reloadWorkspaces]);

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
        if (err.status === 403) {
          getWorkspaces(userId)
            .then(list => {
              setWorkspaces(list);
              const fallback = list.find(w => w.is_default) || list[0] || null;
              if (fallback) {
                navigate(`/workspace/${fallback.id}`);
              } else {
                setWorkspaceError('forbidden');
              }
              setWorkspaceLoading(false);
            })
            .catch(() => {
              setWorkspaceError('forbidden');
              setWorkspaceLoading(false);
            });
        } else {
          const error = err.status === 404 ? 'not_found' : err.status === 400 ? 'invalid' : 'forbidden';
          setWorkspaceError(error);
          setWorkspaceLoading(false);
        }
      });
  }, [workspaceIdParam, userId, navigate]);

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

  const workspaceRole = activeWorkspace ? activeWorkspace.role : 'viewer';

  return {
    workspaces,
    activeWorkspace,
    workspaceRole,
    workspaceError,
    workspaceLoading,
    workspaceIdParam,
    handleSwitch,
    handleWorkspaceCreated,
    handleWorkspaceDeleted,
    reloadWorkspaces,
  };
}
