/**
 * LeagueStandings Component
 * 
 * Displays the league standings table showing:
 * - Team rank and name
 * - Win/loss record
 * - Win percentage
 * - Games played
 * 
 * Features:
 * - Responsive table design with Tailwind CSS
 * - Loading and empty states
 * - Click handler for team navigation
 * - Visual indicators for top teams
 * 
 * Used in LeaguePage to show current season standings.
 */

import React from 'react';
import type { UUID } from '../../types';

/**
 * Standing entry for a single team
 */
export interface StandingsEntry {
  team_id: UUID;
  team_name: string;
  wins: number;
  losses: number;
  rank: number;
}

/**
 * Props for LeagueStandings component
 */
interface LeagueStandingsProps {
  standings: StandingsEntry[];
  loading?: boolean;
  error?: string | null;
  onTeamClick?: (teamId: UUID) => void;
  className?: string;
}

/**
 * Calculate win percentage
 */
const calculateWinPercentage = (wins: number, losses: number): string => {
  const total = wins + losses;
  if (total === 0) return '.000';
  const percentage = wins / total;
  // Format as .XXX (e.g., .750, .500, .333)
  return percentage.toFixed(3).replace(/^0/, '');
};

/**
 * Get games played
 */
const getGamesPlayed = (wins: number, losses: number): number => {
  return wins + losses;
};

/**
 * Get rank indicator styling
 */
const getRankStyle = (rank: number): string => {
  if (rank === 1) {
    return 'bg-yellow-100 text-yellow-800 font-bold';
  }
  if (rank === 2) {
    return 'bg-gray-100 text-gray-800 font-semibold';
  }
  if (rank === 3) {
    return 'bg-orange-100 text-orange-800 font-semibold';
  }
  return 'bg-white text-gray-700';
};

/**
 * Get rank medal/icon
 */
const getRankMedal = (rank: number): string | null => {
  if (rank === 1) return '🥇';
  if (rank === 2) return '🥈';
  if (rank === 3) return '🥉';
  return null;
};

/**
 * LeagueStandings component
 */
export const LeagueStandings: React.FC<LeagueStandingsProps> = ({
  standings,
  loading = false,
  error = null,
  onTeamClick,
  className = '',
}) => {
  // Loading state
  if (loading) {
    return (
      <div className={`bg-white rounded-lg shadow-sm border border-gray-200 ${className}`}>
        <div className="px-6 py-4 border-b border-gray-200">
          <h2 className="text-lg font-semibold text-gray-900">League Standings</h2>
        </div>
        <div className="p-8 text-center">
          <div className="animate-pulse flex flex-col items-center">
            <div className="h-4 bg-gray-200 rounded w-32 mb-4"></div>
            <div className="h-4 bg-gray-200 rounded w-48 mb-2"></div>
            <div className="h-4 bg-gray-200 rounded w-48 mb-2"></div>
            <div className="h-4 bg-gray-200 rounded w-48"></div>
          </div>
          <p className="text-gray-500 mt-4">Loading standings...</p>
        </div>
      </div>
    );
  }

  // Error state
  if (error) {
    return (
      <div className={`bg-white rounded-lg shadow-sm border border-red-200 ${className}`}>
        <div className="px-6 py-4 border-b border-red-200 bg-red-50">
          <h2 className="text-lg font-semibold text-red-900">League Standings</h2>
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
  if (!standings || standings.length === 0) {
    return (
      <div className={`bg-white rounded-lg shadow-sm border border-gray-200 ${className}`}>
        <div className="px-6 py-4 border-b border-gray-200">
          <h2 className="text-lg font-semibold text-gray-900">League Standings</h2>
        </div>
        <div className="p-8 text-center">
          <div className="text-gray-400 mb-2">
            <svg className="w-12 h-12 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 17V7m0 10a2 2 0 01-2 2H5a2 2 0 01-2-2V7a2 2 0 012-2h2a2 2 0 012 2m0 10a2 2 0 002 2h2a2 2 0 002-2M9 7a2 2 0 012-2h2a2 2 0 012 2m0 10V7m0 10a2 2 0 002 2h2a2 2 0 002-2V7a2 2 0 00-2-2h-2a2 2 0 00-2 2" />
            </svg>
          </div>
          <p className="text-gray-500">No teams in the league yet.</p>
          <p className="text-gray-400 text-sm mt-1">Create teams to see standings.</p>
        </div>
      </div>
    );
  }

  return (
    <div className={`bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden ${className}`}>
      {/* Header */}
      <div className="px-6 py-4 border-b border-gray-200 bg-gray-50">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-semibold text-gray-900">League Standings</h2>
          <span className="text-sm text-gray-500">{standings.length} teams</span>
        </div>
      </div>

      {/* Standings Table */}
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th scope="col" className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider w-16">
                Rank
              </th>
              <th scope="col" className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Team
              </th>
              <th scope="col" className="px-4 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider w-16">
                W
              </th>
              <th scope="col" className="px-4 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider w-16">
                L
              </th>
              <th scope="col" className="px-4 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider w-20">
                PCT
              </th>
              <th scope="col" className="px-4 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider w-16">
                GP
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {standings.map((entry) => {
              const medal = getRankMedal(entry.rank);
              const gamesPlayed = getGamesPlayed(entry.wins, entry.losses);
              const winPct = calculateWinPercentage(entry.wins, entry.losses);
              const rankStyle = getRankStyle(entry.rank);
              
              return (
                <tr 
                  key={entry.team_id} 
                  className={`${rankStyle} ${onTeamClick ? 'cursor-pointer hover:bg-blue-50 transition-colors' : ''}`}
                  onClick={() => onTeamClick?.(entry.team_id)}
                  data-testid={`standings-row-${entry.team_id}`}
                >
                  {/* Rank */}
                  <td className="px-4 py-3 whitespace-nowrap">
                    <div className="flex items-center">
                      {medal ? (
                        <span className="text-lg" role="img" aria-label={`Rank ${entry.rank}`}>
                          {medal}
                        </span>
                      ) : (
                        <span className="text-sm text-gray-600 font-medium pl-1">
                          {entry.rank}
                        </span>
                      )}
                    </div>
                  </td>
                  
                  {/* Team Name */}
                  <td className="px-4 py-3 whitespace-nowrap">
                    <div className="text-sm font-medium text-gray-900">
                      {entry.team_name}
                    </div>
                  </td>
                  
                  {/* Wins */}
                  <td className="px-4 py-3 whitespace-nowrap text-center">
                    <span className="text-sm text-green-600 font-medium">
                      {entry.wins}
                    </span>
                  </td>
                  
                  {/* Losses */}
                  <td className="px-4 py-3 whitespace-nowrap text-center">
                    <span className="text-sm text-red-600 font-medium">
                      {entry.losses}
                    </span>
                  </td>
                  
                  {/* Win Percentage */}
                  <td className="px-4 py-3 whitespace-nowrap text-center">
                    <span className="text-sm text-gray-700 font-mono">
                      {winPct}
                    </span>
                  </td>
                  
                  {/* Games Played */}
                  <td className="px-4 py-3 whitespace-nowrap text-center">
                    <span className="text-sm text-gray-500">
                      {gamesPlayed}
                    </span>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      {/* Footer with legend */}
      <div className="px-6 py-3 bg-gray-50 border-t border-gray-200">
        <div className="flex flex-wrap gap-4 text-xs text-gray-500">
          <span><strong>W</strong> = Wins</span>
          <span><strong>L</strong> = Losses</span>
          <span><strong>PCT</strong> = Win Percentage</span>
          <span><strong>GP</strong> = Games Played</span>
        </div>
      </div>
    </div>
  );
};

export default LeagueStandings;
