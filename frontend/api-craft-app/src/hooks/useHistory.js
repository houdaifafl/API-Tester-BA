import { useState, useEffect, useCallback } from 'react';
import { getHistory, createHistoryItem } from '../services/historyService';

export default function useHistory(activeWorkspaceId) {
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!activeWorkspaceId) {
      setHistory([]);
      setError(null);
      return;
    }
    setLoading(true);
    setError(null);
    getHistory(activeWorkspaceId)
      .then(data => {
        setHistory(data);
      })
      .catch(err => {
        setError(err.message || 'Failed to load history');
      })
      .finally(() => {
        setLoading(false);
      });
  }, [activeWorkspaceId]);

  const addHistoryItem = useCallback(async (historyItem) => {
    if (!activeWorkspaceId) return;
    try {
      const savedItem = await createHistoryItem(activeWorkspaceId, historyItem);
      setHistory(prev => [savedItem, ...prev]);
      return savedItem;
    } catch (err) {
      console.error('Failed to create history item:', err);
      throw err;
    }
  }, [activeWorkspaceId]);

  return {
    history,
    loading,
    error,
    addHistoryItem,
  };
}
