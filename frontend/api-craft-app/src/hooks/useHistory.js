import { useState, useEffect, useCallback } from 'react';
import { getHistory, createHistoryItem } from '../services/historyService';

export default function useHistory(activeWorkspaceId) {
  const [history, setHistory] = useState([]);

  useEffect(() => {
    if (!activeWorkspaceId) {
      setHistory([]);
      return;
    }
    getHistory(activeWorkspaceId)
      .then(data => {
        setHistory(data);
      })
      .catch(err => {
        console.error('Failed to load history:', err);
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
    addHistoryItem,
  };
}
