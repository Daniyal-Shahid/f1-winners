import React from 'react';
import { BarChart3, TrendingUp, TrendingDown } from 'lucide-react';

const SentimentVisuals = ({ sentiment }) => {
  const { sentiment_distribution, average_sentiment } = sentiment;
  
  // Convert percentages for visualization
  const positivePercent = Math.round(sentiment_distribution.positive * 100);
  const neutralPercent = Math.round(sentiment_distribution.neutral * 100);
  const negativePercent = Math.round(sentiment_distribution.negative * 100);

  // Determine the sentiment trend color and icon
  const getTrendInfo = () => {
    if (average_sentiment > 0.2) {
      return { color: 'text-status-success', icon: <TrendingUp className="w-6 h-6" /> };
    } else if (average_sentiment < -0.2) {
      return { color: 'text-status-danger', icon: <TrendingDown className="w-6 h-6" /> };
    }
    return { color: 'text-f1-gray', icon: <BarChart3 className="w-6 h-6" /> };
  };

  const trendInfo = getTrendInfo();

  return (
    <div className="space-y-6">
      {/* Sentiment Score Gauge */}
      <div className="bg-surface-card p-6 rounded-xl shadow-card">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-medium text-f1-dark">Overall Sentiment</h3>
          <span className={`${trendInfo.color}`}>{trendInfo.icon}</span>
        </div>
        <div className="relative h-4 bg-gray-200 rounded-full overflow-hidden">
          <div 
            className="absolute left-1/2 h-full w-1 bg-gray-400 z-10"
            style={{ transform: 'translateX(-50%)' }}
          />
          <div 
            className={`absolute h-full transition-all duration-500 ${
              average_sentiment >= 0 ? 'bg-status-success left-1/2' : 'bg-status-danger right-1/2'
            }`}
            style={{ 
              width: `${Math.abs(average_sentiment * 50)}%`,
            }}
          />
        </div>
        <div className="flex justify-between mt-2 text-sm">
          <span className="text-status-danger">-1.0</span>
          <span className="text-f1-gray font-medium">{average_sentiment.toFixed(2)}</span>
          <span className="text-status-success">+1.0</span>
        </div>
      </div>

      {/* Distribution Bar Chart */}
      <div className="bg-surface-card p-6 rounded-xl shadow-card">
        <h3 className="text-lg font-medium text-f1-dark mb-4">Sentiment Distribution</h3>
        <div className="space-y-4">
          {/* Positive Bar */}
          <div className="space-y-2">
            <div className="flex justify-between text-sm">
              <span className="text-f1-dark">Positive</span>
              <span className="text-status-success font-medium">{positivePercent}%</span>
            </div>
            <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
              <div 
                className="h-full bg-status-success transition-all duration-500"
                style={{ width: `${positivePercent}%` }}
              />
            </div>
          </div>

          {/* Neutral Bar */}
          <div className="space-y-2">
            <div className="flex justify-between text-sm">
              <span className="text-f1-dark">Neutral</span>
              <span className="text-f1-gray font-medium">{neutralPercent}%</span>
            </div>
            <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
              <div 
                className="h-full bg-f1-gray transition-all duration-500"
                style={{ width: `${neutralPercent}%` }}
              />
            </div>
          </div>

          {/* Negative Bar */}
          <div className="space-y-2">
            <div className="flex justify-between text-sm">
              <span className="text-f1-dark">Negative</span>
              <span className="text-status-danger font-medium">{negativePercent}%</span>
            </div>
            <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
              <div 
                className="h-full bg-status-danger transition-all duration-500"
                style={{ width: `${negativePercent}%` }}
              />
            </div>
          </div>
        </div>
      </div>

      {/* Time Distribution */}
      <div className="bg-surface-card p-6 rounded-xl shadow-card">
        <h3 className="text-lg font-medium text-f1-dark mb-4">Article Timeline</h3>
        <div className="flex items-center justify-between h-20">
          {Array.from({ length: 7 }).map((_, index) => {
            const height = Math.random() * 100; // This would be real data in production
            return (
              <div key={index} className="flex flex-col items-center flex-1">
                <div className="flex-1 w-full px-1">
                  <div 
                    className="w-full bg-accent-blue/20 rounded-t-sm"
                    style={{ height: `${height}%` }}
                  />
                </div>
                <span className="text-xs text-f1-gray mt-2">
                  {`D-${6-index}`}
                </span>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};

export default SentimentVisuals; 