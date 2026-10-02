import { useState, useEffect } from 'react';
import { useDataset } from '../context/DatasetContext';
import { getProfile, getPreview, getInsights, getAutoCharts } from '../services/api';
import Topbar from '../components/layout/Topbar';
import PlotlyChart from '../components/charts/PlotlyChart';
import { Loader2, TrendingUp, TrendingDown, Database, Columns3, AlertTriangle, CheckCircle2, BarChart3 } from 'lucide-react';

export default function OverviewPage() {
  const { datasetId, datasetInfo } = useDataset();
  const [profile, setProfile] = useState(null);
  const [preview, setPreview] = useState(null);
  const [insights, setInsights] = useState(null);
  const [charts, setCharts] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!datasetId) return;
    setLoading(true);
    Promise.all([
      getProfile(datasetId).catch(() => null),
      getPreview(datasetId, 10).catch(() => null),
      getInsights(datasetId).catch(() => null),
      getAutoCharts(datasetId).catch(() => null),
    ]).then(([prof, prev, ins, ch]) => {
      setProfile(prof);
      setPreview(prev);
      setInsights(ins);
      setCharts(ch);
      setLoading(false);
    });
  }, [datasetId]);

  if (loading) {
    return (
      <>
        <Topbar title="Dashboard" subtitle="Overview" />
        <div className="loading-overlay"><Loader2 size={32} className="spinner" style={{ color: 'var(--neon-cyan)' }} /><div className="loading-text">Loading dashboard...</div></div>
      </>
    );
  }

  const info = datasetInfo || {};
  const prof = profile || {};
  const qualityScore = prof.quality_score || 0;

  const statCards = [
    { label: 'Total Rows', value: (prof.rows || info.rows || 0).toLocaleString(), badge: null, color: 'cyan' },
    { label: 'Total Columns', value: (prof.columns || info.columns || 0).toString(), badge: null, color: 'purple' },
    { label: 'Missing Values', value: `${prof.missing_percentage || 0}%`, badge: prof.missing_percentage > 5 ? 'high' : 'low', color: 'pink' },
    { label: 'Quality Score', value: `${qualityScore}%`, badge: qualityScore >= 80 ? 'good' : 'fair', color: 'orange' },
  ];

  return (
    <>
      <Topbar title="Dashboard" subtitle="Overview" />
      <div className="content fade-in">

        {/* Layout matching the 'Value Analytics' Dashboard Reference */}

        <div style={{ display: 'grid', gridTemplateColumns: '1fr 300px', gap: 24, marginBottom: 24 }}>
          {/* Main Left Column */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: 24 }}>
            
            {/* Top Stat Cards (3 columns) */}
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: 24 }}>
              {statCards.slice(0, 3).map((s) => (
                <div key={s.label} className={`stat-card ${s.color}`}>
                  <div className="stat-card-top">
                    <span className="stat-card-label">{s.label}</span>
                    {s.badge && (
                      <span className={`stat-card-badge ${s.badge === 'high' || s.badge === 'fair' ? 'down' : 'up'}`}>
                        {s.badge === 'high' || s.badge === 'fair' ? <TrendingDown size={12} /> : <TrendingUp size={12} />}
                        {s.badge}
                      </span>
                    )}
                  </div>
                  <div className="stat-card-value">{s.value}</div>
                </div>
              ))}
            </div>

            {/* Middle Row: Data Preview (List) + Main Line Chart */}
            <div style={{ display: 'grid', gridTemplateColumns: '300px 1fr', gap: 24 }}>
              
              {/* Data Preview (Real-time data equivalent) */}
              <div className="card" style={{ display: 'flex', flexDirection: 'column' }}>
                <div className="card-header">
                  <span className="card-title">Data Preview</span>
                  <span className="badge badge-purple"><Database size={12} /></span>
                </div>
                {preview?.data?.length > 0 ? (
                  <div style={{ overflowY: 'auto', flex: 1, paddingRight: 8 }}>
                    {preview.data.slice(0, 5).map((row, i) => (
                      <div key={i} style={{ display: 'flex', justifyContent: 'space-between', padding: '12px 0', borderBottom: '1px solid var(--border)' }}>
                        <span style={{ fontSize: 12, color: 'var(--text-secondary)' }}>{String(row[preview.columns[0]] || '').substring(0, 15)}</span>
                        <span style={{ fontSize: 13, color: '#fff', fontWeight: 600 }}>{String(row[preview.columns[1]] || '').substring(0, 10)}</span>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="empty-state"><p>No data</p></div>
                )}
              </div>

              {/* Main Trend / Line Chart (Site traffic equivalent) */}
              <div className="card">
                <div className="card-header">
                  <span className="card-title">Trend Analysis</span>
                  <span className="badge badge-cyan"><BarChart3 size={12} /> Auto</span>
                </div>
                <div style={{ height: 260 }}>
                  {charts?.charts?.find(c => c.type === 'line') ? (
                    <PlotlyChart data={charts.charts.find(c => c.type === 'line').chart} />
                  ) : charts?.charts?.[0] ? (
                    <PlotlyChart data={charts.charts[0].chart} />
                  ) : (
                    <div className="empty-state"><BarChart3 size={32} /><p>Upload data to see trends</p></div>
                  )}
                </div>
              </div>

            </div>

          </div>

          {/* Right Sidebar Column */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: 24 }}>
            
            {/* Top Right Donut Chart (Devices equivalent) */}
            <div className="card">
              <div className="card-header">
                <span className="card-title">Distribution</span>
              </div>
              <div style={{ height: 220 }}>
                {charts?.charts?.find(c => c.type === 'pie') ? (
                  <PlotlyChart data={charts.charts.find(c => c.type === 'pie').chart} />
                ) : (
                  <div className="empty-state"><BarChart3 size={24} /><p>No category data</p></div>
                )}
              </div>
            </div>

            {/* Additional Stat / Info Box */}
            <div className="stat-card orange" style={{ flex: 1 }}>
              <div className="stat-card-top">
                <span className="stat-card-label">{statCards[3].label}</span>
                {statCards[3].badge && (
                  <span className={`stat-card-badge ${statCards[3].badge === 'high' || statCards[3].badge === 'fair' ? 'down' : 'up'}`}>
                    {statCards[3].badge}
                  </span>
                )}
              </div>
              <div className="stat-card-value">{statCards[3].value}</div>
            </div>

          </div>
        </div>

        {/* Bottom Massive Grid for All Other Plots */}
        <div style={{ marginTop: 24 }}>
          <div className="card-header" style={{ marginBottom: 16 }}>
            <span className="card-title" style={{ fontSize: 18 }}>Extended Analytics Hub</span>
          </div>
          
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(350px, 1fr))', gap: 24 }}>
            
            {/* Quick Insights (Moved to bottom grid) */}
            <div className="card" style={{ display: 'flex', flexDirection: 'column', height: 300 }}>
              <div className="card-header">
                <span className="card-title">System Insights</span>
              </div>
              <div style={{ overflowY: 'auto', flex: 1, paddingRight: 4 }}>
                {(insights?.insights || []).map((ins, i) => (
                  <div key={`insight-${i}`} style={{ marginBottom: 12 }}>
                    <div style={{ fontSize: 13, color: '#fff', fontWeight: 500, display: 'flex', alignItems: 'center', gap: 6 }}>
                      <div style={{ width: 6, height: 6, borderRadius: '50%', background: ins.severity === 'critical' ? 'var(--neon-pink)' : 'var(--neon-cyan)' }} />
                      {ins.title.substring(0, 30)}
                    </div>
                    <div style={{ fontSize: 11, color: 'var(--text-secondary)', paddingLeft: 12, marginTop: 4 }}>
                      {ins.message.substring(0, 60)}...
                    </div>
                  </div>
                ))}
                {(!insights?.insights || insights.insights.length === 0) && (
                  <div className="empty-state"><p>No insights found</p></div>
                )}
              </div>
            </div>

            {/* Map through all available charts */}
            {(charts?.charts || []).map((chartObj, index) => {
              // Skip the first line chart and first pie chart as they are in the top sections
              if (index === 0 && chartObj.type === 'line') return null;
              if (index === 1 && chartObj.type === 'pie') return null;
              
              return (
                <div key={`extra-chart-${index}`} className="card" style={{ height: 300 }}>
                  <div className="card-header">
                    <span className="card-title" style={{ textTransform: 'capitalize' }}>{chartObj.type} | {chartObj.column}</span>
                  </div>
                  <div style={{ height: 240 }}>
                    <PlotlyChart data={chartObj.chart} />
                  </div>
                </div>
              );
            })}

          </div>
        </div>

      </div>
    </>
  );
}
