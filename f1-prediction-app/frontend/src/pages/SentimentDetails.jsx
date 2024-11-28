import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import axios from 'axios';

const SentimentDetails = () => {
  const { driver } = useParams();
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

  if (loading) return <div>Loading...</div>;
  if (error) return <div>Error: {error}</div>;
  if (!sentimentData) return <div>No data available</div>;

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-8">{driver} Media Coverage Analysis</h1>
      
      <div className="grid md:grid-cols-3 gap-8">
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

      {/* Add summary statistics */}
      <div className="mt-8 bg-white p-6 rounded-lg shadow">
        <h2 className="text-xl font-semibold mb-4">Analysis Summary</h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div>
            <p className="text-gray-600">Articles Analyzed</p>
            <p className="text-2xl font-bold">{sentimentData.articles_analyzed}</p>
          </div>
          <div>
            <p className="text-gray-600">Average Sentiment</p>
            <p className="text-2xl font-bold">{sentimentData.average_sentiment.toFixed(2)}</p>
          </div>
          <div>
            <p className="text-gray-600">Time Period</p>
            <p className="text-2xl font-bold">{sentimentData.time_period}</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SentimentDetails; 