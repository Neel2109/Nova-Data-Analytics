import { NavLink, useLocation, useNavigate } from 'react-router-dom';
import { useDataset } from '../../context/DatasetContext';
import { uploadDataset } from '../../services/api';
import { useRef, useState } from 'react';
import {
  LayoutDashboard, Search, Settings, BarChart3, Activity,
  ShieldCheck, Eraser, Brain, Sparkles, FileText, Moon, HelpCircle, Upload, Loader2
} from 'lucide-react';

const navItems = [
  { id: 'overview',  path: '/overview',  label: 'Overview',       icon: LayoutDashboard },
  { id: 'findings',  path: '/findings',  label: 'Data Profile',   icon: Search },
  { id: 'quality',   path: '/quality',   label: 'Data Quality',   icon: ShieldCheck },
  { id: 'eda',       path: '/eda',       label: 'EDA & Charts',   icon: BarChart3 },
  { id: 'cleaning',  path: '/cleaning',  label: 'Data Cleaning',  icon: Eraser },
  { id: 'ml',        path: '/ml',        label: 'Machine Learning', icon: Brain },
  { id: 'ai',        path: '/ai',        label: 'AI Investigation', icon: Sparkles },
  { id: 'reports',   path: '/reports',   label: 'Reports',        icon: FileText },
  { id: 'settings',  path: '/settings',  label: 'Settings',       icon: Settings },
];

export default function Sidebar() {
  const { hasDataset, datasetInfo, setDatasetId, setDatasetInfo } = useDataset();
  const location = useLocation();
  const navigate = useNavigate();
  const fileInputRef = useRef(null);
  const [isUploading, setIsUploading] = useState(false);

  const handleFileUpload = async (event) => {
    const file = event.target.files?.[0];
    if (!file) return;

    setIsUploading(true);
    try {
      const result = await uploadDataset(file);
      setDatasetId(result.dataset_id);
      setDatasetInfo(result);
      navigate('/overview');
    } catch (err) {
      console.error(err);
      alert('Upload failed. Please try again.');
    } finally {
      setIsUploading(false);
      if (fileInputRef.current) fileInputRef.current.value = '';
    }
  };

  return (
    <aside className="sidebar">
      {/* Logo */}
      <div className="sidebar-header">
        <div className="sidebar-logo-icon">D</div>
        <div className="sidebar-brand">
          <h1>DataNova</h1>
          <div className="sidebar-brand-sub">Data Intelligence</div>
        </div>
      </div>

      {/* Upload Button */}
      <div style={{ padding: '20px 24px 0' }}>
        <input 
          type="file" 
          accept=".csv" 
          ref={fileInputRef} 
          style={{ display: 'none' }} 
          onChange={handleFileUpload} 
        />
        <button 
          className="btn btn-primary" 
          style={{ width: '100%' }} 
          onClick={() => fileInputRef.current?.click()}
          disabled={isUploading}
        >
          {isUploading ? <Loader2 size={16} className="spinner" /> : <Upload size={16} />}
          {isUploading ? 'Uploading...' : 'Upload CSV'}
        </button>
      </div>

      {/* Navigation */}
      <div className="sidebar-section-label" style={{ paddingTop: '24px' }}>Analytics</div>
      <nav className="sidebar-nav">
        {navItems.map(({ id, path, label, icon: Icon }) => (
          <NavLink
            key={id}
            to={path}
            className={({ isActive }) =>
              `sidebar-link ${isActive || (path === '/overview' && location.pathname === '/') ? 'active' : ''}`
            }
          >
            <Icon size={18} />
            <span>{label}</span>
          </NavLink>
        ))}
      </nav>

      {/* Widget */}
      {datasetInfo && (
        <div className="sidebar-widget">
          <div className="widget-circle">
            {datasetInfo.rows?.toLocaleString() || '0'}
          </div>
          <div className="widget-label">Total Rows</div>
        </div>
      )}

      {/* Footer */}
      <div className="sidebar-footer">
        <div className="sidebar-footer-icons">
          <Moon size={16} />
          <HelpCircle size={16} />
        </div>
      </div>
    </aside>
  );
}
