/**
 * TeamRoster Component
 * 
 * Displays and manages a team's roster:
 * - Shows all players on the team
 * - Allows designating/removing starters with quick action buttons
 * - Supports removing players from roster
 * - Shows roster size and starter count constraints
 * - Displays budget impact of roster changes
 * 
 * Used in team management interfaces.
 */

import React from 'react';
import type { Team, Player } from '../../types';
import { PlayerCard } from '../player/PlayerCard';

interface TeamRosterProps {
  team: Team;
  players: Player[];
  onAddPlayer?: (playerId: string) => void;
  onRemovePlayer?: (playerId: string) => void;
  onSetStarters?: (starterIds: string[]) => void;
  readonly?: boolean;
  className?: string;
}

/**
 * TeamRoster component
 */
export const TeamRoster: React.FC<TeamRosterProps> = ({
  team,
  players,
  onAddPlayer,
  onRemovePlayer,
  onSetStarters,
  readonly = false,
  className = '',
}) => {
  const rosterSize = team.player_ids.length;
  const starterCount = team.starter_ids.length;
  const canRemovePlayer = rosterSize > 8;
  const needsStarters = starterCount < 5;
  const startersFull = starterCount >= 5;

  // Get players on this team
  const rosterPlayers = players.filter((p) => team.player_ids.includes(p.id));
  const starters = rosterPlayers.filter((p) => team.starter_ids.includes(p.id));
  const bench = rosterPlayers.filter((p) => !team.starter_ids.includes(p.id));

  /**
   * Make a player a starter
   */
  const handleMakeStarter = (playerId: string) => {
    if (readonly || !onSetStarters || startersFull) return;

    const newStarters = [...team.starter_ids, playerId];
    onSetStarters(newStarters);
  };

  /**
   * Move a player to bench
   */
  const handleBenchPlayer = (playerId: string) => {
    if (readonly || !onSetStarters) return;

    const newStarters = team.starter_ids.filter(id => id !== playerId);
    onSetStarters(newStarters);
  };

  /**
   * Handle removing a player from roster
   */
  const handleRemovePlayer = (playerId: string) => {
    if (readonly || !onRemovePlayer || !canRemovePlayer) return;

    onRemovePlayer(playerId);
  };

  return (
    <div className={`space-y-4 ${className}`}>
      {/* Roster Header */}
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-lg font-semibold text-gray-900">Team Roster</h3>
          <p className="text-sm text-gray-600">
            {rosterSize}/12 players • {starterCount}/5 starters
          </p>
        </div>
        {!readonly && needsStarters && (
          <div className="px-3 py-1 bg-orange-100 text-orange-800 rounded text-sm font-medium">
            ⚠️ Set 5 starters
          </div>
        )}
      </div>

      {/* Empty Roster */}
      {rosterSize === 0 && (
        <div className="text-center py-12 bg-gray-50 rounded-lg border-2 border-dashed border-gray-300">
          <div className="text-4xl mb-3">👥</div>
          <h4 className="font-semibold text-gray-900 mb-2">No Players Yet</h4>
          <p className="text-sm text-gray-600 mb-4">
            Add players to your roster to get started
          </p>
          {onAddPlayer && (
            <button
              onClick={() => onAddPlayer('')}
              className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors"
            >
              Browse Players
            </button>
          )}
        </div>
      )}

      {/* Starters Section */}
      {starters.length > 0 && (
        <div>
          <h4 className="font-semibold text-gray-800 mb-3 flex items-center gap-2">
            <span className="px-2 py-0.5 text-xs bg-blue-100 text-blue-800 rounded font-medium">
              STARTERS
            </span>
            <span className="text-sm text-gray-600">
              ({starters.length}/5)
            </span>
          </h4>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {starters.map((player) => (
              <div key={player.id} className="relative">
                <PlayerCard
                  player={player}
                  showStats={false}
                />
                {!readonly && (
                  <div className="absolute top-2 right-2 flex gap-1">
                    {onSetStarters && (
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          handleBenchPlayer(player.id);
                        }}
                        className="px-3 py-1.5 text-xs font-medium bg-gray-600 text-white rounded hover:bg-gray-700 transition-colors shadow-md"
                        title="Move to bench"
                      >
                        Bench
                      </button>
                    )}
                    {onRemovePlayer && canRemovePlayer && (
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          handleRemovePlayer(player.id);
                        }}
                        className="w-7 h-7 bg-red-600 text-white rounded hover:bg-red-700 transition-colors flex items-center justify-center shadow-md"
                        title="Remove from roster"
                      >
                        ×
                      </button>
                    )}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Bench Section */}
      {bench.length > 0 && (
        <div>
          <h4 className="font-semibold text-gray-800 mb-3 flex items-center gap-2">
            <span className="px-2 py-0.5 text-xs bg-gray-100 text-gray-800 rounded font-medium">
              BENCH
            </span>
            <span className="text-sm text-gray-600">
              ({bench.length})
            </span>
          </h4>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {bench.map((player) => (
              <div key={player.id} className="relative">
                <PlayerCard
                  player={player}
                  showStats={false}
                />
                {!readonly && (
                  <div className="absolute top-2 right-2 flex gap-1">
                    {onSetStarters && (
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          handleMakeStarter(player.id);
                        }}
                        disabled={startersFull}
                        className={`px-3 py-1.5 text-xs font-medium rounded transition-colors shadow-md ${
                          startersFull
                            ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                            : 'bg-blue-600 text-white hover:bg-blue-700'
                        }`}
                        title={startersFull ? 'Starting lineup is full (5/5)' : 'Make starter'}
                      >
                        Make Starter
                      </button>
                    )}
                    {onRemovePlayer && canRemovePlayer && (
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          handleRemovePlayer(player.id);
                        }}
                        className="w-7 h-7 bg-red-600 text-white rounded hover:bg-red-700 transition-colors flex items-center justify-center shadow-md"
                        title="Remove from roster"
                      >
                        ×
                      </button>
                    )}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Roster Constraints Info */}
      <div className="p-3 bg-gray-50 rounded-lg border border-gray-200">
        <h5 className="text-xs font-semibold text-gray-700 uppercase mb-2">
          Roster Rules
        </h5>
        <ul className="text-sm text-gray-600 space-y-1">
          <li className={rosterSize >= 8 ? 'text-green-600' : 'text-red-600'}>
            • Minimum 8 players required {rosterSize >= 8 ? '✓' : `(need ${8 - rosterSize} more)`}
          </li>
          <li className={rosterSize <= 12 ? 'text-green-600' : 'text-red-600'}>
            • Maximum 12 players allowed {rosterSize <= 12 ? '✓' : '(over limit)'}
          </li>
          <li className={starterCount === 5 ? 'text-green-600' : 'text-orange-600'}>
            • Exactly 5 starters required {starterCount === 5 ? '✓' : `(have ${starterCount})`}
          </li>
          {!canRemovePlayer && rosterSize > 0 && (
            <li className="text-blue-600">
              • Cannot remove players below minimum roster size
            </li>
          )}
        </ul>
      </div>
    </div>
  );
};

export default TeamRoster;
