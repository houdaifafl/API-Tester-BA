import { generateCurlCommand, exportRequestAsJson } from './requestExportUtils';

describe('generateCurlCommand', () => {
  it('generates basic GET curl command', () => {
    const payload = {
      method: 'GET',
      url: 'https://api.example.com/users',
      params: [],
      headers: [],
      body: { bodyType: 'none' },
      auth: { type: 'none' }
    };
    const curl = generateCurlCommand(payload);
    expect(curl).toBe('curl \\\n  -X GET \\\n  "https://api.example.com/users"');
  });

  it('generates GET curl command with query parameters', () => {
    const payload = {
      method: 'GET',
      url: 'https://api.example.com/users',
      params: [
        { key: 'page', value: '2' },
        { key: 'limit', value: '10' }
      ],
      headers: [],
      body: { bodyType: 'none' },
      auth: { type: 'none' }
    };
    const curl = generateCurlCommand(payload);
    expect(curl).toContain('-X GET');
    expect(curl).toContain('"https://api.example.com/users?page=2&limit=10"');
  });

  it('generates POST curl command with custom headers and JSON body', () => {
    const payload = {
      method: 'POST',
      url: 'https://api.example.com/users',
      params: [],
      headers: [
        { key: 'Accept', value: 'application/json' }
      ],
      body: {
        bodyType: 'raw',
        rawType: 'JSON',
        rawContent: '{"name":"Alice"}'
      },
      auth: { type: 'none' }
    };
    const curl = generateCurlCommand(payload);
    expect(curl).toContain('-X POST');
    expect(curl).toContain('-H "Accept: application/json"');
    expect(curl).toContain('-H "Content-Type: application/json"');
    expect(curl).toContain("-d '{\"name\":\"Alice\"}'");
  });

  it('handles bearer authorization headers correctly', () => {
    const payload = {
      method: 'GET',
      url: 'https://api.example.com/me',
      params: [],
      headers: [],
      body: { bodyType: 'none' },
      auth: {
        type: 'bearer',
        token: 'secret-token'
      }
    };
    const curl = generateCurlCommand(payload);
    expect(curl).toContain('-H "Authorization: Bearer secret-token"');
  });

  it('handles basic authorization headers correctly', () => {
    const payload = {
      method: 'GET',
      url: 'https://api.example.com/me',
      params: [],
      headers: [],
      body: { bodyType: 'none' },
      auth: {
        type: 'basic',
        username: 'admin',
        password: 'password123'
      }
    };
    const curl = generateCurlCommand(payload);
    // btoa("admin:password123") is "YWRtaW46cGFzc3dvcmQxMjM="
    expect(curl).toContain('-H "Authorization: Basic YWRtaW46cGFzc3dvcmQxMjM="');
  });

  it('handles escaping single quotes in body', () => {
    const payload = {
      method: 'POST',
      url: 'https://api.example.com/echo',
      params: [],
      headers: [],
      body: {
        bodyType: 'raw',
        rawType: 'Text',
        rawContent: "User's data"
      },
      auth: { type: 'none' }
    };
    const curl = generateCurlCommand(payload);
    expect(curl).toContain("-d 'User'\\''s data'");
  });

  it('handles form-data and x-www-form-urlencoded inputs correctly', () => {
    const payloadForm = {
      method: 'POST',
      url: 'https://api.example.com/form',
      params: [],
      headers: [],
      body: {
        bodyType: 'form-data',
        formData: [{ key: 'name', value: 'Bob' }]
      },
      auth: { type: 'none' }
    };
    const curlForm = generateCurlCommand(payloadForm);
    expect(curlForm).toContain("-F 'name=Bob'");

    const payloadUrlEncoded = {
      method: 'POST',
      url: 'https://api.example.com/url-encoded',
      params: [],
      headers: [],
      body: {
        bodyType: 'x-www-form-urlencoded',
        urlEncoded: [{ key: 'search', value: "cat's" }]
      },
      auth: { type: 'none' }
    };
    const curlUrlEncoded = generateCurlCommand(payloadUrlEncoded);
    expect(curlUrlEncoded).toContain("--data-urlencode 'search=cat'\\''s'");
  });
});

describe('exportRequestAsJson', () => {
  let appendChildMock, removeMock, clickMock, createElementMock;

  beforeEach(() => {
    clickMock = jest.fn();
    removeMock = jest.fn();
    appendChildMock = jest.fn();

    createElementMock = jest.spyOn(document, 'createElement').mockImplementation(() => {
      return {
        setAttribute: jest.fn(),
        click: clickMock,
        remove: removeMock
      };
    });

    jest.spyOn(document.body, 'appendChild').mockImplementation(appendChildMock);
  });

  afterEach(() => {
    createElementMock.mockRestore();
    jest.restoreAllMocks();
  });

  it('creates an anchor, configures the JSON href, and triggers download', () => {
    const payload = {
      name: 'Get Users',
      method: 'GET',
      url: 'https://api.example.com/users',
      params: [],
      headers: [],
      body: { bodyType: 'none' },
      auth: { type: 'none' }
    };

    exportRequestAsJson(payload);

    expect(createElementMock).toHaveBeenCalledWith('a');
    expect(appendChildMock).toHaveBeenCalled();
    expect(clickMock).toHaveBeenCalled();
    expect(removeMock).toHaveBeenCalled();
  });
});
