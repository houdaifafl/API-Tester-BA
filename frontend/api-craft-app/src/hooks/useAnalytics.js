import { useState, useEffect, useCallback } from 'react';
import { getAnalytics } from '../services/analyticsService';

/**
 * Hook that fetches and caches workspace analytics data.
 * @param {number|null} workspaceId
 * @param {string} timeframe - '24h' | '7d' | '30d'
 */
export default function useAnalytics(workspaceId, timeframe) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchData = useCallback(async () => {
    if (!workspaceId) return;
    setLoading(true);
    setError(null);
    try {
      const result = await getAnalytics(workspaceId, timeframe);
      setData(result);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, [workspaceId, timeframe]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  return { data, loading, error, refresh: fetchData };
}
