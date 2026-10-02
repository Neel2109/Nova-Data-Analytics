import { useState, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { useDropzone } from 'react-dropzone';
import { Upload, ChevronRight, BarChart3, Brain, Sparkles, FileText, Loader2, Zap } from 'lucide-react';
import { uploadDataset } from '../services/api';
import { useDataset } from '../context/DatasetContext';

export default function LandingPage() {
  const navigate = useNavigate();
  const { setDatasetId, setDatasetInfo } = useDataset();
  const [uploading, setUploading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [error, setError] = useState(null);

  const onDrop = useCallback(async (acceptedFiles) => {
    const file = acceptedFiles[0];
    if (!file) return;
    setError(null);
    setUploading(true);
    setProgress(10);

    const interval = setInterval(() => {
      setProgress(prev => Math.min(prev + Math.random() * 15, 85));
    }, 300);

    try {
      const result = await uploadDataset(file);
      clearInterval(interval);
      setProgress(100);
      setDatasetId(result.dataset_id);
      setDatasetInfo(result);
      setTimeout(() => navigate('/overview'), 600);
    } catch (err) {
      clearInterval(interval);
      setProgress(0);
      setUploading(false);
      setError(err.response?.data?.detail || 'Upload failed. Ensure the backend server is running on port 8000.');
    }
  }, [navigate, setDatasetId, setDatasetInfo]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { 'text/csv': ['.csv'] },
    maxFiles: 1,
    disabled: uploading,
  });

  const steps = [
    { num: '01', label: 'Profile' },
    { num: '02', label: 'Clean' },
    { num: '03', label: 'Analyze' },
    { num: '04', label: 'Investigate' },
    { num: '05', label: 'Explain' },
  ];

  const features = [
    { icon: BarChart3, title: 'EDA & Charts', desc: '150+ visualizations' },
    { icon: Brain, title: 'Machine Learning', desc: 'Auto regression & classification' },
    { icon: Sparkles, title: 'AI Insights', desc: 'Evidence-based findings' },
    { icon: FileText, title: 'Reports', desc: 'PDF, Excel & CSV exports' },
  ];

  return (
    <div className="landing fade-in">
      <div className="landing-logo">
        <div className="landing-logo-icon">D</div>
        <h1>DataNova</h1>
      </div>

      <div className="landing-tagline">Automated Data Investigation</div>

      <h2 className="landing-headline">
        Turn raw data into <span>intelligence</span>.
      </h2>

      <p className="landing-description">
        Upload any CSV dataset and let DataNova automatically profile, clean, analyze,
        investigate and explain the important patterns — powered by an automated data science engine.
      </p>

      {uploading ? (
        <div style={{ width: '100%', maxWidth: 520, textAlign: 'center' }}>
          <div className="card" style={{ padding: '48px 40px' }}>
            <Loader2 size={40} className="spinner" style={{ color: 'var(--neon-cyan)', marginBottom: 20 }} />
            <div style={{ fontSize: 18, fontWeight: 700, marginBottom: 8, color: '#fff' }}>
              {progress < 100 ? 'Analyzing your dataset...' : 'Analysis complete!'}
            </div>
            <div style={{ fontSize: 13, color: 'var(--text-secondary)', marginBottom: 24 }}>
              Detecting schema, profiling columns, generating insights
            </div>
            <div className="progress" style={{ marginBottom: 12, height: 8 }}>
              <div className="progress-fill cyan" style={{ width: `${progress}%` }} />
            </div>
            <div style={{ fontSize: 12, color: 'var(--text-muted)' }}>{Math.round(progress)}%</div>
          </div>
        </div>
      ) : (
        <div style={{ width: '100%', maxWidth: 520 }}>
          <div {...getRootProps()} className={`upload-dropzone ${isDragActive ? 'active' : ''}`}>
            <input {...getInputProps()} />
            <div className="upload-icon"><Upload size={28} /></div>
            <div className="upload-title">
              {isDragActive ? 'Drop your dataset here' : 'Upload CSV'}
            </div>
            <div className="upload-subtitle">
              Drop your dataset here or browse from your computer
            </div>
            <button className="btn btn-primary" style={{ margin: '0 auto' }}>
              <Zap size={16} /> Browse Files
            </button>
            <div className="upload-formats" style={{ marginTop: 20 }}>
              CSV · UTF-8 · Automatic schema detection
            </div>
          </div>

          {error && (
            <div className="alert alert-error" style={{ marginTop: 16 }}>
              {error}
            </div>
          )}
        </div>
      )}

      <div className="landing-steps">
        {steps.map((step, i) => (
          <div key={step.num} style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
            {i > 0 && <ChevronRight size={14} className="landing-step-arrow" />}
            <div className="landing-step">
              <div className="landing-step-num">{step.num}</div>
              <span>{step.label}</span>
            </div>
          </div>
        ))}
      </div>

      <div className="landing-features">
        {features.map(({ icon: Icon, title, desc }) => (
          <div key={title} className="feature-card">
            <Icon size={24} />
            <h3>{title}</h3>
            <p>{desc}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
