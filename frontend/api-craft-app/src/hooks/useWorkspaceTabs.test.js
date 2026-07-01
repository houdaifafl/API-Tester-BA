const { TextEncoder, TextDecoder } = require('util');
global.TextEncoder = TextEncoder;
global.TextDecoder = TextDecoder;

const React = require('react');
const { renderHook, act } = require('@testing-library/react');
const useWorkspaceTabs = require('./useWorkspaceTabs').default;

describe('useWorkspaceTabs Hook', () => {
  it('should initialize with overview tab', () => {
    const { result } = renderHook(() => useWorkspaceTabs(1));
    expect(result.current.openTabs.length).toBe(1);
    expect(result.current.openTabs[0].type).toBe('overview');
    expect(result.current.activeTabId).toBe('overview');
  });

  it('should open a history item, create a tab, and populate response metadata', () => {
    const { result } = renderHook(() => useWorkspaceTabs(1));
    
    const mockHistoryItem = {
      id: 99,
      method: 'GET',
      url: 'http://example.com/api',
      params: [{ key: 'x', value: 'y' }],
      headers: [],
      body: null,
      auth: null,
      status: 200,
      response_time: 42.5,
      data: { success: true }
    };

    act(() => {
      result.current.handleHistoryOpen(mockHistoryItem);
    });

    // Verify open tabs
    expect(result.current.openTabs.length).toBe(2);
    expect(result.current.openTabs[1].id).toBe('hist-99');
    expect(result.current.openTabs[1].type).toBe('history');
    expect(result.current.activeTabId).toBe('hist-99');

    // Verify saved response state is restored
    const tabState = result.current.requestStates.current['hist-99'];
    expect(tabState).toBeDefined();
    expect(tabState.url).toBe('http://example.com/api');
    expect(tabState.params).toEqual([{ key: 'x', value: 'y' }]);
    expect(tabState.response).toEqual({
      status: 200,
      response_time: 42.5,
      data: { success: true }
    });
  });
});
