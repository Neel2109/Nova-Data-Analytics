import { useState } from 'react';
import { useDataset } from '../context/DatasetContext';
import { queryDataset } from '../services/api';
import Topbar from '../components/layout/Topbar';
import PlotlyChart from '../components/charts/PlotlyChart';
import { Search, Loader2, Sparkles, Send, Bot, User } from 'lucide-react';

export default function AIPage() {
  const { datasetId } = useDataset();
  const [query, setQuery] = useState('');
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e?.preventDefault();
    if (!query.trim() || !datasetId || loading) return;

    const userMsg = { role: 'user', content: query };
    setHistory(prev => [...prev, userMsg]);
    setQuery('');
    setLoading(true);

    try {
      const res = await queryDataset(datasetId, query);
      setHistory(prev => [...prev, { role: 'bot', ...res }]);
    } catch (err) {
      setHistory(prev => [...prev, { role: 'bot', error: 'Failed to process query. Please try again.' }]);
    }
    setLoading(false);
  };

  const suggestions = [
    "Are there any missing values?",
    "What are the top categories?",
    "Are there any outliers?",
    "Show the distribution of the largest column",
    "Find strong correlations"
  ];

  return (
    <>
      <Topbar title="AI Investigation" subtitle="Natural Language Queries" />
      <div className="content fade-in" style={{ display: 'flex', flexDirection: 'column', height: 'calc(100vh - 100px)' }}>
        
        {/* Chat History */}
        <div className="card" style={{ flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
          <div className="card-header">
            <span className="card-title">Investigation Chat</span>
            <span className="badge badge-purple"><Sparkles size={12} /> AI Powered</span>
          </div>

          <div style={{ flex: 1, overflowY: 'auto', padding: '0 8px 16px', display: 'flex', flexDirection: 'column', gap: 24 }}>
            {history.length === 0 ? (
              <div className="empty-state" style={{ margin: 'auto' }}>
                <Bot size={48} style={{ color: 'var(--neon-purple)', marginBottom: 16 }} />
                <h3>Ask me anything about your data</h3>
                <p>Try one of the suggestions below or type your own question.</p>
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8, justifyContent: 'center', marginTop: 24 }}>
                  {suggestions.map((s, i) => (
                    <button key={i} className="btn btn-secondary btn-sm" onClick={() => { setQuery(s); }}>
                      {s}
                    </button>
                  ))}
                </div>
              </div>
            ) : (
              history.map((msg, i) => (
                <div key={i} style={{ display: 'flex', gap: 16, flexDirection: msg.role === 'user' ? 'row-reverse' : 'row' }}>
                  <div className="btn-icon" style={{ flexShrink: 0, background: msg.role === 'user' ? 'var(--neon-cyan)' : 'var(--neon-purple)', color: '#fff', border: 'none' }}>
                    {msg.role === 'user' ? <User size={18} /> : <Bot size={18} />}
                  </div>
                  <div style={{ 
                    background: msg.role === 'user' ? 'var(--bg-elevated)' : 'rgba(168, 85, 247, 0.08)',
                    border: msg.role === 'bot' ? '1px solid rgba(168, 85, 247, 0.2)' : '1px solid var(--border)',
                    padding: '16px 20px', borderRadius: 'var(--radius-lg)', maxWidth: '80%',
                    borderTopRightRadius: msg.role === 'user' ? 0 : 'var(--radius-lg)',
                    borderTopLeftRadius: msg.role === 'bot' ? 0 : 'var(--radius-lg)'
                  }}>
                    {msg.role === 'user' ? (
                      <div style={{ color: '#fff', fontSize: 14 }}>{msg.content}</div>
                    ) : (
                      <div className="fade-in">
                        {msg.error ? (
                          <div style={{ color: 'var(--neon-red)' }}>{msg.error}</div>
                        ) : (
                          <>
                            <div style={{ color: '#fff', fontSize: 14, lineHeight: 1.6, marginBottom: msg.chart || msg.data ? 16 : 0 }}>{msg.answer}</div>
                            {msg.chart && (
                              <div style={{ height: 280, marginTop: 16, background: 'var(--bg-surface)', padding: 10, borderRadius: 'var(--radius-md)', border: '1px solid var(--border)' }}>
                                <PlotlyChart data={msg.chart} />
                              </div>
                            )}
                            {msg.data && !msg.chart && (
                              <pre style={{ background: 'var(--bg-base)', padding: 12, borderRadius: 'var(--radius-sm)', fontSize: 12, color: 'var(--text-secondary)', overflowX: 'auto', marginTop: 12 }}>
                                {JSON.stringify(msg.data, null, 2)}
                              </pre>
                            )}
                          </>
                        )}
                      </div>
                    )}
                  </div>
                </div>
              ))
            )}
            {loading && (
              <div style={{ display: 'flex', gap: 16 }}>
                <div className="btn-icon" style={{ flexShrink: 0, background: 'var(--neon-purple)', color: '#fff', border: 'none' }}><Bot size={18} /></div>
                <div style={{ padding: '16px 20px', borderRadius: 'var(--radius-lg)', background: 'rgba(168, 85, 247, 0.08)', border: '1px solid rgba(168, 85, 247, 0.2)', borderTopLeftRadius: 0 }}>
                  <Loader2 size={18} className="spinner" style={{ color: 'var(--neon-purple)' }} />
                </div>
              </div>
            )}
          </div>

          <form onSubmit={handleSubmit} style={{ display: 'flex', gap: 12, marginTop: 16, borderTop: '1px solid var(--border)', paddingTop: 16 }}>
            <input 
              type="text" 
              className="form-input" 
              style={{ flex: 1, padding: '12px 16px', borderRadius: '24px' }}
              placeholder="Ask a question about your dataset..." 
              value={query} 
              onChange={e => setQuery(e.target.value)}
              disabled={loading}
            />
            <button type="submit" className="btn btn-primary" style={{ borderRadius: '24px', padding: '10px 24px' }} disabled={!query.trim() || loading}>
              <Send size={16} /> Send
            </button>
          </form>
        </div>

      </div>
    </>
  );
}
