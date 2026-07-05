const BASE_URL = 'http://localhost:5000';

export async function authFetch(endpoint, options = {}) {
  const { skipGlobal403 = false, ...fetchOptions } = options;
  const token = sessionStorage.getItem('token');
  const headers = {
    ...fetchOptions.headers,
  };

  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const response = await fetch(`${BASE_URL}${endpoint}`, {
    ...fetchOptions,
    headers,
  });

  if (response.status === 403 && !skipGlobal403) {
    window.dispatchEvent(new CustomEvent('show-unauthorized-alert', {
      detail: { message: "Action forbidden: You do not have permission to perform this action." }
    }));
  }

  return response;
}

export default BASE_URL;
