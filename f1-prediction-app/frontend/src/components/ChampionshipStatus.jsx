import React from 'react';
import { Trophy, Award } from 'lucide-react';

const ChampionshipStatus = ({ championshipData }) => {
  if (!championshipData) return null;

  const { status, remaining_races, driver_standings, constructor_standings, championship_contenders } = championshipData;

  if (status === 'season_start') {
    return (
      <div className="bg-white rounded-xl shadow-lg overflow-hidden border border-green-100 p-6">
        <h2 className="text-xl font-bold mb-4">Championship Status</h2>
        <p>{championshipData.message}</p>
        <p className="text-gray-600">Remaining races: {remaining_races}</p>
      </div>
    );
  }

  if (status === 'completed') {
    return (
      <div className="bg-white rounded-xl shadow-lg overflow-hidden border border-gold-100 p-6">
        <h2 className="text-xl font-bold mb-4 flex items-center gap-2">
          <Trophy className="text-yellow-500" />
          Championship Winners
        </h2>
        <div className="grid md:grid-cols-2 gap-4">
          <div>
            <h3 className="font-semibold">Drivers' Champion:</h3>
            <p className="text-xl">{championshipData.driver_champion}</p>
          </div>
          <div>
            <h3 className="font-semibold">Constructors' Champion:</h3>
            <p className="text-xl">{championshipData.constructor_champion}</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-xl shadow-lg overflow-hidden border border-blue-100">
      <div className="bg-blue-50 px-6 py-4">
        <h2 className="text-xl font-bold flex items-center gap-2 text-blue-900">
          <Award className="text-blue-500" />
          Championship Battle
        </h2>
        <p className="text-sm text-blue-600">Remaining races: {remaining_races}</p>
      </div>
      <div className="p-6 space-y-6">
        {/* Drivers' Championship */}
        <div>
          <h3 className="font-semibold mb-3">Drivers' Championship Contenders</h3>
          <div className="space-y-2">
            {championship_contenders.drivers.map((driver) => (
              <div key={driver.driver} className="flex items-center justify-between">
                <div>
                  <span className="font-medium">{driver.driver}</span>
                  <span className="text-sm text-gray-600 ml-2">({driver.team})</span>
                </div>
                <div className="text-right">
                  <span className="font-medium">{driver.points} pts</span>
                  {driver.points_needed > 0 && (
                    <span className="text-sm text-gray-600 ml-2">
                      needs {driver.points_needed} pts
                    </span>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Constructors' Championship */}
        <div>
          <h3 className="font-semibold mb-3">Constructors' Championship Contenders</h3>
          <div className="space-y-2">
            {championship_contenders.constructors.map((constructor) => (
              <div key={constructor.team} className="flex items-center justify-between">
                <span className="font-medium">{constructor.team}</span>
                <div className="text-right">
                  <span className="font-medium">{constructor.points} pts</span>
                  {constructor.points_needed > 0 && (
                    <span className="text-sm text-gray-600 ml-2">
                      needs {constructor.points_needed} pts
                    </span>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default ChampionshipStatus;