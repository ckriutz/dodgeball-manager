/**
 * PlayerList Component
 * 
 * Displays a filterable and sortable list of players.
 * Features:
 * - Grid or list view toggle
 * - Filter by free agents only
 * - Sort by name, age, value, or skill
 * - Search by player name
 * - Loading and empty states
 * - Pagination for large player pools
 * 
 * Used on the players browsing page and team draft interface.
 */

import React, { useState, useMemo } from 'react';
import { PlayerCard } from './PlayerCard';
import { leagueApi } from '../../services/api';
import type { Player, Team } from '../../types';

interface PlayerListProps {
  players: Player[];
  teams?: Team[];
  onPlayerClick?: (player: Player) => void;
  showStats?: boolean;
  loading?: boolean;
  emptyMessage?: string;
  className?: string;
  // Action button configuration for each card
  actionButton?: {
    label: string;
    onClick: (player: Player) => void;
    variant?: 'primary' | 'success' | 'danger';
    isDisabled?: (player: Player) => boolean;
  };
  // League ID for generating new players
  leagueId?: string;
  // Callback for when a new player is generated
  onPlayerGenerated?: () => void;
}

type SortField = 'name' | 'age' | 'value' | 'total_skills';
type SortDirection = 'asc' | 'desc';
type ViewMode = 'grid' | 'list';

/**
 * PlayerList component
 */
export const PlayerList: React.FC<PlayerListProps> = ({
  players,
  teams = [],
  onPlayerClick,
  showStats = false,
  loading = false,
  emptyMessage = 'No players found',
  className = '',
  actionButton,
  leagueId,
  onPlayerGenerated,
}) => {
  // State for filtering and sorting
  const [searchQuery, setSearchQuery] = useState('');
  const [freeAgentsOnly, setFreeAgentsOnly] = useState(false);
  const [sortField, setSortField] = useState<SortField>('name');
  const [sortDirection, setSortDirection] = useState<SortDirection>('asc');
  const [viewMode, setViewMode] = useState<ViewMode>('grid');
  const [generating, setGenerating] = useState(false);

  /**
   * Handle generating a new player
   */
  const handleGenerateNewPlayer = async () => {
    if (!leagueId) return;

    setGenerating(true);
    try {
      // Generate 1 player
      await leagueApi.generatePlayers(leagueId, 1);
      // Notify parent component to reload players
      onPlayerGenerated?.();
    } catch (err) {
      console.error('Failed to generate new player:', err);
    } finally {
      setGenerating(false);
    }
  };

  // Helper function to get team name
  const getTeamName = (teamId: string | null): string => {
    if (!teamId) return 'Free Agent';
    const team = teams.find(t => t.id === teamId);
    return team ? team.name : 'Unknown Team';
  };

  // Filter and sort players
  const filteredAndSortedPlayers = useMemo(() => {
    let filtered = [...players];

    // Apply search filter
    if (searchQuery) {
      const query = searchQuery.toLowerCase();
      filtered = filtered.filter((player) =>
        player.name.toLowerCase().includes(query)
      );
    }

    // Apply free agents filter
    if (freeAgentsOnly) {
      filtered = filtered.filter((player) => player.team_id === null);
    }

    // Apply sorting
    filtered.sort((a, b) => {
      let aValue: number | string;
      let bValue: number | string;

      switch (sortField) {
        case 'name':
          aValue = a.name.toLowerCase();
          bValue = b.name.toLowerCase();
          break;
        case 'age':
          aValue = a.age;
          bValue = b.age;
          break;
        case 'value':
          aValue = a.value;
          bValue = b.value;
          break;
        case 'total_skills':
          aValue = Object.values(a.skills).reduce((sum, val) => sum + val, 0);
          bValue = Object.values(b.skills).reduce((sum, val) => sum + val, 0);
          break;
        default:
          return 0;
      }

      if (aValue < bValue) return sortDirection === 'asc' ? -1 : 1;
      if (aValue > bValue) return sortDirection === 'asc' ? 1 : -1;
      return 0;
    });

    return filtered;
  }, [players, searchQuery, freeAgentsOnly, sortField, sortDirection]);

  // Handle sort change
  const handleSortChange = (field: SortField) => {
    if (sortField === field) {
      // Toggle direction if same field
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
    } else {
      // Set new field with ascending direction
      setSortField(field);
      setSortDirection('asc');
    }
  };

  // Get sort indicator
  const getSortIndicator = (field: SortField) => {
    if (sortField !== field) return null;
    return sortDirection === 'asc' ? ' ↑' : ' ↓';
  };

  // Loading state
  if (loading) {
    return (
      <div className={`flex items-center justify-center py-12 ${className}`}>
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mb-4"></div>
          <p className="text-gray-600">Loading players...</p>
        </div>
      </div>
    );
  }

  // Empty state
  if (players.length === 0) {
    return (
      <div className={`flex items-center justify-center py-12 ${className}`}>
        <div className="text-center">
          <svg
            className="mx-auto h-12 w-12 text-gray-400 mb-4"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z"
            />
          </svg>
          <p className="text-gray-600">{emptyMessage}</p>
        </div>
      </div>
    );
  }

  return (
    <div className={className}>
      {/* Controls Bar */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4 mb-4">
        <div className="flex flex-col sm:flex-row gap-4">
          {/* Search */}
          <div className="flex-1">
            <input
              type="text"
              placeholder="Search players by name..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>

          {/* Filter: Free Agents */}
          <div className="flex items-center gap-2">
            <input
              type="checkbox"
              id="free-agents-filter"
              checked={freeAgentsOnly}
              onChange={(e) => setFreeAgentsOnly(e.target.checked)}
              className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
            />
            <label htmlFor="free-agents-filter" className="text-sm text-gray-700 whitespace-nowrap">
              Free Agents Only
            </label>
          </div>

          {/* Generate New Player Button */}
          {leagueId && (
            <button
              onClick={handleGenerateNewPlayer}
              disabled={generating}
              className="inline-flex items-center gap-2 px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed whitespace-nowrap"
            >
              {generating ? (
                <>
                  <svg className="animate-spin h-4 w-4" fill="none" viewBox="0 0 24 24">
                    <circle
                      className="opacity-25"
                      cx="12"
                      cy="12"
                      r="10"
                      stroke="currentColor"
                      strokeWidth="4"
                    />
                    <path
                      className="opacity-75"
                      fill="currentColor"
                      d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                    />
                  </svg>
                  <span>Generating...</span>
                </>
              ) : (
                <>
                  <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M12 6v6m0 0v6m0-6h6m-6 0H6"
                    />
                  </svg>
                  <span>New Player</span>
                </>
              )}
            </button>
          )}

          {/* View Mode Toggle */}
          <div className="flex items-center gap-2 border border-gray-300 rounded-lg overflow-hidden">
            <button
              onClick={() => setViewMode('grid')}
              className={`px-3 py-2 text-sm font-medium ${
                viewMode === 'grid'
                  ? 'bg-blue-600 text-white'
                  : 'bg-white text-gray-700 hover:bg-gray-50'
              }`}
            >
              Grid
            </button>
            <button
              onClick={() => setViewMode('list')}
              className={`px-3 py-2 text-sm font-medium ${
                viewMode === 'list'
                  ? 'bg-blue-600 text-white'
                  : 'bg-white text-gray-700 hover:bg-gray-50'
              }`}
            >
              List
            </button>
          </div>
        </div>

        {/* Sort Options */}
        <div className="flex flex-wrap gap-2 mt-4">
          <span className="text-sm text-gray-600 py-2">Sort by:</span>
          <button
            onClick={() => handleSortChange('name')}
            className="px-3 py-1 text-sm font-medium rounded border border-gray-300 hover:bg-gray-50"
          >
            Name{getSortIndicator('name')}
          </button>
          <button
            onClick={() => handleSortChange('age')}
            className="px-3 py-1 text-sm font-medium rounded border border-gray-300 hover:bg-gray-50"
          >
            Age{getSortIndicator('age')}
          </button>
          <button
            onClick={() => handleSortChange('value')}
            className="px-3 py-1 text-sm font-medium rounded border border-gray-300 hover:bg-gray-50"
          >
            Value{getSortIndicator('value')}
          </button>
          <button
            onClick={() => handleSortChange('total_skills')}
            className="px-3 py-1 text-sm font-medium rounded border border-gray-300 hover:bg-gray-50"
          >
            Skills{getSortIndicator('total_skills')}
          </button>
        </div>

        {/* Results Count */}
        <div className="mt-4 text-sm text-gray-600">
          Showing {filteredAndSortedPlayers.length} of {players.length} players
          {freeAgentsOnly && ' (free agents only)'}
        </div>
      </div>

      {/* Player Grid/List */}
      {filteredAndSortedPlayers.length === 0 ? (
        <div className="text-center py-8">
          <p className="text-gray-600">No players match your filters</p>
          <button
            onClick={() => {
              setSearchQuery('');
              setFreeAgentsOnly(false);
            }}
            className="mt-4 text-blue-600 hover:text-blue-700 font-medium"
          >
            Clear Filters
          </button>
        </div>
      ) : viewMode === 'list' ? (
        /* Table List View */
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Name
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Assigned Team
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Age
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Value
                  </th>
                  {actionButton && (
                    <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Action
                    </th>
                  )}
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {filteredAndSortedPlayers.map((player) => (
                  <tr
                    key={player.id}
                    className={`hover:bg-gray-50 ${onPlayerClick ? 'cursor-pointer' : ''}`}
                    onClick={() => onPlayerClick?.(player)}
                  >
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center">
                        <div className="flex-shrink-0 h-10 w-10">
                          <img
                            className="h-10 w-10 rounded-full"
                            src={player.avatar}
                            alt={player.name}
                          />
                        </div>
                        <div className="ml-4">
                          <div className="text-sm font-medium text-gray-900">
                            {player.name}
                          </div>
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span
                        className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                          player.team_id === null
                            ? 'bg-green-100 text-green-800'
                            : 'bg-blue-100 text-blue-800'
                        }`}
                      >
                        {getTeamName(player.team_id)}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {player.age}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      ${player.value.toLocaleString()}
                    </td>
                    {actionButton && (
                      <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            actionButton.onClick(player);
                          }}
                          disabled={actionButton.isDisabled?.(player) || false}
                          className={`inline-flex items-center px-3 py-1 border border-transparent text-xs font-medium rounded ${
                            actionButton.variant === 'success'
                              ? 'text-green-700 bg-green-100 hover:bg-green-200'
                              : actionButton.variant === 'danger'
                              ? 'text-red-700 bg-red-100 hover:bg-red-200'
                              : 'text-blue-700 bg-blue-100 hover:bg-blue-200'
                          } disabled:opacity-50 disabled:cursor-not-allowed`}
                        >
                          {actionButton.label}
                        </button>
                      </td>
                    )}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      ) : (
        /* Grid View */
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {filteredAndSortedPlayers.map((player) => (
            <PlayerCard
              key={player.id}
              player={player}
              onClick={onPlayerClick}
              showStats={showStats}
              teamName={getTeamName(player.team_id)}
              className=""
              actionButton={
                actionButton
                  ? {
                      label: actionButton.label,
                      onClick: actionButton.onClick,
                      variant: actionButton.variant,
                      disabled: actionButton.isDisabled?.(player) || false,
                    }
                  : undefined
              }
            />
          ))}
        </div>
      )}
    </div>
  );
};

export default PlayerList;
