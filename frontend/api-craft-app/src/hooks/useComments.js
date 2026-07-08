import { useState, useEffect, useCallback } from 'react';
import { getComments, postComment, editComment, deleteComment } from '../services/commentService';

export default function useComments(workspaceId, activeRequestId = null) {
  const [comments, setComments] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [isChatOpen, setIsChatOpen] = useState(false);
  const [filterType, setFilterType] = useState('all'); // 'all', 'request', 'element'
  const [elementFilter, setElementFilter] = useState(null); // { requestId, tab, key }
  const [draftBinding, setDraftBinding] = useState(null); // { requestId, tab, key }
  const [isFocused, setIsFocused] = useState(true);

  // Monitor window focus
  useEffect(() => {
    const onFocus = () => setIsFocused(true);
    const onBlur = () => setIsFocused(false);
    window.addEventListener('focus', onFocus);
    window.addEventListener('blur', onBlur);
    return () => {
      window.removeEventListener('focus', onFocus);
      window.removeEventListener('blur', onBlur);
    };
  }, []);

  const loadComments = useCallback(async (showLoading = false) => {
    if (!workspaceId) return;
    if (showLoading) setLoading(true);
    try {
      const data = await getComments(workspaceId);
      setComments(data);
      setError(null);
    } catch (err) {
      setError(err.message);
    } finally {
      if (showLoading) setLoading(false);
    }
  }, [workspaceId]);

  // Polling loop
  useEffect(() => {
    if (!workspaceId) return;
    loadComments(true);
    const interval = setInterval(() => {
      if (isFocused && document.hasFocus()) {
        loadComments(false);
      }
    }, 10000);
    return () => clearInterval(interval);
  }, [workspaceId, isFocused, loadComments]);

  const handleAddComment = useCallback(async (content, parentId = null) => {
    if (!workspaceId) return;
    
    // If it's a new parent comment, check draftBinding context
    const payload = { content };
    if (parentId !== null) {
      payload.parent_id = parentId;
    } else if (draftBinding) {
      if (draftBinding.collectionId && !draftBinding.requestId) {
        // Collection-only binding (no request selected)
        payload.target_tab = 'collection';
        payload.target_key = String(draftBinding.collectionId);
      } else {
        // Request-level binding (collection is implicit via the request FK)
        if (draftBinding.requestId) payload.request_id = draftBinding.requestId;
        if (draftBinding.tab) payload.target_tab = draftBinding.tab;
        if (draftBinding.key) payload.target_key = draftBinding.key;
      }
    }

    try {
      const newComment = await postComment(workspaceId, payload);
      
      // Optimistically update local comments state
      if (parentId === null) {
        setComments(prev => [...prev, newComment]);
      } else {
        setComments(prev => prev.map(c => {
          if (c.id === parentId) {
            return {
              ...c,
              replies: [...(c.replies || []), newComment]
            };
          }
          return c;
        }));
      }
      return newComment;
    } catch (err) {
      setError(err.message);
      throw err;
    }
  }, [workspaceId, draftBinding]);

  const handleEditComment = useCallback(async (commentId, content) => {
    try {
      const updated = await editComment(commentId, content);
      setComments(prev => prev.map(c => {
        if (c.id === commentId) {
          return { ...c, content: updated.content, updated_at: updated.updated_at };
        }
        if (c.replies) {
          const hasReply = c.replies.some(r => r.id === commentId);
          if (hasReply) {
            return {
              ...c,
              replies: c.replies.map(r => r.id === commentId ? { ...r, content: updated.content, updated_at: updated.updated_at } : r)
            };
          }
        }
        return c;
      }));
    } catch (err) {
      setError(err.message);
      throw err;
    }
  }, []);

  const handleDeleteComment = useCallback(async (commentId) => {
    try {
      await deleteComment(commentId);
      setComments(prev => prev.filter(c => {
        if (c.id === commentId) return false;
        if (c.replies) {
          c.replies = c.replies.filter(r => r.id !== commentId);
        }
        return true;
      }));
    } catch (err) {
      setError(err.message);
      throw err;
    }
  }, []);

  const openCommentsForElement = useCallback((requestId, tab, key = null) => {
    setIsChatOpen(true);
    setFilterType('element');
    setElementFilter({ requestId, tab, key });
    setDraftBinding({ requestId, tab, key });
  }, []);

  const openCommentsForDraft = useCallback((requestId, tab, key = null) => {
    setIsChatOpen(true);
    setDraftBinding({ requestId, tab, key });
  }, []);

  const openCommentsForCollectionDraft = useCallback((collectionId) => {
    setIsChatOpen(true);
    setDraftBinding({ collectionId, requestId: null, tab: null, key: null });
  }, []);

  const toggleChat = useCallback(() => {
    setIsChatOpen(prev => !prev);
  }, []);

  return {
    comments,
    loading,
    error,
    isChatOpen,
    filterType,
    elementFilter,
    draftBinding,
    setFilterType,
    setElementFilter,
    setDraftBinding,
    setIsChatOpen,
    handleAddComment,
    handleEditComment,
    handleDeleteComment,
    openCommentsForElement,
    openCommentsForDraft,
    openCommentsForCollectionDraft,
    toggleChat,
    reloadComments: () => loadComments(true)
  };
}
