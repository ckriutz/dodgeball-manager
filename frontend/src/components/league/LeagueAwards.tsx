/**
 * LeagueAwards Component
 * 
 * Displays league awards including:
 * - MVP (Most Valuable Player)
 * - Most Hits (Top Eliminator)
 * - Most Catches (Best Catcher)
 * - Accuracy Leader (Best Throw Accuracy)
 * - Best Defense (Fewest Times Hit)
 * 
 * Features:
 * - Responsive card grid layout with Tailwind CSS
 * - Loading and empty states
 * - Click handler for player navigation
 * - Visual indicators with award-specific icons
 * 
 * Used in LeaguePage to display season awards and MVPs.
 */

import React from 'react';
import type { UUID } from '../../types';

/**
 * Award winner data for a single award category
 */
export interface AwardWinner {
  player_id: UUID;
  name: string;
  reason?: string | null;
  mvp_score?: number | null;
  successful_hits?: number | null;
  catches_made?: number | null;
  times_hit?: number | null;
  accuracy?: number | null;
}

/**
 * Awards data structure matching backend AwardsResponse
 */
export interface AwardsData {
  league_id: UUID;
  mvp?: AwardWinner | null;
  most_hits?: AwardWinner | null;
  most_catches?: AwardWinner | null;
  accuracy_leader?: AwardWinner | null;
  best_defense?: AwardWinner | null;
}

/**
 * Props for LeagueAwards component
 */
interface LeagueAwardsProps {
  awards: AwardsData | null;
  loading?: boolean;
  error?: string | null;
  onPlayerClick?: (playerId: UUID) => void;
  className?: string;
}

/**
 * Award category configuration for display
 */
interface AwardConfig {
  key: keyof Omit<AwardsData, 'league_id'>;
  title: string;
  icon: string;
  bgColor: string;
  borderColor: string;
  textColor: string;
  iconBg: string;
  formatStat: (winner: AwardWinner) => string;
}

/**
 * Award display configurations
 */
const AWARD_CONFIGS: AwardConfig[] = [
  {
    key: 'mvp',
    title: 'MVP',
    icon: '🏆',
    bgColor: 'bg-gradient-to-br from-yellow-50 to-yellow-100',
    borderColor: 'border-yellow-300',
    textColor: 'text-yellow-800',
    iconBg: 'bg-yellow-200',
    formatStat: (winner) => {
      if (winner.mvp_score !== null && winner.mvp_score !== undefined) {
        return `Score: ${winner.mvp_score.toFixed(1)}`;
      }
      return winner.reason || 'Most Valuable Player';
    },
  },
  {
    key: 'most_hits',
    title: 'Top Eliminator',
    icon: '🎯',
    bgColor: 'bg-gradient-to-br from-red-50 to-red-100',
    borderColor: 'border-red-300',
    textColor: 'text-red-800',
    iconBg: 'bg-red-200',
    formatStat: (winner) => {
      if (winner.successful_hits !== null && winner.successful_hits !== undefined) {
        return `${winner.successful_hits} eliminations`;
      }
      return winner.reason || 'Most Eliminations';
    },
  },
  {
    key: 'most_catches',
    title: 'Best Catcher',
    icon: '🧤',
    bgColor: 'bg-gradient-to-br from-blue-50 to-blue-100',
    borderColor: 'border-blue-300',
    textColor: 'text-blue-800',
    iconBg: 'bg-blue-200',
    formatStat: (winner) => {
      if (winner.catches_made !== null && winner.catches_made !== undefined) {
        return `${winner.catches_made} catches`;
      }
      return winner.reason || 'Most Catches';
    },
  },
  {
    key: 'accuracy_leader',
    title: 'Accuracy Leader',
    icon: '🏹',
    bgColor: 'bg-gradient-to-br from-green-50 to-green-100',
    borderColor: 'border-green-300',
    textColor: 'text-green-800',
    iconBg: 'bg-green-200',
    formatStat: (winner) => {
      if (winner.accuracy !== null && winner.accuracy !== undefined) {
        return `${(winner.accuracy * 100).toFixed(1)}% accuracy`;
      }
      return winner.reason || 'Best Accuracy';
    },
  },
  {
    key: 'best_defense',
    title: 'Best Defense',
    icon: '🛡️',
    bgColor: 'bg-gradient-to-br from-purple-50 to-purple-100',
    borderColor: 'border-purple-300',
    textColor: 'text-purple-800',
    iconBg: 'bg-purple-200',
    formatStat: (winner) => {
      if (winner.times_hit !== null && winner.times_hit !== undefined) {
        return `Only ${winner.times_hit} times hit`;
      }
      return winner.reason || 'Fewest Times Eliminated';
    },
  },
];

/**
 * Individual award card component
 */
const AwardCard: React.FC<{
  config: AwardConfig;
  winner: AwardWinner;
  onPlayerClick?: (playerId: UUID) => void;
}> = ({ config, winner, onPlayerClick }) => {
  return (
    <div
      className={`${config.bgColor} rounded-lg border-2 ${config.borderColor} p-4 ${
        onPlayerClick ? 'cursor-pointer hover:shadow-md transition-shadow' : ''
      }`}
      onClick={() => onPlayerClick?.(winner.player_id)}
      data-testid={`award-card-${config.key}`}
    >
      {/* Award Icon and Title */}
      <div className="flex items-center gap-3 mb-3">
        <div className={`${config.iconBg} w-10 h-10 rounded-full flex items-center justify-center`}>
          <span className="text-xl" role="img" aria-label={config.title}>
            {config.icon}
          </span>
        </div>
        <div>
          <h3 className={`font-bold ${config.textColor}`}>{config.title}</h3>
        </div>
      </div>

      {/* Winner Info */}
      <div className="mt-2">
        <p className="text-gray-900 font-semibold text-lg truncate" title={winner.name}>
          {winner.name}
        </p>
        <p className="text-gray-600 text-sm mt-1">
          {config.formatStat(winner)}
        </p>
        {winner.reason && winner.reason !== config.formatStat(winner) && (
          <p className="text-gray-500 text-xs mt-1 italic">
            {winner.reason}
          </p>
        )}
      </div>
    </div>
  );
};

/**
 * Empty award card placeholder
 */
const EmptyAwardCard: React.FC<{ config: AwardConfig }> = ({ config }) => {
  return (
    <div
      className="bg-gray-50 rounded-lg border-2 border-dashed border-gray-200 p-4"
      data-testid={`award-card-${config.key}-empty`}
    >
      {/* Award Icon and Title */}
      <div className="flex items-center gap-3 mb-3">
        <div className="bg-gray-200 w-10 h-10 rounded-full flex items-center justify-center opacity-50">
          <span className="text-xl grayscale" role="img" aria-label={config.title}>
            {config.icon}
          </span>
        </div>
        <div>
          <h3 className="font-bold text-gray-400">{config.title}</h3>
        </div>
      </div>

      {/* No Winner */}
      <div className="mt-2">
        <p className="text-gray-400 text-sm">No winner yet</p>
        <p className="text-gray-300 text-xs mt-1">Play more games to determine winners</p>
      </div>
    </div>
  );
};

/**
 * LeagueAwards component
 */
export const LeagueAwards: React.FC<LeagueAwardsProps> = ({
  awards,
  loading = false,
  error = null,
  onPlayerClick,
  className = '',
}) => {
  // Loading state
  if (loading) {
    return (
      <div className={`bg-white rounded-lg shadow-sm border border-gray-200 ${className}`}>
        <div className="px-6 py-4 border-b border-gray-200">
          <h2 className="text-lg font-semibold text-gray-900">League Awards</h2>
        </div>
        <div className="p-6">
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {[1, 2, 3, 4, 5].map((i) => (
              <div key={i} className="animate-pulse">
                <div className="bg-gray-100 rounded-lg p-4 h-32">
                  <div className="flex items-center gap-3 mb-3">
                    <div className="bg-gray-200 w-10 h-10 rounded-full"></div>
                    <div className="h-4 bg-gray-200 rounded w-24"></div>
                  </div>
                  <div className="h-5 bg-gray-200 rounded w-32 mb-2"></div>
                  <div className="h-3 bg-gray-200 rounded w-20"></div>
                </div>
              </div>
            ))}
          </div>
          <p className="text-gray-500 text-center mt-4">Loading awards...</p>
        </div>
      </div>
    );
  }

  // Error state
  if (error) {
    return (
      <div className={`bg-white rounded-lg shadow-sm border border-red-200 ${className}`}>
        <div className="px-6 py-4 border-b border-red-200 bg-red-50">
          <h2 className="text-lg font-semibold text-red-900">League Awards</h2>
        </div>
        <div className="p-8 text-center">
          <div className="text-red-500 mb-2">
            <svg className="w-12 h-12 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
          </div>
          <p className="text-red-600 font-medium">{error}</p>
        </div>
      </div>
    );
  }

  // Check if any awards exist
  const hasAnyAwards = awards && AWARD_CONFIGS.some((config) => awards[config.key]);

  // Empty state (no awards data)
  if (!awards) {
    return (
      <div className={`bg-white rounded-lg shadow-sm border border-gray-200 ${className}`}>
        <div className="px-6 py-4 border-b border-gray-200">
          <h2 className="text-lg font-semibold text-gray-900">League Awards</h2>
        </div>
        <div className="p-8 text-center">
          <div className="text-gray-400 mb-2">
            <svg className="w-12 h-12 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L21 12l-5.714 2.143L13 21l-2.286-6.857L5 12l5.714-2.143L13 3z" />
            </svg>
          </div>
          <p className="text-gray-500">No awards data available.</p>
          <p className="text-gray-400 text-sm mt-1">Play games to earn awards!</p>
        </div>
      </div>
    );
  }

  return (
    <div className={`bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden ${className}`}>
      {/* Header */}
      <div className="px-6 py-4 border-b border-gray-200 bg-gray-50">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span className="text-2xl" role="img" aria-label="Trophy">
              🏆
            </span>
            <h2 className="text-lg font-semibold text-gray-900">League Awards</h2>
          </div>
          {hasAnyAwards && (
            <span className="text-sm text-gray-500">
              {AWARD_CONFIGS.filter((config) => awards[config.key]).length} awards
            </span>
          )}
        </div>
      </div>

      {/* Awards Grid */}
      <div className="p-6">
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {AWARD_CONFIGS.map((config) => {
            const winner = awards[config.key];
            
            if (winner) {
              return (
                <AwardCard
                  key={config.key}
                  config={config}
                  winner={winner}
                  onPlayerClick={onPlayerClick}
                />
              );
            }
            
            return <EmptyAwardCard key={config.key} config={config} />;
          })}
        </div>
      </div>

      {/* Footer with info */}
      {!hasAnyAwards && (
        <div className="px-6 py-3 bg-gray-50 border-t border-gray-200">
          <p className="text-xs text-gray-500 text-center">
            Awards are determined based on player performance throughout the season.
            Play more games to see award winners!
          </p>
        </div>
      )}
    </div>
  );
};

export default LeagueAwards;
