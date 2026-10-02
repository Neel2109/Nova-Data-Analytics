import Plot from 'react-plotly.js';

export default function PlotlyChart({ data, style }) {
  if (!data || !data.data) return null;

  return (
    <div className="chart-container" style={style}>
      <Plot
        data={data.data}
        layout={{
          ...data.layout,
          autosize: true,
          margin: { l: 50, r: 30, t: 50, b: 50 },
        }}
        config={{
          responsive: true,
          displayModeBar: true,
          displaylogo: false,
          modeBarButtonsToRemove: ['lasso2d', 'select2d'],
        }}
        useResizeHandler
        style={{ width: '100%', height: '100%' }}
      />
    </div>
  );
}
