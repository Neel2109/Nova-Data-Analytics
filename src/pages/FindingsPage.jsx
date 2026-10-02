import { useState, useEffect } from 'react';
import { useDataset } from '../context/DatasetContext';
import { getProfile, getPreview } from '../services/api';
import Topbar from '../components/layout/Topbar';
import { Loader2, Hash, Type, Calendar, ToggleLeft, ArrowUpDown } from 'lucide-react';

export default function FindingsPage() {
  const { datasetId } = useDataset();
  const [profile, setProfile] = useState(null);
  const [preview, setPreview] = useState(null);
  const [loading, setLoading] = useState(true);
  const [selectedCol, setSelectedCol] = useState(null);

  useEffect(() => {
    if (!datasetId) return;
    setLoading(true);
    Promise.all([
      getProfile(datasetId),
      getPreview(datasetId, 20),
    ]).then(([prof, prev]) => {
      setProfile(prof);
      setPreview(prev);
      setLoading(false);
    }).catch(() => setLoading(false));
  }, [datasetId]);

  if (loading) {
    return (
      <>
        <Topbar title="Data Profile" subtitle="Profiling" />
        <div className="loading-overlay"><Loader2 size={32} className="spinner" style={{ color: 'var(--neon-cyan)' }} /><div className="loading-text">Profiling dataset...</div></div>
      </>
    );
  }

  const columns = profile?.column_profiles || [];
  const typeIcon = (type) => {
    switch (type) {
      case 'numerical': return <Hash size={14} style={{ color: 'var(--neon-cyan)' }} />;
      case 'categorical': return <Type size={14} style={{ color: 'var(--neon-purple)' }} />;
      case 'datetime': return <Calendar size={14} style={{ color: 'var(--neon-pink)' }} />;
      case 'boolean': return <ToggleLeft size={14} style={{ color: 'var(--neon-orange)' }} />;
      default: return <Hash size={14} style={{ color: 'var(--text-muted)' }} />;
    }
  };

  const selected = selectedCol ? columns.find(c => c.name === selectedCol) : null;

  return (
    <>
      <Topbar title="Data Profile" subtitle="Column Analysis" />
      <div className="content fade-in">

        {/* Summary Row */}
        <div className="grid grid-4" style={{ marginBottom: 24 }}>
          <div className="stat-card cyan">
            <div className="stat-card-label">Total Columns</div>
            <div className="stat-card-value">{profile?.columns || 0}</div>
          </div>
          <div className="stat-card purple">
            <div className="stat-card-label">Numerical</div>
            <div className="stat-card-value">{profile?.numerical_columns?.length || 0}</div>
          </div>
          <div className="stat-card pink">
            <div className="stat-card-label">Categorical</div>
            <div className="stat-card-value">{profile?.categorical_columns?.length || 0}</div>
          </div>
          <div className="stat-card orange">
            <div className="stat-card-label">Datetime</div>
            <div className="stat-card-value">{profile?.datetime_columns?.length || 0}</div>
          </div>
        </div>

        <div className="grid grid-main-side">
          {/* Column Table */}
          <div className="card">
            <div className="card-header">
              <span className="card-title">Column Profiles</span>
              <span className="badge badge-cyan">{columns.length} columns</span>
            </div>
            <div className="table-container" style={{ maxHeight: 500, overflowY: 'auto' }}>
              <table>
                <thead>
                  <tr>
                    <th>Column</th>
                    <th>Type</th>
                    <th>Non-Null</th>
                    <th>Missing %</th>
                    <th>Unique</th>
                    <th>Action</th>
                  </tr>
                </thead>
                <tbody>
                  {columns.map((col) => (
                    <tr key={col.name} style={{ cursor: 'pointer', background: selectedCol === col.name ? 'var(--bg-elevated)' : undefined }}
                        onClick={() => setSelectedCol(col.name)}>
                      <td style={{ fontWeight: 600, color: '#fff' }}>{col.name}</td>
                      <td><span className="badge" style={{ gap: 4 }}>{typeIcon(col.column_type)} {col.column_type}</span></td>
                      <td>{col.count}</td>
                      <td>
                        <span style={{ color: col.missing_percentage > 10 ? 'var(--neon-red)' : col.missing_percentage > 0 ? 'var(--neon-yellow)' : 'var(--neon-green)' }}>
                          {col.missing_percentage?.toFixed(1)}%
                        </span>
                      </td>
                      <td>{col.unique}</td>
                      <td><button className="btn btn-ghost btn-sm" onClick={(e) => { e.stopPropagation(); setSelectedCol(col.name); }}>Details</button></td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* Detail Panel */}
          <div className="card">
            <div className="card-header">
              <span className="card-title">{selected ? selected.name : 'Select a Column'}</span>
              {selected && <span className={`badge badge-${selected.column_type === 'numerical' ? 'cyan' : 'purple'}`}>{selected.column_type}</span>}
            </div>
            {selected ? (
              <div>
                <div className="metric-row"><span className="metric-label">Count</span><span className="metric-value">{selected.count}</span></div>
                <div className="metric-row"><span className="metric-label">Missing</span><span className="metric-value" style={{ color: selected.missing > 0 ? 'var(--neon-red)' : 'var(--neon-green)' }}>{selected.missing} ({selected.missing_percentage?.toFixed(1)}%)</span></div>
                <div className="metric-row"><span className="metric-label">Unique</span><span className="metric-value">{selected.unique}</span></div>

                {selected.column_type === 'numerical' && (
                  <>
                    <div style={{ borderTop: '1px solid var(--border)', margin: '12px 0', paddingTop: 12 }}>
                      <div className="section-title" style={{ fontSize: 11, marginBottom: 10 }}>Statistics</div>
                    </div>
                    <div className="metric-row"><span className="metric-label">Mean</span><span className="metric-value">{selected.mean?.toFixed(2)}</span></div>
                    <div className="metric-row"><span className="metric-label">Median</span><span className="metric-value">{selected.median?.toFixed(2)}</span></div>
                    <div className="metric-row"><span className="metric-label">Std Dev</span><span className="metric-value">{selected.std?.toFixed(2)}</span></div>
                    <div className="metric-row"><span className="metric-label">Min</span><span className="metric-value">{selected.min_val}</span></div>
                    <div className="metric-row"><span className="metric-label">Max</span><span className="metric-value">{selected.max_val}</span></div>
                    <div className="metric-row"><span className="metric-label">Skewness</span><span className="metric-value">{selected.skewness?.toFixed(3)}</span></div>
                  </>
                )}

                {selected.column_type === 'categorical' && selected.top_values && (
                  <>
                    <div style={{ borderTop: '1px solid var(--border)', margin: '12px 0', paddingTop: 12 }}>
                      <div className="section-title" style={{ fontSize: 11, marginBottom: 10 }}>Top Values</div>
                    </div>
                    {selected.top_values.slice(0, 5).map((v, i) => (
                      <div key={`top-${i}`} className="metric-row">
                        <span className="metric-label">{String(v.value).substring(0, 25)}</span>
                        <span className="metric-value">{v.count}</span>
                      </div>
                    ))}
                  </>
                )}
              </div>
            ) : (
              <div className="empty-state" style={{ padding: 40 }}>
                <ArrowUpDown size={32} />
                <h3>Click a column</h3>
                <p>Select any column from the table to see detailed statistics</p>
              </div>
            )}
          </div>
        </div>

        {/* Data Preview */}
        {preview?.data?.length > 0 && (
          <div className="card" style={{ marginTop: 24 }}>
            <div className="card-header">
              <span className="card-title">Data Preview (First 20 Rows)</span>
            </div>
            <div className="table-container" style={{ maxHeight: 350, overflowY: 'auto' }}>
              <table>
                <thead><tr>{preview.columns.map(c => <th key={c}>{c}</th>)}</tr></thead>
                <tbody>
                  {preview.data.map((row, i) => (
                    <tr key={`prev-${i}`}>{preview.columns.map(c => <td key={`${i}-${c}`}>{row[c] != null ? String(row[c]).substring(0, 50) : '—'}</td>)}</tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

      </div>
    </>
  );
}
