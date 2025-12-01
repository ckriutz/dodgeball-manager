/**
 * SeasonHistory Component
 * 
 * Displays the history of completed seasons in a league including:
 * - Season number and champion
 * - MVP for each season
 * - Final standings summary
 * - Statistical leaders
 * - Completion date
 * 
 * Features:
 * - Expandable accordion for each season
 * - Responsive design with Tailwind CSS
 * - Loading and empty states
 * - Click handlers for team and player navigation
 * 
 * Used in LeaguePage to display historical season data.
 */

import React, { useState } from 'react';
import type { UUID } from '../../types';

/**
 * Standing entry in final standings
 */
export interface FinalStanding {
  team_id: UUID;
  team_name: string;
  wins: number;
  losses: number;
  rank: number;
}

/**
 * Season archive data structure matching backend SeasonArchive
 */
export interface SeasonArchiveData {
  season_number: number;
  champion_team_id: UUID;
  mvp_player_id?: string | null;
  final_standings: FinalStanding[];
  team_rosters: Record<string, string[]>;
  player_stats: Record<string, Record<string, any>>;
  statistical_leaders: Record<string, string>;
  completed_at: string;
  archived_at: string;
}

/**
 * Props for SeasonHistory component
 */
interface SeasonHistoryProps {
  seasons: SeasonArchiveData[];
  loading?: boolean;
  error?: string | null;
  onTeamClick?: (teamId: UUID) => void;
  onPlayerClick?: (playerId: UUID) => void;
  className?: string;
  /** Optional map of player IDs to player names for display */
  playerNames?: Record<string, string>;
  /** Optional map of team IDs to team names for display */
  teamNames?: Record<string, string>;
}

/**
 * Format date for display
 */
const formatDate = (dateString: string): string => {
  try {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    });
  } catch {
    return dateString;
  }
};

/**
 * Get ordinal suffix for a number (1st, 2nd, 3rd, etc.)
 */
const getOrdinalSuffix = (n: number): string => {
  const s = ['th', 'st', 'nd', 'rd'];
  const v = n % 100;
  return n + (s[(v - 20) % 10] || s[v] || s[0]);
};

/**
 * Statistical leader display names
 */
const STAT_LEADER_NAMES: Record<string, string> = {
  most_hits: '🎯 Most Eliminations',
  most_catches: '🧤 Most Catches',
  highest_accuracy: '🏹 Best Accuracy',
  best_defense: '🛡️ Best Defense',
  fewest_times_hit: '🛡️ Best Defense',
};

/**
 * Individual season card component
 */
const SeasonCard: React.FC<{
  season: SeasonArchiveData;
  isExpanded: boolean;
  onToggle: () => void;
  onTeamClick?: (teamId: UUID) => void;
  onPlayerClick?: (playerId: UUID) => void;
  playerNames?: Record<string, string>;
  teamNames?: Record<string, string>;
}> = ({ season, isExpanded, onToggle, onTeamClick, onPlayerClick, playerNames, teamNames }) => {
  // Find champion team name from standings
  const championStanding = season.final_standings.find(
    (s) => s.team_id === season.champion_team_id
  );
  const championName = teamNames?.[season.champion_team_id] || 
    championStanding?.team_name || 
    'Unknown Team';
  
  // Get MVP name
  const mvpName = season.mvp_player_id 
    ? (playerNames?.[season.mvp_player_id] || 'Unknown Player')
    : null;

  return (
    <div 
      className="bg-white rounded-lg border border-gray-200 shadow-sm overflow-hidden"
      data-testid={`season-card-${season.season_number}`}
    >
      {/* Header - Always visible */}
      <button
        className="w-full px-4 py-3 flex items-center justify-between bg-gray-50 hover:bg-gray-100 transition-colors"
        onClick={onToggle}
        aria-expanded={isExpanded}
      >
        <div className="flex items-center gap-3">
          <span className="text-2xl" role="img" aria-label="Trophy">
            🏆
          </span>
          <div className="text-left">
            <h3 className="font-semibold text-gray-900">
              Season {season.season_number}
            </h3>
            <p className="text-sm text-gray-500">
              {formatDate(season.completed_at)}
            </p>
          </div>
        </div>
        
        <div className="flex items-center gap-4">
          {/* Champion Badge */}
          <div className="text-right hidden sm:block">
            <p className="text-xs text-gray-500 uppercase">Champion</p>
            <p 
              className={`font-medium text-yellow-700 ${onTeamClick ? 'hover:underline cursor-pointer' : ''}`}
              onClick={(e) => {
                if (onTeamClick) {
                  e.stopPropagation();
                  onTeamClick(season.champion_team_id);
                }
              }}
            >
              {championName}
            </p>
          </div>
          
          {/* Expand/Collapse Icon */}
          <svg 
            className={`w-5 h-5 text-gray-400 transition-transform ${isExpanded ? 'rotate-180' : ''}`} 
            fill="none" 
            stroke="currentColor" 
            viewBox="0 0 24 24"
          >
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
          </svg>
        </div>
      </button>

      {/* Expanded Content */}
      {isExpanded && (
        <div className="px-4 py-4 border-t border-gray-200 space-y-4">
          {/* Champion & MVP Row */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            {/* Champion */}
            <div className="bg-yellow-50 rounded-lg p-3 border border-yellow-200">
              <p className="text-xs text-yellow-600 uppercase font-medium mb-1">Champion</p>
              <p 
                className={`font-semibold text-yellow-800 ${onTeamClick ? 'hover:underline cursor-pointer' : ''}`}
                onClick={() => onTeamClick?.(season.champion_team_id)}
              >
                🏆 {championName}
              </p>
              {championStanding && (
                <p className="text-sm text-yellow-700 mt-1">
                  {championStanding.wins}W - {championStanding.losses}L
                </p>
              )}
            </div>

            {/* MVP */}
            {mvpName && season.mvp_player_id && (
              <div className="bg-purple-50 rounded-lg p-3 border border-purple-200">
                <p className="text-xs text-purple-600 uppercase font-medium mb-1">Season MVP</p>
                <p 
                  className={`font-semibold text-purple-800 ${onPlayerClick ? 'hover:underline cursor-pointer' : ''}`}
                  onClick={() => onPlayerClick?.(season.mvp_player_id!)}
                >
                  ⭐ {mvpName}
                </p>
              </div>
            )}
          </div>

          {/* Final Standings */}
          {season.final_standings.length > 0 && (
            <div>
              <h4 className="text-sm font-medium text-gray-700 mb-2">Final Standings</h4>
              <div className="bg-gray-50 rounded-lg overflow-hidden">
                <table className="min-w-full text-sm">
                  <thead>
                    <tr className="bg-gray-100">
                      <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">Rank</th>
                      <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">Team</th>
                      <th className="px-3 py-2 text-center text-xs font-medium text-gray-500 uppercase">W</th>
                      <th className="px-3 py-2 text-center text-xs font-medium text-gray-500 uppercase">L</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-200">
                    {season.final_standings.slice(0, 5).map((standing) => (
                      <tr 
                        key={standing.team_id}
                        className={`${standing.rank === 1 ? 'bg-yellow-50' : 'bg-white'} ${onTeamClick ? 'cursor-pointer hover:bg-blue-50' : ''}`}
                        onClick={() => onTeamClick?.(standing.team_id)}
                      >
                        <td className="px-3 py-2 whitespace-nowrap">
                          {standing.rank === 1 && '🥇 '}
                          {standing.rank === 2 && '🥈 '}
                          {standing.rank === 3 && '🥉 '}
                          {standing.rank > 3 && `${getOrdinalSuffix(standing.rank)} `}
                        </td>
                        <td className="px-3 py-2 whitespace-nowrap font-medium text-gray-900">
                          {standing.team_name}
                        </td>
                        <td className="px-3 py-2 whitespace-nowrap text-center text-green-600">
                          {standing.wins}
                        </td>
                        <td className="px-3 py-2 whitespace-nowrap text-center text-red-600">
                          {standing.losses}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
                {season.final_standings.length > 5 && (
                  <div className="px-3 py-2 text-xs text-gray-500 bg-gray-100">
                    +{season.final_standings.length - 5} more teams
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Statistical Leaders */}
          {Object.keys(season.statistical_leaders).length > 0 && (
            <div>
              <h4 className="text-sm font-medium text-gray-700 mb-2">Statistical Leaders</h4>
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
                {Object.entries(season.statistical_leaders).map(([stat, playerId]) => {
                  const leaderName = playerNames?.[playerId] || 'Unknown';
                  const displayName = STAT_LEADER_NAMES[stat] || stat;
                  
                  return (
                    <div 
                      key={stat}
                      className={`bg-gray-50 rounded p-2 text-center ${onPlayerClick ? 'cursor-pointer hover:bg-blue-50' : ''}`}
                      onClick={() => onPlayerClick?.(playerId)}
                    >
                      <p className="text-xs text-gray-500 truncate">{displayName}</p>
                      <p className="text-sm font-medium text-gray-800 truncate" title={leaderName}>
                        {leaderName}
                      </p>
                    </div>
                  );
                })}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

/**
 * SeasonHistory component
 */
export const SeasonHistory: React.FC<SeasonHistoryProps> = ({
  seasons,
  loading = false,
  error = null,
  onTeamClick,
  onPlayerClick,
  className = '',
  playerNames = {},
  teamNames = {},
}) => {
  // Track which seasons are expanded (default: most recent)
  const [expandedSeasons, setExpandedSeasons] = useState<Set<number>>(() => {
    if (seasons.length > 0) {
      // Expand the most recent season by default
      const mostRecent = Math.max(...seasons.map(s => s.season_number));
      return new Set([mostRecent]);
    }
    return new Set();
  });

  const toggleSeason = (seasonNumber: number) => {
    setExpandedSeasons((prev) => {
      const next = new Set(prev);
      if (next.has(seasonNumber)) {
        next.delete(seasonNumber);
      } else {
        next.add(seasonNumber);
      }
      return next;
    });
  };

  // Loading state
  if (loading) {
    return (
      <div className={`bg-white rounded-lg shadow-sm border border-gray-200 ${className}`}>
        <div className="px-6 py-4 border-b border-gray-200">
          <h2 className="text-lg font-semibold text-gray-900">Season History</h2>
        </div>
        <div className="p-6 space-y-4">
          {[1, 2].map((i) => (
            <div key={i} className="animate-pulse">
              <div className="bg-gray-100 rounded-lg p-4 h-20">
                <div className="flex items-center gap-3">
                  <div className="bg-gray-200 w-10 h-10 rounded-full"></div>
                  <div className="flex-1">
                    <div className="h-4 bg-gray-200 rounded w-32 mb-2"></div>
                    <div className="h-3 bg-gray-200 rounded w-24"></div>
                  </div>
                </div>
              </div>
            </div>
          ))}
          <p className="text-gray-500 text-center">Loading season history...</p>
        </div>
      </div>
    );
  }

  // Error state
  if (error) {
    return (
      <div className={`bg-white rounded-lg shadow-sm border border-red-200 ${className}`}>
        <div className="px-6 py-4 border-b border-red-200 bg-red-50">
          <h2 className="text-lg font-semibold text-red-900">Season History</h2>
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

  // Empty state
  if (!seasons || seasons.length === 0) {
    return (
      <div className={`bg-white rounded-lg shadow-sm border border-gray-200 ${className}`}>
        <div className="px-6 py-4 border-b border-gray-200">
          <h2 className="text-lg font-semibold text-gray-900">Season History</h2>
        </div>
        <div className="p-8 text-center">
          <div className="text-gray-400 mb-2">
            <svg className="w-12 h-12 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <p className="text-gray-500">No completed seasons yet.</p>
          <p className="text-gray-400 text-sm mt-1">Complete your first season to see it recorded here!</p>
        </div>
      </div>
    );
  }

  // Sort seasons by season number descending (most recent first)
  const sortedSeasons = [...seasons].sort((a, b) => b.season_number - a.season_number);

  return (
    <div className={`bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden ${className}`}>
      {/* Header */}
      <div className="px-6 py-4 border-b border-gray-200 bg-gray-50">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span className="text-2xl" role="img" aria-label="Calendar">
              📅
            </span>
            <h2 className="text-lg font-semibold text-gray-900">Season History</h2>
          </div>
          <span className="text-sm text-gray-500">
            {seasons.length} completed season{seasons.length !== 1 ? 's' : ''}
          </span>
        </div>
      </div>

      {/* Season Cards */}
      <div className="p-4 space-y-3">
        {sortedSeasons.map((season) => (
          <SeasonCard
            key={season.season_number}
            season={season}
            isExpanded={expandedSeasons.has(season.season_number)}
            onToggle={() => toggleSeason(season.season_number)}
            onTeamClick={onTeamClick}
            onPlayerClick={onPlayerClick}
            playerNames={playerNames}
            teamNames={teamNames}
          />
        ))}
      </div>

      {/* Footer info */}
      <div className="px-6 py-3 bg-gray-50 border-t border-gray-200">
        <p className="text-xs text-gray-500 text-center">
          Click on a season to view details. Click on teams or players to navigate.
        </p>
      </div>
    </div>
  );
};

export default SeasonHistory;
