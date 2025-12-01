/**
 * SkillPointAllocator Component
 * 
 * Allows users to allocate available skill points to player skills.
 * Displays current skill levels with + buttons to increase each skill.
 * Used on player detail pages when a player has unspent skill points.
 */

import React, { useState } from 'react';
import type { Player, PlayerSkills } from '../../types';

interface SkillPointAllocatorProps {
  player: Player;
  availablePoints: number;
  onAllocate: (allocations: Record<string, number>) => Promise<void>;
  onCancel?: () => void;
  className?: string;
  maxSkillValue?: number;
}

type SkillName = keyof PlayerSkills;

const SKILL_INFO: Record<SkillName, { label: string; icon: string; description: string }> = {
  catching: { 
    label: 'Catching', 
    icon: '✋', 
    description: 'Ability to catch incoming throws' 
  },
  throwing: { 
    label: 'Throwing', 
    icon: '🎯', 
    description: 'Accuracy and power of throws' 
  },
  dodging: { 
    label: 'Dodging', 
    icon: '💨', 
    description: 'Ability to evade incoming throws' 
  },
  speed: { 
    label: 'Speed', 
    icon: '⚡', 
    description: 'Movement speed on the court' 
  },
  iq: { 
    label: 'IQ', 
    icon: '🧠', 
    description: 'Game intelligence and decision making' 
  },
  luck: { 
    label: 'Luck', 
    icon: '🍀', 
    description: 'Random chance bonus in various situations' 
  },
};

const SKILL_ORDER: SkillName[] = ['throwing', 'catching', 'dodging', 'speed', 'iq', 'luck'];

/**
 * Get skill bar color based on value
 */
const getSkillColor = (value: number, maxValue: number): string => {
  const percentage = value / maxValue;
  if (percentage >= 0.8) return 'bg-green-500';
  if (percentage >= 0.6) return 'bg-blue-500';
  if (percentage >= 0.4) return 'bg-yellow-500';
  if (percentage >= 0.2) return 'bg-orange-500';
  return 'bg-red-500';
};

/**
 * SkillPointAllocator component
 */
export const SkillPointAllocator: React.FC<SkillPointAllocatorProps> = ({
  player,
  availablePoints,
  onAllocate,
  onCancel,
  className = '',
  maxSkillValue = 100,
}) => {
  // Track pending allocations (points to add to each skill)
  const [pendingAllocations, setPendingAllocations] = useState<Record<string, number>>({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Calculate points spent in pending allocations
  const pointsSpent = Object.values(pendingAllocations).reduce((sum, val) => sum + val, 0);
  const remainingPoints = availablePoints - pointsSpent;

  /**
   * Get current skill value including pending allocations
   */
  const getCurrentValue = (skillName: SkillName): number => {
    return player.skills[skillName] + (pendingAllocations[skillName] || 0);
  };

  /**
   * Check if a skill can be increased
   */
  const canIncrease = (skillName: SkillName): boolean => {
    return remainingPoints > 0 && getCurrentValue(skillName) < maxSkillValue;
  };

  /**
   * Check if a skill can be decreased (from pending allocations)
   */
  const canDecrease = (skillName: SkillName): boolean => {
    return (pendingAllocations[skillName] || 0) > 0;
  };

  /**
   * Handle increasing a skill
   */
  const handleIncrease = (skillName: SkillName) => {
    if (!canIncrease(skillName)) return;
    
    setPendingAllocations(prev => ({
      ...prev,
      [skillName]: (prev[skillName] || 0) + 1,
    }));
    setError(null);
  };

  /**
   * Handle decreasing a skill (removing from pending)
   */
  const handleDecrease = (skillName: SkillName) => {
    if (!canDecrease(skillName)) return;
    
    setPendingAllocations(prev => {
      const newValue = (prev[skillName] || 0) - 1;
      if (newValue === 0) {
        const { [skillName]: _, ...rest } = prev;
        return rest;
      }
      return { ...prev, [skillName]: newValue };
    });
  };

  /**
   * Reset all pending allocations
   */
  const handleReset = () => {
    setPendingAllocations({});
    setError(null);
  };

  /**
   * Submit allocations to API
   */
  const handleSubmit = async () => {
    if (pointsSpent === 0) return;
    
    setIsSubmitting(true);
    setError(null);
    
    try {
      await onAllocate(pendingAllocations);
      setPendingAllocations({});
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to allocate skill points');
    } finally {
      setIsSubmitting(false);
    }
  };

  const hasChanges = pointsSpent > 0;

  return (
    <div className={`bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden ${className}`}>
      {/* Header */}
      <div className="bg-gradient-to-r from-purple-600 to-indigo-600 px-6 py-4">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-lg font-bold text-white">Allocate Skill Points</h3>
            <p className="text-purple-200 text-sm mt-1">
              {player.name} has skill points to spend
            </p>
          </div>
          <div className="text-right">
            <div className="text-3xl font-bold text-white">{remainingPoints}</div>
            <div className="text-purple-200 text-xs">Points Available</div>
          </div>
        </div>
      </div>

      {/* Error Message */}
      {error && (
        <div className="mx-6 mt-4 p-3 bg-red-50 border border-red-200 rounded-lg">
          <p className="text-sm text-red-700">{error}</p>
        </div>
      )}

      {/* Skills List */}
      <div className="p-6 space-y-4">
        {SKILL_ORDER.map(skillName => {
          const info = SKILL_INFO[skillName];
          const baseValue = player.skills[skillName];
          const currentValue = getCurrentValue(skillName);
          const pendingIncrease = pendingAllocations[skillName] || 0;
          const isAtMax = currentValue >= maxSkillValue;

          return (
            <div key={skillName} className="space-y-2">
              {/* Skill Header */}
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <span className="text-xl">{info.icon}</span>
                  <div>
                    <span className="text-sm font-semibold text-gray-900">{info.label}</span>
                    <p className="text-xs text-gray-500">{info.description}</p>
                  </div>
                </div>
                
                {/* Controls */}
                <div className="flex items-center gap-2">
                  {/* Decrease Button */}
                  <button
                    onClick={() => handleDecrease(skillName)}
                    disabled={!canDecrease(skillName) || isSubmitting}
                    className={`w-8 h-8 rounded-full flex items-center justify-center font-bold text-lg transition-colors ${
                      canDecrease(skillName) && !isSubmitting
                        ? 'bg-red-100 text-red-600 hover:bg-red-200'
                        : 'bg-gray-100 text-gray-300 cursor-not-allowed'
                    }`}
                    aria-label={`Decrease ${info.label}`}
                  >
                    −
                  </button>

                  {/* Value Display */}
                  <div className="w-20 text-center">
                    <span className="text-lg font-bold text-gray-900">{currentValue}</span>
                    <span className="text-gray-400">/{maxSkillValue}</span>
                    {pendingIncrease > 0 && (
                      <span className="ml-1 text-green-600 text-sm font-semibold">
                        (+{pendingIncrease})
                      </span>
                    )}
                  </div>

                  {/* Increase Button */}
                  <button
                    onClick={() => handleIncrease(skillName)}
                    disabled={!canIncrease(skillName) || isSubmitting}
                    className={`w-8 h-8 rounded-full flex items-center justify-center font-bold text-lg transition-colors ${
                      canIncrease(skillName) && !isSubmitting
                        ? 'bg-green-100 text-green-600 hover:bg-green-200'
                        : 'bg-gray-100 text-gray-300 cursor-not-allowed'
                    }`}
                    aria-label={`Increase ${info.label}`}
                  >
                    +
                  </button>
                </div>
              </div>

              {/* Progress Bar */}
              <div className="relative">
                <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
                  {/* Base value */}
                  <div
                    className={`h-full ${getSkillColor(baseValue, maxSkillValue)} transition-all duration-300`}
                    style={{ width: `${(baseValue / maxSkillValue) * 100}%` }}
                  />
                </div>
                {/* Pending increase overlay */}
                {pendingIncrease > 0 && (
                  <div
                    className="absolute top-0 h-2 bg-green-400 rounded-r-full transition-all duration-300 animate-pulse"
                    style={{ 
                      left: `${(baseValue / maxSkillValue) * 100}%`,
                      width: `${(pendingIncrease / maxSkillValue) * 100}%` 
                    }}
                  />
                )}
                {isAtMax && (
                  <span className="absolute -right-1 -top-1 text-xs">⭐</span>
                )}
              </div>
            </div>
          );
        })}
      </div>

      {/* Summary */}
      {hasChanges && (
        <div className="mx-6 mb-4 p-4 bg-purple-50 border border-purple-200 rounded-lg">
          <h4 className="text-sm font-semibold text-purple-900 mb-2">Pending Changes</h4>
          <div className="space-y-1">
            {Object.entries(pendingAllocations)
              .filter(([_, value]) => value > 0)
              .map(([skill, points]) => (
                <div key={skill} className="flex justify-between text-sm">
                  <span className="text-purple-700 capitalize">
                    {SKILL_INFO[skill as SkillName]?.icon} {skill}
                  </span>
                  <span className="font-semibold text-purple-900">+{points}</span>
                </div>
              ))}
          </div>
        </div>
      )}

      {/* Action Buttons */}
      <div className="px-6 pb-6 flex gap-3">
        {onCancel && (
          <button
            onClick={onCancel}
            disabled={isSubmitting}
            className="flex-1 px-4 py-3 border border-gray-300 rounded-lg text-gray-700 font-medium hover:bg-gray-50 transition-colors disabled:opacity-50"
          >
            Cancel
          </button>
        )}
        <button
          onClick={handleReset}
          disabled={!hasChanges || isSubmitting}
          className={`flex-1 px-4 py-3 border rounded-lg font-medium transition-colors ${
            hasChanges && !isSubmitting
              ? 'border-orange-300 text-orange-700 hover:bg-orange-50'
              : 'border-gray-200 text-gray-400 cursor-not-allowed'
          }`}
        >
          Reset
        </button>
        <button
          onClick={handleSubmit}
          disabled={!hasChanges || isSubmitting}
          className={`flex-1 px-4 py-3 rounded-lg font-medium transition-colors ${
            hasChanges && !isSubmitting
              ? 'bg-purple-600 text-white hover:bg-purple-700 shadow-sm'
              : 'bg-gray-200 text-gray-400 cursor-not-allowed'
          }`}
        >
          {isSubmitting ? (
            <span className="flex items-center justify-center gap-2">
              <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
              </svg>
              Saving...
            </span>
          ) : (
            `Confirm (${pointsSpent} point${pointsSpent !== 1 ? 's' : ''})`
          )}
        </button>
      </div>

      {/* Help Text */}
      <div className="px-6 pb-6">
        <p className="text-xs text-gray-500 text-center">
          💡 Skill points are earned by leveling up through game experience. 
          Each point spent increases a skill by 1 (max {maxSkillValue}).
        </p>
      </div>
    </div>
  );
};

export default SkillPointAllocator;
