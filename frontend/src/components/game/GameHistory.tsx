/**
 * GameHistory Component
 * 
 * Displays play-by-play event history from a completed game.
 * Shows chronological events with visual indicators for different event types.
 */

import React, { useState } from 'react';
import type { Game, GameEventType, Player } from '../../types';

interface GameHistoryProps {
  game: Game;
  players?: Record<string, Player>; // Optional player lookup for names
  className?: string;
  maxEvents?: number; // Limit displayed events (with show more button)
}

/**
 * Get display info for event type
 */
const getEventTypeInfo = (type: GameEventType): { icon: string; color: string; label: string } => {
  switch (type) {
    case 'throw':
      return { icon: '🎯', color: 'text-blue-600', label: 'Throw' };
    case 'hit':
      return { icon: '💥', color: 'text-red-600', label: 'Hit' };
    case 'catch':
      return { icon: '✋', color: 'text-green-600', label: 'Catch' };
    case 'miss':
      return { icon: '❌', color: 'text-gray-500', label: 'Miss' };
    case 'elimination':
      return { icon: '☠️', color: 'text-red-700', label: 'Eliminated' };
    default:
      return { icon: '📝', color: 'text-gray-600', label: 'Event' };
  }
};

/**
 * Get player name from ID
 */
const getPlayerName = (playerId: string | null, players?: Record<string, Player>): string => {
  if (!playerId) return 'Unknown';
  if (!players || !players[playerId]) return playerId;
  return players[playerId].name;
};

/**
 * Format turn number with leading zeros
 */
const formatTurn = (turn: number): string => {
  return `T${turn.toString().padStart(3, '0')}`;
};

/**
 * GameHistory component - Play-by-play event display
 */
export const GameHistory: React.FC<GameHistoryProps> = ({
  game,
  players,
  className = '',
  maxEvents,
}) => {
  const [showAll, setShowAll] = useState(false);

  // Determine which events to display
  const displayedEvents = maxEvents && !showAll
    ? game.events.slice(0, maxEvents)
    : game.events;

  const hasMoreEvents = maxEvents && game.events.length > maxEvents;

  // Check if game is completed
  const isCompleted = game.completed_at !== null;

  if (game.events.length === 0) {
    return (
      <div className={`bg-gray-50 border border-gray-200 rounded-lg p-6 ${className}`}>
        <div className="text-center">
          <div className="text-4xl mb-2">📋</div>
          <h3 className="text-lg font-semibold text-gray-700 mb-1">No Events Yet</h3>
          <p className="text-sm text-gray-500">
            {isCompleted 
              ? 'This game has no recorded events.'
              : 'The game hasn\'t started or events are still being recorded.'}
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className={`bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden ${className}`}>
      {/* Header */}
      <div className="bg-gradient-to-r from-slate-700 to-slate-800 px-6 py-4">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-xl font-bold text-white">Play-by-Play</h3>
            <p className="text-slate-300 text-sm mt-1">
              {game.events.length} event{game.events.length !== 1 ? 's' : ''} recorded
            </p>
          </div>
          {isCompleted && (
            <div className="text-green-400 text-sm font-medium flex items-center gap-2">
              <span className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></span>
              Complete
            </div>
          )}
        </div>
      </div>

      {/* Event Timeline */}
      <div className="p-6">
        <div className="space-y-3">
          {displayedEvents.map((event, index) => {
            const typeInfo = getEventTypeInfo(event.type);
            const throwerName = getPlayerName(event.thrower_id, players);
            const targetName = getPlayerName(event.target_id, players);

            return (
              <div
                key={`${event.turn}-${index}`}
                className="flex items-start gap-4 p-3 bg-gray-50 rounded-lg border border-gray-200 hover:bg-gray-100 transition-colors"
              >
                {/* Turn Number */}
                <div className="flex-shrink-0 w-16 text-center">
                  <div className="text-xs font-mono font-bold text-gray-500 bg-white px-2 py-1 rounded border border-gray-200">
                    {formatTurn(event.turn)}
                  </div>
                </div>

                {/* Event Icon */}
                <div className="flex-shrink-0 text-2xl">
                  {typeInfo.icon}
                </div>

                {/* Event Details */}
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-1">
                    <span className={`text-sm font-semibold ${typeInfo.color}`}>
                      {typeInfo.label}
                    </span>
                    {(event.thrower_id || event.target_id) && (
                      <span className="text-xs text-gray-400">•</span>
                    )}
                    {event.thrower_id && (
                      <span className="text-xs text-gray-600">
                        from <span className="font-medium">{throwerName}</span>
                      </span>
                    )}
                    {event.target_id && (
                      <span className="text-xs text-gray-600">
                        to <span className="font-medium">{targetName}</span>
                      </span>
                    )}
                  </div>
                  <p className="text-sm text-gray-700">
                    {event.outcome}
                  </p>
                </div>
              </div>
            );
          })}
        </div>

        {/* Show More Button */}
        {hasMoreEvents && !showAll && (
          <button
            onClick={() => setShowAll(true)}
            className="w-full mt-4 px-4 py-2 bg-blue-50 hover:bg-blue-100 text-blue-700 font-medium rounded-lg border border-blue-200 transition-colors"
          >
            Show All Events ({game.events.length - displayedEvents.length} more)
          </button>
        )}

        {/* Show Less Button */}
        {hasMoreEvents && showAll && (
          <button
            onClick={() => setShowAll(false)}
            className="w-full mt-4 px-4 py-2 bg-gray-50 hover:bg-gray-100 text-gray-700 font-medium rounded-lg border border-gray-200 transition-colors"
          >
            Show Less
          </button>
        )}
      </div>

      {/* Summary Footer */}
      {isCompleted && (
        <div className="bg-gray-50 border-t border-gray-200 px-6 py-4">
          <div className="flex items-center justify-between text-sm">
            <span className="text-gray-600">
              Game duration: <span className="font-semibold text-gray-900">
                {Math.max(...game.events.map(e => e.turn))} turns
              </span>
            </span>
            {game.seed !== null && game.seed !== undefined && (
              <span className="text-gray-500 text-xs font-mono">
                Seed: {game.seed}
              </span>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default GameHistory;
