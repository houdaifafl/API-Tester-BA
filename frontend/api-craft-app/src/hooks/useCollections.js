import { useState, useEffect, useCallback, useRef } from 'react';
import { getCollections, addCollection, renameCollection, deleteCollection } from '../services/collectionService';
import { createRequest, renameRequest, deleteRequest, updateRequestMethod, saveRequest } from '../services/requestService';

export default function useCollections({
  activeWorkspaceId,
  handleRequestOpen,
  updateTabMethod,
  updateTabLabel,
  updateTabCollectionName,
  removeTabsByRequestIds,
}) {
  const [collections, setCollections] = useState([]);
  const collectionsRef = useRef([]);

  useEffect(() => {
    collectionsRef.current = collections;
  }, [collections]);

  // Reload collections whenever the active workspace changes
  useEffect(() => {
    if (!activeWorkspaceId) {
      setCollections([]);
      return;
    }
    getCollections(activeWorkspaceId)
      .then(data => {
        setCollections(data.map(col => ({
          ...col,
          requests: col.requests.map(r => ({ ...r, collectionName: col.name })),
        })));
      })
      .catch(() => {});
  }, [activeWorkspaceId]);

  const handleSaveRequest = useCallback(async (requestId, data) => {
    await saveRequest(requestId, data);
    setCollections(prev => prev.map(col => ({
      ...col,
      requests: col.requests.map(r => r.id === requestId ? { ...r, ...data } : r),
    })));
  }, []);

  const handleRequestMethodChange = useCallback(async (id, newMethod) => {
    setCollections(prev => prev.map(col => ({
      ...col,
      requests: col.requests.map(r => r.id === id ? { ...r, method: newMethod } : r),
    })));
    updateTabMethod(id, newMethod);
    try {
      await updateRequestMethod(id, newMethod);
    } catch {}
  }, [updateTabMethod]);

  const handleRequestRename = useCallback(async (id, newName) => {
    setCollections(prev => prev.map(col => ({
      ...col,
      requests: col.requests.map(r => r.id === id ? { ...r, name: newName } : r),
    })));
    updateTabLabel(id, newName);
    try {
      await renameRequest(id, newName);
    } catch {}
  }, [updateTabLabel]);

  const handleRequestDelete = useCallback(async (id) => {
    try {
      await deleteRequest(id);
    } catch {}
    setCollections(prev => prev.map(col => ({
      ...col,
      requests: col.requests.filter(r => r.id !== id),
    })));
    removeTabsByRequestIds([id]);
  }, [removeTabsByRequestIds]);

  const handleRequestAdd = useCallback(async (collectionId) => {
    try {
      const newReq = await createRequest(collectionId);
      const col = collectionsRef.current.find(c => c.id === collectionId);
      const reqWithMeta = { ...newReq, collectionName: col ? col.name : '' };
      setCollections(prev => prev.map(c =>
        c.id === collectionId
          ? { ...c, requests: [...c.requests, reqWithMeta] }
          : c
      ));
      handleRequestOpen(reqWithMeta);
    } catch {}
  }, [handleRequestOpen]);

  const handleCollectionAdd = useCallback(async () => {
    if (!activeWorkspaceId) return;
    try {
      const newCol = await addCollection(activeWorkspaceId);
      setCollections(prev => [...prev, { ...newCol, requests: [] }]);
    } catch {}
  }, [activeWorkspaceId]);

  const handleCollectionRename = useCallback(async (id, newName) => {
    const oldName = collectionsRef.current.find(c => c.id === id)?.name;
    setCollections(prev => prev.map(c => c.id === id ? { ...c, name: newName } : c));
    if (oldName) {
      updateTabCollectionName(oldName, newName);
    }
    try {
      await renameCollection(id, newName);
    } catch {}
  }, [updateTabCollectionName]);

  const handleCollectionDelete = useCallback(async (id) => {
    try {
      await deleteCollection(id);
    } catch {}
    const col = collectionsRef.current.find(c => c.id === id);
    const requestIds = (col?.requests ?? []).map(r => r.id);
    setCollections(prev => prev.filter(c => c.id !== id));
    removeTabsByRequestIds(requestIds);
  }, [removeTabsByRequestIds]);

  return {
    collections,
    handleSaveRequest,
    handleRequestMethodChange,
    handleRequestRename,
    handleRequestDelete,
    handleRequestAdd,
    handleCollectionAdd,
    handleCollectionRename,
    handleCollectionDelete,
  };
}
