import { useState, useEffect } from 'react';
import { useDataset } from '../context/DatasetContext';
import { getMLTargets, runRegression, runClassification, runClustering, getProfile } from '../services/api';
import Topbar from '../components/layout/Topbar';
import PlotlyChart from '../components/charts/PlotlyChart';
import { Loader2, Brain, Target, Zap, GitBranch } from 'lucide-react';

const TABS = ['Regression', 'Classification', 'Clustering'];

export default function MLPage() {
  const { datasetId } = useDataset();
  const [activeTab, setActiveTab] = useState('Regression');
  const [targets, setTargets] = useState(null);
  const [profile, setProfile] = useState(null);
  const [selectedTarget, setSelectedTarget] = useState('');
  const [model, setModel] = useState('random_forest');
  const [nClusters, setNClusters] = useState(3);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [initLoading, setInitLoading] = useState(true);

  useEffect(() => {
    if (!datasetId) return;
    Promise.all([
      getMLTargets(datasetId),
      getProfile(datasetId),
    ]).then(([t, p]) => {
      setTargets(t);
      setProfile(p);
      if (t?.targets?.length > 0) setSelectedTarget(t.targets[0].column);
      setInitLoading(false);
    }).catch(() => setInitLoading(false));
  }, [datasetId]);

  const handleRun = async () => {
    setLoading(true);
    setResult(null);
    try {
      let res;
      switch (activeTab) {
        case 'Regression':
          res = await runRegression(datasetId, { target_column: selectedTarget, model_name: model });
          break;
        case 'Classification':
          res = await runClassification(datasetId, { target_column: selectedTarget, model_name: model });
          break;
        case 'Clustering':
          res = await runClustering(datasetId, { n_clusters: nClusters });
          break;
      }
      setResult(res);
    } catch (err) {
      setResult({ error: err.response?.data?.detail || 'Model training failed' });
    }
    setLoading(false);
  };

  if (initLoading) {
    return (<><Topbar title="Machine Learning" subtitle="ML" /><div className="loading-overlay"><Loader2 size={32} className="spinner" style={{ color: 'var(--neon-cyan)' }} /><div className="loading-text">Analyzing targets...</div></div></>);
  }

  return (
    <>
      <Topbar title="Machine Learning" subtitle="Model Training" />
      <div className="content fade-in">
        <div className="tabs">
          {TABS.map(tab => (
            <div key={tab} className={`tab ${activeTab === tab ? 'active' : ''}`} onClick={() => { setActiveTab(tab); setResult(null); }}>
              {tab}
            </div>
          ))}
        </div>

        {/* Configuration */}
        <div className="grid grid-3" style={{ marginBottom: 24 }}>
          {activeTab !== 'Clustering' && (
            <div className="card">
              <div className="card-header"><span className="card-title"><Target size={14} /> Target Column</span></div>
              <select className="form-select" value={selectedTarget} onChange={e => setSelectedTarget(e.target.value)}>
                {(targets?.targets || []).map(t => (
                  <option key={t.column} value={t.column}>{t.column} ({t.type})</option>
                ))}
              </select>
            </div>
          )}
          <div className="card">
            <div className="card-header"><span className="card-title"><Brain size={14} /> Model</span></div>
            {activeTab === 'Clustering' ? (
              <div>
                <label className="form-label">Number of Clusters</label>
                <input type="number" className="form-input" min={2} max={10} value={nClusters} onChange={e => setNClusters(parseInt(e.target.value))} />
              </div>
            ) : (
              <select className="form-select" value={model} onChange={e => setModel(e.target.value)}>
                <option value="random_forest">Random Forest</option>
                <option value="linear">Linear / Logistic</option>
                <option value="gradient_boosting">Gradient Boosting</option>
              </select>
            )}
          </div>
          <div className="card" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <button className="btn btn-primary btn-lg" onClick={handleRun} disabled={loading} style={{ width: '100%' }}>
              {loading ? <Loader2 size={18} className="spinner" /> : <Zap size={18} />}
              {loading ? 'Training...' : 'Train Model'}
            </button>
          </div>
        </div>

        {/* Error */}
        {result?.error && <div className="alert alert-error">{result.error}</div>}

        {/* Results */}
        {result && !result.error && (
          <div className="fade-in">
            {/* Metrics */}
            <div className="grid grid-4" style={{ marginBottom: 24 }}>
              {result.r2_score != null && <div className="stat-card cyan"><div className="stat-card-label">R² Score</div><div className="stat-card-value">{result.r2_score?.toFixed(4)}</div></div>}
              {result.rmse != null && <div className="stat-card pink"><div className="stat-card-label">RMSE</div><div className="stat-card-value">{result.rmse?.toFixed(4)}</div></div>}
              {result.mae != null && <div className="stat-card purple"><div className="stat-card-label">MAE</div><div className="stat-card-value">{result.mae?.toFixed(4)}</div></div>}
              {result.accuracy != null && <div className="stat-card cyan"><div className="stat-card-label">Accuracy</div><div className="stat-card-value">{(result.accuracy * 100)?.toFixed(2)}%</div></div>}
              {result.precision != null && <div className="stat-card pink"><div className="stat-card-label">Precision</div><div className="stat-card-value">{result.precision?.toFixed(4)}</div></div>}
              {result.recall != null && <div className="stat-card purple"><div className="stat-card-label">Recall</div><div className="stat-card-value">{result.recall?.toFixed(4)}</div></div>}
              {result.f1_score != null && <div className="stat-card orange"><div className="stat-card-label">F1 Score</div><div className="stat-card-value">{result.f1_score?.toFixed(4)}</div></div>}
              {result.silhouette_score != null && <div className="stat-card cyan"><div className="stat-card-label">Silhouette</div><div className="stat-card-value">{result.silhouette_score?.toFixed(4)}</div></div>}
              {result.inertia != null && <div className="stat-card pink"><div className="stat-card-label">Inertia</div><div className="stat-card-value">{result.inertia?.toFixed(2)}</div></div>}
            </div>

            {/* Charts */}
            <div className="grid grid-2">
              {result.importance_chart && (
                <div className="card">
                  <div className="card-header"><span className="card-title">Feature Importance</span></div>
                  <div style={{ height: 320 }}><PlotlyChart data={result.importance_chart} /></div>
                </div>
              )}
              {result.cm_chart && (
                <div className="card">
                  <div className="card-header"><span className="card-title">Confusion Matrix</span></div>
                  <div style={{ height: 320 }}><PlotlyChart data={result.cm_chart} /></div>
                </div>
              )}
              {result.cluster_chart && (
                <div className="card span-2">
                  <div className="card-header"><span className="card-title">Cluster Visualization</span></div>
                  <div style={{ height: 350 }}><PlotlyChart data={result.cluster_chart} /></div>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </>
  );
}
