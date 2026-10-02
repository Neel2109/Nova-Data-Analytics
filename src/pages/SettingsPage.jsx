import { useState, useEffect } from 'react';
import { useDataset } from '../context/DatasetContext';
import { healthCheck, deleteDataset } from '../services/api';
import { useNavigate } from 'react-router-dom';
import Topbar from '../components/layout/Topbar';
import { Server, Trash2, Shield, HardDrive, LogOut } from 'lucide-react';

export default function SettingsPage() {
  const { datasetId, setDatasetId, setDatasetInfo } = useDataset();
  const navigate = useNavigate();
  const [health, setHealth] = useState(null);

  useEffect(() => {
    healthCheck().then(setHealth).catch(() => setHealth({ status: 'offline' }));
  }, []);

  const handleClear = async () => {
    if (datasetId) {
      try { await deleteDataset(datasetId); } catch(e) {}
    }
    setDatasetId(null);
    setDatasetInfo(null);
    navigate('/');
  };

  return (
    <>
      <Topbar title="Settings" subtitle="System Configuration" />
      <div className="content fade-in">
        
        <div className="grid grid-2">
          
          <div className="card">
            <div className="card-header"><span className="card-title">Backend Status</span></div>
            <div style={{ display: 'flex', alignItems: 'center', gap: 24 }}>
              <div className="circle-ring cyan" style={{ width: 80, height: 80 }}>
                <Server size={32} />
              </div>
              <div style={{ flex: 1 }}>
                <div className="metric-row">
                  <span className="metric-label">Status</span>
                  <span className="metric-value">
                    {health?.status === 'operational' ? (
                      <span className="badge badge-green">Operational</span>
                    ) : (
                      <span className="badge badge-red">Offline</span>
                    )}
                  </span>
                </div>
                <div className="metric-row">
                  <span className="metric-label">Version</span>
                  <span className="metric-value">{health?.version || 'Unknown'}</span>
                </div>
                <div className="metric-row">
                  <span className="metric-label">Datasets Loaded</span>
                  <span className="metric-value">{health?.datasets_loaded || 0}</span>
                </div>
              </div>
            </div>
          </div>

          <div className="card">
            <div className="card-header"><span className="card-title">Dataset Management</span></div>
            <div style={{ display: 'flex', alignItems: 'center', gap: 24, flex: 1 }}>
              <div className="circle-ring orange" style={{ width: 80, height: 80 }}>
                <HardDrive size={32} />
              </div>
              <div style={{ flex: 1 }}>
                <p style={{ fontSize: 13, color: 'var(--text-secondary)', marginBottom: 16 }}>
                  Current active dataset: <strong style={{ color: '#fff' }}>{datasetId || 'None'}</strong>
                </p>
                <button className="btn btn-danger" onClick={handleClear} disabled={!datasetId} style={{ width: '100%' }}>
                  <Trash2 size={16} /> Delete Current Dataset
                </button>
              </div>
            </div>
          </div>

          <div className="card">
            <div className="card-header"><span className="card-title">Security & Privacy</span></div>
            <div style={{ display: 'flex', alignItems: 'flex-start', gap: 16 }}>
              <Shield size={32} style={{ color: 'var(--neon-purple)', flexShrink: 0 }} />
              <div>
                <p style={{ fontSize: 13, color: 'var(--text-secondary)', lineHeight: 1.6 }}>
                  DataNova runs entirely locally. Your data is not sent to any external servers or third-party APIs. 
                  Machine learning, data profiling, and AI insights are executed directly on your machine.
                </p>
              </div>
            </div>
          </div>

        </div>

      </div>
    </>
  );
}
