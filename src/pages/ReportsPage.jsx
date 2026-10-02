import { useDataset } from '../context/DatasetContext';
import { exportCSV, exportJSON, exportExcel } from '../services/api';
import Topbar from '../components/layout/Topbar';
import { FileText, FileSpreadsheet, FileCode, Download, CheckCircle2 } from 'lucide-react';

export default function ReportsPage() {
  const { datasetId } = useDataset();

  const handleExport = (type) => {
    if (!datasetId) return;
    let url;
    if (type === 'csv') url = exportCSV(datasetId);
    if (type === 'json') url = exportJSON(datasetId);
    if (type === 'excel') url = exportExcel(datasetId);
    if (url) window.open(url, '_blank');
  };

  return (
    <>
      <Topbar title="Reports & Export" subtitle="Download" />
      <div className="content fade-in">
        
        <div className="grid grid-3">
          <div className="stat-card cyan" style={{ padding: 32, alignItems: 'center', textAlign: 'center', cursor: 'pointer' }} onClick={() => handleExport('excel')}>
            <FileSpreadsheet size={48} style={{ color: 'var(--neon-cyan)', marginBottom: 16 }} />
            <h3 style={{ fontSize: 18, color: '#fff', marginBottom: 8 }}>Excel Report</h3>
            <p style={{ fontSize: 12, color: 'var(--text-secondary)', marginBottom: 20 }}>Comprehensive multi-sheet workbook with data dictionary, stats, and insights.</p>
            <button className="btn btn-primary"><Download size={16} /> Download .xlsx</button>
          </div>

          <div className="stat-card pink" style={{ padding: 32, alignItems: 'center', textAlign: 'center', cursor: 'pointer' }} onClick={() => handleExport('csv')}>
            <FileText size={48} style={{ color: 'var(--neon-pink)', marginBottom: 16 }} />
            <h3 style={{ fontSize: 18, color: '#fff', marginBottom: 8 }}>Cleaned CSV</h3>
            <p style={{ fontSize: 12, color: 'var(--text-secondary)', marginBottom: 20 }}>Export the processed and cleaned dataset as a standard CSV file.</p>
            <button className="btn btn-primary" style={{ background: 'var(--neon-pink)' }}><Download size={16} /> Download .csv</button>
          </div>

          <div className="stat-card purple" style={{ padding: 32, alignItems: 'center', textAlign: 'center', cursor: 'pointer' }} onClick={() => handleExport('json')}>
            <FileCode size={48} style={{ color: 'var(--neon-purple)', marginBottom: 16 }} />
            <h3 style={{ fontSize: 18, color: '#fff', marginBottom: 8 }}>JSON Analysis</h3>
            <p style={{ fontSize: 12, color: 'var(--text-secondary)', marginBottom: 20 }}>Full raw profiling data, correlations, and insights in structured JSON format.</p>
            <button className="btn btn-primary" style={{ background: 'var(--neon-purple)' }}><Download size={16} /> Download .json</button>
          </div>
        </div>

        <div className="card" style={{ marginTop: 24 }}>
          <div className="card-header"><span className="card-title">What's included in the Excel Report?</span></div>
          <div className="grid grid-3">
            <div>
              <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 8 }}>
                <CheckCircle2 size={16} style={{ color: 'var(--neon-green)' }} />
                <strong style={{ color: '#fff' }}>Dataset Sample</strong>
              </div>
              <p style={{ fontSize: 12, color: 'var(--text-secondary)', paddingLeft: 24 }}>First 10,000 rows of the cleaned dataset for quick reference.</p>
            </div>
            <div>
              <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 8 }}>
                <CheckCircle2 size={16} style={{ color: 'var(--neon-green)' }} />
                <strong style={{ color: '#fff' }}>Data Dictionary</strong>
              </div>
              <p style={{ fontSize: 12, color: 'var(--text-secondary)', paddingLeft: 24 }}>Detailed profiling for every column, including missing %, unique counts, and basic stats.</p>
            </div>
            <div>
              <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 8 }}>
                <CheckCircle2 size={16} style={{ color: 'var(--neon-green)' }} />
                <strong style={{ color: '#fff' }}>Detailed Statistics</strong>
              </div>
              <p style={{ fontSize: 12, color: 'var(--text-secondary)', paddingLeft: 24 }}>Advanced numerical and categorical statistics broken down into separate sheets.</p>
            </div>
            <div>
              <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 8 }}>
                <CheckCircle2 size={16} style={{ color: 'var(--neon-green)' }} />
                <strong style={{ color: '#fff' }}>AI Insights</strong>
              </div>
              <p style={{ fontSize: 12, color: 'var(--text-secondary)', paddingLeft: 24 }}>List of automated findings and warnings about data quality and patterns.</p>
            </div>
          </div>
        </div>

      </div>
    </>
  );
}
