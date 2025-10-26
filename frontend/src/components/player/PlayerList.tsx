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
import type { Player } from '../../types';

interface PlayerListProps {
  players: Player[];
  onPlayerClick?: (player: Player) => void;
  showStats?: boolean;
  showTeamInfo?: boolean;
  loading?: boolean;
  emptyMessage?: string;
  className?: string;
}

type SortField = 'name' | 'age' | 'value' | 'total_skills';
type SortDirection = 'asc' | 'desc';
type ViewMode = 'grid' | 'list';

/**
 * PlayerList component
 */
export const PlayerList: React.FC<PlayerListProps> = ({
  players,
  onPlayerClick,
  showStats = false,
  showTeamInfo = true,
  loading = false,
  emptyMessage = 'No players found',
  className = '',
}) => {
  // State for filtering and sorting
  const [searchQuery, setSearchQuery] = useState('');
  const [freeAgentsOnly, setFreeAgentsOnly] = useState(false);
  const [sortField, setSortField] = useState<SortField>('name');
  const [sortDirection, setSortDirection] = useState<SortDirection>('asc');
  const [viewMode, setViewMode] = useState<ViewMode>('grid');

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
      ) : (
        <div
          className={
            viewMode === 'grid'
              ? 'grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4'
              : 'space-y-4'
          }
        >
          {filteredAndSortedPlayers.map((player) => (
            <PlayerCard
              key={player.id}
              player={player}
              onClick={onPlayerClick}
              showStats={showStats}
              showTeamInfo={showTeamInfo}
              className={viewMode === 'list' ? 'w-full' : ''}
            />
          ))}
        </div>
      )}
    </div>
  );
};

export default PlayerList;
