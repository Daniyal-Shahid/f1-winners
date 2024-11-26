import React, { useState, useEffect } from 'react';
import { Trophy, Timer, Flag, AlertCircle, Calendar, Dot } from 'lucide-react';
import axios from 'axios';
import { getNextRace, getLastRace } from '../utils/raceCalendar';
import ChampionshipStatus from './ChampionshipStatus';

const F1Dashboard = () => {
  const [prediction, setPrediction] = useState(null);
  const [lastRaceResults, setLastRaceResults] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const nextRace = getNextRace();
  const lastRace = getLastRace();
  const [championshipData, setChampionshipData] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        setError(null);
        
        // Fetch data from both endpoints concurrently
        const [predictionRes, lastRaceRes, championshipRes] = await Promise.all([
          axios.get('http://127.0.0.1:5000/api/prediction'),
          axios.get('http://127.0.0.1:5000/api/last-race'),
          axios.get('http://127.0.0.1:5000/api/championship')
        ]);

        console.log('Prediction Response:', predictionRes.data);
        console.log('Last Race Response:', lastRaceRes.data);

        if (predictionRes.data.warning) {
          setError(predictionRes.data.warning);
          setPrediction(null);
        } else if (predictionRes.data.message) {
          setError(predictionRes.data.message);
          setPrediction(null);
        } else if (predictionRes.data.prediction) {
          setPrediction(predictionRes.data.prediction);
        } else {
          setError('Invalid prediction data format');
        }

        if (lastRaceRes.data) {
          // Merge the last race name from our calendar with the results
          setLastRaceResults({
            ...lastRaceRes.data,
            name: lastRace.name // Use the name from our calendar
          });
        }

        if (championshipRes.data) {
          setChampionshipData(championshipRes.data);
        }
      } catch (err) {
        console.error('Error fetching data:', err);
        setError('Failed to fetch F1 data. Please try again later.');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [lastRace.name]);

  // Debug render state
  console.log('Current State:', {
    loading,
    error,
    prediction,
    lastRaceResults
  });

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-gray-900"></div>
      </div>
    );
  }

  // Show error state
  if (error) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="bg-yellow-50 border border-yellow-200 text-yellow-700 px-4 py-3 rounded relative" role="alert">
          <strong className="font-bold">Note: </strong>
          <span className="block sm:inline">{error}</span>
        </div>
      </div>
    );
  }

  // Show loading state if either prediction or lastRaceResults is not available
  if (!prediction && !lastRaceResults) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="bg-yellow-50 border border-yellow-200 text-yellow-700 px-4 py-3 rounded relative" role="alert">
          <strong className="font-bold">No data available. </strong>
          <span className="block sm:inline">Please try again later.</span>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">F1 Race Predictions</h1>
          <div className="flex items-center justify-center gap-2 text-gray-600">
            <Calendar className="w-5 h-5" />
            <span>Next Race: {nextRace.name} - {new Date(nextRace.date).toLocaleDateString()}</span>
          </div>
        </div>
        
        {/* Prediction Cards */}
        {prediction && (
          <div className="grid lg:grid-cols-2 gap-8 mb-12">
            {/* Qualifying Prediction Card */}
            {prediction.qualifying && (
              <div className="bg-white rounded-xl shadow-lg overflow-hidden border border-purple-100 transform transition-all hover:scale-[1.02]">
                <div className="bg-purple-50 px-6 py-4">
                  <h2 className="text-xl font-bold flex items-center gap-2 text-purple-900">
                    <Timer className="text-purple-500" />
                    Qualifying Prediction for {nextRace.name}
                  </h2>
                </div>
                <div className="p-6 space-y-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <h3 className="text-2xl font-bold text-gray-900">{prediction.qualifying.driver}</h3>
                      <p className="text-purple-600 font-medium">{prediction.qualifying.team}</p>
                    </div>
                    <div className="bg-purple-50 px-4 py-2 rounded-full">
                      <span className="text-purple-700 font-semibold">
                        {prediction.qualifying.confidence}% Confidence
                      </span>
                    </div>
                  </div>
                  {prediction.qualifying.reasons && prediction.qualifying.reasons.length > 0 && (
                    <div>
                      <h4 className="font-semibold mb-2">Why we predict this pole position:</h4>
                      <ul className="space-y-2">
                        {prediction.qualifying.reasons.map((reason, index) => (
                          <li key={index} className="flex items-start gap-2">
                            <AlertCircle className="w-5 h-5 text-purple-500 mt-1 flex-shrink-0" />
                            <span>{reason}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* Race Prediction Card */}
            {prediction.race && (
              <div className="bg-white rounded-xl shadow-lg overflow-hidden border border-yellow-100 transform transition-all hover:scale-[1.02]">
                <div className="bg-yellow-50 px-6 py-4">
                  <h2 className="text-xl font-bold flex items-center gap-2 text-yellow-900">
                    <Trophy className="text-yellow-500" />
                    Race Winner Prediction for {nextRace.name}
                  </h2>
                </div>
                <div className="p-6 space-y-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <h3 className="text-2xl font-bold text-gray-900">{prediction.race.driver}</h3>
                      <p className="text-yellow-600 font-medium">{prediction.race.team}</p>
                    </div>
                    <div className="bg-yellow-50 px-4 py-2 rounded-full">
                      <span className="text-yellow-700 font-semibold">
                        {prediction.race.confidence}% Confidence
                      </span>
                    </div>
                  </div>
                  {prediction.race.reasons && prediction.race.reasons.length > 0 && (
                    <div>
                      <h4 className="font-semibold mb-2">Why we predict this win:</h4>
                      <ul className="space-y-2">
                        {prediction.race.reasons.map((reason, index) => (
                          <li key={index} className="flex items-start gap-2">
                            <AlertCircle className="w-5 h-5 text-blue-500 mt-1 flex-shrink-0" />
                            <span>{reason}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>
        )}

        {championshipData && (
          <div className="mb-8">
            <ChampionshipStatus championshipData={championshipData} />
          </div>
        )}

        {/* Last Race Results Card */}
        {lastRaceResults && (
          <div className="bg-white rounded-xl shadow-lg overflow-hidden border border-red-100">
            <div className="bg-red-50 px-6 py-4">
              <h2 className="text-xl font-bold flex items-center gap-2 text-red-900">
                <Flag className="text-red-500" />
                {lastRaceResults.name} - Results
              </h2>
            </div>
            <div className="space-y-6">
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="bg-gray-50">
                      <th className="p-4 text-left">Position</th>
                      <th className="p-4 text-left">Driver</th>
                      <th className="p-4 text-left">Team</th>
                      <th className="p-4 text-left">Points</th>
                    </tr>
                  </thead>
                  <tbody>
                    {lastRaceResults.results.map((result) => (
                      <tr key={result.position} className="border-t">
                        <td className="p-4 text-left">{result.position}</td>
                        <td className="p-4 text-left font-medium">{result.driver}</td>
                        <td className="p-4 text-left">{result.team}</td>
                        <td className="p-4 text-left">{result.points}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
              
              <div>
                <h4 className="font-semibold mb-2">Race Highlights:</h4>
                <ul className="space-y-2">
                  {lastRaceResults.highlights.map((highlight, index) => (
                    <li key={index} className="flex items-start gap-2">
                      {/* <Timer className="w-5 h-5 text-purple-500 mt-1 flex-shrink-0" /> */}
                      <Dot className="w-5 h-5 text-black-500 mt-1 flex-shrink-0" />
                      <span>{highlight}</span>
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default F1Dashboard;