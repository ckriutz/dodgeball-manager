/**
 * TeamBudget Component
 * 
 * Displays team budget information:
 * - Total budget ($15,000 initial)
 * - Remaining budget
 * - Spent budget
 */

import React from 'react';
import type { Team, Player } from '../../types';

interface TeamBudgetProps {
  team: Team;
  players?: Player[];
  showBreakdown?: boolean;
  className?: string;
}

/**
 * Format dollar value with comma separators
 */
const formatMoney = (value: number): string => {
  return `$${value.toLocaleString()}`;
};

/**
 * Get color based on budget percentage remaining
 */
const getBudgetColor = (percentage: number): string => {
  if (percentage >= 50) return 'bg-green-500';
  if (percentage >= 25) return 'bg-yellow-500';
  if (percentage >= 10) return 'bg-orange-500';
  return 'bg-red-500';
};

/**
 * Get text color based on budget percentage remaining
 */
const getBudgetTextColor = (percentage: number): string => {
  if (percentage >= 50) return 'text-green-600';
  if (percentage >= 25) return 'text-yellow-600';
  if (percentage >= 10) return 'text-orange-600';
  return 'text-red-600';
};

/**
 * Get budget status message
 */
const getBudgetStatus = (remaining: number, percentage: number): string => {
  if (remaining === 0) return 'Budget Exhausted';
  if (percentage < 10) return 'Critical Budget';
  if (percentage < 25) return 'Low Budget';
  if (percentage < 50) return 'Moderate Budget';
  return 'Healthy Budget';
};

/**
 * TeamBudget component
 */
export const TeamBudget: React.FC<TeamBudgetProps> = ({
  team,
  players = [],
  showBreakdown = false,
  className = '',
}) => {
  const maxBudget = 15000;
  const remainingBudget = team.budget;
  const spentBudget = maxBudget - remainingBudget;
  const percentageRemaining = (remainingBudget / maxBudget) * 100;
  const percentageSpent = (spentBudget / maxBudget) * 100;

  // Get roster players
  const rosterPlayers = players.filter((p) => team.player_ids.includes(p.id));
  const averagePlayerCost = rosterPlayers.length > 0 
    ? spentBudget / rosterPlayers.length 
    : 0;

  const budgetStatus = getBudgetStatus(remainingBudget, percentageRemaining);
  const progressColor = getBudgetColor(percentageRemaining);
  const textColor = getBudgetTextColor(percentageRemaining);

  // Calculate how many $1000 players can still be afforded
  const minPlayers = Math.floor(remainingBudget / 1000);

  return (
    <div className={`bg-white rounded-lg shadow-md border border-gray-200 p-5 ${className}`}>
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-900">Team Budget</h3>
        <span className={`px-3 py-1 rounded-full text-xs font-medium ${
          percentageRemaining >= 50 ? 'bg-green-100 text-green-800' :
          percentageRemaining >= 25 ? 'bg-yellow-100 text-yellow-800' :
          percentageRemaining >= 10 ? 'bg-orange-100 text-orange-800' :
          'bg-red-100 text-red-800'
        }`}>
          {budgetStatus}
        </span>
      </div>

      {/* Main Budget Display */}
      <div className="mb-6">
        <div className="flex justify-between items-baseline mb-2">
          <span className="text-sm font-medium text-gray-600">Remaining</span>
          <span className={`text-3xl font-bold ${textColor}`}>
            {formatMoney(remainingBudget)}
          </span>
        </div>
        
        {/* Progress Bar */}
        <div className="relative">
          <div className="w-full bg-gray-200 rounded-full h-4 overflow-hidden">
            <div
              className={`h-4 rounded-full transition-all duration-500 ${progressColor}`}
              style={{ width: `${percentageRemaining}%` }}
            />
          </div>
          <div className="absolute inset-0 flex items-center justify-center">
            <span className="text-xs font-medium text-gray-700">
              {percentageRemaining.toFixed(1)}% remaining
            </span>
          </div>
        </div>
      </div>

      {/* Budget Breakdown */}
      <div className="grid grid-cols-2 gap-4 mb-4">
        <div className="p-3 bg-gray-50 rounded-lg">
          <div className="text-xs font-semibold text-gray-600 uppercase mb-1">
            Total Budget
          </div>
          <div className="text-xl font-bold text-gray-900">
            {formatMoney(maxBudget)}
          </div>
        </div>
        
        <div className="p-3 bg-gray-50 rounded-lg">
          <div className="text-xs font-semibold text-gray-600 uppercase mb-1">
            Spent
          </div>
          <div className="text-xl font-bold text-gray-900">
            {formatMoney(spentBudget)}
          </div>
          <div className="text-xs text-gray-500 mt-0.5">
            {percentageSpent.toFixed(1)}%
          </div>
        </div>
      </div>

      {/* Roster Stats */}
      {rosterPlayers.length > 0 && (
        <div className="p-3 bg-blue-50 rounded-lg border border-blue-200 mb-4">
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div>
              <div className="text-xs font-semibold text-blue-700 uppercase mb-1">
                Players
              </div>
              <div className="text-lg font-bold text-blue-900">
                {rosterPlayers.length}
              </div>
            </div>
            <div>
              <div className="text-xs font-semibold text-blue-700 uppercase mb-1">
                Avg Cost
              </div>
              <div className="text-lg font-bold text-blue-900">
                {formatMoney(Math.round(averagePlayerCost))}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Budget Capacity */}
      <div className="p-3 bg-gray-50 rounded-lg border border-gray-200">
        <div className="flex items-center justify-between">
          <div>
            <div className="text-xs font-semibold text-gray-600 uppercase mb-1">
              Affordable Players
            </div>
            <div className="text-sm text-gray-700">
              Can afford <span className="font-semibold">{minPlayers}</span> more minimum-value players
            </div>
          </div>
          <div className="text-2xl">💰</div>
        </div>
      </div>

      {/* Warnings */}
      {percentageRemaining < 25 && (
        <div className={`mt-4 p-3 rounded-lg border ${
          percentageRemaining < 10 
            ? 'bg-red-50 border-red-200 text-red-700'
            : 'bg-orange-50 border-orange-200 text-orange-700'
        }`}>
          <div className="flex items-start gap-2">
            <span className="text-lg">⚠️</span>
            <div className="text-sm">
              {percentageRemaining < 10 ? (
                <>
                  <div className="font-semibold mb-1">Critical Budget Alert</div>
                  <div>Less than 10% of budget remaining. Be very selective with remaining roster spots.</div>
                </>
              ) : (
                <>
                  <div className="font-semibold mb-1">Low Budget Warning</div>
                  <div>Less than 25% of budget remaining. Consider budget carefully for remaining roster spots.</div>
                </>
              )}
            </div>
          </div>
        </div>
      )}

      {remainingBudget === 0 && team.player_ids.length < 12 && (
        <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
          <div className="flex items-start gap-2">
            <span className="text-lg">🚫</span>
            <div>
              <div className="font-semibold mb-1">Budget Exhausted</div>
              <div>No remaining budget to add more players. Remove players to free up budget.</div>
            </div>
          </div>
        </div>
      )}

      {/* Player Breakdown */}
      {showBreakdown && rosterPlayers.length > 0 && (
        <div className="mt-4 pt-4 border-t border-gray-200">
          <h4 className="text-sm font-semibold text-gray-700 uppercase mb-3">
            Spending Breakdown
          </h4>
          <div className="space-y-2 max-h-64 overflow-y-auto">
            {rosterPlayers
              .sort((a, b) => b.value - a.value)
              .map((player) => (
                <div
                  key={player.id}
                  className="flex items-center justify-between p-2 bg-gray-50 rounded"
                >
                  <div className="flex items-center gap-2 flex-1 min-w-0">
                    <div className="w-8 h-8 rounded-full bg-gradient-to-br from-blue-400 to-purple-500 flex items-center justify-center text-white text-xs font-bold flex-shrink-0">
                      {player.name.charAt(0)}
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="font-medium text-sm text-gray-900 truncate">
                        {player.name}
                      </div>
                      {team.starter_ids.includes(player.id) && (
                        <span className="text-xs text-blue-600">Starter</span>
                      )}
                    </div>
                  </div>
                  <div className="text-right flex-shrink-0">
                    <div className="font-semibold text-gray-900">
                      {formatMoney(player.value)}
                    </div>
                    <div className="text-xs text-gray-500">
                      {((player.value / maxBudget) * 100).toFixed(1)}%
                    </div>
                  </div>
                </div>
              ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default TeamBudget;
