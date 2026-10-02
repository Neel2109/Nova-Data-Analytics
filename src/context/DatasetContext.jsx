import { createContext, useContext, useState } from 'react';

const DatasetContext = createContext(null);

export function DatasetProvider({ children }) {
  const [datasetId, setDatasetId] = useState(null);
  const [datasetInfo, setDatasetInfo] = useState(null);
  const [loading, setLoading] = useState(false);

  const value = {
    datasetId, setDatasetId,
    datasetInfo, setDatasetInfo,
    loading, setLoading,
    hasDataset: !!datasetId,
  };

  return (
    <DatasetContext.Provider value={value}>
      {children}
    </DatasetContext.Provider>
  );
}

export const useDataset = () => {
  const ctx = useContext(DatasetContext);
  if (!ctx) throw new Error('useDataset must be used within DatasetProvider');
  return ctx;
};
