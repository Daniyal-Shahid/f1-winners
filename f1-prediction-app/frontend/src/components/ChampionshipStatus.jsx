import React from 'react';
import { Trophy, Award, Star, Crown, Flag } from 'lucide-react';
import { getTeamColorClass, getTeamBgColorClass } from '../utils/teamColors';

const ChampionshipStatus = ({ championshipData }) => {
  if (!championshipData) return null;

  const { status, remaining_races, championship_contenders } = championshipData;

  // Add early return for when there's no championship data
  if (!championship_contenders?.drivers || !championship_contenders?.constructors) {
    return (
      <div className="bg-surface-card rounded-xl p-6 text-center">
        <p className="text-lg text-f1-gray">
          No championship data available yet. The season hasn't started.
        </p>
      </div>
    );
  }

  // Helper function to check if there's a mathematical winner
  const hasDriverWinner = championship_contenders.drivers.length === 1 && 
    championship_contenders.drivers[0].points_needed === 0;
  const hasConstructorWinner = championship_contenders.constructors.length === 1 && 
    championship_contenders.constructors[0].points_needed === 0;

  // Update the driver standings display
  const DriverStanding = ({ driver, team, points, pointsNeeded, position }) => (
    <div className={`relative flex items-center justify-between p-4 rounded-xl ${getTeamBgColorClass(team)} transition-transform hover:scale-[1.02] cursor-default`}>
      {/* Position Indicator */}
      <div className="absolute -left-2 -top-2 w-8 h-8 rounded-lg bg-f1-dark text-white flex items-center justify-center font-bold shadow-lg">
        {position}
      </div>
      
      <div className="flex items-center gap-4 ml-6">
        <div>
          <div className="font-bold text-lg">{driver}</div>
          <div className={`text-sm ${getTeamColorClass(team)}`}>{team}</div>
        </div>
      </div>
      
      <div className="text-right">
        <div className="text-xl font-bold">{points}</div>
        <div className="text-sm">PTS</div>
        {pointsNeeded > 0 && (
          <div className="text-xs text-status-danger mt-1">
            Need {pointsNeeded} pts to win
          </div>
        )}
      </div>
    </div>
  );

  // Update the constructor standings display
  const ConstructorStanding = ({ team, points, pointsNeeded, position }) => (
    <div className={`relative flex items-center justify-between p-4 rounded-xl ${getTeamBgColorClass(team)} transition-transform hover:scale-[1.02] cursor-default`}>
      {/* Position Indicator */}
      <div className="absolute -left-2 -top-2 w-8 h-8 rounded-lg bg-f1-dark text-white flex items-center justify-center font-bold shadow-lg">
        {position}
      </div>
      
      <div className={`ml-6 font-bold text-lg ${getTeamColorClass(team)}`}>
        {team}
      </div>
      
      <div className="text-right">
        <div className="text-xl font-bold">{points}</div>
        <div className="text-sm">PTS</div>
        {pointsNeeded > 0 && (
          <div className="text-xs text-status-danger mt-1">
            Need {pointsNeeded} pts to win
          </div>
        )}
      </div>
    </div>
  );

  return (
    <div className="grid gap-6">
      {/* Champions Section */}
      {(hasDriverWinner || hasConstructorWinner) && (
        <div className="bg-gradient-to-r from-yellow-500 to-amber-500 rounded-xl p-8 shadow-lg text-white relative overflow-hidden">
          <div className="absolute top-0 right-0 opacity-10">
            <Trophy className="w-48 h-48 -rotate-12" />
          </div>
          
          <h2 className="text-3xl font-display mb-8 flex items-center gap-2">
            <Crown className="w-8 h-8" />
            {new Date().getFullYear()} Champions
          </h2>
          
          <div className="grid md:grid-cols-2 gap-6 relative z-10">
            {hasDriverWinner && (
              <div className="bg-white/10 backdrop-blur-sm rounded-xl p-6">
                <div className="flex items-center gap-2 mb-4">
                  <Star className="w-6 h-6" />
                  <h3 className="text-xl font-bold">Drivers' Champion</h3>
                </div>
                <p className="text-3xl font-display mb-2">
                  {championship_contenders.drivers[0].driver}
                </p>
                <div className={`inline-block px-3 py-1 rounded-full bg-white/20 ${
                  getTeamColorClass(championship_contenders.drivers[0].team)
                }`}>
                  {championship_contenders.drivers[0].team}
                </div>
                <p className="mt-4 text-2xl font-bold">
                  {championship_contenders.drivers[0].points} PTS
                </p>
              </div>
            )}
            
            {hasConstructorWinner && (
              <div className="bg-white/10 backdrop-blur-sm rounded-xl p-6">
                <div className="flex items-center gap-2 mb-4">
                  <Award className="w-6 h-6" />
                  <h3 className="text-xl font-bold">Constructors' Champion</h3>
                </div>
                <p className="text-3xl font-display mb-2">
                  {championship_contenders.constructors[0].team}
                </p>
                <p className="mt-4 text-2xl font-bold">
                  {championship_contenders.constructors[0].points} PTS
                </p>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Championship Status */}
      <div className="grid md:grid-cols-2 gap-6">
        {/* Drivers' Championship */}
        <div className="bg-surface-card rounded-xl shadow-lg overflow-hidden border border-gray-100">
          <div className="bg-gradient-to-r from-f1-dark to-f1-carbon p-6">
            <h3 className="text-xl font-bold text-white flex items-center gap-2">
              <Star className="w-6 h-6 text-accent-yellow" />
              Drivers' Championship
            </h3>
            {remaining_races > 0 && (
              <div className="flex items-center gap-2 mt-2 text-f1-gray text-sm">
                <Flag className="w-4 h-4" />
                {remaining_races} races remaining
              </div>
            )}
          </div>
          
          <div className="p-6 space-y-4">
            {championship_contenders.drivers.map((driver, index) => (
              <DriverStanding 
                key={driver.driver}
                position={index + 1}
                driver={driver.driver}
                team={driver.team}
                points={driver.points}
                pointsNeeded={driver.points_needed}
              />
            ))}
          </div>
        </div>

        {/* Constructors' Championship */}
        <div className="bg-surface-card rounded-xl shadow-lg overflow-hidden border border-gray-100">
          <div className="bg-gradient-to-r from-f1-dark to-f1-carbon p-6">
            <h3 className="text-xl font-bold text-white flex items-center gap-2">
              <Award className="w-6 h-6 text-accent-purple" />
              Constructors' Championship
            </h3>
            {remaining_races > 0 && (
              <div className="flex items-center gap-2 mt-2 text-f1-gray text-sm">
                <Flag className="w-4 h-4" />
                {remaining_races} races remaining
              </div>
            )}
          </div>
          
          <div className="p-6 space-y-4">
            {championship_contenders.constructors.map((constructor, index) => (
              <ConstructorStanding 
                key={constructor.team}
                position={index + 1}
                team={constructor.team}
                points={constructor.points}
                pointsNeeded={constructor.points_needed}
              />
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default ChampionshipStatus;