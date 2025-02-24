import React, { useState, useEffect } from 'react';
import { Trophy, Timer, Flag, AlertCircle, Calendar, Dot, InfoIcon } from 'lucide-react';
import axios from 'axios';
import { getNextRace, getLastRace } from '../utils/raceCalendar';
import ChampionshipStatus from './ChampionshipStatus';
import LoadingBar from './LoadingBar';
import SentimentCard from './SentimentCard';
import { getDriverPhoto } from '../utils/driverPhotos';
import RaceResults from './RaceResults';

const DashboardHeader = ({ nextRace }) => (
  <div className="bg-gradient-to-r from-f1-dark to-f1-carbon text-white py-8 mb-12 border-b-4 border-f1-red">
    <div className="container mx-auto px-4">
      <h1 className="font-display text-5xl text-center mb-4 text-white">F1 Race Predictions</h1>
      <div className="flex items-center justify-center gap-2 text-f1-gray">
        <Calendar className="w-5 h-5" />
        <span>
          Next Race: {nextRace ? (
            <>
              <span className="text-accent-yellow">{nextRace.name}</span> - {new Date(nextRace.date).toLocaleDateString()}
            </>
          ) : (
            <span className="text-accent-yellow">Loading...</span>
          )}
        </span>
      </div>
    </div>
  </div>
);

const F1Dashboard = () => {
  const [prediction, setPrediction] = useState(null);
  const [lastRaceResults, setLastRaceResults] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [nextRace, setNextRace] = useState(null);
  const [lastRace, setLastRace] = useState(null);
  const [championshipData, setChampionshipData] = useState(null);
  const [driverPhotos, setDriverPhotos] = useState({});

  useEffect(() => {
    const fetchRaceData = async () => {
      try {
        const next = await getNextRace();
        const last = await getLastRace();
        setNextRace(next);
        setLastRace(last);
      } catch (err) {
        console.error('Error fetching race data:', err);
      }
    };

    fetchRaceData();
  }, []);

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

        // Only set lastRaceResults if we have both the results and lastRace
        if (lastRaceRes.data && lastRace) {
          setLastRaceResults({
            ...lastRaceRes.data,
            name: lastRace.name
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

    // Only fetch data if lastRace is available
    if (lastRace) {
      fetchData();
    }
  }, [lastRace]); // Add lastRace as a dependency

  useEffect(() => {
    const fetchDriverPhotos = async () => {
      if (prediction) {
        const photos = {};
        
        // Fetch photos for qualifying prediction
        if (prediction.qualifying) {
          photos.qualifying = {
            winner: await getDriverPhoto(prediction.qualifying.driver),
            others: await Promise.all(
              prediction.qualifying.other_predictions.map(p => getDriverPhoto(p.driver))
            )
          };
        }
        
        // Fetch photos for race prediction
        if (prediction.race) {
          photos.race = {
            winner: await getDriverPhoto(prediction.race.driver),
            others: await Promise.all(
              prediction.race.other_predictions.map(p => getDriverPhoto(p.driver))
            )
          };
        }
        
        setDriverPhotos(photos);
      }
    };

    fetchDriverPhotos();
  }, [prediction]);

  // Debug render state
  console.log('Current State:', {
    loading,
    error,
    prediction,
    lastRaceResults
  });

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex flex-col items-center justify-center p-4">
        <div className="w-full max-w-md">
          <h2 className="text-xl font-semibold text-gray-700 mb-4 text-center">
            Loading F1 Data
          </h2>
          <LoadingBar />
          <br></br>
          <p className="text-gray-500 text-center mt-4">
            Fetching latest race information and predictions...
          </p>
        </div>
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
      <DashboardHeader nextRace={nextRace} />
      
      <div className="container mx-auto px-4 pb-12">
        {/* Prediction Cards */}
        {prediction && (
          <div className="grid lg:grid-cols-2 gap-8 mb-12">
            {/* Qualifying Prediction Card */}
            {prediction.qualifying && (
              <div className="bg-surface-card rounded-xl shadow-card hover:shadow-hover transition-shadow duration-300 overflow-hidden border-t-4 border-accent-purple">
                <div className="bg-gradient-to-r from-f1-dark to-f1-carbon px-6 py-4">
                  <h2 className="text-xl font-bold flex items-center gap-2 text-white">
                    <Timer className="text-accent-purple" />
                    Qualifying Prediction for {nextRace.name}
                  </h2>
                </div>
                <div className="p-6 space-y-6">
                  {/* Top 3 Predictions */}
                  <div className="space-y-4">
                    {/* Primary Prediction (Highest Confidence) */}
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-4">
                        {driverPhotos.qualifying?.winner && (
                          <img 
                            src={driverPhotos.qualifying.winner} 
                            alt={prediction.qualifying.driver}
                            className="w-16 h-16 rounded-full object-cover border-2 border-purple-200"
                          />
                        )}
                        <div>
                          <h3 className="text-2xl font-bold text-gray-900">{prediction.qualifying.driver}</h3>
                          <p className="text-purple-600 font-medium">{prediction.qualifying.team}</p>
                        </div>
                      </div>
                      <div className="bg-purple-50 px-4 py-2 rounded-full">
                        <span className="text-purple-700 font-semibold">
                          {prediction.qualifying.confidence}% Confidence
                        </span>
                      </div>
                    </div>

                    {/* Secondary Predictions */}
                    {prediction.qualifying.other_predictions?.slice(0, 2).map((pred, index) => (
                      <div key={index} className="flex items-center justify-between border-t pt-3">
                        <div className="flex items-center gap-3">
                          {driverPhotos.qualifying?.others[index] && (
                            <img 
                              src={driverPhotos.qualifying.others[index]} 
                              alt={pred.driver}
                              className="w-12 h-12 rounded-full object-cover border border-purple-100"
                            />
                          )}
                          <div>
                            <h4 className="text-lg font-medium text-gray-800">{pred.driver}</h4>
                            <p className="text-purple-500 text-sm">{pred.team}</p>
                          </div>
                        </div>
                        <div className="bg-purple-50/50 px-3 py-1 rounded-full">
                          <span className="text-purple-600 text-sm">
                            {pred.confidence}% Confidence
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>

                  {/* Reasons Section */}
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
              <div className="bg-surface-card rounded-xl shadow-card hover:shadow-hover transition-shadow duration-300 overflow-hidden border-t-4 border-f1-red">
                <div className="bg-gradient-to-r from-f1-dark to-f1-carbon px-6 py-4">
                  <h2 className="text-xl font-bold flex items-center gap-2 text-white">
                    <Trophy className="text-f1-red" />
                    Race Winner Prediction for {nextRace.name}
                  </h2>
                </div>
                <div className="p-6 space-y-6">
                  {/* Top 3 Predictions */}
                  <div className="space-y-4">
                    {/* Primary Prediction (Highest Confidence) */}
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-4">
                        {driverPhotos.race?.winner && (
                          <img 
                            src={driverPhotos.race.winner} 
                            alt={prediction.race.driver}
                            className="w-16 h-16 rounded-full object-cover border-2 border-yellow-200"
                          />
                        )}
                        <div>
                          <h3 className="text-2xl font-bold text-gray-900">{prediction.race.driver}</h3>
                          <p className="text-yellow-600 font-medium">{prediction.race.team}</p>
                        </div>
                      </div>
                      <div className="bg-yellow-50 px-4 py-2 rounded-full">
                        <span className="text-yellow-700 font-semibold">
                          {Math.round(prediction.race.confidence * 
                            (prediction.race.prediction_metadata?.confidence_adjustment || 1))}% Confidence
                        </span>
                      </div>
                    </div>

                    {/* Secondary Predictions */}
                    {prediction.race.other_predictions?.slice(0, 2).map((pred, index) => (
                      <div key={index} className="flex items-center justify-between border-t pt-3">
                        <div className="flex items-center gap-3">
                          {driverPhotos.race?.others[index] && (
                            <img 
                              src={driverPhotos.race.others[index]} 
                              alt={pred.driver}
                              className="w-12 h-12 rounded-full object-cover border border-yellow-100"
                            />
                          )}
                          <div>
                            <h4 className="text-lg font-medium text-gray-800">{pred.driver}</h4>
                            <p className="text-yellow-500 text-sm">{pred.team}</p>
                          </div>
                        </div>
                        <div className="bg-yellow-50/50 px-3 py-1 rounded-full">
                          <span className="text-yellow-600 text-sm">
                            {Math.round(pred.confidence * 
                              (prediction.race.prediction_metadata?.confidence_adjustment || 1))}% Confidence
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>

                  {/* Reasons Section */}
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

            {/* Add warning banner if using previous season data */}
            {(prediction.race?.prediction_metadata?.using_previous_season || 
              prediction.qualifying?.prediction_metadata?.using_previous_season) && (
              <div className="lg:col-span-2 bg-blue-50 border-l-4 border-blue-400 p-4 rounded">
                <div className="flex items-center">
                  <div className="flex-shrink-0">
                    <InfoIcon className="h-5 w-5 text-blue-400" />
                  </div>
                  <div className="ml-3">
                    <p className="text-sm text-blue-700">
                      These predictions are based on {prediction.race?.prediction_metadata?.season_used} season data. 
                      Predictions will be updated once current season data becomes available.
                    </p>
                  </div>
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
          <div className="mb-12">
            <RaceResults 
              results={lastRaceResults.results} 
              raceName={lastRaceResults.name}
              highlights={lastRaceResults.highlights}
              analysis={lastRaceResults.analysis}
            />
          </div>
        )}

        {/* Sentiment Analysis Section */}
        <div className="mb-12">
          <h2 className="text-2xl font-bold text-gray-900 mb-6">Media Sentiment Analysis</h2>
          {prediction && (prediction.race?.sentiment || prediction.qualifying?.sentiment) ? (
            <div className="grid lg:grid-cols-2 gap-8">
              {prediction.race?.sentiment && (
                <SentimentCard 
                  sentiment={prediction.race.sentiment} 
                  driver={prediction.race.driver}
                />
              )}
              {prediction.qualifying?.sentiment && (
                <SentimentCard 
                  sentiment={prediction.qualifying.sentiment} 
                  driver={prediction.qualifying.driver}
                />
              )}
            </div>
          ) : (
            <div className="bg-white rounded-lg shadow-md p-6 border border-gray-200">
              <div className="flex items-center justify-center text-gray-500">
                <p>No sentiment analysis available at this time. This could be due to:</p>
              </div>
              <ul className="list-disc list-inside mt-4 text-gray-500 space-y-2">
                <li>Limited recent media coverage</li>
                <li>RSS feed connectivity issues</li>
                <li>Processing delays in news aggregation</li>
              </ul>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default F1Dashboard;