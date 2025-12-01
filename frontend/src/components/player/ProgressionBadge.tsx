/**
 * ProgressionBadge Component
 * 
 * Displays player progression information including:
 * - Current level with visual badge
 * - XP progress bar towards next level
 * - Available skill points indicator (when > 0)
 * 
 * This component can be used standalone or embedded in player cards/lists.
 * Supports multiple display modes (compact, full, minimal).
 */

import React from 'react';
import type { Player } from '../../types';

/**
 * Calculate XP required for next level.
 * Uses exponential scaling: 100 * level^1.5
 */
const calculateXpForNextLevel = (level: number): number => {
  return Math.floor(100 * Math.pow(level, 1.5));
};

/**
 * Calculate total XP needed to reach a target level from level 1.
 */
const calculateTotalXpForLevel = (targetLevel: number): number => {
  let total = 0;
  for (let lvl = 1; lvl < targetLevel; lvl++) {
    total += Math.floor(100 * Math.pow(lvl, 1.5));
  }
  return total;
};

/**
 * Calculate XP progress within current level (0-100%).
 */
const calculateXpProgress = (currentXp: number, level: number): number => {
  const xpForCurrentLevel = calculateTotalXpForLevel(level);
  const xpForNextLevel = calculateTotalXpForLevel(level + 1);
  const xpInCurrentLevel = currentXp - xpForCurrentLevel;
  const xpNeededForNextLevel = xpForNextLevel - xpForCurrentLevel;
  
  if (xpNeededForNextLevel <= 0) return 100;
  return Math.min(100, Math.max(0, (xpInCurrentLevel / xpNeededForNextLevel) * 100));
};

/**
 * Get badge color based on level range.
 */
const getLevelBadgeColor = (level: number): string => {
  if (level >= 50) return 'bg-gradient-to-r from-purple-500 to-pink-500'; // Legendary
  if (level >= 30) return 'bg-gradient-to-r from-yellow-400 to-orange-500'; // Epic
  if (level >= 20) return 'bg-gradient-to-r from-blue-400 to-indigo-500'; // Rare
  if (level >= 10) return 'bg-gradient-to-r from-green-400 to-emerald-500'; // Uncommon
  return 'bg-gradient-to-r from-gray-400 to-slate-500'; // Common
};

/**
 * Get level tier name for display.
 */
const getLevelTier = (level: number): string => {
  if (level >= 50) return 'Legendary';
  if (level >= 30) return 'Epic';
  if (level >= 20) return 'Rare';
  if (level >= 10) return 'Uncommon';
  return 'Common';
};

export type ProgressionDisplayMode = 'full' | 'compact' | 'minimal' | 'badge-only';

export interface PlayerProgression {
  level: number;
  experience_points: number;
  available_skill_points: number;
}

export interface ProgressionBadgeProps {
  /**
   * Player object containing progression data in stats.
   * Alternatively, you can pass `progression` prop directly.
   */
  player?: Player;
  
  /**
   * Direct progression data (alternative to passing full player).
   */
  progression?: PlayerProgression;
  
  /**
   * Display mode:
   * - 'full': Level badge + XP bar + skill points + tier name
   * - 'compact': Level badge + XP bar (smaller)
   * - 'minimal': Level badge + skill points indicator only
   * - 'badge-only': Just the level badge
   */
  mode?: ProgressionDisplayMode;
  
  /**
   * Additional CSS classes.
   */
  className?: string;
  
  /**
   * Show animation when skill points are available.
   */
  animate?: boolean;
  
  /**
   * Callback when badge is clicked.
   */
  onClick?: () => void;
}

/**
 * ProgressionBadge - Displays player level and progression info
 */
export const ProgressionBadge: React.FC<ProgressionBadgeProps> = ({
  player,
  progression,
  mode = 'compact',
  className = '',
  animate = true,
  onClick,
}) => {
  // Extract progression data from player or direct prop
  const progressionData: PlayerProgression = progression || {
    level: player?.stats?.level ?? 1,
    experience_points: player?.stats?.experience_points ?? 0,
    available_skill_points: player?.stats?.available_skill_points ?? 0,
  };

  const { level, experience_points, available_skill_points } = progressionData;
  
  const xpProgress = calculateXpProgress(experience_points, level);
  const xpForNext = calculateXpForNextLevel(level);
  const xpInLevel = experience_points - calculateTotalXpForLevel(level);
  const badgeColor = getLevelBadgeColor(level);
  const tier = getLevelTier(level);
  
  const hasSkillPoints = available_skill_points > 0;
  const isClickable = !!onClick;
  
  // Skill points indicator component
  const SkillPointsIndicator = () => {
    if (!hasSkillPoints) return null;
    
    return (
      <div 
        className={`
          inline-flex items-center gap-1 px-2 py-0.5 rounded-full 
          bg-amber-100 text-amber-700 text-xs font-semibold
          border border-amber-300
          ${animate ? 'animate-pulse' : ''}
        `}
        title={`${available_skill_points} skill point${available_skill_points > 1 ? 's' : ''} available`}
      >
        <svg 
          className="w-3 h-3" 
          fill="currentColor" 
          viewBox="0 0 20 20"
          aria-hidden="true"
        >
          <path d="M10 2a8 8 0 100 16 8 8 0 000-16zm1 11H9v-2h2v2zm0-4H9V5h2v4z" />
        </svg>
        <span>+{available_skill_points}</span>
      </div>
    );
  };
  
  // Level badge component
  const LevelBadge = ({ size = 'md' }: { size?: 'sm' | 'md' | 'lg' }) => {
    const sizeClasses = {
      sm: 'w-6 h-6 text-xs',
      md: 'w-8 h-8 text-sm',
      lg: 'w-10 h-10 text-base',
    };
    
    return (
      <div 
        className={`
          ${sizeClasses[size]} ${badgeColor}
          rounded-full flex items-center justify-center
          text-white font-bold shadow-md
          ${isClickable ? 'cursor-pointer hover:scale-110 transition-transform' : ''}
        `}
        title={`Level ${level} - ${tier}`}
      >
        {level}
      </div>
    );
  };
  
  // XP Progress bar component
  const XpProgressBar = ({ showLabel = true, height = 'h-2' }: { showLabel?: boolean; height?: string }) => {
    return (
      <div className="flex-1">
        {showLabel && (
          <div className="flex justify-between items-center mb-1">
            <span className="text-xs text-gray-500">XP</span>
            <span className="text-xs text-gray-600 font-medium">
              {xpInLevel.toLocaleString()} / {xpForNext.toLocaleString()}
            </span>
          </div>
        )}
        <div className={`${height} bg-gray-200 rounded-full overflow-hidden`}>
          <div
            className={`h-full ${badgeColor} transition-all duration-500 ease-out rounded-full`}
            style={{ width: `${xpProgress}%` }}
            role="progressbar"
            aria-valuenow={xpProgress}
            aria-valuemin={0}
            aria-valuemax={100}
            aria-label={`XP Progress: ${xpProgress.toFixed(0)}%`}
          />
        </div>
      </div>
    );
  };
  
  // Wrapper component for click handling
  const Wrapper: React.FC<{ children: React.ReactNode; wrapperClassName?: string }> = ({ 
    children, 
    wrapperClassName = '' 
  }) => {
    if (isClickable) {
      return (
        <button
          onClick={onClick}
          className={`${wrapperClassName} ${className} focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-1 rounded-lg`}
          aria-label={`Player progression: Level ${level}, ${available_skill_points} skill points available`}
        >
          {children}
        </button>
      );
    }
    return <div className={`${wrapperClassName} ${className}`}>{children}</div>;
  };
  
  // Badge-only mode - just the level number in a colored badge
  if (mode === 'badge-only') {
    return (
      <Wrapper>
        <div className="inline-flex items-center gap-1">
          <LevelBadge size="sm" />
          <SkillPointsIndicator />
        </div>
      </Wrapper>
    );
  }
  
  // Minimal mode - level badge + skill points indicator
  if (mode === 'minimal') {
    return (
      <Wrapper wrapperClassName="inline-flex items-center gap-2">
        <LevelBadge size="md" />
        <div className="flex flex-col items-start">
          <span className="text-xs text-gray-500">Lv.{level}</span>
          <SkillPointsIndicator />
        </div>
      </Wrapper>
    );
  }
  
  // Compact mode - level badge + small XP bar
  if (mode === 'compact') {
    return (
      <Wrapper wrapperClassName="inline-flex items-center gap-2 min-w-[140px]">
        <LevelBadge size="md" />
        <div className="flex-1 flex flex-col gap-1">
          <XpProgressBar showLabel={false} height="h-1.5" />
          {hasSkillPoints && (
            <div className="flex justify-end">
              <SkillPointsIndicator />
            </div>
          )}
        </div>
      </Wrapper>
    );
  }
  
  // Full mode - complete progression display
  return (
    <Wrapper wrapperClassName="block p-3 bg-gradient-to-br from-slate-50 to-white rounded-xl border border-gray-200 shadow-sm">
      <div className="flex items-center gap-3">
        <LevelBadge size="lg" />
        
        <div className="flex-1">
          <div className="flex items-center justify-between mb-1">
            <span className="text-sm font-semibold text-gray-800">Level {level}</span>
            <span className={`text-xs font-medium px-2 py-0.5 rounded-full ${
              tier === 'Legendary' ? 'bg-purple-100 text-purple-700' :
              tier === 'Epic' ? 'bg-orange-100 text-orange-700' :
              tier === 'Rare' ? 'bg-blue-100 text-blue-700' :
              tier === 'Uncommon' ? 'bg-green-100 text-green-700' :
              'bg-gray-100 text-gray-600'
            }`}>
              {tier}
            </span>
          </div>
          
          <XpProgressBar showLabel={true} height="h-2" />
        </div>
      </div>
      
      {hasSkillPoints && (
        <div className="mt-3 pt-3 border-t border-gray-100">
          <div className="flex items-center justify-between">
            <span className="text-sm text-gray-600">Available Skill Points</span>
            <span className={`
              text-lg font-bold text-amber-600
              ${animate ? 'animate-bounce' : ''}
            `}>
              +{available_skill_points}
            </span>
          </div>
          <p className="text-xs text-gray-400 mt-1">
            Click to allocate points to skills
          </p>
        </div>
      )}
    </Wrapper>
  );
};

export default ProgressionBadge;
