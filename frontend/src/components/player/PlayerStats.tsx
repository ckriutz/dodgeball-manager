/**
 * PlayerStats Component
 * 
 * Displays detailed statistics for a player, including career stats,
 * performance metrics, and skill breakdown.
 */

import React from 'react';
import type { Player } from '../../types';

interface PlayerStatsProps {
  player: Player;
  className?: string;
  compact?: boolean; // Compact mode for smaller displays
}

/**
 * Calculate derived statistics
 */
const calculateDerivedStats = (player: Player) => {
  const { stats } = player;
  
  const accuracy = stats.throws_attempted > 0
    ? ((stats.successful_hits / stats.throws_attempted) * 100).toFixed(1)
    : '0.0';
  
  const catchRate = (stats.throws_attempted - stats.successful_hits) > 0
    ? ((stats.catches_made / (stats.throws_attempted - stats.successful_hits)) * 100).toFixed(1)
    : '0.0';
  
  const hitRate = stats.throws_attempted > 0
    ? ((stats.times_hit / stats.throws_attempted) * 100).toFixed(1)
    : '0.0';

  const totalGames = Math.ceil(stats.throws_attempted / 10) || 0; // Rough estimate

  return {
    accuracy: `${accuracy}%`,
    catchRate: `${catchRate}%`,
    hitRate: `${hitRate}%`,
    totalGames,
  };
};

/**
 * Get skill color based on value
 */
const getSkillColor = (value: number): string => {
  if (value >= 8) return 'bg-green-500';
  if (value >= 6) return 'bg-blue-500';
  if (value >= 4) return 'bg-yellow-500';
  if (value >= 2) return 'bg-orange-500';
  return 'bg-red-500';
};

/**
 * SkillBar - Visual skill level indicator
 */
const SkillBar: React.FC<{ name: string; value: number; maxValue?: number }> = ({
  name,
  value,
  maxValue = 10,
}) => {
  const percentage = (value / maxValue) * 100;
  const color = getSkillColor(value);

  return (
    <div>
      <div className="flex justify-between items-center mb-1">
        <span className="text-sm text-gray-700 capitalize font-medium">{name}</span>
        <span className="text-sm font-bold text-gray-900">{value}/{maxValue}</span>
      </div>
      <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
        <div
          className={`h-full ${color} transition-all duration-300 rounded-full`}
          style={{ width: `${percentage}%` }}
        />
      </div>
    </div>
  );
};

/**
 * StatCard - Compact stat display
 */
const StatCard: React.FC<{ label: string; value: string | number; icon?: string }> = ({
  label,
  value,
  icon,
}) => (
  <div className="bg-gray-50 rounded-lg p-3 text-center border border-gray-200">
    {icon && <div className="text-2xl mb-1">{icon}</div>}
    <div className="text-2xl font-bold text-gray-900">{value}</div>
    <div className="text-xs text-gray-600 mt-1">{label}</div>
  </div>
);

/**
 * PlayerStats component - Comprehensive player statistics
 */
export const PlayerStats: React.FC<PlayerStatsProps> = ({
  player,
  className = '',
  compact = false,
}) => {
  const derived = calculateDerivedStats(player);
  const { stats, skills, injury } = player;

  // Check if player has any game history
  const hasGameHistory = stats.throws_attempted > 0;

  if (compact) {
    // Compact view - just key numbers
    return (
      <div className={`bg-white rounded-lg border border-gray-200 p-4 ${className}`}>
        <h4 className="text-sm font-semibold text-gray-700 mb-3">Quick Stats</h4>
        <div className="grid grid-cols-3 gap-2 text-center text-xs">
          <div>
            <div className="font-bold text-gray-900">{stats.successful_hits}</div>
            <div className="text-gray-500">Hits</div>
          </div>
          <div>
            <div className="font-bold text-gray-900">{stats.catches_made}</div>
            <div className="text-gray-500">Catches</div>
          </div>
          <div>
            <div className="font-bold text-gray-900">{derived.accuracy}</div>
            <div className="text-gray-500">Accuracy</div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className={`bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden ${className}`}>
      {/* Header */}
      <div className="bg-gradient-to-r from-indigo-600 to-blue-600 px-6 py-4">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-xl font-bold text-white">{player.name}</h3>
            <p className="text-indigo-200 text-sm mt-1">
              Player Statistics & Performance
            </p>
          </div>
          {injury && (
            <div className="bg-red-500 text-white px-3 py-1 rounded-full text-xs font-semibold">
              Injured
            </div>
          )}
        </div>
      </div>

      <div className="p-6 space-y-6">
        {/* Basic Info */}
        <div className="grid grid-cols-3 gap-4">
          <div className="text-center">
            <div className="text-sm text-gray-500 mb-1">Age</div>
            <div className="text-2xl font-bold text-gray-900">{player.age}</div>
          </div>
          <div className="text-center">
            <div className="text-sm text-gray-500 mb-1">Value</div>
            <div className="text-2xl font-bold text-green-600">
              ${player.value.toLocaleString()}
            </div>
          </div>
          <div className="text-center">
            <div className="text-sm text-gray-500 mb-1">Status</div>
            <div className="text-sm font-semibold text-gray-900">
              {player.is_starter ? '⭐ Starter' : 'Bench'}
            </div>
          </div>
        </div>

        {/* Career Stats */}
        <div className="border-t border-gray-200 pt-6">
          <h4 className="text-sm font-semibold text-gray-700 uppercase mb-4">Career Statistics</h4>
          
          {!hasGameHistory ? (
            <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 text-center">
              <div className="text-yellow-600 mb-2">⚠️</div>
              <p className="text-sm text-yellow-700">
                No game history yet. Stats will appear after playing games.
              </p>
            </div>
          ) : (
            <>
              {/* Key Performance Stats */}
              <div className="grid grid-cols-2 gap-3 mb-4">
                <StatCard
                  label="Successful Hits"
                  value={stats.successful_hits}
                  icon="💥"
                />
                <StatCard
                  label="Catches Made"
                  value={stats.catches_made}
                  icon="✋"
                />
                <StatCard
                  label="Times Hit"
                  value={stats.times_hit}
                  icon="☠️"
                />
                <StatCard
                  label="Throws Attempted"
                  value={stats.throws_attempted}
                  icon="🎯"
                />
              </div>

              {/* Derived Metrics */}
              <div className="bg-slate-50 border border-slate-200 rounded-lg p-4 space-y-2">
                <div className="flex justify-between text-sm">
                  <span className="text-gray-600">Throwing Accuracy</span>
                  <span className="font-bold text-gray-900">{derived.accuracy}</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-gray-600">Catch Success Rate</span>
                  <span className="font-bold text-gray-900">{derived.catchRate}</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-gray-600">Missed Throws</span>
                  <span className="font-bold text-gray-900">{stats.missed_throws}</span>
                </div>
              </div>
            </>
          )}
        </div>

        {/* Skills Breakdown */}
        <div className="border-t border-gray-200 pt-6">
          <h4 className="text-sm font-semibold text-gray-700 uppercase mb-4">Skills Profile</h4>
          <div className="space-y-3">
            {Object.entries(skills).map(([name, value]) => (
              <SkillBar key={name} name={name} value={value} />
            ))}
          </div>
          <div className="mt-3 text-xs text-gray-500 text-center">
            Total Skill Points: {Object.values(skills).reduce((a, b) => a + b, 0)}/60
          </div>
        </div>

        {/* Injury Status */}
        {injury && (
          <div className="border-t border-gray-200 pt-6">
            <h4 className="text-sm font-semibold text-gray-700 uppercase mb-4">Injury Status</h4>
            <div className="bg-red-50 border border-red-200 rounded-lg p-4">
              <div className="flex items-start gap-3">
                <div className="text-2xl">🏥</div>
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-2">
                    <span className="text-sm font-semibold text-red-900 capitalize">
                      {injury.severity} Injury
                    </span>
                    <span className="text-xs text-red-600 bg-red-100 px-2 py-1 rounded">
                      -{Math.round(injury.affected_reduction * 100)}% Performance
                    </span>
                  </div>
                  <div className="text-sm text-red-700">
                    <span className="font-medium">{injury.games_remaining}</span> game
                    {injury.games_remaining !== 1 ? 's' : ''} until recovery
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default PlayerStats;
