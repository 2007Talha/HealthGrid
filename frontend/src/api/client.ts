const RAW_BASE = import.meta.env.VITE_API_BASE_URL || import.meta.env.VITE_API_URL || '';
const API_BASE_URL = RAW_BASE ? RAW_BASE.replace(/\/$/, '') : ['/api', 'v1'].join('/');

export class ApiError extends Error {
  constructor(public status: number, message: string, public data?: any) {
    super(message);
    this.name = 'ApiError';
  }
}

export async function fetchJson<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const url = `${API_BASE_URL}${endpoint.startsWith('/') ? endpoint : `/${endpoint}`}`;
  
  const headers = new Headers(options.headers || {});
  if (!headers.has('Content-Type') && !(options.body instanceof FormData)) {
    headers.set('Content-Type', 'application/json');
  }

  // Attach session authorization headers if available
  try {
    const savedRole = localStorage.getItem('swasthya_user_role') || 'ADMIN';
    const savedToken = localStorage.getItem('swasthya_auth_token') || `swasthya-${savedRole.toLowerCase()}-token`;
    const savedRegion = localStorage.getItem('swasthya_user_region') || '';
    const savedUserId = localStorage.getItem('swasthya_user_id') || `usr-${savedRole.toLowerCase()}`;

    if (!headers.has('Authorization')) {
      headers.set('Authorization', `Bearer ${savedToken}`);
    }
    if (!headers.has('X-User-Role')) {
      headers.set('X-User-Role', savedRole);
    }
    if (savedRegion && !headers.has('X-User-Region')) {
      headers.set('X-User-Region', savedRegion);
    }
    if (savedUserId && !headers.has('X-User-Id')) {
      headers.set('X-User-Id', savedUserId);
    }
  } catch {
    // localStorage not accessible in non-browser context
  }

  const response = await fetch(url, {
    ...options,
    headers,
  });

  if (!response.ok) {
    let errorMessage = `API Request failed with status ${response.status}`;
    let errorData = null;
    try {
      errorData = await response.json();
      if (errorData?.detail) {
        errorMessage = typeof errorData.detail === 'string' ? errorData.detail : JSON.stringify(errorData.detail);
      } else if (errorData?.message) {
        errorMessage = errorData.message;
      }
    } catch {
      // Ignored if not JSON
    }
    throw new ApiError(response.status, errorMessage, errorData);
  }

  return response.json() as Promise<T>;
}
