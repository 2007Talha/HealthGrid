import { describe, it, expect, vi } from 'vitest';
import { fetchJson, ApiError } from '../api/client';

describe('API Client Suite', () => {
  it('handles ApiError correctly on non-200 responses', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue({
      ok: false,
      status: 404,
      json: async () => ({ detail: 'Resource not found' })
    }));

    await expect(fetchJson('/test-endpoint')).rejects.toThrow(ApiError);
  });

  it('parses JSON successfully on 200 response', async () => {
    const mockData = { status: 'SUCCESS', count: 42 };
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue({
      ok: true,
      status: 200,
      json: async () => mockData
    }));

    const result = await fetchJson('/test-success');
    expect(result).toEqual(mockData);
  });
});
