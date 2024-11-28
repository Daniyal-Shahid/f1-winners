import React from 'react';
import { MessageCircle, TrendingUp, TrendingDown, ExternalLink } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

const SentimentCard = ({ sentiment, driver }) => {
  const navigate = useNavigate();

  if (!sentiment) return null;

  // Helper function to get sentiment class and icon
  const getSentimentInfo = (score) => {
    if (score > 0.2) {
      return {
        class: 'text-green-600 bg-green-50',
        icon: <TrendingUp className="w-5 h-5" />,
        label: 'Positive'
      };
    } else if (score < -0.2) {
      return {
        class: 'text-red-600 bg-red-50',
        icon: <TrendingDown className="w-5 h-5" />,
        label: 'Negative'
      };
    }
    return {
      class: 'text-gray-600 bg-gray-50',
      icon: <MessageCircle className="w-5 h-5" />,
      label: 'Neutral'
    };
  };

  const sentimentInfo = getSentimentInfo(sentiment.average_sentiment);

  return (
    <div className="bg-white rounded-lg shadow-md p-4 border border-gray-200">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold">{driver} Media Sentiment</h3>
        <div className={`flex items-center gap-2 px-3 py-1 rounded-full ${sentimentInfo.class}`}>
          {sentimentInfo.icon}
          <span className="font-medium">{sentimentInfo.label}</span>
        </div>
      </div>

      <div className="space-y-4">
        {/* Analysis Details */}
        <div className="text-sm text-gray-500">
          <p>Based on {sentiment.articles_analyzed || 0} articles from the {sentiment.time_period}</p>
        </div>

        {/* Sentiment Distribution */}
        <div className="flex justify-between text-sm">
          <div className="text-center">
            <div className="font-medium text-green-600">
              {Math.round(sentiment.sentiment_distribution.positive * 100)}%
            </div>
            <div className="text-gray-500">Positive</div>
          </div>
          <div className="text-center">
            <div className="font-medium text-gray-600">
              {Math.round(sentiment.sentiment_distribution.neutral * 100)}%
            </div>
            <div className="text-gray-500">Neutral</div>
          </div>
          <div className="text-center">
            <div className="font-medium text-red-600">
              {Math.round(sentiment.sentiment_distribution.negative * 100)}%
            </div>
            <div className="text-gray-500">Negative</div>
          </div>
        </div>

        {/* Recent Headlines */}
        {sentiment.recent_headlines && sentiment.recent_headlines.length > 0 ? (
          <div className="mt-4">
            <h4 className="font-medium mb-2">Recent Headlines</h4>
            <ul className="space-y-2">
              {sentiment.recent_headlines.map((headline, index) => (
                <li key={index} className="text-sm text-gray-600 flex items-start gap-2">
                  <MessageCircle className="w-4 h-4 mt-1 flex-shrink-0" />
                  <span>{headline.title}</span>
                </li>
              ))}
            </ul>
          </div>
        ) : (
          <div className="text-sm text-gray-500 mt-4">
            No recent headlines available
          </div>
        )}
      </div>

      {/* Add View More button */}
      <div className="mt-4 text-center">
        <button
          onClick={() => navigate(`/sentiment/${encodeURIComponent(driver)}`)}
          className="inline-flex items-center gap-2 text-blue-600 hover:text-blue-800"
        >
          <span>View All Articles</span>
          <ExternalLink className="w-4 h-4" />
        </button>
      </div>
    </div>
  );
};

export default SentimentCard; 