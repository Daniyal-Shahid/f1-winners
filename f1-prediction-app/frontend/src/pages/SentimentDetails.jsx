import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, TrendingUp, TrendingDown, MessageCircle, BarChart3 } from 'lucide-react';
import axios from 'axios';
import SentimentVisuals from '../components/SentimentVisuals';

const SentimentDetails = () => {
  const { driver } = useParams();
  const navigate = useNavigate();
  const [sentimentData, setSentimentData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const response = await axios.get(`http://127.0.0.1:5000/api/driver-sentiment/${driver}`);
        setSentimentData(response.data);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [driver]);

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="animate-pulse text-f1-gray">Loading analysis...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-status-danger">Error: {error}</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-gradient-to-r from-f1-dark to-f1-carbon text-white py-8 mb-8">
        <div className="container mx-auto px-4">
          <button 
            onClick={() => navigate(-1)}
            className="flex items-center gap-2 text-f1-gray hover:text-white transition-colors mb-4"
          >
            <ArrowLeft className="w-4 h-4" />
            Back to Dashboard
          </button>
          <h1 className="text-3xl font-display">{driver} Media Coverage Analysis</h1>
        </div>
      </div>

      <div className="container mx-auto px-4 pb-12">
        <div className="mb-12">
          <SentimentVisuals sentiment={sentimentData} />
        </div>

        {/* Summary Statistics */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div className="bg-surface-card p-6 rounded-xl shadow-card">
            <div className="text-sm text-f1-gray mb-2">Articles Analyzed</div>
            <div className="text-3xl font-bold text-f1-dark">{sentimentData.articles_analyzed}</div>
          </div>
          <div className="bg-surface-card p-6 rounded-xl shadow-card">
            <div className="text-sm text-f1-gray mb-2">Average Sentiment</div>
            <div className="text-3xl font-bold text-f1-dark">{sentimentData.average_sentiment.toFixed(2)}</div>
          </div>
          <div className="bg-surface-card p-6 rounded-xl shadow-card">
            <div className="text-sm text-f1-gray mb-2">Time Period</div>
            <div className="text-3xl font-bold text-f1-dark">{sentimentData.time_period}</div>
          </div>
          <div className="bg-surface-card p-6 rounded-xl shadow-card">
            <div className="text-sm text-f1-gray mb-2">Total Sources</div>
            <div className="text-3xl font-bold text-f1-dark">{sentimentData.total_sources}</div>
          </div>
        </div>

        {/* Positive Articles */}
        <div className="bg-green-50 p-6 rounded-lg">
          <h2 className="text-xl font-semibold text-green-700 mb-4">
            Positive Coverage ({Math.round(sentimentData.sentiment_distribution.positive * 100)}%)
          </h2>
          <div className="space-y-4">
            {sentimentData.positive_articles.map((article, index) => (
              <div key={index} className="bg-white p-4 rounded shadow">
                <h3 className="font-medium">{article.title}</h3>
                <p className="text-sm text-gray-500 mt-2">
                  Source: {article.source} | Sentiment: {article.sentiment.toFixed(2)}
                </p>
              </div>
            ))}
          </div>
        </div>

        {/* Neutral Articles */}
        <div className="bg-gray-50 p-6 rounded-lg">
          <h2 className="text-xl font-semibold text-gray-700 mb-4">
            Neutral Coverage ({Math.round(sentimentData.sentiment_distribution.neutral * 100)}%)
          </h2>
          <div className="space-y-4">
            {sentimentData.neutral_articles.map((article, index) => (
              <div key={index} className="bg-white p-4 rounded shadow">
                <h3 className="font-medium">{article.title}</h3>
                <p className="text-sm text-gray-500 mt-2">
                  Source: {article.source} | Sentiment: {article.sentiment.toFixed(2)}
                </p>
              </div>
            ))}
          </div>
        </div>

        {/* Negative Articles */}
        <div className="bg-red-50 p-6 rounded-lg">
          <h2 className="text-xl font-semibold text-red-700 mb-4">
            Negative Coverage ({Math.round(sentimentData.sentiment_distribution.negative * 100)}%)
          </h2>
          <div className="space-y-4">
            {sentimentData.negative_articles.map((article, index) => (
              <div key={index} className="bg-white p-4 rounded shadow">
                <h3 className="font-medium">{article.title}</h3>
                <p className="text-sm text-gray-500 mt-2">
                  Source: {article.source} | Sentiment: {article.sentiment.toFixed(2)}
                </p>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default SentimentDetails; 