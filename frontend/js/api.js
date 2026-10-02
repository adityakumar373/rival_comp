/**
 * API Client for the AI Competitor Intelligence backend.
 * All methods are async and return parsed JSON.
 */

const BASE = '';

async function _request(method, path, { body, params } = {}) {
  let url = `${BASE}${path}`;

  if (params) {
    const qs = new URLSearchParams();
    for (const [k, v] of Object.entries(params)) {
      if (v !== undefined && v !== null && v !== '') {
        qs.append(k, String(v));
      }
    }
    const qsStr = qs.toString();
    if (qsStr) url += `?${qsStr}`;
  }

  const opts = { method, headers: {} };

  if (body) {
    opts.headers['Content-Type'] = 'application/json';
    opts.body = JSON.stringify(body);
  }

  const res = await fetch(url, opts);

  if (!res.ok) {
    let detail = `HTTP ${res.status}`;
    try {
      const err = await res.json();
      detail = err.detail || JSON.stringify(err);
    } catch { /* ignore parse error */ }
    throw new Error(detail);
  }

  return res.json();
}

const API = {
  competitors: {
    create: (data) => _request('POST', '/competitor/', { body: data }),
    list: ({ includeInactive, skip, limit } = {}) =>
      _request('GET', '/competitor/', {
        params: { include_inactive: includeInactive, skip, limit },
      }),
    get: (id) => _request('GET', `/competitor/${id}`),
    update: (id, data) => _request('PUT', `/competitor/${id}`, { body: data }),
    delete: (id) => _request('DELETE', `/competitor/${id}`),
  },

  sources: {
    create: (data) =>
      _request('POST', '/sources/', {
        body: {
          competitor_id: data.competitorId || data.competitor_id,
          source_type: data.sourceType || data.source_type,
          url: data.url,
          scrape_frequency: data.scrapeFrequency || data.scrape_frequency || 1440,
        },
      }),
    list: ({ competitorId, includeInactive, skip, limit } = {}) =>
      _request('GET', '/sources/', {
        params: {
          competitor_id: competitorId,
          include_inactive: includeInactive,
          skip,
          limit,
        },
      }),
    get: (id) => _request('GET', `/sources/${id}`),
    update: (id, data) => _request('PUT', `/sources/${id}`, { body: data }),
    delete: (id) => _request('DELETE', `/sources/${id}`),
  },

  scraper: {
    scrapeSource: (sourceId) => _request('POST', `/scraper/source/${sourceId}`),
    scrapeAll: (competitorId) => _request('POST', `/scraper/competitor/${competitorId}/scrape-all`),
    due: () => _request('GET', '/scraper/due'),
    schedulerStatus: () => _request('GET', '/scraper/scheduler/status'),
    triggerScheduler: () => _request('POST', '/scraper/scheduler/trigger'),
  },

  changes: {
    listForSource: (sourceId, { skip, limit } = {}) =>
      _request('GET', `/changes/source/${sourceId}`, { params: { skip, limit } }),
    get: (changeId) => _request('GET', `/changes/${changeId}`),
  },

  insights: {
    listAll: ({ category, minImpact, skip, limit } = {}) =>
      _request('GET', '/insights/', { params: { category, min_impact: minImpact, skip, limit } }),
    listForCompetitor: (competitorId, { skip, limit } = {}) =>
      _request('GET', `/insights/competitor/${competitorId}`, { params: { skip, limit } }),
    get: (insightId) => _request('GET', `/insights/${insightId}`),
  },

  alerts: {
    listAll: ({ unsentOnly, minImpact, skip, limit } = {}) =>
      _request('GET', '/alerts/', {
        params: { unsent_only: unsentOnly, min_impact: minImpact, skip, limit },
      }),
    listForCompetitor: (competitorId, { unsentOnly, skip, limit } = {}) =>
      _request('GET', `/alerts/competitor/${competitorId}`, {
        params: { unsent_only: unsentOnly, skip, limit },
      }),
    markSent: (alertId) => _request('POST', `/alerts/${alertId}/mark-sent`),
  },

  dashboard: {
    overview: () => _request('GET', '/dashboard/competitors'),
    competitorDetail: (competitorId) =>
      _request('GET', `/dashboard/competitor/${competitorId}`),
    analytics: () => _request('GET', '/dashboard/analytics'),
  },

  discovery: {
    autocomplete: (q) => _request('GET', '/discovery/autocomplete', { params: { q } }),
    search: (query) => _request('POST', '/discovery/search', { body: { query } }),
    batchAdd: (payload) => _request('POST', '/discovery/batch-add', { body: payload }),
  },
};

export default API;
