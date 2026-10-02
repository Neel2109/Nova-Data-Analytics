import { BrowserRouter, Routes, Route, useLocation } from 'react-router-dom';
import { DatasetProvider, useDataset } from './context/DatasetContext';
import Sidebar from './components/layout/Sidebar';
import LandingPage from './pages/LandingPage';
import OverviewPage from './pages/OverviewPage';
import FindingsPage from './pages/FindingsPage';
import QualityPage from './pages/QualityPage';
import CleaningPage from './pages/CleaningPage';
import EDAPage from './pages/EDAPage';
import MLPage from './pages/MLPage';
import AIPage from './pages/AIPage';
import ReportsPage from './pages/ReportsPage';
import SettingsPage from './pages/SettingsPage';

function AppLayout() {
  const location = useLocation();
  const { hasDataset } = useDataset();
  const isLanding = location.pathname === '/' && !hasDataset;

  if (isLanding) {
    return <LandingPage />;
  }

  return (
    <div className="app-layout">
      <Sidebar />
      <main className="app-main">
        <Routes>
          <Route path="/" element={<LandingPage />} />
          <Route path="/overview" element={<OverviewPage />} />
          <Route path="/findings" element={<FindingsPage />} />
          <Route path="/quality" element={<QualityPage />} />
          <Route path="/cleaning" element={<CleaningPage />} />
          <Route path="/eda" element={<EDAPage />} />
          <Route path="/ml" element={<MLPage />} />
          <Route path="/ai" element={<AIPage />} />
          <Route path="/reports" element={<ReportsPage />} />
          <Route path="/settings" element={<SettingsPage />} />
        </Routes>
      </main>
    </div>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <DatasetProvider>
        <AppLayout />
      </DatasetProvider>
    </BrowserRouter>
  );
}
