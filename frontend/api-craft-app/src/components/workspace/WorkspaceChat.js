import React, { useState, useEffect, useRef } from 'react';
import { FaTimes, FaCommentAlt, FaPaperPlane } from 'react-icons/fa';
import CommentNode from './CommentNode';
import './WorkspaceChat.css';

export default function WorkspaceChat({
  workspaceId,
  currentUserId,
  workspaceRole,
  collections = [],
  activeRequestId = null,
  commentsState, // From useComments hook
  onBadgeNavigate // Custom event dispatcher or callback
}) {
  const {
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
    handleDeleteComment
  } = commentsState;

  const [inputVal, setInputVal] = useState('');
  const [replyingTo, setReplyingTo] = useState(null); // comment object
  const [showLinkContext, setShowLinkContext] = useState(false);
  const [selectedColId, setSelectedColId] = useState('');
  const [selectedReqId, setSelectedReqId] = useState('');
  const [selectedTab, setSelectedTab] = useState('');
  const [selectedKey, setSelectedKey] = useState('');

  const feedRef = useRef(null);

  // Auto-scroll to bottom of feed on load/new message
  useEffect(() => {
    if (feedRef.current) {
      feedRef.current.scrollTop = feedRef.current.scrollHeight;
    }
  }, [comments, isChatOpen]);

  if (!isChatOpen) return null;

  // Flattened requests list for link selectors
  const requests = collections.flatMap(c => c.requests || []);

  const getRequestCollectionName = (requestId) => {
    if (!requestId) return '';
    const col = collections.find(c => (c.requests || []).some(r => r.id === requestId));
    return col ? col.name : '';
  };

  const getFilteredComments = () => {
    if (filterType === 'element' && elementFilter) {
      return comments.filter(c => 
        c.request_id === elementFilter.requestId &&
        c.target_tab === elementFilter.tab &&
        (!elementFilter.key || c.target_key === elementFilter.key)
      );
    }
    if (filterType === 'request' && activeRequestId) {
      return comments.filter(c => c.request_id === activeRequestId);
    }
    return comments; // 'all'
  };

  const handlePost = async (e) => {
    e.preventDefault();
    if (!inputVal.trim()) return;

    try {
      if (replyingTo) {
        await handleAddComment(inputVal, replyingTo.id);
        setReplyingTo(null);
      } else {
        await handleAddComment(inputVal);
        // Clear binding context and manual selectors on successful submit
        setDraftBinding(null);
        setSelectedReqId('');
        setSelectedTab('');
        setSelectedKey('');
        if (showLinkContext) {
          setShowLinkContext(false);
        }
      }
      setInputVal('');
    } catch (err) {
      alert(err.message);
    }
  };

  const handleCancelReply = () => {
    setReplyingTo(null);
  };

  const handleCancelBinding = () => {
    setDraftBinding(null);
    setSelectedColId('');
    setSelectedReqId('');
    setSelectedTab('');
    setSelectedKey('');
  };

  const handleLinkCollectionSelect = (colIdStr) => {
    setSelectedColId(colIdStr);
    setSelectedReqId('');
    setSelectedTab('');
    setSelectedKey('');
    if (!colIdStr) {
      setDraftBinding(null);
    } else {
      setDraftBinding({ collectionId: parseInt(colIdStr), requestId: null, tab: null, key: null });
    }
  };

  const handleLinkRequestSelect = (reqIdStr) => {
    setSelectedReqId(reqIdStr);
    setSelectedTab('');
    setSelectedKey('');
    if (!reqIdStr) {
      setDraftBinding({ collectionId: parseInt(selectedColId), requestId: null, tab: null, key: null });
    } else {
      setDraftBinding({ collectionId: parseInt(selectedColId), requestId: parseInt(reqIdStr), tab: null, key: null });
    }
  };

  const handleLinkTabSelect = (tabVal) => {
    setSelectedTab(tabVal);
    setSelectedKey('');
    if (!tabVal) {
      setDraftBinding(prev => ({ ...prev, tab: null, key: null }));
    } else {
      setDraftBinding(prev => ({ ...prev, tab: tabVal, key: null }));
    }
  };

  const handleLinkKeySelect = (keyVal) => {
    setSelectedKey(keyVal);
    setDraftBinding(prev => ({ ...prev, key: keyVal || null }));
  };

  const getRequestOptions = () => {
    if (!selectedColId) return [];
    const col = collections.find(c => c.id === parseInt(selectedColId));
    return col ? (col.requests || []) : [];
  };

  const getSelectedRequestKeys = () => {
    if (!selectedReqId) return [];
    const req = requests.find(r => r.id === parseInt(selectedReqId));
    if (!req) return [];
    if (selectedTab === 'params') {
      return (req.params || []).map(p => p.key).filter(Boolean);
    }
    if (selectedTab === 'headers') {
      return (req.headers || []).map(h => h.key).filter(Boolean);
    }
    return [];
  };

  const getDraftBindingLabel = () => {
    if (!draftBinding) return '';
    if (draftBinding.collectionId && !draftBinding.requestId) {
      const col = collections.find(c => c.id === draftBinding.collectionId);
      return col ? col.name : 'Unknown Collection';
    }
    const colName = getRequestCollectionName(draftBinding.requestId);
    const req = requests.find(r => r.id === draftBinding.requestId);
    const reqName = req ? req.name : 'Unknown Request';
    let label = colName ? `${colName} > ${reqName}` : reqName;
    if (draftBinding.tab) {
      const tabNames = { params: 'Params', headers: 'Headers', body: 'Body', auth: 'Auth' };
      label += ` > ${tabNames[draftBinding.tab] || draftBinding.tab}`;
      if (draftBinding.key) {
        label += ` > ${draftBinding.key}`;
      }
    }
    return label;
  };

  const filteredComments = getFilteredComments();

  return (
    <div className="workspace-chat">
      <div className="chat-header">
        <div className="chat-header-title">
          <FaCommentAlt />
          <span>Workspace Chat</span>
        </div>
        <button className="chat-close-btn" onClick={() => setIsChatOpen(false)} title="Close Chat">
          <FaTimes />
        </button>
      </div>

      <div className="chat-filters">
        <button
          className={`chat-filter-btn ${filterType === 'all' ? 'active' : ''}`}
          onClick={() => { setFilterType('all'); setElementFilter(null); }}
        >
          All
        </button>
        {activeRequestId && (
          <button
            className={`chat-filter-btn ${filterType === 'request' ? 'active' : ''}`}
            onClick={() => { setFilterType('request'); setElementFilter(null); }}
          >
            Current Request
          </button>
        )}
        {filterType === 'element' && elementFilter && (
          <button className="chat-filter-btn active element">
            Element Filter
          </button>
        )}
      </div>

      {filterType === 'element' && elementFilter && (
        <div className="element-filter-banner">
          <span>Filtered to element context</span>
          <button
            className="clear-banner-btn"
            onClick={() => { setFilterType('all'); setElementFilter(null); }}
          >
            Clear
          </button>
        </div>
      )}

      <div className="chat-feed" ref={feedRef}>
        {loading && <div className="chat-status">Loading comments...</div>}
        {error && <div className="chat-status error">Error: {error}</div>}
        {!loading && filteredComments.length === 0 && (
          <div className="chat-empty">No comments found.</div>
        )}
        {!loading && filteredComments.map(c => (
          <div key={c.id} className="comment-thread">
            <CommentNode
              comment={c}
              collectionName={getRequestCollectionName(c.request_id)}
              currentUserId={currentUserId}
              workspaceRole={workspaceRole}
              onReplyClick={(parent) => setReplyingTo(parent)}
              onEdit={handleEditComment}
              onDelete={handleDeleteComment}
              onBadgeClick={onBadgeNavigate}
            />
            {c.replies && c.replies.map(r => (
              <CommentNode
                key={r.id}
                comment={r}
                isReply
                currentUserId={currentUserId}
                workspaceRole={workspaceRole}
                onEdit={handleEditComment}
                onDelete={handleDeleteComment}
              />
            ))}
          </div>
        ))}
      </div>

      <form className="chat-input-area" onSubmit={handlePost}>
        {replyingTo && (
          <div className="input-indicator">
            <span>Replying to <strong>{replyingTo.username}</strong></span>
            <button type="button" onClick={handleCancelReply} className="indicator-cancel">
              <FaTimes />
            </button>
          </div>
        )}

        {!replyingTo && draftBinding && !showLinkContext && (
          <div className="input-indicator binding">
            <span>Binding context: <strong>{getDraftBindingLabel()}</strong></span>
            <button type="button" onClick={handleCancelBinding} className="indicator-cancel">
              <FaTimes />
            </button>
          </div>
        )}

        {!replyingTo && (
          <div className="link-context-container">
            <button
              type="button"
              className="link-context-toggle"
              onClick={() => setShowLinkContext(o => !o)}
            >
              {showLinkContext ? 'Hide Context Binder' : 'Link Request Context...'}
            </button>

            {showLinkContext && (
              <div className="link-context-selectors">
                <select
                  value={selectedColId}
                  onChange={e => handleLinkCollectionSelect(e.target.value)}
                  className="link-select"
                >
                  <option value="">-- Select Collection --</option>
                  {collections.map(c => (
                    <option key={c.id} value={c.id}>{c.name}</option>
                  ))}
                </select>

                {selectedColId && (
                  <select
                    value={selectedReqId}
                    onChange={e => handleLinkRequestSelect(e.target.value)}
                    className="link-select"
                  >
                    <option value="">-- Select Request (Optional) --</option>
                    {getRequestOptions().map(r => (
                      <option key={r.id} value={r.id}>{r.name}</option>
                    ))}
                  </select>
                )}

                {selectedColId && selectedReqId && (
                  <select
                    value={selectedTab}
                    onChange={e => handleLinkTabSelect(e.target.value)}
                    className="link-select"
                  >
                    <option value="">-- Select Tab (Optional) --</option>
                    <option value="params">Params</option>
                    <option value="headers">Headers</option>
                    <option value="body">Body</option>
                    <option value="auth">Auth</option>
                  </select>
                )}

                {selectedColId && selectedReqId && (selectedTab === 'params' || selectedTab === 'headers') && (
                  <select
                    value={selectedKey}
                    onChange={e => handleLinkKeySelect(e.target.value)}
                    className="link-select"
                  >
                    <option value="">-- Select Key (Optional) --</option>
                    {getSelectedRequestKeys().map(k => (
                      <option key={k} value={k}>{k}</option>
                    ))}
                  </select>
                )}

                {draftBinding && (
                  <div className="link-context-preview">
                    <span>📌 {getDraftBindingLabel()}</span>
                    <button type="button" onClick={handleCancelBinding} className="indicator-cancel" title="Clear binding">
                      <FaTimes />
                    </button>
                  </div>
                )}
              </div>
            )}
          </div>
        )}

        <div className="input-row">
          <textarea
            className="chat-textarea"
            placeholder={replyingTo ? "Write a reply..." : "Write a comment..."}
            value={inputVal}
            onChange={e => setInputVal(e.target.value)}
            spellCheck={false}
          />
          <button type="submit" className="chat-send-btn" disabled={!inputVal.trim()} title="Send">
            <FaPaperPlane />
          </button>
        </div>
      </form>
    </div>
  );
}
