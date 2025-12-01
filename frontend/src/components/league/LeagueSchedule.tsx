/**
 * LeagueSchedule Component
 * 
 * Displays the league season schedule with visual status indicators.
 * Shows game pairings with completion status, highlighting the next game.
 * Used on the LeaguePage to show season progress.
 * 
 * Features:
 * - Visual indicators: pending (default), completed (grayed), next (highlighted)
 * - Progress bar showing season completion percentage
 * - "Play Next Game" button for the next pending game
 * - Team names with logos
 * - Game results for completed games
 */

import React from 'react';
import type { Team, LeagueScheduleItem, Game } from '../../types';

interface ScheduleGame extends LeagueScheduleItem {
  game_id?: string | null;
}

interface LeagueScheduleProps {
  schedule: ScheduleGame[];
  teams: Team[];
  games?: Game[];
  onPlayGame?: (gameNumber: number) => void;
  isLoading?: boolean;
  className?: string;
  seasonNumber?: number;
  seasonStatus?: string;
}

/**
 * Get team by ID
 */
const getTeam = (teamId: string, teams: Team[]): Team | undefined => {
  return teams.find(t => t.id === teamId);
};

/**
 * Get game result for a completed game
 */
const getGameResult = (gameId: string | null | undefined, games: Game[]): Game | undefined => {
  if (!gameId) return undefined;
  return games.find(g => g.id === gameId);
};

/**
 * Calculate schedule progress
 */
const calculateProgress = (schedule: ScheduleGame[]): { completed: number; total: number; percentage: number } => {
  const total = schedule.length;
  const completed = schedule.filter(g => g.completed).length;
  const percentage = total > 0 ? Math.round((completed / total) * 100) : 0;
  return { completed, total, percentage };
};

/**
 * Find the next game to play
 */
const findNextGame = (schedule: ScheduleGame[]): number | null => {
  const nextGame = schedule.find(g => !g.completed);
  return nextGame ? nextGame.game_number : null;
};

/**
 * TeamDisplay - Shows team info with logo
 */
const TeamDisplay: React.FC<{ team: Team | undefined; isWinner?: boolean; align?: 'left' | 'right' }> = ({
  team,
  isWinner = false,
  align = 'left',
}) => {
  if (!team) {
    return <span className="text-gray-400 italic">Unknown Team</span>;
  }

  const content = (
    <>
      <div className={`w-8 h-8 rounded-full overflow-hidden bg-gray-100 flex-shrink-0 ${align === 'right' ? 'order-2' : ''}`}>
        <img
          src={`/images/team_avatars/${team.logo}`}
          alt={team.name}
          className="w-full h-full object-cover"
          onError={(e) => {
            (e.target as HTMLImageElement).src = '/images/team_avatars/default.png';
          }}
        />
      </div>
      <span className={`font-medium truncate ${isWinner ? 'text-green-700 font-bold' : 'text-gray-900'}`}>
        {team.name}
      </span>
    </>
  );

  return (
    <div className={`flex items-center gap-2 ${align === 'right' ? 'flex-row-reverse' : ''}`}>
      {content}
    </div>
  );
};

/**
 * GameRow - Single game in the schedule
 */
const GameRow: React.FC<{
  game: ScheduleGame;
  teams: Team[];
  games: Game[];
  isNext: boolean;
  onPlay?: () => void;
  isLoading?: boolean;
}> = ({ game, teams, games, isNext, onPlay, isLoading }) => {
  const team1 = getTeam(game.team1_id, teams);
  const team2 = getTeam(game.team2_id, teams);
  const gameResult = game.game_id ? getGameResult(game.game_id, games) : undefined;

  // Determine winner for completed games
  let team1IsWinner = false;
  let team2IsWinner = false;
  let score = '';
  
  if (gameResult && game.completed) {
    team1IsWinner = gameResult.winner_id === game.team1_id;
    team2IsWinner = gameResult.winner_id === game.team2_id;
    // Calculate score from events if available
    const team1Score = team1IsWinner ? 1 : 0;
    const team2Score = team2IsWinner ? 1 : 0;
    score = `${team1Score} - ${team2Score}`;
  }

  const rowClasses = `
    flex items-center gap-4 p-4 rounded-lg border transition-all
    ${game.completed 
      ? 'bg-gray-50 border-gray-200 opacity-75' 
      : isNext 
        ? 'bg-blue-50 border-blue-300 shadow-sm ring-2 ring-blue-200' 
        : 'bg-white border-gray-200 hover:border-gray-300'
    }
  `;

  return (
    <div className={rowClasses}>
      {/* Game Number */}
      <div className="flex-shrink-0 w-10 h-10 rounded-full bg-gray-100 flex items-center justify-center">
        <span className={`text-sm font-bold ${isNext ? 'text-blue-600' : 'text-gray-500'}`}>
          {game.game_number}
        </span>
      </div>

      {/* Teams */}
      <div className="flex-1 grid grid-cols-3 items-center gap-2 min-w-0">
        {/* Team 1 */}
        <div className="flex justify-end">
          <TeamDisplay team={team1} isWinner={team1IsWinner} align="right" />
        </div>

        {/* VS / Score */}
        <div className="text-center">
          {game.completed ? (
            <div className="flex flex-col items-center">
              <span className="text-sm font-bold text-gray-700">{score}</span>
              <span className="text-xs text-gray-400">Final</span>
            </div>
          ) : (
            <span className={`text-sm font-medium ${isNext ? 'text-blue-600' : 'text-gray-400'}`}>
              vs
            </span>
          )}
        </div>

        {/* Team 2 */}
        <div className="flex justify-start">
          <TeamDisplay team={team2} isWinner={team2IsWinner} align="left" />
        </div>
      </div>

      {/* Status / Action */}
      <div className="flex-shrink-0 w-28">
        {game.completed ? (
          <span className="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium bg-gray-200 text-gray-600">
            ✓ Completed
          </span>
        ) : isNext ? (
          <button
            onClick={onPlay}
            disabled={isLoading}
            className={`w-full px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
              isLoading
                ? 'bg-gray-200 text-gray-400 cursor-not-allowed'
                : 'bg-blue-600 text-white hover:bg-blue-700 shadow-sm'
            }`}
          >
            {isLoading ? (
              <span className="flex items-center justify-center gap-1">
                <svg className="animate-spin h-3 w-3" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                </svg>
                Playing...
              </span>
            ) : (
              '▶ Play'
            )}
          </button>
        ) : (
          <span className="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium bg-yellow-100 text-yellow-700">
            Pending
          </span>
        )}
      </div>
    </div>
  );
};

/**
 * LeagueSchedule component
 */
export const LeagueSchedule: React.FC<LeagueScheduleProps> = ({
  schedule,
  teams,
  games = [],
  onPlayGame,
  isLoading = false,
  className = '',
  seasonNumber,
  seasonStatus,
}) => {
  const progress = calculateProgress(schedule);
  const nextGameNumber = findNextGame(schedule);
  const isSeasonComplete = progress.completed === progress.total && progress.total > 0;

  // Handle empty schedule
  if (schedule.length === 0) {
    return (
      <div className={`bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden ${className}`}>
        <div className="bg-gradient-to-r from-slate-600 to-slate-700 px-6 py-4">
          <h3 className="text-lg font-bold text-white">Season Schedule</h3>
          {seasonNumber && (
            <p className="text-slate-300 text-sm mt-1">Season {seasonNumber}</p>
          )}
        </div>
        <div className="p-8 text-center">
          <div className="text-4xl mb-3">📅</div>
          <h4 className="text-lg font-semibold text-gray-900 mb-2">No Schedule Generated</h4>
          <p className="text-gray-500 text-sm">
            Generate a schedule to start the season and begin playing games.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className={`bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden ${className}`}>
      {/* Header */}
      <div className="bg-gradient-to-r from-slate-600 to-slate-700 px-6 py-4">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-lg font-bold text-white">Season Schedule</h3>
            {seasonNumber && (
              <p className="text-slate-300 text-sm mt-1">
                Season {seasonNumber}
                {seasonStatus && ` • ${seasonStatus.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}`}
              </p>
            )}
          </div>
          <div className="text-right">
            <div className="text-2xl font-bold text-white">
              {progress.completed}/{progress.total}
            </div>
            <div className="text-slate-300 text-xs">Games Played</div>
          </div>
        </div>

        {/* Progress Bar */}
        <div className="mt-4">
          <div className="flex justify-between text-xs text-slate-300 mb-1">
            <span>Progress</span>
            <span>{progress.percentage}%</span>
          </div>
          <div className="h-2 bg-slate-500 rounded-full overflow-hidden">
            <div
              className={`h-full transition-all duration-500 ${
                isSeasonComplete ? 'bg-green-400' : 'bg-blue-400'
              }`}
              style={{ width: `${progress.percentage}%` }}
            />
          </div>
        </div>
      </div>

      {/* Season Complete Banner */}
      {isSeasonComplete && (
        <div className="bg-green-50 border-b border-green-200 px-6 py-3">
          <div className="flex items-center gap-2">
            <span className="text-xl">🏆</span>
            <span className="text-green-800 font-medium">
              All games completed! Ready to finish the season.
            </span>
          </div>
        </div>
      )}

      {/* Next Game Highlight */}
      {nextGameNumber && !isSeasonComplete && (
        <div className="bg-blue-50 border-b border-blue-200 px-6 py-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <span className="text-xl">⏭️</span>
              <span className="text-blue-800 font-medium">
                Next up: Game {nextGameNumber}
              </span>
            </div>
            {onPlayGame && (
              <button
                onClick={() => onPlayGame(nextGameNumber)}
                disabled={isLoading}
                className={`px-4 py-1.5 rounded-lg text-sm font-medium transition-colors ${
                  isLoading
                    ? 'bg-gray-200 text-gray-400 cursor-not-allowed'
                    : 'bg-blue-600 text-white hover:bg-blue-700 shadow-sm'
                }`}
              >
                {isLoading ? 'Playing...' : 'Play Next Game'}
              </button>
            )}
          </div>
        </div>
      )}

      {/* Schedule List */}
      <div className="p-4 space-y-2 max-h-[500px] overflow-y-auto">
        {schedule.map((game) => (
          <GameRow
            key={game.game_number}
            game={game}
            teams={teams}
            games={games}
            isNext={game.game_number === nextGameNumber}
            onPlay={onPlayGame ? () => onPlayGame(game.game_number) : undefined}
            isLoading={isLoading && game.game_number === nextGameNumber}
          />
        ))}
      </div>

      {/* Footer Stats */}
      <div className="border-t border-gray-200 px-6 py-4 bg-gray-50">
        <div className="grid grid-cols-3 gap-4 text-center text-sm">
          <div>
            <div className="font-bold text-gray-900">{progress.completed}</div>
            <div className="text-gray-500 text-xs">Completed</div>
          </div>
          <div>
            <div className="font-bold text-gray-900">{progress.total - progress.completed}</div>
            <div className="text-gray-500 text-xs">Remaining</div>
          </div>
          <div>
            <div className="font-bold text-gray-900">{teams.length}</div>
            <div className="text-gray-500 text-xs">Teams</div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LeagueSchedule;
