/**
 * GameStats Component
 * 
 * Displays aggregate statistics and key metrics from a completed game.
 * Shows team comparisons, player highlights, and game analysis.
 */

import React from 'react';
import type { Game, Player } from '../../types';

interface GameStatsProps {
  game: Game;
  team1Name?: string;
  team2Name?: string;
  team1Logo?: string;
  team2Logo?: string;
  players?: Record<string, Player>; // Optional player lookup
  className?: string;
}

/**
 * Calculate statistics from game events
 */
const calculateGameStats = (game: Game) => {
  const team1Stats = {
    throws: 0,
    hits: 0,
    catches: 0,
    misses: 0,
    eliminations: 0, // Eliminations this team CAUSED (opponents eliminated)
  };

  const team2Stats = {
    throws: 0,
    hits: 0,
    catches: 0,
    misses: 0,
    eliminations: 0, // Eliminations this team CAUSED (opponents eliminated)
  };

  // Guard: Check if events exist
  if (!game.events) {
    return { team1Stats, team2Stats };
  }

  // Count events per team
  game.events.forEach(event => {
    const throwerIsTeam1 = event.thrower_id ? game.team1_starters.includes(event.thrower_id) : false;
    const targetIsTeam1 = event.target_id ? game.team1_starters.includes(event.target_id) : false;
    
    switch (event.type) {
      case 'throw':
        if (throwerIsTeam1) team1Stats.throws++;
        else team2Stats.throws++;
        break;
      case 'hit':
        if (throwerIsTeam1) team1Stats.hits++;
        else team2Stats.hits++;
        break;
      case 'catch':
        // Catch is attributed to the catcher (target of throw)
        if (targetIsTeam1) team1Stats.catches++;
        else team2Stats.catches++;
        break;
      case 'miss':
        if (throwerIsTeam1) team1Stats.misses++;
        else team2Stats.misses++;
        break;
      case 'elimination':
        // Count eliminations caused by each team
        // If target was eliminated and is on team1, team2 gets credit
        if (targetIsTeam1) {
          team2Stats.eliminations++;
        } else {
          team1Stats.eliminations++;
        }
        break;
    }
  });

  return { team1Stats, team2Stats };
};

/**
 * Calculate accuracy percentage
 */
const calculateAccuracy = (hits: number, throws: number): string => {
  if (throws === 0) return '0%';
  return `${((hits / throws) * 100).toFixed(1)}%`;
};

/**
 * GameStats component - Comprehensive game statistics display
 */
export const GameStats: React.FC<GameStatsProps> = ({
  game,
  team1Name = 'Team 1',
  team2Name = 'Team 2',
  team1Logo,
  team2Logo,
  className = '',
}) => {
  // Guard: Check if events are loaded
  if (!game.events) {
    return (
      <div className={`bg-yellow-50 border border-yellow-200 rounded-lg p-6 ${className}`}>
        <div className="text-center">
          <div className="text-4xl mb-2">⏳</div>
          <h3 className="text-lg font-semibold text-yellow-700 mb-1">Loading Game Details...</h3>
          <p className="text-sm text-yellow-600">
            Game statistics are being loaded.
          </p>
        </div>
      </div>
    );
  }

  const { team1Stats, team2Stats } = calculateGameStats(game);
  
  const team1Accuracy = calculateAccuracy(team1Stats.hits, team1Stats.throws);
  const team2Accuracy = calculateAccuracy(team2Stats.hits, team2Stats.throws);
  
  const gameDuration = game.events.length > 0 
    ? Math.max(...game.events.map(e => e.turn))
    : 0;

  const isCompleted = game.completed_at !== null;
  const team1Won = game.winner_id === game.team1_id;

  if (game.events.length === 0) {
    return (
      <div className={`bg-gray-50 border border-gray-200 rounded-lg p-6 ${className}`}>
        <div className="text-center">
          <div className="text-4xl mb-2">📊</div>
          <h3 className="text-lg font-semibold text-gray-700 mb-1">No Statistics Available</h3>
          <p className="text-sm text-gray-500">
            Statistics will appear once the game has been played.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className={`bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden ${className}`}>
      {/* Header */}
      <div className="bg-gradient-to-r from-emerald-600 to-teal-600 px-6 py-4">
        <h3 className="text-xl font-bold text-white">Game Statistics</h3>
        <p className="text-emerald-100 text-sm mt-1">
          Performance analysis and key metrics
        </p>
      </div>

      {/* Winner Banner (if completed) */}
      {isCompleted && game.winner_id && (
        <div className={`px-6 py-4 ${team1Won ? 'bg-blue-50' : 'bg-purple-50'} border-b ${team1Won ? 'border-blue-200' : 'border-purple-200'}`}>
          <div className="flex items-center justify-center gap-2">
            <span className="text-2xl">🏆</span>
            <span className={`font-bold text-lg ${team1Won ? 'text-blue-900' : 'text-purple-900'}`}>
              {team1Won ? team1Name : team2Name} Wins!
            </span>
          </div>
        </div>
      )}

      <div className="p-6 space-y-6">
        {/* Team Names */}
        <div className="flex items-center justify-between text-center">
          <div className="flex-1">
            <div className="w-16 h-16 mx-auto mb-2 bg-gradient-to-br from-blue-500 to-blue-600 rounded-full flex items-center justify-center text-white font-bold text-2xl shadow-lg overflow-hidden">
              {team1Logo ? (
                <img 
                  src={`/images/team_avatars/${team1Logo}`} 
                  alt={team1Name}
                  className="w-full h-full object-cover"
                />
              ) : (
                team1Name.charAt(0)
              )}
            </div>
            <h4 className="font-bold text-gray-900">{team1Name}</h4>
            {team1Won && <span className="text-xs text-blue-600 font-semibold">WINNER</span>}
          </div>
          <div className="text-2xl text-gray-400 mx-4">VS</div>
          <div className="flex-1">
            <div className="w-16 h-16 mx-auto mb-2 bg-gradient-to-br from-purple-500 to-purple-600 rounded-full flex items-center justify-center text-white font-bold text-2xl shadow-lg overflow-hidden">
              {team2Logo ? (
                <img 
                  src={`/images/team_avatars/${team2Logo}`} 
                  alt={team2Name}
                  className="w-full h-full object-cover"
                />
              ) : (
                team2Name.charAt(0)
              )}
            </div>
            <h4 className="font-bold text-gray-900">{team2Name}</h4>
            {!team1Won && isCompleted && <span className="text-xs text-purple-600 font-semibold">WINNER</span>}
          </div>
        </div>

        {/* Key Stats Grid */}
        <div className="grid grid-cols-2 gap-4">
          <div className="bg-blue-50 rounded-lg p-4 text-center border border-blue-200">
            <div className="text-3xl font-bold text-blue-900">{team1Stats.eliminations}</div>
            <div className="text-xs text-blue-700 font-medium mt-1">Eliminations</div>
          </div>
          <div className="bg-purple-50 rounded-lg p-4 text-center border border-purple-200">
            <div className="text-3xl font-bold text-purple-900">{team2Stats.eliminations}</div>
            <div className="text-xs text-purple-700 font-medium mt-1">Eliminations</div>
          </div>
        </div>

        {/* Detailed Statistics */}
        <div className="space-y-4 pt-4 border-t border-gray-200">
          <h4 className="text-sm font-semibold text-gray-700 uppercase text-center">Performance Breakdown</h4>

          <div className="grid grid-cols-2 gap-4">
            {/* Team 1 Stats */}
            <div className="space-y-2">
              <h5 className="text-xs font-semibold text-blue-700 uppercase text-center mb-2">{team1Name}</h5>
              
              <div className="flex justify-between items-center p-2 bg-blue-50 rounded-lg border border-blue-200">
                <span className="text-xs font-medium text-gray-700">Throws</span>
                <span className="text-sm font-bold text-blue-900">{team1Stats.throws}</span>
              </div>

              <div className="flex justify-between items-center p-2 bg-blue-50 rounded-lg border border-blue-200">
                <span className="text-xs font-medium text-gray-700">Hits</span>
                <span className="text-sm font-bold text-blue-900">{team1Stats.hits}</span>
              </div>

              <div className="flex justify-between items-center p-2 bg-blue-50 rounded-lg border border-blue-200">
                <span className="text-xs font-medium text-gray-700">Catches</span>
                <span className="text-sm font-bold text-blue-900">{team1Stats.catches}</span>
              </div>

              <div className="flex justify-between items-center p-2 bg-blue-50 rounded-lg border border-blue-200">
                <span className="text-xs font-medium text-gray-700">Misses</span>
                <span className="text-sm font-bold text-blue-900">{team1Stats.misses}</span>
              </div>

              <div className="flex justify-between items-center p-2 bg-blue-50 rounded-lg border border-blue-200">
                <span className="text-xs font-medium text-gray-700">Accuracy</span>
                <span className="text-sm font-bold text-blue-900">{team1Accuracy}</span>
              </div>
            </div>

            {/* Team 2 Stats */}
            <div className="space-y-2">
              <h5 className="text-xs font-semibold text-purple-700 uppercase text-center mb-2">{team2Name}</h5>
              
              <div className="flex justify-between items-center p-2 bg-purple-50 rounded-lg border border-purple-200">
                <span className="text-xs font-medium text-gray-700">Throws</span>
                <span className="text-sm font-bold text-purple-900">{team2Stats.throws}</span>
              </div>

              <div className="flex justify-between items-center p-2 bg-purple-50 rounded-lg border border-purple-200">
                <span className="text-xs font-medium text-gray-700">Hits</span>
                <span className="text-sm font-bold text-purple-900">{team2Stats.hits}</span>
              </div>

              <div className="flex justify-between items-center p-2 bg-purple-50 rounded-lg border border-purple-200">
                <span className="text-xs font-medium text-gray-700">Catches</span>
                <span className="text-sm font-bold text-purple-900">{team2Stats.catches}</span>
              </div>

              <div className="flex justify-between items-center p-2 bg-purple-50 rounded-lg border border-purple-200">
                <span className="text-xs font-medium text-gray-700">Misses</span>
                <span className="text-sm font-bold text-purple-900">{team2Stats.misses}</span>
              </div>

              <div className="flex justify-between items-center p-2 bg-purple-50 rounded-lg border border-purple-200">
                <span className="text-xs font-medium text-gray-700">Accuracy</span>
                <span className="text-sm font-bold text-purple-900">{team2Accuracy}</span>
              </div>
            </div>
          </div>
        </div>

        {/* Game Metadata */}
        <div className="pt-4 border-t border-gray-200">
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div className="bg-gray-50 rounded-lg p-3">
              <div className="text-gray-500 text-xs mb-1">Game Duration</div>
              <div className="font-semibold text-gray-900">{gameDuration} turns</div>
            </div>
            <div className="bg-gray-50 rounded-lg p-3">
              <div className="text-gray-500 text-xs mb-1">Total Events</div>
              <div className="font-semibold text-gray-900">{game.events?.length || 0}</div>
            </div>
          </div>
        </div>

        {/* Seed Info (if available) */}
        {game.seed !== null && game.seed !== undefined && (
          <div className="bg-slate-50 border border-slate-200 rounded-lg p-3 text-center">
            <span className="text-xs text-slate-600">
              Simulation Seed: <span className="font-mono font-semibold text-slate-800">{game.seed}</span>
            </span>
            <p className="text-xs text-slate-500 mt-1">
              Use this seed to reproduce the exact same game result
            </p>
          </div>
        )}
      </div>
    </div>
  );
};

export default GameStats;
