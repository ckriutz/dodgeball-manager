/**
 * GamesPage Component
 * 
 * Game simulation and history page for a league.
 * Features:
 * - Select two teams to simulate a game
 * - View play-by-play history
 * - View game statistics
 * - View player statistics
 * - Browse past game history
 * - Play Next Game from schedule
 * - Schedule status display
 * 
 * This page integrates GameSimulator, GameHistory, GameStats, and PlayerStats components.
 */

import React, { useState, useEffect, useCallback } from 'react';
import { useParams } from 'react-router-dom';
import { GameSimulator } from '../components/game/GameSimulator';
import { GameHistory } from '../components/game/GameHistory';
import { GameStats } from '../components/game/GameStats';
import { PlayerStats } from '../components/player/PlayerStats';
import { Breadcrumbs, type BreadcrumbItem } from '../components/common/Breadcrumbs';
import { gameApi, leagueApi, teamApi } from '../services/api';
import type { Team, Player, League, Game, CreateGameRequest, LeagueScheduleItem } from '../types';

type ViewMode = 'simulator' | 'game-detail' | 'player-stats';

/**
 * GamesPage component
 */
export const GamesPage: React.FC = () => {
  const { leagueId } = useParams<{ leagueId: string }>();

  // State
  const [viewMode, setViewMode] = useState<ViewMode>('simulator');
  const [league, setLeague] = useState<League | null>(null);
  const [teams, setTeams] = useState<Team[]>([]);
  const [playerMap, setPlayerMap] = useState<Record<string, Player>>({});
  const [games, setGames] = useState<Game[]>([]);
  const [schedule, setSchedule] = useState<LeagueScheduleItem[]>([]);
  const [selectedGame, setSelectedGame] = useState<Game | null>(null);
  const [selectedPlayer] = useState<Player | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [simulationError, setSimulationError] = useState<string | null>(null);
  const [playingNextGame, setPlayingNextGame] = useState(false);

  /**
   * Load league, teams, players, and games on mount
   */
  useEffect(() => {
    const loadData = async () => {
      if (!leagueId) {
        setError('League ID is required');
        setLoading(false);
        return;
      }

      setLoading(true);
      setError(null);

      try {
        // Load league info
        const leagueResponse = await leagueApi.getLeague(leagueId);
        if (leagueResponse.error) {
          throw new Error(leagueResponse.error.message);
        }
        const leagueData = leagueResponse.data as League;
        setLeague(leagueData);

        // Load teams for this league
        const teamsPromises = leagueData.team_ids.map((teamId) =>
          teamApi.getTeam(teamId)
        );
        const teamsResponses = await Promise.all(teamsPromises);
        const teamsData = teamsResponses
          .filter((r) => !r.error)
          .map((r) => r.data as Team);
        setTeams(teamsData);

        // Load all players in league
        const playersResponse = await leagueApi.getPlayers(leagueId);
        if (playersResponse.error) {
          throw new Error(playersResponse.error.message);
        }
        const playersData = playersResponse.data as Player[];

        // Create player lookup map
        const map: Record<string, Player> = {};
        playersData.forEach((player) => {
          map[player.id] = player;
        });
        setPlayerMap(map);

        // Load games for this league
        const gamesResponse = await gameApi.getGames(leagueId);
        if (gamesResponse.error) {
          throw new Error(gamesResponse.error.message);
        }
        const gamesData = gamesResponse.data as Game[];
        setGames(gamesData);

        // Load schedule for this league
        const scheduleResponse = await leagueApi.getSchedule(leagueId);
        if (!scheduleResponse.error && scheduleResponse.data) {
          // The API returns an object with a schedule array property
          const scheduleData = scheduleResponse.data as { schedule: LeagueScheduleItem[] };
          setSchedule(scheduleData.schedule || []);
        }
      } catch (err) {
        console.error('Failed to load data:', err);
        setError(
          err instanceof Error
            ? err.message
            : 'Failed to load league data. Please try again.'
        );
      } finally {
        setLoading(false);
      }
    };

    loadData();
  }, [leagueId]);

  /**
   * Handle game simulation
   */
  const handleSimulateGame = async (request: CreateGameRequest): Promise<Game> => {
    setSimulationError(null);

    try {
      const response = await gameApi.createGame(request);
      if (response.error) {
        throw new Error(response.error.message);
      }

      const game = response.data as Game;

      // Add game to list
      setGames((prev) => [game, ...prev]);

      // Refresh teams to get updated win/loss records
      const teamsPromises = [
        teamApi.getTeam(game.team1_id),
        teamApi.getTeam(game.team2_id),
      ];
      const teamsResponses = await Promise.all(teamsPromises);
      const updatedTeams = teamsResponses
        .filter((r) => !r.error)
        .map((r) => r.data as Team);

      // Update teams in state
      setTeams((prev) =>
        prev.map((team) => {
          const updated = updatedTeams.find((t) => t.id === team.id);
          return updated || team;
        })
      );

      // Refresh players to get updated stats
      if (leagueId) {
        const playersResponse = await leagueApi.getPlayers(leagueId);
        if (!playersResponse.error) {
          const playersData = playersResponse.data as Player[];

          // Update player map
          const map: Record<string, Player> = {};
          playersData.forEach((player) => {
            map[player.id] = player;
          });
          setPlayerMap(map);
        }

        // Refresh schedule to update completed status
        const scheduleResponse = await leagueApi.getSchedule(leagueId);
        if (!scheduleResponse.error && scheduleResponse.data) {
          const scheduleData = scheduleResponse.data as { schedule: LeagueScheduleItem[] };
          setSchedule(scheduleData.schedule || []);
        }
      }

      // Show the new game
      setSelectedGame(game);
      setViewMode('game-detail');

      return game;
    } catch (err) {
      console.error('Failed to simulate game:', err);
      const errorMsg = err instanceof Error
        ? err.message
        : 'Failed to simulate game. Please try again.';
      setSimulationError(errorMsg);
      throw new Error(errorMsg);
    }
  };

  /**
   * Handle selecting a past game
   */
  const handleSelectGame = async (game: Game) => {
    // Fetch full game details if events are not loaded
    if (!game.events || game.events.length === 0) {
      try {
        const response = await gameApi.getGame(game.id);
        if (response.error) {
          console.error('Failed to load game details:', response.error);
          setSimulationError(`Failed to load game details: ${response.error.message}`);
          return;
        }
        const fullGame = response.data as Game;
        setSelectedGame(fullGame);
      } catch (err) {
        console.error('Failed to load game details:', err);
        setSimulationError('Failed to load game details. Please try again.');
        return;
      }
    } else {
      setSelectedGame(game);
    }
    setViewMode('game-detail');
  };

  /**
   * Get team name by ID
   */
  const getTeamName = (teamId: string): string => {
    const team = teams.find((t) => t.id === teamId);
    return team ? team.name : 'Unknown Team';
  };

  /**
   * Get team logo by ID
   */
  const getTeamLogo = (teamId: string): string | undefined => {
    const team = teams.find((t) => t.id === teamId);
    return team?.logo;
  };

  /**
   * Get the next unplayed game from the schedule
   */
  const nextScheduledGame = schedule.find((item) => !item.completed);

  /**
   * Get schedule statistics
   */
  const scheduleStats = {
    total: schedule.length,
    completed: schedule.filter((item) => item.completed).length,
    remaining: schedule.filter((item) => !item.completed).length,
  };

  /**
   * Handle playing the next scheduled game
   */
  const handlePlayNextGame = useCallback(async () => {
    if (!nextScheduledGame || !leagueId) return;

    setPlayingNextGame(true);
    setSimulationError(null);

    try {
      const request: CreateGameRequest = {
        league_id: leagueId,
        team1_id: nextScheduledGame.team1_id,
        team2_id: nextScheduledGame.team2_id,
      };

      await handleSimulateGame(request);
    } catch (err) {
      // Error is already handled by handleSimulateGame
    } finally {
      setPlayingNextGame(false);
    }
  }, [nextScheduledGame, leagueId]);

  // Build breadcrumb items
  const getBreadcrumbs = (): BreadcrumbItem[] => {
    const items: BreadcrumbItem[] = [
      { label: 'Leagues', path: '/leagues' },
    ];
    
    if (league) {
      items.push({ label: league.name, path: `/leagues/${league.id}` });
      
      // Add Games breadcrumb - make it clickable if not in simulator view
      if (viewMode === 'game-detail' || viewMode === 'player-stats') {
        items.push({ 
          label: 'Games',
          onClick: () => {
            setViewMode('simulator');
            setSelectedGame(null);
            setSimulationError(null);
          }
        });
      } else {
        items.push({ label: 'Games' });
      }
      
      if (viewMode === 'game-detail' && selectedGame) {
        const team1 = teams.find((t) => t.id === selectedGame.team1_id);
        const team2 = teams.find((t) => t.id === selectedGame.team2_id);
        items.push({ label: `${team1?.name || 'Team 1'} vs ${team2?.name || 'Team 2'}` });
      } else if (viewMode === 'player-stats' && selectedPlayer) {
        items.push({ label: selectedPlayer.name });
      }
    }
    
    return items;
  };

  // Loading state
  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 py-8">
        <div className="container mx-auto px-4 max-w-7xl">
          <div className="flex items-center justify-center h-64">
            <div className="text-center">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
              <p className="text-gray-600">Loading game data...</p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // Error state
  if (error) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 py-8">
        <div className="container mx-auto px-4 max-w-7xl">
          <Breadcrumbs items={getBreadcrumbs()} className="mb-6" />
          <div className="bg-red-50 border border-red-200 rounded-lg p-6">
            <div className="flex items-center gap-3">
              <div className="text-red-600 text-2xl">⚠️</div>
              <div>
                <h3 className="text-lg font-semibold text-red-800 mb-1">Error Loading Data</h3>
                <p className="text-sm text-red-700">{error}</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // No league
  if (!league) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 py-8">
        <div className="container mx-auto px-4 max-w-7xl">
          <Breadcrumbs items={getBreadcrumbs()} className="mb-6" />
          <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6">
            <p className="text-yellow-700">League not found</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 py-8">
      <div className="container mx-auto px-4 max-w-7xl">
        {/* Header */}
        <div className="mb-6">
          <Breadcrumbs items={getBreadcrumbs()} className="mb-4" />
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 mb-2">
                {viewMode === 'game-detail' && selectedGame
                  ? 'Game Details'
                  : viewMode === 'player-stats' && selectedPlayer
                  ? 'Player Stats'
                  : 'Game Center'}
              </h1>
              <p className="text-gray-600">{league.name}</p>
            </div>
          </div>
        </div>

      {/* Error Display */}
      {simulationError && (
        <div className="mb-6 bg-red-50 border border-red-200 rounded-lg p-4">
          <div className="flex items-center gap-2">
            <span className="text-red-600">❌</span>
            <p className="text-sm text-red-700">{simulationError}</p>
          </div>
          <button
            onClick={() => setSimulationError(null)}
            className="mt-2 text-sm text-red-600 hover:text-red-800 font-medium"
          >
            Dismiss
          </button>
        </div>
      )}

      {/* View Mode: Simulator */}
      {viewMode === 'simulator' && (
        <div className="space-y-8">
          {/* Schedule Status and Play Next Game */}
          {schedule.length > 0 && (
            <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
              <div className="bg-gradient-to-r from-emerald-600 to-teal-600 px-6 py-4">
                <h2 className="text-xl font-bold text-white">Season Schedule</h2>
                <p className="text-emerald-100 text-sm mt-1">
                  {scheduleStats.completed} of {scheduleStats.total} games completed
                </p>
              </div>
              <div className="p-6">
                {/* Progress Bar */}
                <div className="mb-6">
                  <div className="flex items-center justify-between text-sm mb-2">
                    <span className="text-gray-600">Season Progress</span>
                    <span className="font-medium text-gray-900">
                      {scheduleStats.total > 0 
                        ? Math.round((scheduleStats.completed / scheduleStats.total) * 100)
                        : 0}%
                    </span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-3">
                    <div 
                      className="bg-gradient-to-r from-emerald-500 to-teal-500 h-3 rounded-full transition-all duration-500"
                      style={{ 
                        width: scheduleStats.total > 0 
                          ? `${(scheduleStats.completed / scheduleStats.total) * 100}%`
                          : '0%'
                      }}
                    />
                  </div>
                </div>

                {/* Next Game or Season Complete */}
                {nextScheduledGame ? (
                  <div className="bg-gradient-to-r from-emerald-50 to-teal-50 rounded-lg p-4 border border-emerald-200">
                    <div className="flex items-center justify-between">
                      <div>
                        <div className="text-sm text-emerald-600 font-medium mb-1">
                          Next Scheduled Game (#{nextScheduledGame.game_number})
                        </div>
                        <div className="text-lg font-bold text-gray-900">
                          {getTeamName(nextScheduledGame.team1_id)} vs {getTeamName(nextScheduledGame.team2_id)}
                        </div>
                        <div className="text-sm text-gray-500 mt-1">
                          {scheduleStats.remaining} game{scheduleStats.remaining !== 1 ? 's' : ''} remaining
                        </div>
                      </div>
                      <button
                        onClick={handlePlayNextGame}
                        disabled={playingNextGame}
                        className="px-6 py-3 bg-gradient-to-r from-emerald-600 to-teal-600 text-white font-bold rounded-lg hover:from-emerald-700 hover:to-teal-700 transition-all shadow-lg hover:shadow-xl disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
                      >
                        {playingNextGame ? (
                          <>
                            <span className="animate-spin">⏳</span>
                            Simulating...
                          </>
                        ) : (
                          <>
                            <span>🎮</span>
                            Play Next Game
                          </>
                        )}
                      </button>
                    </div>
                  </div>
                ) : (
                  <div className="bg-gradient-to-r from-amber-50 to-yellow-50 rounded-lg p-6 border border-amber-200 text-center">
                    <div className="text-4xl mb-3">🏆</div>
                    <h3 className="text-lg font-bold text-amber-900">Season Complete!</h3>
                    <p className="text-sm text-amber-700 mt-1">
                      All {scheduleStats.total} scheduled games have been played.
                    </p>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Game Simulator */}
          <GameSimulator
            leagueId={leagueId!}
            teams={teams}
            onSimulate={handleSimulateGame}
          />

          {/* Game History */}
          {games.length > 0 && (
            <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
              <div className="bg-gradient-to-r from-slate-700 to-slate-800 px-6 py-4">
                <h2 className="text-xl font-bold text-white">Game History</h2>
                <p className="text-slate-300 text-sm mt-1">
                  {games.length} game{games.length !== 1 ? 's' : ''} played
                </p>
              </div>
              <div className="p-6">
                <div className="space-y-3">
                  {games.map((game) => {
                    const team1 = teams.find((t) => t.id === game.team1_id);
                    const team2 = teams.find((t) => t.id === game.team2_id);
                    const team1Won = game.winner_id === game.team1_id;

                    return (
                      <button
                        key={game.id}
                        onClick={() => handleSelectGame(game)}
                        className="w-full text-left p-4 bg-gray-50 hover:bg-gray-100 rounded-lg border border-gray-200 transition-colors"
                      >
                        <div className="flex items-center justify-between">
                          <div className="flex items-center gap-4 flex-1">
                            <div className="text-center min-w-[120px]">
                              <div className={`text-sm font-semibold ${team1Won ? 'text-green-600' : 'text-gray-600'}`}>
                                {team1?.name || 'Team 1'}
                              </div>
                              {team1Won && <span className="text-xs text-green-600">WINNER</span>}
                            </div>
                            <div className="text-gray-400 font-bold">VS</div>
                            <div className="text-center min-w-[120px]">
                              <div className={`text-sm font-semibold ${!team1Won ? 'text-green-600' : 'text-gray-600'}`}>
                                {team2?.name || 'Team 2'}
                              </div>
                              {!team1Won && <span className="text-xs text-green-600">WINNER</span>}
                            </div>
                          </div>
                          <div className="text-right">
                            <div className="text-xs text-gray-500">
                              {game.event_count ?? game.events?.length ?? 0} events
                            </div>
                            {game.completed_at && (
                              <div className="text-xs text-gray-400">
                                {new Date(game.completed_at).toLocaleDateString()}
                              </div>
                            )}
                          </div>
                        </div>
                      </button>
                    );
                  })}
                </div>
              </div>
            </div>
          )}

          {/* No games yet */}
          {games.length === 0 && (
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-8 text-center">
              <div className="text-4xl mb-3">🎮</div>
              <h3 className="text-lg font-semibold text-blue-900 mb-2">No Games Yet</h3>
              <p className="text-sm text-blue-700">
                Simulate your first game using the form above!
              </p>
            </div>
          )}
        </div>
      )}

      {/* View Mode: Game Detail */}
      {viewMode === 'game-detail' && selectedGame && (
        <div className="space-y-6">
          {/* Game Stats */}
          <GameStats
            game={selectedGame}
            team1Name={getTeamName(selectedGame.team1_id)}
            team2Name={getTeamName(selectedGame.team2_id)}
            team1Logo={getTeamLogo(selectedGame.team1_id)}
            team2Logo={getTeamLogo(selectedGame.team2_id)}
            players={playerMap}
          />

          {/* Game History */}
          <GameHistory
            game={selectedGame}
            players={playerMap}
            maxEvents={20}
          />
        </div>
      )}

      {/* View Mode: Player Stats */}
      {viewMode === 'player-stats' && selectedPlayer && (
        <div className="space-y-6">
          {/* Player Stats */}
          <PlayerStats player={selectedPlayer} />
        </div>
      )}
      </div>
    </div>
  );
};

export default GamesPage;
