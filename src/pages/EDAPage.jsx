import { useState, useEffect } from 'react';
import { useDataset } from '../context/DatasetContext';
import { getDistributions, getCorrelations, getOutliers, getCategorical, getAutoCharts, getProfile } from '../services/api';
import Topbar from '../components/layout/Topbar';
import PlotlyChart from '../components/charts/PlotlyChart';
import { Loader2, BarChart3, GitBranch, AlertTriangle, PieChart } from 'lucide-react';

const TABS = ['Charts', 'Distributions', 'Correlations', 'Outliers', 'Categorical'];

export default function EDAPage() {
  const { datasetId } = useDataset();
  const [activeTab, setActiveTab] = useState('Charts');
  const [autoCharts, setAutoCharts] = useState(null);
  const [distributions, setDistributions] = useState(null);
  const [correlations, setCorrelations] = useState(null);
  const [outliers, setOutliers] = useState(null);
  const [categorical, setCategorical] = useState(null);
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [corrMethod, setCorrMethod] = useState('pearson');

  useEffect(() => {
    if (!datasetId) return;
    getProfile(datasetId).then(setProfile).catch(() => {});
    loadTab('Charts');
  }, [datasetId]);

  const loadTab = async (tab) => {
    setActiveTab(tab);
    setLoading(true);
    try {
      switch (tab) {
        case 'Charts': { const res = await getAutoCharts(datasetId); setAutoCharts(res); break; }
        case 'Distributions': { const res = await getDistributions(datasetId); setDistributions(res); break; }
        case 'Correlations': { const res = await getCorrelations(datasetId, corrMethod); setCorrelations(res); break; }
        case 'Outliers': { const res = await getOutliers(datasetId); setOutliers(res); break; }
        case 'Categorical': { const res = await getCategorical(datasetId); setCategorical(res); break; }
      }
    } catch (e) { console.error(e); }
    setLoading(false);
  };

  const renderContent = () => {
    if (loading) return <div className="loading-overlay"><Loader2 size={28} className="spinner" style={{ color: 'var(--neon-cyan)' }} /><div className="loading-text">Loading {activeTab.toLowerCase()}...</div></div>;

    switch (activeTab) {
      case 'Charts':
        return (
          <div className="grid grid-2">
            {(autoCharts?.charts || []).map((chart, i) => (
              <div key={`ac-${i}`} className="card">
                <div style={{ height: 320 }}><PlotlyChart data={chart.chart} /></div>
              </div>
            ))}
            {(!autoCharts?.charts || autoCharts.charts.length === 0) && (
              <div className="card span-2"><div className="empty-state"><BarChart3 size={32} /><h3>No auto-generated charts</h3><p>Try uploading a dataset with more columns</p></div></div>
            )}
          </div>
        );

      case 'Distributions':
        return (
          <div className="grid grid-2">
            {(distributions?.distributions || []).map((dist, i) => (
              <div key={`dist-${i}`} className="card">
                <div className="card-header"><span className="card-title">{dist.column}</span><span className="badge badge-cyan">Histogram</span></div>
                <div style={{ height: 280 }}><PlotlyChart data={dist.chart} /></div>
              </div>
            ))}
          </div>
        );

      case 'Correlations':
        return (
          <div>
            <div className="chart-controls">
              {['pearson', 'spearman', 'kendall'].map(m => (
                <button key={m} className={`btn btn-sm ${corrMethod === m ? 'btn-primary' : 'btn-secondary'}`}
                  onClick={() => { setCorrMethod(m); loadTab('Correlations'); }}>
                  {m.charAt(0).toUpperCase() + m.slice(1)}
                </button>
              ))}
            </div>
            <div className="grid grid-main-side">
              <div className="card">
                <div className="card-header"><span className="card-title">Correlation Heatmap</span></div>
                {correlations?.heatmap_chart ? (
                  <div style={{ height: 450 }}><PlotlyChart data={correlations.heatmap_chart} /></div>
                ) : <div className="empty-state"><GitBranch size={32} /><p>Not enough numerical columns for correlation analysis</p></div>}
              </div>
              <div className="card">
                <div className="card-header"><span className="card-title">Strong Relationships</span></div>
                <div style={{ maxHeight: 450, overflowY: 'auto' }}>
                  {[...(correlations?.strong_positive || []), ...(correlations?.strong_negative || [])].map((rel, i) => (
                    <div key={`rel-${i}`} className="metric-row">
                      <span className="metric-label" style={{ flex: 1 }}>{rel.column_a} ↔ {rel.column_b}</span>
                      <span className="metric-value" style={{ color: rel.correlation > 0 ? 'var(--neon-green)' : 'var(--neon-red)' }}>{rel.correlation?.toFixed(3)}</span>
                    </div>
                  ))}
                  {!(correlations?.strong_positive?.length || correlations?.strong_negative?.length) && (
                    <div className="empty-state" style={{ padding: 20 }}><p>No strong correlations found</p></div>
                  )}
                </div>
              </div>
            </div>
            {/* Scatter Plots */}
            {correlations?.scatter_plots?.length > 0 && (
              <div className="grid grid-2" style={{ marginTop: 20 }}>
                {correlations.scatter_plots.map((sp, i) => (
                  <div key={`sc-${i}`} className="card">
                    <div className="card-header"><span className="card-title">{sp.columns.join(' vs ')}</span><span className="badge badge-purple">r = {sp.correlation?.toFixed(3)}</span></div>
                    <div style={{ height: 280 }}><PlotlyChart data={sp.chart} /></div>
                  </div>
                ))}
              </div>
            )}
          </div>
        );

      case 'Outliers':
        return (
          <div>
            <div className="grid grid-4" style={{ marginBottom: 20 }}>
              <div className="stat-card pink">
                <div className="stat-card-label">Total Outliers</div>
                <div className="stat-card-value">{outliers?.total_outliers || 0}</div>
              </div>
              <div className="stat-card cyan">
                <div className="stat-card-label">Columns Affected</div>
                <div className="stat-card-value">{outliers?.summary?.filter(s => s.outlier_count > 0).length || 0}</div>
              </div>
              <div className="stat-card purple">
                <div className="stat-card-label">Method</div>
                <div className="stat-card-value" style={{ fontSize: 16 }}>{outliers?.method?.toUpperCase() || 'IQR'}</div>
              </div>
              <div className="stat-card orange">
                <div className="stat-card-label">Outlier %</div>
                <div className="stat-card-value">{outliers?.outlier_percentage?.toFixed(1) || 0}%</div>
              </div>
            </div>
            <div className="grid grid-2">
              {(outliers?.box_plots || []).map((bp, i) => (
                <div key={`bp-${i}`} className="card">
                  <div className="card-header"><span className="card-title">{bp.column}</span><span className="badge badge-pink"><AlertTriangle size={12} /> Box Plot</span></div>
                  <div style={{ height: 280 }}><PlotlyChart data={bp.chart} /></div>
                </div>
              ))}
            </div>
            {outliers?.summary?.length > 0 && (
              <div className="card" style={{ marginTop: 20 }}>
                <div className="card-header"><span className="card-title">Outlier Summary</span></div>
                <div className="table-container">
                  <table>
                    <thead><tr><th>Column</th><th>Outliers</th><th>Lower</th><th>Upper</th></tr></thead>
                    <tbody>{outliers.summary.filter(s => s.outlier_count > 0).map((s, i) => (
                      <tr key={`os-${i}`}>
                        <td style={{ fontWeight: 600, color: '#fff' }}>{s.column}</td>
                        <td><span className="badge badge-pink">{s.outlier_count}</span></td>
                        <td>{s.lower_bound?.toFixed(2)}</td>
                        <td>{s.upper_bound?.toFixed(2)}</td>
                      </tr>
                    ))}</tbody>
                  </table>
                </div>
              </div>
            )}
          </div>
        );

      case 'Categorical':
        return (
          <div className="grid grid-2">
            {(categorical?.columns || []).map((col, i) => (
              <div key={`cat-${i}`} className="card">
                <div className="card-header"><span className="card-title">{col.column}</span><span className="badge badge-purple">{col.unique_values} unique</span></div>
                {col.bar_chart && <div style={{ height: 280 }}><PlotlyChart data={col.bar_chart} /></div>}
                {col.pie_chart && <div style={{ height: 280, marginTop: 16 }}><PlotlyChart data={col.pie_chart} /></div>}
              </div>
            ))}
          </div>
        );

      default: return null;
    }
  };

  return (
    <>
      <Topbar title="EDA & Charts" subtitle="Exploratory Analysis" />
      <div className="content fade-in">
        <div className="tabs">
          {TABS.map(tab => (
            <div key={tab} className={`tab ${activeTab === tab ? 'active' : ''}`} onClick={() => loadTab(tab)}>
              {tab}
            </div>
          ))}
        </div>
        {renderContent()}
      </div>
    </>
  );
}
