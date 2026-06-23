const { TextEncoder, TextDecoder } = require('util');
global.TextEncoder = TextEncoder;
global.TextDecoder = TextDecoder;

require('@testing-library/jest-dom');

const React = require('react');
const { render, screen } = require('@testing-library/react');
const { MemoryRouter, Routes, Route } = require('react-router-dom');
const MainPage = require('./MainPage').default;
const { useAuth } = require('../../contexts/AuthContext');
const { getWorkspaces, getWorkspaceById } = require('../../services/workspaceService');
const { getCollections } = require('../../services/collectionService');

// Mock contexts
jest.mock('../../contexts/AuthContext', () => ({
  useAuth: jest.fn(),
}));

// Mock services
jest.mock('../../services/workspaceService', () => ({
  getWorkspaces: jest.fn(),
  getWorkspaceById: jest.fn(),
}));

jest.mock('../../services/collectionService', () => ({
  getCollections: jest.fn(),
}));

describe('MainPage Smoke Test', () => {
  beforeEach(() => {
    useAuth.mockReturnValue({
      user: { userId: 1, username: 'testuser', email: 'test@example.com' },
    });
    getWorkspaces.mockResolvedValue([]);
    getWorkspaceById.mockResolvedValue({ id: 1, name: 'Default Workspace', is_default: true });
    getCollections.mockResolvedValue([]);
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  it('renders without crashing when authenticated', async () => {
    const { container } = render(
      <MemoryRouter initialEntries={['/workspace/1']}>
        <Routes>
          <Route path="/workspace/:workspaceId" element={<MainPage />} />
        </Routes>
      </MemoryRouter>
    );

    // Wait for mock data to resolve and render, wrapping state changes in act() implicitly
    const workspaceTitle = await screen.findByText('Default Workspace');
    expect(workspaceTitle).toBeInTheDocument();

    const workspaceElement = container.querySelector('.workspace');
    expect(workspaceElement).toBeInTheDocument();
  });
});
