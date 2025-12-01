/**
 * GameResultsModal Component
 * 
 * A modal dialog displayed after a game is completed, showing:
 * - Winner announcement
 * - Final score summary
 * - XP awards for all players
 * - Level-up notifications with celebratory animations
 * - Key game statistics
 * 
 * Features:
 * - Celebratory design for winners
 * - Level-up animations and notifications
 * - XP earned per player
 * - Accessible modal with focus trapping
 * - Click handlers for player/team navigation
 * 
 * Used after game simulation to display results and progression.
 */

import React, { useEffect, useRef } from 'react';
import type { UUID } from '../../types';

/**
 * Player XP award entry
 */
export interface PlayerXPAward {
  player_id: UUID;
  player_name: string;
  xp_earned: number;
  leveled_up: boolean;
  new_level?: number;
  team_id: UUID;
}

/**
 * Game result data structure
 */
export interface GameResultData {
  game_id: UUID;
  winner_id: UUID | null;
  winner_name?: string;
  loser_name?: string;
  team1_id: UUID;
  team2_id: UUID;
  team1_name: string;
  team2_name: string;
  team1_eliminations: number;
  team2_eliminations: number;
  player_xp_awards: Record<string, number>;
  player_level_ups: Record<string, number>;
  /** Optional map of player IDs to player names */
  player_names?: Record<string, string>;
  /** Optional map of player IDs to team IDs */
  player_teams?: Record<string, string>;
}

/**
 * Props for GameResultsModal component
 */
interface GameResultsModalProps {
  isOpen: boolean;
  onClose: () => void;
  data: GameResultData | null;
  onPlayerClick?: (playerId: UUID) => void;
  onTeamClick?: (teamId: UUID) => void;
  onPlayAgain?: () => void;
}

/**
 * Calculate total XP for a team
 */
const getTeamTotalXP = (
  teamId: string,
  playerXP: Record<string, number>,
  playerTeams: Record<string, string>
): number => {
  return Object.entries(playerXP)
    .filter(([playerId]) => playerTeams[playerId] === teamId)
    .reduce((sum, [, xp]) => sum + xp, 0);
};

/**
 * Level-up notification card
 */
const LevelUpCard: React.FC<{
  playerName: string;
  playerId: UUID;
  newLevel: number;
  onPlayerClick?: (playerId: UUID) => void;
}> = ({ playerName, playerId, newLevel, onPlayerClick }) => {
  return (
    <div
      className={`bg-gradient-to-r from-yellow-100 to-amber-100 rounded-lg p-3 border-2 border-yellow-400 animate-pulse-slow ${
        onPlayerClick ? 'cursor-pointer hover:shadow-md' : ''
      }`}
      onClick={() => onPlayerClick?.(playerId)}
      data-testid={`level-up-${playerId}`}
    >
      <div className="flex items-center gap-3">
        <div className="text-3xl animate-bounce-slow">⬆️</div>
        <div className="flex-1">
          <div className="text-yellow-800 font-bold">{playerName}</div>
          <div className="text-yellow-700 text-sm">
            Leveled up to <span className="font-bold">Level {newLevel}</span>!
          </div>
        </div>
        <div className="bg-yellow-500 text-white font-bold rounded-full w-10 h-10 flex items-center justify-center text-lg">
          {newLevel}
        </div>
      </div>
    </div>
  );
};

/**
 * XP Award row
 */
const XPAwardRow: React.FC<{
  playerName: string;
  playerId: UUID;
  xpEarned: number;
  leveledUp: boolean;
  onPlayerClick?: (playerId: UUID) => void;
}> = ({ playerName, playerId, xpEarned, leveledUp, onPlayerClick }) => {
  return (
    <div
      className={`flex items-center justify-between py-2 px-3 rounded ${
        leveledUp ? 'bg-yellow-50' : 'hover:bg-gray-50'
      } ${onPlayerClick ? 'cursor-pointer' : ''}`}
      onClick={() => onPlayerClick?.(playerId)}
    >
      <div className="flex items-center gap-2">
        <span className="text-gray-800 truncate max-w-[150px]" title={playerName}>
          {playerName}
        </span>
        {leveledUp && (
          <span className="text-yellow-600 text-xs font-medium bg-yellow-100 px-1.5 py-0.5 rounded">
            LEVEL UP!
          </span>
        )}
      </div>
      <div className="flex items-center gap-1 text-green-600 font-medium">
        <span>+{xpEarned}</span>
        <span className="text-xs text-green-500">XP</span>
      </div>
    </div>
  );
};

/**
 * GameResultsModal component
 */
export const GameResultsModal: React.FC<GameResultsModalProps> = ({
  isOpen,
  onClose,
  data,
  onPlayerClick,
  onTeamClick,
  onPlayAgain,
}) => {
  const modalRef = useRef<HTMLDivElement>(null);
  const closeButtonRef = useRef<HTMLButtonElement>(null);

  // Focus trap and escape key handling
  useEffect(() => {
    if (!isOpen) return;

    closeButtonRef.current?.focus();

    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        onClose();
      }
    };

    const handleTab = (e: KeyboardEvent) => {
      if (e.key !== 'Tab' || !modalRef.current) return;

      const focusableElements = modalRef.current.querySelectorAll(
        'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
      );
      const firstElement = focusableElements[0] as HTMLElement;
      const lastElement = focusableElements[focusableElements.length - 1] as HTMLElement;

      if (e.shiftKey && document.activeElement === firstElement) {
        e.preventDefault();
        lastElement.focus();
      } else if (!e.shiftKey && document.activeElement === lastElement) {
        e.preventDefault();
        firstElement.focus();
      }
    };

    document.addEventListener('keydown', handleEscape);
    document.addEventListener('keydown', handleTab);
    document.body.style.overflow = 'hidden';

    return () => {
      document.removeEventListener('keydown', handleEscape);
      document.removeEventListener('keydown', handleTab);
      document.body.style.overflow = '';
    };
  }, [isOpen, onClose]);

  if (!isOpen || !data) return null;

  const {
    winner_id,
    winner_name,
    loser_name,
    team1_id,
    team2_id,
    team1_name,
    team2_name,
    team1_eliminations,
    team2_eliminations,
    player_xp_awards,
    player_level_ups,
    player_names = {},
    player_teams = {},
  } = data;

  const hasLevelUps = Object.keys(player_level_ups).length > 0;
  const hasXPAwards = Object.keys(player_xp_awards).length > 0;

  // Organize XP awards by team
  const team1XP = Object.entries(player_xp_awards)
    .filter(([playerId]) => player_teams[playerId] === team1_id)
    .map(([playerId, xp]) => ({
      playerId,
      playerName: player_names[playerId] || 'Unknown',
      xp,
      leveledUp: playerId in player_level_ups,
    }))
    .sort((a, b) => b.xp - a.xp);

  const team2XP = Object.entries(player_xp_awards)
    .filter(([playerId]) => player_teams[playerId] === team2_id)
    .map(([playerId, xp]) => ({
      playerId,
      playerName: player_names[playerId] || 'Unknown',
      xp,
      leveledUp: playerId in player_level_ups,
    }))
    .sort((a, b) => b.xp - a.xp);

  const isTeam1Winner = winner_id === team1_id;
  const isTeam2Winner = winner_id === team2_id;

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center p-4"
      role="dialog"
      aria-modal="true"
      aria-labelledby="game-results-title"
    >
      {/* Backdrop */}
      <div
        className="absolute inset-0 bg-black/60 backdrop-blur-sm"
        onClick={onClose}
        aria-hidden="true"
      />

      {/* Modal Content */}
      <div
        ref={modalRef}
        className="relative bg-white rounded-2xl shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto"
        data-testid="game-results-modal"
      >
        {/* Victory banner */}
        <div className={`px-6 py-4 ${winner_id ? 'bg-gradient-to-r from-green-500 to-emerald-600' : 'bg-gray-500'}`}>
          <div className="text-center">
            <div className="text-4xl mb-2">{winner_id ? '🎉' : '🤝'}</div>
            <h2 id="game-results-title" className="text-2xl font-bold text-white">
              {winner_id ? `${winner_name || 'Winner'} Wins!` : 'Game Complete'}
            </h2>
            {loser_name && (
              <p className="text-green-100 text-sm mt-1">defeated {loser_name}</p>
            )}
          </div>
        </div>

        {/* Close Button */}
        <button
          ref={closeButtonRef}
          onClick={onClose}
          className="absolute top-4 right-4 text-white/80 hover:text-white transition-colors z-10"
          aria-label="Close modal"
        >
          <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>

        {/* Score Summary */}
        <div className="px-6 py-4 border-b border-gray-200">
          <div className="flex items-center justify-center gap-8">
            {/* Team 1 */}
            <div
              className={`text-center ${onTeamClick ? 'cursor-pointer' : ''}`}
              onClick={() => onTeamClick?.(team1_id)}
            >
              <div className={`text-lg font-semibold ${isTeam1Winner ? 'text-green-600' : 'text-gray-700'}`}>
                {team1_name}
                {isTeam1Winner && ' 🏆'}
              </div>
              <div className="text-3xl font-bold text-gray-900">{team1_eliminations}</div>
              <div className="text-xs text-gray-500 uppercase">Eliminations</div>
            </div>

            {/* VS */}
            <div className="text-gray-400 text-xl font-bold">VS</div>

            {/* Team 2 */}
            <div
              className={`text-center ${onTeamClick ? 'cursor-pointer' : ''}`}
              onClick={() => onTeamClick?.(team2_id)}
            >
              <div className={`text-lg font-semibold ${isTeam2Winner ? 'text-green-600' : 'text-gray-700'}`}>
                {team2_name}
                {isTeam2Winner && ' 🏆'}
              </div>
              <div className="text-3xl font-bold text-gray-900">{team2_eliminations}</div>
              <div className="text-xs text-gray-500 uppercase">Eliminations</div>
            </div>
          </div>
        </div>

        {/* Level-Up Notifications */}
        {hasLevelUps && (
          <div className="px-6 py-4 bg-gradient-to-r from-yellow-50 to-amber-50 border-b border-yellow-200">
            <h3 className="text-lg font-semibold text-yellow-800 mb-3 flex items-center gap-2">
              <span className="text-2xl">🌟</span>
              Level Ups!
            </h3>
            <div className="space-y-2">
              {Object.entries(player_level_ups).map(([playerId, newLevel]) => (
                <LevelUpCard
                  key={playerId}
                  playerId={playerId}
                  playerName={player_names[playerId] || 'Unknown'}
                  newLevel={newLevel}
                  onPlayerClick={onPlayerClick}
                />
              ))}
            </div>
          </div>
        )}

        {/* XP Awards */}
        {hasXPAwards && (
          <div className="px-6 py-4">
            <h3 className="text-lg font-semibold text-gray-800 mb-3 flex items-center gap-2">
              <span className="text-xl">⚡</span>
              Experience Earned
            </h3>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {/* Team 1 XP */}
              <div className="bg-gray-50 rounded-lg p-3">
                <div className="flex items-center justify-between mb-2 pb-2 border-b border-gray-200">
                  <span className="font-medium text-gray-700">{team1_name}</span>
                  <span className="text-green-600 font-medium text-sm">
                    +{getTeamTotalXP(team1_id, player_xp_awards, player_teams)} XP
                  </span>
                </div>
                <div className="space-y-1">
                  {team1XP.map(({ playerId, playerName, xp, leveledUp }) => (
                    <XPAwardRow
                      key={playerId}
                      playerId={playerId}
                      playerName={playerName}
                      xpEarned={xp}
                      leveledUp={leveledUp}
                      onPlayerClick={onPlayerClick}
                    />
                  ))}
                  {team1XP.length === 0 && (
                    <p className="text-gray-400 text-sm text-center py-2">No XP data</p>
                  )}
                </div>
              </div>

              {/* Team 2 XP */}
              <div className="bg-gray-50 rounded-lg p-3">
                <div className="flex items-center justify-between mb-2 pb-2 border-b border-gray-200">
                  <span className="font-medium text-gray-700">{team2_name}</span>
                  <span className="text-green-600 font-medium text-sm">
                    +{getTeamTotalXP(team2_id, player_xp_awards, player_teams)} XP
                  </span>
                </div>
                <div className="space-y-1">
                  {team2XP.map(({ playerId, playerName, xp, leveledUp }) => (
                    <XPAwardRow
                      key={playerId}
                      playerId={playerId}
                      playerName={playerName}
                      xpEarned={xp}
                      leveledUp={leveledUp}
                      onPlayerClick={onPlayerClick}
                    />
                  ))}
                  {team2XP.length === 0 && (
                    <p className="text-gray-400 text-sm text-center py-2">No XP data</p>
                  )}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Action Buttons */}
        <div className="px-6 pb-6 pt-2 flex flex-col sm:flex-row gap-3">
          {onPlayAgain && (
            <button
              onClick={onPlayAgain}
              className="flex-1 bg-gradient-to-r from-blue-500 to-blue-600 text-white font-semibold py-3 px-6 rounded-lg hover:from-blue-600 hover:to-blue-700 transition-all shadow-md hover:shadow-lg"
            >
              🎮 Play Another Game
            </button>
          )}
          <button
            onClick={onClose}
            className="flex-1 bg-gray-100 text-gray-700 font-semibold py-3 px-6 rounded-lg hover:bg-gray-200 transition-colors border border-gray-300"
          >
            Close
          </button>
        </div>
      </div>

      {/* CSS Animations */}
      <style>{`
        @keyframes pulse-slow {
          0%, 100% {
            opacity: 1;
          }
          50% {
            opacity: 0.85;
          }
        }
        .animate-pulse-slow {
          animation: pulse-slow 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
        }
        @keyframes bounce-slow {
          0%, 100% {
            transform: translateY(0);
          }
          50% {
            transform: translateY(-5px);
          }
        }
        .animate-bounce-slow {
          animation: bounce-slow 1s ease-in-out infinite;
        }
      `}</style>
    </div>
  );
};

export default GameResultsModal;
