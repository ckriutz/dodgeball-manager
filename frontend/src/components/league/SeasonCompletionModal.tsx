/**
 * SeasonCompletionModal Component
 * 
 * A modal dialog displayed when a season is completed, showing:
 * - Season number and completion message
 * - Champion team with record
 * - MVP player with stats
 * - Final standings summary
 * - Statistical leaders
 * 
 * Features:
 * - Celebratory design with animations
 * - Confetti effect on open
 * - Responsive design with Tailwind CSS
 * - Click handlers for team/player navigation
 * - Accessible modal with focus trapping and escape key
 * 
 * Used when finishing a season to celebrate and display results.
 */

import React, { useEffect, useRef } from 'react';
import type { UUID } from '../../types';

/**
 * Champion data structure
 */
export interface ChampionData {
  team_id: UUID;
  team_name: string;
  wins: number;
  losses: number;
}

/**
 * MVP data structure
 */
export interface MVPData {
  player_id: UUID;
  name: string;
  reason?: string | null;
  mvp_score?: number | null;
  successful_hits?: number | null;
  catches_made?: number | null;
}

/**
 * Standing entry in final standings
 */
export interface FinalStanding {
  team_id: UUID;
  team_name: string;
  wins: number;
  losses: number;
  rank: number;
}

/**
 * Season completion result data
 */
export interface SeasonCompletionData {
  season_number: number;
  final_standings: FinalStanding[];
  champion?: ChampionData | null;
  mvp?: MVPData | null;
  statistical_leaders?: Record<string, string> | null;
  message?: string;
}

/**
 * Props for SeasonCompletionModal component
 */
interface SeasonCompletionModalProps {
  isOpen: boolean;
  onClose: () => void;
  data: SeasonCompletionData | null;
  onTeamClick?: (teamId: UUID) => void;
  onPlayerClick?: (playerId: UUID) => void;
  onStartNewSeason?: () => void;
  /** Optional map of player IDs to player names for statistical leaders */
  playerNames?: Record<string, string>;
}

/**
 * Statistical leader display names
 */
const STAT_LEADER_NAMES: Record<string, string> = {
  most_hits: '🎯 Top Eliminator',
  most_catches: '🧤 Best Catcher',
  highest_accuracy: '🏹 Accuracy King',
  best_defense: '🛡️ Iron Wall',
  fewest_times_hit: '🛡️ Iron Wall',
};

/**
 * Get ordinal suffix for a number (1st, 2nd, 3rd, etc.)
 */
const getOrdinalSuffix = (n: number): string => {
  const s = ['th', 'st', 'nd', 'rd'];
  const v = n % 100;
  return n + (s[(v - 20) % 10] || s[v] || s[0]);
};

/**
 * SeasonCompletionModal component
 */
export const SeasonCompletionModal: React.FC<SeasonCompletionModalProps> = ({
  isOpen,
  onClose,
  data,
  onTeamClick,
  onPlayerClick,
  onStartNewSeason,
  playerNames = {},
}) => {
  const modalRef = useRef<HTMLDivElement>(null);
  const closeButtonRef = useRef<HTMLButtonElement>(null);

  // Focus trap and escape key handling
  useEffect(() => {
    if (!isOpen) return;

    // Focus the modal when it opens
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

    // Prevent body scroll when modal is open
    document.body.style.overflow = 'hidden';

    return () => {
      document.removeEventListener('keydown', handleEscape);
      document.removeEventListener('keydown', handleTab);
      document.body.style.overflow = '';
    };
  }, [isOpen, onClose]);

  if (!isOpen || !data) return null;

  const { season_number, final_standings, champion, mvp, statistical_leaders } = data;

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center p-4"
      role="dialog"
      aria-modal="true"
      aria-labelledby="season-completion-title"
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
        className="relative bg-white rounded-2xl shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto animate-bounce-in"
        data-testid="season-completion-modal"
      >
        {/* Confetti decoration at top */}
        <div className="absolute top-0 left-0 right-0 h-2 bg-gradient-to-r from-yellow-400 via-red-500 to-purple-500" />

        {/* Close Button */}
        <button
          ref={closeButtonRef}
          onClick={onClose}
          className="absolute top-4 right-4 text-gray-400 hover:text-gray-600 transition-colors z-10"
          aria-label="Close modal"
        >
          <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>

        {/* Header */}
        <div className="text-center pt-8 pb-4 px-6">
          <div className="text-6xl mb-4" role="img" aria-label="Trophy">
            🏆
          </div>
          <h2 id="season-completion-title" className="text-3xl font-bold text-gray-900">
            Season {season_number} Complete!
          </h2>
          <p className="text-gray-500 mt-2">
            Congratulations on completing another exciting season!
          </p>
        </div>

        {/* Champion Section */}
        {champion && (
          <div className="mx-6 mb-6">
            <div
              className={`bg-gradient-to-br from-yellow-50 to-yellow-100 rounded-xl p-6 border-2 border-yellow-300 text-center ${
                onTeamClick ? 'cursor-pointer hover:shadow-lg transition-shadow' : ''
              }`}
              onClick={() => onTeamClick?.(champion.team_id)}
            >
              <div className="text-sm text-yellow-600 uppercase font-semibold tracking-wide mb-2">
                🎉 Season Champion 🎉
              </div>
              <div className="text-2xl font-bold text-yellow-800 mb-2">
                {champion.team_name}
              </div>
              <div className="text-yellow-700">
                {champion.wins}W - {champion.losses}L
              </div>
            </div>
          </div>
        )}

        {/* MVP Section */}
        {mvp && (
          <div className="mx-6 mb-6">
            <div
              className={`bg-gradient-to-br from-purple-50 to-purple-100 rounded-xl p-5 border-2 border-purple-300 ${
                onPlayerClick ? 'cursor-pointer hover:shadow-lg transition-shadow' : ''
              }`}
              onClick={() => onPlayerClick?.(mvp.player_id)}
            >
              <div className="flex items-center gap-4">
                <div className="text-4xl">⭐</div>
                <div className="flex-1">
                  <div className="text-sm text-purple-600 uppercase font-semibold tracking-wide">
                    Season MVP
                  </div>
                  <div className="text-xl font-bold text-purple-800">
                    {mvp.name}
                  </div>
                  {mvp.reason && (
                    <div className="text-purple-700 text-sm mt-1">
                      {mvp.reason}
                    </div>
                  )}
                  {(mvp.successful_hits !== null || mvp.catches_made !== null) && (
                    <div className="text-purple-600 text-sm mt-1">
                      {mvp.successful_hits !== null && `${mvp.successful_hits} eliminations`}
                      {mvp.successful_hits !== null && mvp.catches_made !== null && ' • '}
                      {mvp.catches_made !== null && `${mvp.catches_made} catches`}
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Final Standings */}
        {final_standings && final_standings.length > 0 && (
          <div className="mx-6 mb-6">
            <h3 className="text-lg font-semibold text-gray-800 mb-3">Final Standings</h3>
            <div className="bg-gray-50 rounded-lg overflow-hidden border border-gray-200">
              <table className="min-w-full text-sm">
                <thead>
                  <tr className="bg-gray-100 border-b border-gray-200">
                    <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">
                      Rank
                    </th>
                    <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">
                      Team
                    </th>
                    <th className="px-4 py-2 text-center text-xs font-medium text-gray-500 uppercase">
                      W
                    </th>
                    <th className="px-4 py-2 text-center text-xs font-medium text-gray-500 uppercase">
                      L
                    </th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200">
                  {final_standings.slice(0, 6).map((standing, index) => {
                    const rank = standing.rank ?? index + 1;
                    const isChampion = rank === 1;
                    
                    return (
                      <tr
                        key={standing.team_id}
                        className={`${isChampion ? 'bg-yellow-50' : 'bg-white'} ${
                          onTeamClick ? 'cursor-pointer hover:bg-blue-50' : ''
                        }`}
                        onClick={() => onTeamClick?.(standing.team_id)}
                      >
                        <td className="px-4 py-2 whitespace-nowrap">
                          {rank === 1 && '🥇 '}
                          {rank === 2 && '🥈 '}
                          {rank === 3 && '🥉 '}
                          {rank > 3 && `${getOrdinalSuffix(rank)} `}
                        </td>
                        <td className="px-4 py-2 whitespace-nowrap font-medium text-gray-900">
                          {standing.team_name}
                        </td>
                        <td className="px-4 py-2 whitespace-nowrap text-center text-green-600 font-medium">
                          {standing.wins}
                        </td>
                        <td className="px-4 py-2 whitespace-nowrap text-center text-red-600 font-medium">
                          {standing.losses}
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
              {final_standings.length > 6 && (
                <div className="px-4 py-2 text-xs text-gray-500 bg-gray-100 border-t border-gray-200">
                  +{final_standings.length - 6} more teams
                </div>
              )}
            </div>
          </div>
        )}

        {/* Statistical Leaders */}
        {statistical_leaders && Object.keys(statistical_leaders).length > 0 && (
          <div className="mx-6 mb-6">
            <h3 className="text-lg font-semibold text-gray-800 mb-3">Statistical Leaders</h3>
            <div className="grid grid-cols-2 gap-3">
              {Object.entries(statistical_leaders).map(([stat, playerId]) => {
                const leaderName = playerNames[playerId] || 'Unknown';
                const displayName = STAT_LEADER_NAMES[stat] || stat;

                return (
                  <div
                    key={stat}
                    className={`bg-gray-50 rounded-lg p-3 border border-gray-200 ${
                      onPlayerClick ? 'cursor-pointer hover:bg-blue-50 hover:border-blue-200' : ''
                    }`}
                    onClick={() => onPlayerClick?.(playerId)}
                  >
                    <div className="text-xs text-gray-500 mb-1">{displayName}</div>
                    <div className="font-medium text-gray-800 truncate" title={leaderName}>
                      {leaderName}
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        )}

        {/* Action Buttons */}
        <div className="px-6 pb-6 flex flex-col sm:flex-row gap-3">
          {onStartNewSeason && (
            <button
              onClick={onStartNewSeason}
              className="flex-1 bg-gradient-to-r from-green-500 to-green-600 text-white font-semibold py-3 px-6 rounded-lg hover:from-green-600 hover:to-green-700 transition-all shadow-md hover:shadow-lg"
            >
              🚀 Start New Season
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

      {/* CSS Animation */}
      <style>{`
        @keyframes bounce-in {
          0% {
            opacity: 0;
            transform: scale(0.9) translateY(-20px);
          }
          50% {
            transform: scale(1.02) translateY(0);
          }
          100% {
            opacity: 1;
            transform: scale(1) translateY(0);
          }
        }
        .animate-bounce-in {
          animation: bounce-in 0.4s ease-out forwards;
        }
      `}</style>
    </div>
  );
};

export default SeasonCompletionModal;
