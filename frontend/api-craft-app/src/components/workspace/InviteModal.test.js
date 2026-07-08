const { TextEncoder, TextDecoder } = require('util');
global.TextEncoder = TextEncoder;
global.TextDecoder = TextDecoder;

require('@testing-library/jest-dom');

const React = require('react');
const { render, screen, fireEvent, waitFor } = require('@testing-library/react');
const InviteModal = require('./InviteModal').default;
const { inviteUserToWorkspace } = require('../../services/invitationService');

// Mock service
jest.mock('../../services/invitationService', () => ({
  inviteUserToWorkspace: jest.fn(),
}));

describe('InviteModal Component Smoke Test', () => {
  const mockWorkspace = { id: 1, name: 'Default Workspace' };
  const mockOnClose = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders correctly with initial elements', () => {
    render(<InviteModal workspace={mockWorkspace} onClose={mockOnClose} />);

    expect(screen.getByText('Invite members')).toBeInTheDocument();
    expect(screen.getByText('Default Workspace')).toBeInTheDocument();
    expect(screen.getByPlaceholderText('Enter username')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Send Invitation' })).toBeInTheDocument();
  });

  it('calls onClose when Cancel button is clicked', () => {
    render(<InviteModal workspace={mockWorkspace} onClose={mockOnClose} />);

    const cancelBtn = screen.getByRole('button', { name: 'Cancel' });
    fireEvent.click(cancelBtn);

    expect(mockOnClose).toHaveBeenCalledTimes(1);
  });

  it('submits successfully and shows success feedback', async () => {
    inviteUserToWorkspace.mockResolvedValue({ message: 'Invitation sent successfully' });

    render(<InviteModal workspace={mockWorkspace} onClose={mockOnClose} />);

    const input = screen.getByPlaceholderText('Enter username');
    fireEvent.change(input, { target: { value: 'inviteduser' } });

    const submitBtn = screen.getByRole('button', { name: 'Send Invitation' });
    fireEvent.click(submitBtn);

    expect(inviteUserToWorkspace).toHaveBeenCalledWith(1, 'inviteduser', 'editor');

    await waitFor(() => {
      expect(screen.getByText('Successfully invited inviteduser as editor!')).toBeInTheDocument();
      expect(input.value).toBe('');
    });
  });

  it('shows error feedback on failure', async () => {
    inviteUserToWorkspace.mockRejectedValue(new Error('User not found'));

    render(<InviteModal workspace={mockWorkspace} onClose={mockOnClose} />);

    const input = screen.getByPlaceholderText('Enter username');
    fireEvent.change(input, { target: { value: 'nonexistent' } });

    const submitBtn = screen.getByRole('button', { name: 'Send Invitation' });
    fireEvent.click(submitBtn);

    await waitFor(() => {
      expect(screen.getByText('User not found')).toBeInTheDocument();
    });
  });
});
