import axios from 'axios';

const API_BASE = 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_BASE,
  timeout: 120000,
});

const cache = new Map();

const cachedGet = async (url) => {
  if (cache.has(url)) return cache.get(url);
  const { data } = await api.get(url);
  cache.set(url, data);
  return data;
};

// ── Upload ────────────────────────────────────────────────────
export const uploadDataset = async (file) => {
  const formData = new FormData();
  formData.append('file', file);
  const { data } = await api.post('/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return data;
};

// ── Dataset ───────────────────────────────────────────────────
export const getDatasets = async () => cachedGet('/datasets');
export const getDatasetInfo = async (id) => cachedGet(`/dataset/${id}`);
export const getPreview = async (id, head = 50) => cachedGet(`/dataset/${id}/preview?head=${head}`);
export const deleteDataset = async (id) => {
  const { data } = await api.delete(`/dataset/${id}`);
  cache.clear();
  return data;
};

// ── Profile ───────────────────────────────────────────────────
export const getProfile = async (id) => cachedGet(`/dataset/${id}/profile`);

// ── Quality ───────────────────────────────────────────────────
export const getQuality = async (id) => cachedGet(`/dataset/${id}/quality`);

// ── Cleaning ──────────────────────────────────────────────────
export const cleanDataset = async (id, options) => {
  const { data } = await api.post(`/dataset/${id}/clean`, options);
  cache.clear();
  return data;
};
export const resetDataset = async (id) => {
  const { data } = await api.post(`/dataset/${id}/reset`);
  cache.clear();
  return data;
};

// ── Statistics ────────────────────────────────────────────────
export const getStatistics = async (id) => cachedGet(`/dataset/${id}/statistics`);

// ── Distributions ─────────────────────────────────────────────
export const getDistributions = async (id, column = null) => {
  const url = column ? `/dataset/${id}/distributions?column=${column}` : `/dataset/${id}/distributions`;
  return cachedGet(url);
};

// ── Correlations ──────────────────────────────────────────────
export const getCorrelations = async (id, method = 'pearson') =>
  cachedGet(`/dataset/${id}/correlations?method=${method}`);

// ── Outliers ──────────────────────────────────────────────────
export const getOutliers = async (id, method = 'iqr') =>
  cachedGet(`/dataset/${id}/outliers?method=${method}`);

// ── Categorical ───────────────────────────────────────────────
export const getCategorical = async (id) => cachedGet(`/dataset/${id}/categorical`);

// ── Time Series ───────────────────────────────────────────────
export const getTimeSeries = async (id, dateCol, valueCol, frequency = 'monthly') => {
  let url = `/dataset/${id}/timeseries?frequency=${frequency}`;
  if (dateCol) url += `&date_column=${dateCol}`;
  if (valueCol) url += `&value_column=${valueCol}`;
  return cachedGet(url);
};

// ── Hypothesis Testing ───────────────────────────────────────
export const runHypothesisTest = async (id, request) =>
  (await api.post(`/dataset/${id}/hypothesis`, request)).data;

// ── Machine Learning ──────────────────────────────────────────
export const getMLTargets = async (id) => cachedGet(`/dataset/${id}/ml/targets`);
export const runRegression = async (id, request) => (await api.post(`/dataset/${id}/ml/regression`, request)).data;
export const runClassification = async (id, request) => (await api.post(`/dataset/${id}/ml/classification`, request)).data;
export const runClustering = async (id, request) => (await api.post(`/dataset/${id}/ml/clustering`, request)).data;

// ── Insights ──────────────────────────────────────────────────
export const getInsights = async (id) => cachedGet(`/dataset/${id}/insights`);

// ── Query ─────────────────────────────────────────────────────
export const queryDataset = async (id, question) =>
  (await api.post(`/dataset/${id}/query`, { question })).data;

// ── Charts ────────────────────────────────────────────────────
export const getAutoCharts = async (id) => cachedGet(`/dataset/${id}/charts`);

// ── Exports ───────────────────────────────────────────────────
export const exportCSV = (id) => `${API_BASE}/dataset/${id}/export/csv`;
export const exportJSON = (id) => `${API_BASE}/dataset/${id}/export/json`;
export const exportExcel = (id) => `${API_BASE}/dataset/${id}/export/excel`;

// ── Health ────────────────────────────────────────────────────
export const healthCheck = async () => (await axios.get('http://127.0.0.1:8000/health')).data;

export default api;
