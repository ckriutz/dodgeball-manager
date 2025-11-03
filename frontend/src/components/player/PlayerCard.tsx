/**
 * PlayerCard Component
 * 
 * Clean, simplified player card design inspired by modern profile layouts.
 * Displays essential player information with a focus on readability and visual hierarchy.
 */

import React from 'react';
import type { Player } from '../../types';

interface PlayerCardProps {
  player: Player;
  onClick?: (player: Player) => void;
  showStats?: boolean;
  className?: string;
  teamName?: string; // Optional team name to display
  // Action button configuration
  actionButton?: {
    label: string;
    onClick: (player: Player) => void;
    variant?: 'primary' | 'success' | 'danger';
    disabled?: boolean;
  };
}

/**
 * Format dollar value with comma separators
 */
const formatValue = (value: number): string => {
  return `$${value.toLocaleString()}`;
};

/**
 * Get top 3 skills for display
 */
const getTopSkills = (skills: Player['skills']): Array<{ name: string; value: number }> => {
  return Object.entries(skills)
    .sort(([, a], [, b]) => b - a)
    .slice(0, 3)
    .map(([name, value]) => ({ name, value }));
};

/**
 * PlayerCard component - Simplified clean design
 */
export const PlayerCard: React.FC<PlayerCardProps> = ({
  player,
  onClick,
  showStats = false,
  className = '',
  teamName,
  actionButton,
}) => {
  const { name, age, avatar, skills, value, injury, stats, team_id, is_starter } = player;

  const topSkills = getTopSkills(skills);

  const handleClick = () => {
    if (onClick) {
      onClick(player);
    }
  };

  const handleActionClick = (e: React.MouseEvent) => {
    e.stopPropagation(); // Prevent card click when clicking action button
    if (actionButton && !actionButton.disabled) {
      actionButton.onClick(player);
    }
  };

  const getActionButtonClasses = () => {
    const baseClasses = 'px-4 py-2 rounded-lg font-medium text-sm transition-all duration-200';
    const variant = actionButton?.variant || 'primary';
    
    if (actionButton?.disabled) {
      return `${baseClasses} bg-gray-300 text-gray-500 cursor-not-allowed`;
    }

    switch (variant) {
      case 'success':
        return `${baseClasses} bg-green-600 text-white hover:bg-green-700 shadow-sm hover:shadow`;
      case 'danger':
        return `${baseClasses} bg-red-600 text-white hover:bg-red-700 shadow-sm hover:shadow`;
      case 'primary':
      default:
        return `${baseClasses} bg-blue-600 text-white hover:bg-blue-700 shadow-sm hover:shadow`;
    }
  };

  const cardClasses = `
    bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden
    transition-all duration-200
    ${onClick ? 'cursor-pointer hover:shadow-md hover:border-gray-300' : ''}
    ${className}
  `;

  return (
    <div className={cardClasses} onClick={handleClick}>
      {/* Header Section with Avatar and Name */}
      <div className="relative bg-gradient-to-br from-slate-50 to-slate-100 p-6 pb-4">
        {injury && (
          <div className="absolute top-3 right-3">
            <span className="inline-flex items-center px-2 py-1 rounded-md text-xs font-medium bg-red-100 text-red-700 border border-red-200">
              Injured
            </span>
          </div>
        )}
        
        <div className="flex items-start gap-4">
          {/* Avatar */}
          <div className="relative">
            <div className="w-20 h-20 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center text-white font-bold text-2xl shadow-md">
              <img src={`/images/avatars/${avatar}.png`} alt={name} className="w-full h-full rounded-full object-cover" />
            </div>
            {is_starter && (
              <div className="absolute -bottom-1 -right-1 w-6 h-6 bg-yellow-400 rounded-full border-2 border-white flex items-center justify-center shadow-sm">
                <span className="text-xs">⭐</span>
              </div>
            )}
          </div>

          {/* Name and Team */}
          <div className="flex-1 pt-1">
            <h3 className="text-xl font-bold text-gray-900 mb-1">{name}</h3>
            <p className="text-sm text-gray-500">
              {teamName || (team_id ? 'Team Player' : 'Free Agent')}
            </p>
          </div>
        </div>
      </div>

      {/* Info Grid */}
      <div className="p-6 pt-4 space-y-3">
        {/* Key Stats Grid */}
        <div className="grid grid-cols-2 gap-3 text-sm">
          <div className="flex justify-between items-center">
            <span className="text-gray-500">Age</span>
            <span className="font-semibold text-gray-900">{age}</span>
          </div>
          <div className="flex justify-between items-center">
            <span className="text-gray-500">Value</span>
            <span className="font-semibold text-green-600">{formatValue(value)}</span>
          </div>
        </div>

        {/* Top Skills and Performance - Combined Row */}
        <div className="pt-2 border-t border-gray-100">
          <div className={`grid ${(showStats || team_id) ? 'grid-cols-2 gap-4' : 'grid-cols-1'}`}>
            {/* Top Skills */}
            <div>
              <div className="text-xs font-medium text-gray-600 uppercase mb-2">Top Skills</div>
              <div className="space-y-2">
                {topSkills.map(({ name, value }) => (
                  <div key={name} className="flex justify-between items-center text-sm">
                    <span className="text-gray-600 capitalize">{name}</span>
                    <span className="font-semibold text-gray-900">{value}/10</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Performance (if enabled or player is on a team) */}
            {(showStats || team_id) && (
              <div>
                <div className="text-xs font-medium text-gray-600 uppercase mb-2">Performance</div>
                <div className="space-y-2">
                  <div className="flex justify-between items-center text-sm">
                    <span className="text-gray-500">Eliminations</span>
                    <span className="font-semibold text-gray-900">{stats.successful_hits}</span>
                  </div>
                  <div className="flex justify-between items-center text-sm">
                    <span className="text-gray-500">Catches</span>
                    <span className="font-semibold text-gray-900">{stats.catches_made}</span>
                  </div>
                  <div className="flex justify-between items-center text-sm">
                    <span className="text-gray-500">Accuracy</span>
                    <span className="font-semibold text-gray-900">
                      {stats.throws_attempted > 0
                        ? ((stats.successful_hits / stats.throws_attempted) * 100).toFixed(0)
                        : '0'}
                      %
                    </span>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Action Button (if provided) */}
      {actionButton && (
        <div className="px-6 pb-4">
          <button
            onClick={handleActionClick}
            disabled={actionButton.disabled}
            className={`w-full ${getActionButtonClasses()}`}
          >
            {actionButton.label}
          </button>
        </div>
      )}
    </div>
  );
};

export default PlayerCard;
