/**
 * PlayerCard Component
 * 
 * Displays a single player's information including:
 * - Name, age, and avatar
 * - Six skill attributes (catching, throwing, dodging, speed, iq, luck)
 * - Calculated dollar value
 * - Injury status (if injured)
 * - Statistics (games played, eliminations, etc.)
 * - Team assignment status (free agent or team name)
 * - Starter designation
 * 
 * Used in player browsing, team roster management, and draft interfaces.
 */

import React from 'react';
import type { Player } from '../../types';

interface PlayerCardProps {
  player: Player;
  onClick?: (player: Player) => void;
  showStats?: boolean;
  showTeamInfo?: boolean;
  className?: string;
}

/**
 * Get color class for skill value
 */
const getSkillColor = (value: number): string => {
  if (value >= 4) return 'text-green-600 font-semibold';
  if (value >= 2) return 'text-blue-600';
  if (value >= 1) return 'text-gray-600';
  return 'text-gray-400';
};

/**
 * Get injury severity badge color
 */
const getInjuryColor = (severity: string): string => {
  switch (severity) {
    case 'severe':
      return 'bg-red-100 text-red-800 border-red-300';
    case 'moderate':
      return 'bg-orange-100 text-orange-800 border-orange-300';
    case 'minor':
      return 'bg-yellow-100 text-yellow-800 border-yellow-300';
    default:
      return 'bg-gray-100 text-gray-800 border-gray-300';
  }
};

/**
 * Format dollar value with comma separators
 */
const formatValue = (value: number): string => {
  return `$${value.toLocaleString()}`;
};

/**
 * PlayerCard component
 */
export const PlayerCard: React.FC<PlayerCardProps> = ({
  player,
  onClick,
  showStats = false,
  showTeamInfo = true,
  className = '',
}) => {
  const { name, age, avatar, skills, value, injury, stats, team_id, is_starter } = player;

  // Calculate total skill points for validation display
  const totalSkills = Object.values(skills).reduce((sum, val) => sum + val, 0);

  const handleClick = () => {
    if (onClick) {
      onClick(player);
    }
  };

  const cardClasses = `
    bg-white rounded-lg shadow-md border border-gray-200 p-4
    transition-all duration-200
    ${onClick ? 'cursor-pointer hover:shadow-lg hover:border-blue-400' : ''}
    ${injury ? 'border-l-4 border-l-red-500' : ''}
    ${className}
  `;

  return (
    <div className={cardClasses} onClick={handleClick}>
      {/* Header: Name, Age, Avatar */}
      <div className="flex items-center gap-3 mb-3">
        <div className="w-12 h-12 rounded-full bg-gradient-to-br from-blue-400 to-purple-500 flex items-center justify-center text-white font-bold text-lg">
          {avatar ? (
            <img src={avatar} alt={name} className="w-full h-full rounded-full object-cover" />
          ) : (
            name.charAt(0)
          )}
        </div>
        <div className="flex-1">
          <div className="flex items-center gap-2">
            <h3 className="font-semibold text-lg text-gray-900">{name}</h3>
            {is_starter && (
              <span className="px-2 py-0.5 text-xs font-medium bg-blue-100 text-blue-800 rounded">
                STARTER
              </span>
            )}
          </div>
          <p className="text-sm text-gray-600">Age {age}</p>
        </div>
        <div className="text-right">
          <p className="text-lg font-bold text-green-600">{formatValue(value)}</p>
          <p className="text-xs text-gray-500">Value</p>
        </div>
      </div>

      {/* Injury Status */}
      {injury && (
        <div className={`mb-3 px-3 py-2 rounded border ${getInjuryColor(injury.severity)}`}>
          <div className="flex items-center justify-between">
            <div>
              <span className="font-semibold text-sm capitalize">{injury.severity} Injury</span>
              <p className="text-xs mt-0.5">
                -{(injury.affected_reduction * 100).toFixed(0)}% to affected skills
              </p>
            </div>
            <span className="text-xs font-medium">
              {injury.games_remaining} game{injury.games_remaining !== 1 ? 's' : ''} to heal
            </span>
          </div>
        </div>
      )}

      {/* Skills Grid */}
      <div className="mb-3">
        <div className="flex items-center justify-between mb-2">
          <h4 className="text-xs font-semibold text-gray-700 uppercase">Skills</h4>
          <span className="text-xs text-gray-500">
            Total: {totalSkills}/10
          </span>
        </div>
        <div className="grid grid-cols-3 gap-2">
          {Object.entries(skills).map(([skillName, skillValue]) => (
            <div key={skillName} className="flex flex-col">
              <span className="text-xs text-gray-600 capitalize mb-1">{skillName}</span>
              <div className="flex items-center gap-1">
                <div className="flex-1 bg-gray-200 rounded-full h-2">
                  <div
                    className="bg-blue-500 h-2 rounded-full transition-all duration-300"
                    style={{ width: `${(skillValue / 10) * 100}%` }}
                  />
                </div>
                <span className={`text-sm font-medium ${getSkillColor(skillValue)}`}>
                  {skillValue}
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Statistics */}
      {showStats && (
        <div className="pt-3 border-t border-gray-200">
          <h4 className="text-xs font-semibold text-gray-700 uppercase mb-2">Statistics</h4>
          <div className="grid grid-cols-2 gap-2 text-xs">
            <div className="flex justify-between">
              <span className="text-gray-600">Eliminations:</span>
              <span className="font-medium">{stats.successful_hits}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Catches:</span>
              <span className="font-medium">{stats.catches_made}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Throws:</span>
              <span className="font-medium">{stats.throws_attempted}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Times Hit:</span>
              <span className="font-medium">{stats.times_hit}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Missed:</span>
              <span className="font-medium">{stats.missed_throws}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Accuracy:</span>
              <span className="font-medium">
                {stats.throws_attempted > 0
                  ? ((stats.successful_hits / stats.throws_attempted) * 100).toFixed(1)
                  : '0.0'}
                %
              </span>
            </div>
          </div>
        </div>
      )}

      {/* Team Info */}
      {showTeamInfo && (
        <div className="pt-3 border-t border-gray-200 mt-3">
          {team_id ? (
            <div className="flex items-center justify-between text-sm">
              <span className="text-gray-600">Team:</span>
              <span className="font-medium text-blue-600">{team_id}</span>
            </div>
          ) : (
            <div className="flex items-center gap-2">
              <span className="inline-flex items-center px-2 py-1 rounded text-xs font-medium bg-green-100 text-green-800">
                Free Agent
              </span>
              <span className="text-xs text-gray-500">Available for draft</span>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default PlayerCard;
