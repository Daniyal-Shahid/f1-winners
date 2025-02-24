import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft } from 'lucide-react';
import { Line } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
} from 'chart.js';

// Register ChartJS components
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
);

const DriverAnalysis = () => {
  const { driver } = useParams();
  const navigate = useNavigate();
  const [analysis, setAnalysis] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchAnalysis = async () => {
      try {
        const response = await fetch(`/api/race-analysis/${encodeURIComponent(driver)}`);
        const data = await response.json();
        setAnalysis(data);
      } catch (error) {
        console.error('Error fetching analysis:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchAnalysis();
  }, [driver]);

  const lapTimesChart = analysis ? {
    labels: analysis.lap_times.lap_numbers,
    datasets: [{
      label: 'Lap Times',
      data: analysis.lap_times.lap_times,
      borderColor: 'rgb(255, 99, 132)',
      tension: 0.1
    }]
  } : null;

  const positionChart = analysis ? {
    labels: analysis.position_changes.lap_numbers,
    datasets: [{
      label: 'Position',
      data: analysis.position_changes.positions,
      borderColor: 'rgb(75, 192, 192)',
      tension: 0.1
    }]
  } : null;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-surface-card rounded-xl shadow-lg overflow-hidden border border-gray-100">
        <div className="bg-gradient-to-r from-f1-dark to-f1-carbon p-6">
          <button 
            onClick={() => navigate(-1)}
            className="text-white flex items-center gap-2 hover:text-accent-yellow transition-colors mb-4"
          >
            <ArrowLeft className="w-5 h-5" />
            Back to Results
          </button>
          <h2 className="text-2xl font-bold text-white">
            {decodeURIComponent(driver)} - Race Analysis
          </h2>
        </div>

        {loading ? (
          <div className="p-6">
            <p className="text-f1-gray">Loading analysis...</p>
          </div>
        ) : analysis ? (
          <div className="p-6 space-y-8">
            {/* Race Summary */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div className="bg-gray-50 p-4 rounded-lg">
                <h3 className="text-sm text-f1-gray mb-1">Final Position</h3>
                <p className="text-2xl font-bold">{analysis.race_summary.final_position}</p>
              </div>
              <div className="bg-gray-50 p-4 rounded-lg">
                <h3 className="text-sm text-f1-gray mb-1">Grid Position</h3>
                <p className="text-2xl font-bold">{analysis.race_summary.grid}</p>
              </div>
              <div className="bg-gray-50 p-4 rounded-lg">
                <h3 className="text-sm text-f1-gray mb-1">Points</h3>
                <p className="text-2xl font-bold">{analysis.race_summary.points}</p>
              </div>
              <div className="bg-gray-50 p-4 rounded-lg">
                <h3 className="text-sm text-f1-gray mb-1">Status</h3>
                <p className="text-2xl font-bold">{analysis.race_summary.status}</p>
              </div>
            </div>

            {/* Lap Times Chart */}
            <div className="bg-white p-6 rounded-lg shadow">
              <h3 className="text-lg font-bold mb-4">Lap Times Progression</h3>
              {lapTimesChart && (
                <Line 
                  data={lapTimesChart}
                  options={{
                    responsive: true,
                    scales: {
                      y: {
                        reverse: true,
                        title: {
                          display: true,
                          text: 'Lap Time (seconds)'
                        }
                      }
                    }
                  }}
                />
              )}
            </div>

            {/* Position Changes Chart */}
            <div className="bg-white p-6 rounded-lg shadow">
              <h3 className="text-lg font-bold mb-4">Position Changes</h3>
              {positionChart && (
                <Line 
                  data={positionChart}
                  options={{
                    responsive: true,
                    scales: {
                      y: {
                        reverse: true,
                        title: {
                          display: true,
                          text: 'Position'
                        }
                      }
                    }
                  }}
                />
              )}
            </div>

            {/* Sector Analysis */}
            <div className="bg-white p-6 rounded-lg shadow">
              <h3 className="text-lg font-bold mb-4">Sector Analysis</h3>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {Object.entries(analysis.sector_performance).map(([sector, data]) => (
                  <div key={sector} className="bg-gray-50 p-4 rounded-lg">
                    <h4 className="font-medium mb-2">{sector.replace('_', ' ').toUpperCase()}</h4>
                    <div className="space-y-2">
                      <p className="text-sm">Best: {data.best.toFixed(3)}s</p>
                      <p className="text-sm">Average: {data.average.toFixed(3)}s</p>
                      <p className="text-sm">Consistency: {data.consistency.toFixed(3)}s</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Tyre Performance */}
            <div className="bg-white p-6 rounded-lg shadow">
              <h3 className="text-lg font-bold mb-4">Tyre Performance</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {Object.entries(analysis.tyre_performance).map(([compound, data]) => (
                  <div key={compound} className="bg-gray-50 p-4 rounded-lg">
                    <h4 className="font-medium mb-2">{compound}</h4>
                    <div className="space-y-2">
                      <p className="text-sm">Average Pace: {data.average_pace.toFixed(3)}s</p>
                      <p className="text-sm">Degradation: {data.degradation.toFixed(3)}s/lap</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        ) : (
          <div className="p-6">
            <p className="text-f1-gray">Error loading analysis data</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default DriverAnalysis; 