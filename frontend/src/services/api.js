// API Client Service connecting React Frontend to FastAPI Backend

const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL || '').replace(/\/+$/, '');

if (import.meta.env.PROD) {
  if (!API_BASE_URL) {
    throw new Error('VITE_API_BASE_URL must be configured for production builds.');
  }

  const backendUrl = new URL(API_BASE_URL);
  if (backendUrl.protocol !== 'https:' || ['localhost', '127.0.0.1'].includes(backendUrl.hostname)) {
    throw new Error('VITE_API_BASE_URL must use the deployed HTTPS backend origin.');
  }
}

const apiUrl = (path) => `${API_BASE_URL}${path}`;

export async function fetchHealth() {
  const res = await fetch(apiUrl('/api/health'));
  if (!res.ok) throw new Error('Health check failed');
  return await res.json();
}

export async function sendQuery(queryPayload) {
  const res = await fetch(apiUrl('/api/v1/assistant/query'), {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(queryPayload)
  });
  if (!res.ok) throw new Error('Failed to process assistant query');
  return await res.json();
}

export async function assessFormulation(formulationPayload) {
  const res = await fetch(apiUrl('/api/v1/formulation/assess'), {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(formulationPayload)
  });
  if (!res.ok) throw new Error('Failed to assess formulation');
  return await res.json();
}

export async function assessFullFormulation(fullPayload) {
  const res = await fetch(apiUrl('/api/v1/intelligence/assess-formulation'), {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(fullPayload)
  });
  if (!res.ok) throw new Error('Failed to assess full formulation intelligence');
  return await res.json();
}

export async function fetchSources() {
  const res = await fetch(apiUrl('/api/v1/sources'));
  if (!res.ok) throw new Error('Failed to fetch source registry');
  return await res.json();
}

export async function fetchSourceSections(documentId) {
  const res = await fetch(apiUrl(`/api/v1/sources/${documentId}/sections`));
  if (!res.ok) throw new Error('Failed to fetch document sections');
  return await res.json();
}

export async function fetchDemoQueries() {
  const res = await fetch(apiUrl('/api/v1/demo/cached-queries'));
  if (!res.ok) throw new Error('Failed to fetch demo queries');
  return await res.json();
}

export async function createHumanReviewCase(casePayload) {
  const res = await fetch(apiUrl('/api/v1/cases/create'), {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(casePayload)
  });
  if (!res.ok) throw new Error('Failed to create human review case');
  return await res.json();
}

export async function fetchHumanReviewCases() {
  const res = await fetch(apiUrl('/api/v1/cases'));
  if (!res.ok) throw new Error('Failed to fetch human review cases');
  return await res.json();
}

export async function fetchKnowledgeGraph(formulationPayload) {
  const res = await fetch(apiUrl('/api/v1/knowledge-graph'), {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(formulationPayload)
  });
  if (!res.ok) throw new Error('Failed to fetch knowledge graph');
  return await res.json();
}

export async function fetchPaidConnectors() {
  const res = await fetch(apiUrl('/api/v1/connectors'));
  if (!res.ok) throw new Error('Failed to fetch paid connectors');
  return await res.json();
}

export async function runBenchmarkEvaluation() {
  const res = await fetch(apiUrl('/api/v1/evaluation/run-benchmark'), {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' }
  });
  if (!res.ok) throw new Error('Failed to run 50-query benchmark evaluation');
  return await res.json();
}
