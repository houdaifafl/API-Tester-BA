const { TextEncoder, TextDecoder } = require('util');
global.TextEncoder = TextEncoder;
global.TextDecoder = TextDecoder;

require('@testing-library/jest-dom');

const React = require('react');
const { render, screen, fireEvent } = require('@testing-library/react');
const Sidebar = require('./Sidebar').default;

describe('Sidebar Component Smoke Test', () => {
  const mockProps = {
    sidebarWidth: 200,
    onResizeStart: jest.fn(),
    activeRequestId: null,
    onRequestOpen: jest.fn(),
    collections: [
      {
        id: 1,
        name: 'Test Collection',
        is_default: true,
        requests: [
          {
            id: 1,
            name: 'Get Users',
            method: 'GET',
            url: '/api/users',
            collectionName: 'Test Collection'
          }
        ]
      }
    ],
    onRequestAdd: jest.fn(),
    onRequestRename: jest.fn(),
    onRequestDelete: jest.fn(),
    onCollectionAdd: jest.fn(),
    onCollectionRename: jest.fn(),
    onCollectionDelete: jest.fn(),
    history: [
      {
        id: 101,
        method: 'POST',
        url: '/api/login',
        params: { debug: 'true' },
        created_at: new Date().toISOString()
      }
    ],
    onHistoryOpen: jest.fn(),
    activeHistoryId: null
  };

  it('renders collections list by default', () => {
    render(<Sidebar {...mockProps} />);
    
    // Assert collections tab/button is present
    const collectionsBtn = screen.getByTitle('Collections');
    expect(collectionsBtn).toBeInTheDocument();
    
    // Assert collection name is rendered
    expect(screen.getByText('Test Collection')).toBeInTheDocument();
    // Assert request name is rendered
    expect(screen.getByText('Get Users')).toBeInTheDocument();
  });

  it('toggles to history mode and renders history entries', () => {
    render(<Sidebar {...mockProps} />);
    
    const historyBtn = screen.getByTitle('History');
    expect(historyBtn).toBeInTheDocument();

    // Click on history tab
    fireEvent.click(historyBtn);

    // Assert that the history item is rendered (URL and params)
    expect(screen.getByText('/api/login')).toBeInTheDocument();
    expect(screen.getByText('debug=true')).toBeInTheDocument();
  });
});
