import React from 'react';
import { MessageCircle, TrendingUp, TrendingDown, ExternalLink } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { getTeamColorClass, getTeamBgColorClass } from '../utils/teamColors';

const SentimentCard = ({ sentiment, driver, team }) => {
  const navigate = useNavigate();

  if (!sentiment) return null;

  // Helper function to get sentiment class and icon
  const getSentimentInfo = (score) => {
    if (score > 0.2) {
      return {
        class: 'text-status-success bg-status-success/10',
        icon: <TrendingUp className="w-5 h-5" />,
        label: 'Positive'
      };
    } else if (score < -0.2) {
      return {
        class: 'text-status-danger bg-status-danger/10',
        icon: <TrendingDown className="w-5 h-5" />,
        label: 'Negative'
      };
    }
    return {
      class: 'text-f1-gray bg-status-neutral',
      icon: <MessageCircle className="w-5 h-5" />,
      label: 'Neutral'
    };
  };

  const sentimentInfo = getSentimentInfo(sentiment.average_sentiment);

  return (
    <div className="bg-surface-card rounded-xl shadow-card hover:shadow-hover transition-shadow duration-300 overflow-hidden border-l-4 border-accent-blue">
      <div className="p-6">
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <div>
            <h3 className="text-xl font-display text-f1-dark">{driver}</h3>
            {team && (
              <span className={`inline-block px-2 py-1 rounded ${getTeamBgColorClass(team)} ${getTeamColorClass(team)} text-sm font-medium mt-1`}>
                {team}
              </span>
            )}
          </div>
          <div className={`flex items-center gap-2 px-4 py-2 rounded-full ${sentimentInfo.class}`}>
            {sentimentInfo.icon}
            <span className="font-medium">{sentimentInfo.label}</span>
          </div>
        </div>

        {/* Analysis Stats */}
        <div className="bg-gray-50 rounded-lg p-4 mb-6">
          <div className="text-sm text-f1-gray mb-4">
            Analysis based on {sentiment.articles_analyzed || 0} articles from the {sentiment.time_period}
          </div>
          
          {/* Sentiment Distribution */}
          <div className="grid grid-cols-3 gap-4">
            <div className="text-center p-3 bg-white rounded-lg shadow-sm">
              <div className="font-medium text-status-success text-lg">
                {Math.round(sentiment.sentiment_distribution.positive * 100)}%
              </div>
              <div className="text-sm text-f1-gray">Positive</div>
            </div>
            <div className="text-center p-3 bg-white rounded-lg shadow-sm">
              <div className="font-medium text-f1-gray text-lg">
                {Math.round(sentiment.sentiment_distribution.neutral * 100)}%
              </div>
              <div className="text-sm text-f1-gray">Neutral</div>
            </div>
            <div className="text-center p-3 bg-white rounded-lg shadow-sm">
              <div className="font-medium text-status-danger text-lg">
                {Math.round(sentiment.sentiment_distribution.negative * 100)}%
              </div>
              <div className="text-sm text-f1-gray">Negative</div>
            </div>
          </div>
        </div>

        {/* Recent Headlines */}
        {sentiment.recent_headlines && sentiment.recent_headlines.length > 0 ? (
          <div className="space-y-3">
            <h4 className="font-medium text-f1-dark">Recent Headlines</h4>
            <div className="space-y-2">
              {sentiment.recent_headlines.map((headline, index) => (
                <div 
                  key={index} 
                  className="flex items-start gap-2 p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
                >
                  <MessageCircle className="w-4 h-4 mt-1 flex-shrink-0 text-accent-blue" />
                  <span className="text-sm text-f1-dark">{headline.title}</span>
                </div>
              ))}
            </div>
          </div>
        ) : (
          <div className="text-sm text-f1-gray bg-gray-50 p-4 rounded-lg">
            No recent headlines available
          </div>
        )}

        {/* View More Button */}
        <div className="mt-6 text-center">
          <button
            onClick={() => navigate(`/sentiment/${encodeURIComponent(driver)}`)}
            className="inline-flex items-center gap-2 px-6 py-2 bg-gradient-to-r from-f1-dark to-f1-carbon text-white rounded-full hover:opacity-90 transition-opacity duration-300"
          >
            <span>View All Articles</span>
            <ExternalLink className="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  );
};

export default SentimentCard; 