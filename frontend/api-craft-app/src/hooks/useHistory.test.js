const { TextEncoder, TextDecoder } = require('util');
global.TextEncoder = TextEncoder;
global.TextDecoder = TextDecoder;

const React = require('react');
const { renderHook, act } = require('@testing-library/react');
const useHistory = require('./useHistory').default;
const { getHistory, createHistoryItem } = require('../services/historyService');

// Mock historyService API calls
jest.mock('../services/historyService', () => ({
  getHistory: jest.fn(),
  createHistoryItem: jest.fn(),
}));

describe('useHistory Hook', () => {
  const mockHistoryData = [
    { id: 1, method: 'GET', url: 'http://example.com/1', created_at: new Date().toISOString() }
  ];

  beforeEach(() => {
    getHistory.mockResolvedValue(mockHistoryData);
    createHistoryItem.mockResolvedValue({
      id: 2,
      method: 'POST',
      url: 'http://example.com/2',
      created_at: new Date().toISOString()
    });
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  it('should fetch and load history on mount for active workspace', async () => {
    let result;
    await act(async () => {
      const rendered = renderHook(() => useHistory(1));
      result = rendered.result;
    });

    expect(getHistory).toHaveBeenCalledWith(1);
    expect(result.current.history).toEqual(mockHistoryData);
  });

  it('should append a new history item when addHistoryItem is called', async () => {
    let result;
    await act(async () => {
      const rendered = renderHook(() => useHistory(1));
      result = rendered.result;
    });

    await act(async () => {
      await result.current.addHistoryItem({ method: 'POST', url: 'http://example.com/2' });
    });

    expect(createHistoryItem).toHaveBeenCalledWith(1, { method: 'POST', url: 'http://example.com/2' });
    expect(result.current.history.length).toBe(2);
    expect(result.current.history[0].id).toBe(2);
  });
});
