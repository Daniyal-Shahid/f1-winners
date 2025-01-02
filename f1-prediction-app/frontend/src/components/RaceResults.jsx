import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Trophy, Medal, Flag, Clock, Award, Dot, Zap, Target } from 'lucide-react';
import { getTeamColorClass, getTeamBgColorClass } from '../utils/teamColors';

const RaceResults = ({ results, raceName, highlights }) => {
  const navigate = useNavigate();

  const handleDriverClick = (driver) => {
    navigate(`/driver-analysis/${encodeURIComponent(driver)}`);
  };

  const getPositionDisplay = (position) => {
    switch (position) {
      case 1:
        return <Trophy className="w-5 h-5 text-yellow-500" />;
      case 2:
        return <Medal className="w-5 h-5 text-gray-400" />;
      case 3:
        return <Medal className="w-5 h-5 text-amber-700" />;
      default:
        return <span className="font-bold text-f1-gray">{position}</span>;
    }
  };

  const getPointsDisplay = (points) => {
    if (points === 0) return '-';
    if (points === 1) return '1 PT';
    return `${points} PTS`;
  };

  return (
    <div className="space-y-6">
      {/* Results Table Card */}
      <div className="bg-surface-card rounded-xl shadow-lg overflow-hidden border border-gray-100">
        <div className="bg-gradient-to-r from-f1-dark to-f1-carbon p-6">
          <h2 className="text-xl font-bold text-white flex items-center gap-2">
            <Flag className="w-6 h-6 text-accent-yellow" />
            {raceName} Results
          </h2>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="bg-gray-50 text-sm text-f1-gray">
                <th className="py-4 px-6 text-left">POS</th>
                <th className="py-4 px-6 text-left">DRIVER</th>
                <th className="py-4 px-6 text-left">TEAM</th>
                <th className="py-4 px-6 text-left">TIME/GAP</th>
                <th className="py-4 px-6 text-right">POINTS</th>
              </tr>
            </thead>
            <tbody>
              {results.map((result, index) => (
                <tr 
                  key={result.driver}
                  className={`
                    border-t border-gray-100 
                    transition-colors duration-150
                    hover:bg-gray-50
                    ${index < 3 ? 'font-medium' : ''}
                  `}
                  onClick={() => handleDriverClick(result.driver)}
                >
                  {/* Position */}
                  <td className="py-4 px-6">
                    <div className="flex items-center gap-2">
                      {getPositionDisplay(result.position)}
                      {result.fastestLap && (
                        <Clock className="w-4 h-4 text-purple-500" title="Fastest Lap" />
                      )}
                    </div>
                  </td>

                  {/* Driver */}
                  <td className="py-4 px-6">
                    <div className="flex items-center gap-3">
                      <span className="font-medium">{result.driver}</span>
                      {result.driverOfDay && (
                        <Award className="w-4 h-4 text-accent-yellow" title="Driver of the Day" />
                      )}
                    </div>
                  </td>

                  {/* Team */}
                  <td className="py-4 px-6">
                    <span className={`
                      px-2 py-1 rounded-full text-sm
                      ${getTeamBgColorClass(result.team)}
                      ${getTeamColorClass(result.team)}
                    `}>
                      {result.team}
                    </span>
                  </td>

                  {/* Time/Gap */}
                  <td className="py-4 px-6">
                    <span className="text-f1-gray font-mono">
                      {result.gap_to_leader ? 
                        (result.position === 1 ? result.gap_to_leader : `+${result.gap_to_leader}`) : 
                        (result.status || 'DNF')}
                    </span>
                  </td>

                  {/* Points */}
                  <td className="py-4 px-6 text-right">
                    <span className={`
                      font-medium
                      ${result.points > 0 ? 'text-f1-dark' : 'text-f1-gray'}
                    `}>
                      {getPointsDisplay(result.points)}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Race Highlights Card */}
      {highlights && highlights.length > 0 && (
        <div className="bg-surface-card rounded-xl shadow-lg overflow-hidden border border-gray-100">
          <div className="bg-gradient-to-r from-f1-dark to-f1-carbon p-6">
            <h2 className="text-xl font-bold text-white flex items-center gap-2">
              <Zap className="w-6 h-6 text-accent-yellow" />
              Race Highlights
            </h2>
          </div>
          
          <div className="p-6">
            <div className="grid gap-3">
              {highlights.map((highlight, index) => (
                <div 
                  key={index}
                  className="flex items-start gap-3 p-3 rounded-lg hover:bg-gray-50 transition-colors"
                >
                  <Dot className="w-5 h-5 text-accent-blue mt-1 flex-shrink-0" />
                  <span className="text-f1-dark">{highlight}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default RaceResults; 