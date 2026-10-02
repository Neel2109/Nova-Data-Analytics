import { useState, useEffect } from 'react';
import { useDataset } from '../context/DatasetContext';
import { cleanDataset, resetDataset, getProfile } from '../services/api';
import Topbar from '../components/layout/Topbar';
import { Loader2, Eraser, RotateCcw, CheckCircle2, Sparkles } from 'lucide-react';

export default function CleaningPage() {
  const { datasetId } = useDataset();
  const [profile, setProfile] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(true);
  const [cleaning, setCleaning] = useState(false);
  const [options, setOptions] = useState({
    missing_strategy: 'median',
    duplicate_strategy: 'remove',
    outlier_strategy: 'keep',
    standardize_text: true,
    convert_types: true,
  });

  useEffect(() => {
    if (!datasetId) return;
    getProfile(datasetId).then(setProfile).catch(() => {}).finally(() => setLoading(false));
  }, [datasetId]);

  const handleClean = async () => {
    setCleaning(true);
    try {
      const res = await cleanDataset(datasetId, options);
      setResult(res);
    } catch (err) {
      console.error(err);
    }
    setCleaning(false);
  };

  const handleReset = async () => {
    try {
      await resetDataset(datasetId);
      setResult(null);
      const prof = await getProfile(datasetId);
      setProfile(prof);
    } catch (err) {
      console.error(err);
    }
  };

  if (loading) {
    return (<><Topbar title="Data Cleaning" subtitle="Clean" /><div className="loading-overlay"><Loader2 size={32} className="spinner" style={{ color: 'var(--neon-cyan)' }} /><div className="loading-text">Loading...</div></div></>);
  }

  return (
    <>
      <Topbar title="Data Cleaning" subtitle="Clean & Transform" />
      <div className="content fade-in">

        {/* Config Cards */}
        <div className="grid grid-3" style={{ marginBottom: 24 }}>
          <div className="card">
            <div className="card-header"><span className="card-title">Missing Values Strategy</span></div>
            <div className="form-group">
              <select className="form-select" value={options.missing_strategy} onChange={e => setOptions({...options, missing_strategy: e.target.value})}>
                <option value="median">Fill with Median</option>
                <option value="mean">Fill with Mean</option>
                <option value="mode">Fill with Mode</option>
                <option value="drop">Drop rows with missing</option>
                <option value="ffill">Forward Fill</option>
              </select>
            </div>
            <div style={{ fontSize: 12, color: 'var(--text-muted)' }}>
              Current missing: <strong style={{ color: 'var(--neon-pink)' }}>{profile?.missing_cells || 0}</strong> cells
            </div>
          </div>

          <div className="card">
            <div className="card-header"><span className="card-title">Duplicate Strategy</span></div>
            <div className="form-group">
              <select className="form-select" value={options.duplicate_strategy} onChange={e => setOptions({...options, duplicate_strategy: e.target.value})}>
                <option value="remove">Remove Duplicates</option>
                <option value="keep">Keep All</option>
              </select>
            </div>
            <div style={{ fontSize: 12, color: 'var(--text-muted)' }}>
              Current duplicates: <strong style={{ color: 'var(--neon-orange)' }}>{profile?.duplicate_rows || 0}</strong> rows
            </div>
          </div>

          <div className="card">
            <div className="card-header"><span className="card-title">Additional Options</span></div>
            <label style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 12, fontSize: 13, color: 'var(--text-secondary)', cursor: 'pointer' }}>
              <input type="checkbox" checked={options.standardize_text} onChange={e => setOptions({...options, standardize_text: e.target.checked})} style={{ accentColor: 'var(--neon-cyan)' }} />
              Standardize text columns
            </label>
            <label style={{ display: 'flex', alignItems: 'center', gap: 10, fontSize: 13, color: 'var(--text-secondary)', cursor: 'pointer' }}>
              <input type="checkbox" checked={options.convert_types} onChange={e => setOptions({...options, convert_types: e.target.checked})} style={{ accentColor: 'var(--neon-cyan)' }} />
              Auto-convert data types
            </label>
          </div>
        </div>

        {/* Action Buttons */}
        <div style={{ display: 'flex', gap: 12, marginBottom: 24 }}>
          <button className="btn btn-primary btn-lg" onClick={handleClean} disabled={cleaning}>
            {cleaning ? <Loader2 size={18} className="spinner" /> : <Sparkles size={18} />}
            {cleaning ? 'Cleaning...' : 'Clean Dataset'}
          </button>
          <button className="btn btn-secondary btn-lg" onClick={handleReset}>
            <RotateCcw size={18} /> Reset to Original
          </button>
        </div>

        {/* Results */}
        {result && (
          <div className="card fade-in">
            <div className="card-header">
              <span className="card-title">Cleaning Results</span>
              <span className="badge badge-green"><CheckCircle2 size={12} /> Complete</span>
            </div>

            <div className="grid grid-3" style={{ marginBottom: 20 }}>
              <div style={{ textAlign: 'center', padding: 16 }}>
                <div style={{ fontSize: 12, color: 'var(--text-muted)', marginBottom: 4 }}>Rows</div>
                <div style={{ fontSize: 20, fontWeight: 800, color: '#fff' }}>{result.original_rows} → {result.cleaned_rows}</div>
              </div>
              <div style={{ textAlign: 'center', padding: 16 }}>
                <div style={{ fontSize: 12, color: 'var(--text-muted)', marginBottom: 4 }}>Missing</div>
                <div style={{ fontSize: 20, fontWeight: 800, color: '#fff' }}>{result.original_missing} → <span className="glow-green">{result.cleaned_missing}</span></div>
              </div>
              <div style={{ textAlign: 'center', padding: 16 }}>
                <div style={{ fontSize: 12, color: 'var(--text-muted)', marginBottom: 4 }}>Duplicates</div>
                <div style={{ fontSize: 20, fontWeight: 800, color: '#fff' }}>{result.original_duplicates} → <span className="glow-green">{result.cleaned_duplicates}</span></div>
              </div>
            </div>

            {result.operations_log?.length > 0 && (
              <>
                <div className="section-header"><span className="section-title">Operations Log</span></div>
                <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
                  {result.operations_log.map((op, i) => (
                    <div key={`op-${i}`} style={{ display: 'flex', alignItems: 'center', gap: 10, padding: '8px 12px', background: 'var(--bg-elevated)', borderRadius: 'var(--radius-sm)', fontSize: 13 }}>
                      <CheckCircle2 size={14} style={{ color: 'var(--neon-green)', flexShrink: 0 }} />
                      <span style={{ color: 'var(--text-secondary)' }}>{op}</span>
                    </div>
                  ))}
                </div>
              </>
            )}
          </div>
        )}

      </div>
    </>
  );
}
