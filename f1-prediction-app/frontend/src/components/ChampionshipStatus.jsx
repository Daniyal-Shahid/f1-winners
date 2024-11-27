import React from 'react';
import { Trophy, Award, Star } from 'lucide-react';

const ChampionshipStatus = ({ championshipData }) => {
  if (!championshipData) return null;

  const { status, remaining_races, championship_contenders } = championshipData;

  // Helper function to check if there's a mathematical winner
  const hasDriverWinner = championship_contenders?.drivers?.length === 1 && 
    championship_contenders.drivers[0].points_needed === 0;
  const hasConstructorWinner = championship_contenders?.constructors?.length === 1 && 
    championship_contenders.constructors[0].points_needed === 0;

  return (
    <div className="grid gap-6">
      {/* Champions Section */}
      {(hasDriverWinner || hasConstructorWinner) && (
        <div className="bg-gradient-to-r from-yellow-500 to-amber-500 rounded-xl p-6 shadow-lg text-white">
          <h2 className="text-2xl font-bold mb-6 flex items-center gap-2">
            <Trophy className="w-8 h-8" />
            {new Date().getFullYear()} Champions
          </h2>
          
          <div className="grid md:grid-cols-2 gap-6">
            {hasDriverWinner && (
              <div className="bg-white/10 backdrop-blur-sm rounded-lg p-4">
                <div className="flex items-center gap-2 mb-2">
                  <Star className="w-5 h-5" />
                  <h3 className="text-lg font-semibold">Drivers' Champion</h3>
                </div>
                <p className="text-2xl font-bold">
                  {championship_contenders.drivers[0].driver}
                </p>
                <p className="text-yellow-100">
                  {championship_contenders.drivers[0].team} • 
                  {championship_contenders.drivers[0].points} points
                </p>
              </div>
            )}
            
            {hasConstructorWinner && (
              <div className="bg-white/10 backdrop-blur-sm rounded-lg p-4">
                <div className="flex items-center gap-2 mb-2">
                  <Award className="w-5 h-5" />
                  <h3 className="text-lg font-semibold">Constructors' Champion</h3>
                </div>
                <p className="text-2xl font-bold">
                  {championship_contenders.constructors[0].team}
                </p>
                <p className="text-yellow-100">
                  {championship_contenders.constructors[0].points} points
                </p>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Championship Contenders Section */}
      <div className="grid md:grid-cols-2 gap-6">
        {/* Drivers' Championship */}
        <div className="bg-white rounded-xl shadow-lg overflow-hidden border border-gray-100 p-6">
          <h3 className="font-semibold mb-4 flex items-center gap-2">
            <Star className="w-5 h-5 text-blue-500" />
            Drivers' Championship Standings
          </h3>
          <div className="space-y-3">
            {championship_contenders.drivers.map((driver, index) => (
              <div 
                key={driver.driver} 
                className={`flex items-center justify-between p-2 rounded-lg ${
                  index === 0 ? 'bg-blue-50' : ''
                }`}
              >
                <div>
                  <span className="font-medium">{driver.driver}</span>
                  <span className="text-sm text-gray-600 ml-2">({driver.team})</span>
                </div>
                <div className="text-right">
                  <span className="font-medium">{driver.points} pts</span>
                  {driver.points_needed > 0 && (
                    <span className="text-sm text-red-600 ml-2">
                      need <b>{driver.points_needed}</b> points to win
                    </span>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Constructors' Championship */}
        <div className="bg-white rounded-xl shadow-lg overflow-hidden border border-gray-100 p-6">
          <h3 className="font-semibold mb-4 flex items-center gap-2">
            <Award className="w-5 h-5 text-purple-500" />
            Constructors' Championship Standings
          </h3>
          <div className="space-y-3">
            {championship_contenders.constructors.map((constructor, index) => (
              <div 
                key={constructor.team} 
                className={`flex items-center justify-between p-2 rounded-lg ${
                  index === 0 ? 'bg-purple-50' : ''
                }`}
              >
                <span className="font-medium">{constructor.team}</span>
                <div className="text-right">
                  <span className="font-medium">{constructor.points} pts</span>
                  {constructor.points_needed > 0 && (
                    <span className="text-sm text-red-600 ml-2">
                      need <b>{constructor.points_needed}</b> points to win
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