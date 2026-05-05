import React from 'react';

const DOCS = {
  GET: (
    <>
      <p>
        This is a GET request and it is used to &ldquo;get&rdquo; data from an endpoint.
        There is no request body for a GET request, but you can use query parameters to
        help specify the resource you want data on (e.g., in this request, we have id=1).
      </p>
      <p>
        A successful GET response will have a 200 OK status, and should include some
        kind of response body - for example, HTML web content or JSON data.
      </p>
    </>
  ),
  POST: (
    <>
      <p>
        This is a POST request, submitting data to an API via the request body. This
        request submits JSON data, and the data is reflected in the response.
      </p>
      <p>
        A successful POST request typically returns a <code>200 OK</code> or{' '}
        <code>201 Created</code> response code.
      </p>
    </>
  ),
};

export default function DocsTab({ method = 'GET' }) {
  return (
    <div className="docs-content">
      {DOCS[method] ?? <p>No documentation available for {method} requests.</p>}
    </div>
  );
}
