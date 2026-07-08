const { TextEncoder, TextDecoder } = require('util');
global.TextEncoder = TextEncoder;
global.TextDecoder = TextDecoder;

require('@testing-library/jest-dom');

const React = require('react');
const { render, screen } = require('@testing-library/react');
const WorkspaceChat = require('./WorkspaceChat').default;

describe('WorkspaceChat Component Smoke Test', () => {
  const mockCommentsState = {
    comments: [
      {
        id: 1,
        workspace_id: 1,
        user_id: 1,
        username: 'alice',
        content: 'This is a test comment',
        parent_id: null,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
        replies: []
      }
    ],
    loading: false,
    error: null,
    isChatOpen: true,
    filterType: 'all',
    elementFilter: null,
    draftBinding: null,
    setFilterType: jest.fn(),
    setElementFilter: jest.fn(),
    setDraftBinding: jest.fn(),
    setIsChatOpen: jest.fn(),
    handleAddComment: jest.fn(),
    handleEditComment: jest.fn(),
    handleDeleteComment: jest.fn()
  };

  it('renders chat header and comments list when open', () => {
    render(
      <WorkspaceChat
        workspaceId={1}
        currentUserId={1}
        workspaceRole="owner"
        collections={[]}
        commentsState={mockCommentsState}
      />
    );

    expect(screen.getByText('Workspace Chat')).toBeInTheDocument();
    expect(screen.getByText('This is a test comment')).toBeInTheDocument();
    expect(screen.getByText('alice')).toBeInTheDocument();
  });
});
