import { useState, useEffect } from 'react';
import { useDataset } from '../context/DatasetContext';
import { getQuality } from '../services/api';
import Topbar from '../components/layout/Topbar';
import PlotlyChart from '../components/charts/PlotlyChart';
import { Loader2, ShieldCheck, AlertTriangle, CheckCircle2, XCircle } from 'lucide-react';

export default function QualityPage() {
  const { datasetId } = useDataset();
  const [quality, setQuality] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!datasetId) return;
    setLoading(true);
    getQuality(datasetId).then(setQuality).catch(() => {}).finally(() => setLoading(false));
  }, [datasetId]);

  if (loading) {
    return (<><Topbar title="Data Quality" subtitle="Assessment" /><div className="loading-overlay"><Loader2 size={32} className="spinner" style={{ color: 'var(--neon-cyan)' }} /><div className="loading-text">Analyzing data quality...</div></div></>);
  }

  const q = quality || {};
  const score = q.quality_score || 0;
  const scoreColor = score >= 80 ? 'var(--neon-green)' : score >= 60 ? 'var(--neon-yellow)' : 'var(--neon-red)';
  const scoreLabel = score >= 80 ? 'Excellent' : score >= 60 ? 'Good' : score >= 40 ? 'Fair' : 'Poor';

  return (
    <>
      <Topbar title="Data Quality" subtitle="Assessment" />
      <div className="content fade-in">

        {/* Score + Summary Cards */}
        <div className="grid grid-4" style={{ marginBottom: 24 }}>
          {/* Quality Score Circle */}
          <div className="card" style={{ alignItems: 'center', justifyContent: 'center', padding: 30 }}>
            <div className="circle-ring" style={{ width: 100, height: 100, fontSize: 28, border: `5px solid ${scoreColor}`, boxShadow: `0 0 25px ${scoreColor}40` }}>
              {score}%
            </div>
            <div style={{ marginTop: 12, fontSize: 14, fontWeight: 700, color: scoreColor }}>{scoreLabel}</div>
            <div style={{ fontSize: 11, color: 'var(--text-muted)', marginTop: 4 }}>Quality Score</div>
          </div>

          <div className="stat-card cyan">
            <div className="stat-card-label">Completeness</div>
            <div className="stat-card-value">{q.completeness?.toFixed(1) || 0}%</div>
            <div className="progress" style={{ marginTop: 8 }}><div className="progress-fill cyan" style={{ width: `${q.completeness || 0}%` }} /></div>
          </div>

          <div className="stat-card purple">
            <div className="stat-card-label">Uniqueness</div>
            <div className="stat-card-value">{q.uniqueness?.toFixed(1) || 0}%</div>
            <div className="progress" style={{ marginTop: 8 }}><div className="progress-fill purple" style={{ width: `${q.uniqueness || 0}%` }} /></div>
          </div>

          <div className="stat-card pink">
            <div className="stat-card-label">Missing Cells</div>
            <div className="stat-card-value">{q.missing_cells?.toLocaleString() || 0}</div>
            <div className="stat-card-sub">{q.missing_percentage?.toFixed(1)}% of total</div>
          </div>
        </div>

        <div className="grid grid-main-side" style={{ marginBottom: 24 }}>
          {/* Missing Values Chart */}
          <div className="card">
            <div className="card-header">
              <span className="card-title">Missing Values Distribution</span>
            </div>
            {q.missing_chart ? (
              <div style={{ height: 350 }}><PlotlyChart data={q.missing_chart} /></div>
            ) : (
              <div className="empty-state"><CheckCircle2 size={32} style={{ color: 'var(--neon-green)' }} /><h3>No missing values!</h3><p>Your dataset is complete</p></div>
            )}
          </div>

          {/* Missing by Column */}
          <div className="card">
            <div className="card-header">
              <span className="card-title">Columns with Missing Data</span>
              <span className="badge badge-red">{q.missing_by_column?.length || 0}</span>
            </div>
            <div style={{ maxHeight: 350, overflowY: 'auto' }}>
              {(q.missing_by_column || []).length > 0 ? (
                q.missing_by_column.map((col, i) => (
                  <div key={`miss-${i}`} style={{ padding: '10px 0', borderBottom: '1px solid var(--border)' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 6 }}>
                      <span style={{ fontSize: 13, fontWeight: 600, color: '#fff' }}>{col.column}</span>
                      <span style={{ fontSize: 12, color: col.missing_percentage > 20 ? 'var(--neon-red)' : 'var(--neon-yellow)' }}>
                        {col.missing_count} ({col.missing_percentage}%)
                      </span>
                    </div>
                    <div className="progress">
                      <div className="progress-fill pink" style={{ width: `${Math.min(col.missing_percentage, 100)}%` }} />
                    </div>
                  </div>
                ))
              ) : (
                <div className="empty-state" style={{ padding: 30 }}>
                  <CheckCircle2 size={28} style={{ color: 'var(--neon-green)' }} />
                  <h3>All columns complete</h3>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Duplicate Info */}
        <div className="card">
          <div className="card-header">
            <span className="card-title">Duplicate Records</span>
            <span className={`badge ${q.duplicate_rows > 0 ? 'badge-orange' : 'badge-green'}`}>
              {q.duplicate_rows > 0 ? <AlertTriangle size={12} /> : <CheckCircle2 size={12} />}
              {q.duplicate_rows || 0} duplicates
            </span>
          </div>
          <div style={{ display: 'flex', gap: 40, alignItems: 'center' }}>
            <div>
              <div style={{ fontSize: 36, fontWeight: 800, color: '#fff' }}>{q.duplicate_rows || 0}</div>
              <div style={{ fontSize: 13, color: 'var(--text-muted)' }}>Duplicate rows found</div>
            </div>
            <div style={{ flex: 1 }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 12, marginBottom: 6 }}>
                <span style={{ color: 'var(--text-muted)' }}>Duplicate Percentage</span>
                <span style={{ color: '#fff', fontWeight: 600 }}>{q.duplicate_percentage?.toFixed(1)}%</span>
              </div>
              <div className="progress" style={{ height: 10 }}>
                <div className="progress-fill orange" style={{ width: `${q.duplicate_percentage || 0}%` }} />
              </div>
            </div>
          </div>
        </div>

      </div>
    </>
  );
}
