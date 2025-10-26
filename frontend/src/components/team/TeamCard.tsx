/**
 * TeamCard Component
 * 
 * Displays a team's summary information including:
 * - Team name, description, and logo
 * - Budget information (total and remaining)
 * - Roster size (current/max players)
 * - Starter count (current/required)
 * - Win/loss record
 * - Awards and achievements
 * 
 * Used in team browsing, league overview, and team selection interfaces.
 */

import React from 'react';
import type { Team } from '../../types';

interface TeamCardProps {
  team: Team;
  onClick?: (team: Team) => void;
  showDetails?: boolean;
  className?: string;
}

/**
 * Format dollar value with comma separators
 */
const formatBudget = (value: number): string => {
  return `$${value.toLocaleString()}`;
};

/**
 * Get win percentage
 */
const getWinPercentage = (wins: number, losses: number): string => {
  const total = wins + losses;
  if (total === 0) return '0.0';
  return ((wins / total) * 100).toFixed(1);
};

/**
 * Get color for budget status
 */
const getBudgetColor = (budget: number, maxBudget: number = 100000): string => {
  const percentage = (budget / maxBudget) * 100;
  if (percentage >= 50) return 'text-green-600';
  if (percentage >= 25) return 'text-yellow-600';
  if (percentage >= 10) return 'text-orange-600';
  return 'text-red-600';
};

/**
 * Get roster status indicator
 */
const getRosterStatus = (rosterSize: number): { color: string; message: string } => {
  if (rosterSize < 8) {
    return { color: 'text-red-600', message: 'Incomplete' };
  }
  if (rosterSize === 12) {
    return { color: 'text-blue-600', message: 'Full' };
  }
  return { color: 'text-green-600', message: 'Active' };
};

/**
 * Get starter status indicator
 */
const getStarterStatus = (starterCount: number): { color: string; message: string } => {
  if (starterCount === 0) {
    return { color: 'text-gray-600', message: 'None set' };
  }
  if (starterCount < 5) {
    return { color: 'text-orange-600', message: 'Incomplete' };
  }
  if (starterCount === 5) {
    return { color: 'text-green-600', message: 'Ready' };
  }
  return { color: 'text-red-600', message: 'Invalid' };
};

/**
 * TeamCard component
 */
export const TeamCard: React.FC<TeamCardProps> = ({
  team,
  onClick,
  showDetails = false,
  className = '',
}) => {
  const {
    name,
    description,
    logo,
    budget,
    player_ids,
    starter_ids,
    wins,
    losses,
    awards,
  } = team;

  const rosterSize = player_ids.length;
  const starterCount = starter_ids.length;
  const maxBudget = 100000;
  const spentBudget = maxBudget - budget;
  const rosterStatus = getRosterStatus(rosterSize);
  const starterStatus = getStarterStatus(starterCount);
  const winPercentage = getWinPercentage(wins, losses);

  const handleClick = () => {
    if (onClick) {
      onClick(team);
    }
  };

  const cardClasses = `
    bg-white rounded-lg shadow-md border border-gray-200 p-5
    transition-all duration-200
    ${onClick ? 'cursor-pointer hover:shadow-lg hover:border-blue-400' : ''}
    ${className}
  `;

  return (
    <div className={cardClasses} onClick={handleClick}>
      {/* Header: Logo, Name, Description */}
      <div className="flex items-start gap-4 mb-4">
        <div className="w-16 h-16 rounded-lg bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center text-white font-bold text-2xl flex-shrink-0">
          {logo ? (
            <img src={logo} alt={name} className="w-full h-full rounded-lg object-cover" />
          ) : (
            name.charAt(0).toUpperCase()
          )}
        </div>
        <div className="flex-1 min-w-0">
          <h3 className="font-bold text-xl text-gray-900 mb-1">{name}</h3>
          {description && (
            <p className="text-sm text-gray-600 line-clamp-2">{description}</p>
          )}
        </div>
        {(wins > 0 || losses > 0) && (
          <div className="text-right flex-shrink-0">
            <div className="text-2xl font-bold text-gray-900">
              {wins}-{losses}
            </div>
            <div className="text-xs text-gray-500">
              {winPercentage}% Win Rate
            </div>
          </div>
        )}
      </div>

      {/* Budget Summary */}
      <div className="mb-4 p-3 bg-gray-50 rounded-lg">
        <div className="flex justify-between items-center mb-2">
          <span className="text-sm font-medium text-gray-700">Budget</span>
          <span className={`text-lg font-bold ${getBudgetColor(budget, maxBudget)}`}>
            {formatBudget(budget)}
          </span>
        </div>
        <div className="flex items-center gap-2">
          <div className="flex-1 bg-gray-200 rounded-full h-2">
            <div
              className="bg-green-500 h-2 rounded-full transition-all duration-300"
              style={{ width: `${(budget / maxBudget) * 100}%` }}
            />
          </div>
          <span className="text-xs text-gray-600">
            {formatBudget(spentBudget)} spent
          </span>
        </div>
      </div>

      {/* Roster & Starters Stats */}
      <div className="grid grid-cols-2 gap-3 mb-4">
        {/* Roster */}
        <div className="p-3 bg-gray-50 rounded-lg">
          <div className="text-xs font-semibold text-gray-600 uppercase mb-1">
            Roster
          </div>
          <div className="flex items-baseline gap-1">
            <span className="text-2xl font-bold text-gray-900">{rosterSize}</span>
            <span className="text-sm text-gray-500">/12</span>
          </div>
          <div className={`text-xs font-medium mt-1 ${rosterStatus.color}`}>
            {rosterStatus.message}
          </div>
        </div>

        {/* Starters */}
        <div className="p-3 bg-gray-50 rounded-lg">
          <div className="text-xs font-semibold text-gray-600 uppercase mb-1">
            Starters
          </div>
          <div className="flex items-baseline gap-1">
            <span className="text-2xl font-bold text-gray-900">{starterCount}</span>
            <span className="text-sm text-gray-500">/5</span>
          </div>
          <div className={`text-xs font-medium mt-1 ${starterStatus.color}`}>
            {starterStatus.message}
          </div>
        </div>
      </div>

      {/* Awards */}
      {showDetails && awards && awards.length > 0 && (
        <div className="pt-3 border-t border-gray-200">
          <div className="text-xs font-semibold text-gray-700 uppercase mb-2">
            Awards & Achievements
          </div>
          <div className="flex flex-wrap gap-1">
            {awards.map((award, index) => (
              <span
                key={index}
                className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800 border border-yellow-300"
              >
                🏆 {award}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Roster Status Warnings */}
      {rosterSize < 8 && (
        <div className="mt-3 p-2 bg-red-50 border border-red-200 rounded text-xs text-red-700">
          ⚠️ Team needs at least 8 players to compete
        </div>
      )}
      {rosterSize >= 8 && starterCount !== 5 && (
        <div className="mt-3 p-2 bg-orange-50 border border-orange-200 rounded text-xs text-orange-700">
          ⚠️ Team needs exactly 5 starters designated
        </div>
      )}
    </div>
  );
};

export default TeamCard;
