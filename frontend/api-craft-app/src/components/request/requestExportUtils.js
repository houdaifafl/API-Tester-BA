const safeBtoa = (str) => {
  if (typeof window !== 'undefined' && typeof window.btoa === 'function') {
    return window.btoa(str);
  }
  return Buffer.from(str).toString('base64');
};

/**
 * Generates a bash-compatible cURL command string based on the request settings.
 */
export function generateCurlCommand({ method, url, params, headers, body, auth }) {
  let fullUrl = (url || '').trim() || 'http://localhost';

  // Format query parameters
  const queryParts = [];
  if (params && Array.isArray(params)) {
    params.forEach(p => {
      if (p.key && p.key.trim()) {
        queryParts.push(`${encodeURIComponent(p.key.trim())}=${encodeURIComponent(p.value || '')}`);
      }
    });
  }

  if (queryParts.length > 0) {
    const queryString = queryParts.join('&');
    fullUrl += (fullUrl.includes('?') ? '&' : '?') + queryString;
  }

  const curlParts = ['curl'];

  // Method flag
  if (method) {
    curlParts.push(`-X ${method.toUpperCase()}`);
  }

  // URL argument
  curlParts.push(`"${fullUrl}"`);

  // Headers (including Auth headers if applicable)
  const headerMap = {};
  if (headers && Array.isArray(headers)) {
    headers.forEach(h => {
      if (h.key && h.key.trim()) {
        headerMap[h.key.trim()] = h.value || '';
      }
    });
  }

  // Inject Authorization headers from auth tab if present
  if (auth?.type === 'bearer' && auth.token) {
    headerMap['Authorization'] = `Bearer ${auth.token}`;
  } else if (auth?.type === 'basic') {
    const creds = safeBtoa(`${auth.username || ''}:${auth.password || ''}`);
    headerMap['Authorization'] = `Basic ${creds}`;
  }

  // Format headers to curl -H flags
  Object.entries(headerMap).forEach(([key, val]) => {
    curlParts.push(`-H "${key}: ${val}"`);
  });

  // Body handling
  if (body && body.bodyType !== 'none') {
    if (body.bodyType === 'raw') {
      if (body.rawContent) {
        // If content is JSON, auto-add content type if not already there
        if (body.rawType === 'JSON' && !headerMap['Content-Type']) {
          curlParts.push(`-H "Content-Type: application/json"`);
        } else if (body.rawType === 'Text' && !headerMap['Content-Type']) {
          curlParts.push(`-H "Content-Type: text/plain"`);
        } else if (body.rawType === 'HTML' && !headerMap['Content-Type']) {
          curlParts.push(`-H "Content-Type: text/html"`);
        } else if (body.rawType === 'XML' && !headerMap['Content-Type']) {
          curlParts.push(`-H "Content-Type: application/xml"`);
        }

        // Escape single quotes for shell string
        const escapedContent = body.rawContent.replace(/'/g, "'\\''");
        curlParts.push(`-d '${escapedContent}'`);
      }
    } else if (body.bodyType === 'form-data' && Array.isArray(body.formData)) {
      body.formData.forEach(f => {
        if (f.key && f.key.trim()) {
          const escapedVal = (f.value || '').replace(/'/g, "'\\''");
          curlParts.push(`-F '${f.key.trim()}=${escapedVal}'`);
        }
      });
    } else if (body.bodyType === 'x-www-form-urlencoded' && Array.isArray(body.urlEncoded)) {
      body.urlEncoded.forEach(u => {
        if (u.key && u.key.trim()) {
          const escapedVal = (u.value || '').replace(/'/g, "'\\''");
          curlParts.push(`--data-urlencode '${u.key.trim()}=${escapedVal}'`);
        }
      });
    }
  }

  return curlParts.join(' \\\n  ');
}

/**
 * Triggers a client-side download of the request settings as a JSON file.
 */
export function exportRequestAsJson({ name, method, url, params, headers, body, auth }) {
  const data = {
    name: name || 'Exported Request',
    method: method || 'GET',
    url: url || '',
    params: params || null,
    headers: headers || null,
    body: body || null,
    auth: auth || null,
  };

  const jsonString = `data:text/json;charset=utf-8,${encodeURIComponent(
    JSON.stringify(data, null, 2)
  )}`;

  const downloadAnchor = document.createElement('a');
  downloadAnchor.setAttribute('href', jsonString);
  const safeName = (name || 'request').toLowerCase().replace(/[^a-z0-9]+/g, '-');
  downloadAnchor.setAttribute('download', `${safeName}.json`);
  document.body.appendChild(downloadAnchor);
  downloadAnchor.click();
  downloadAnchor.remove();
}
