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
 * 
 * This page integrates GameSimulator, GameHistory, GameStats, and PlayerStats components.
 */

import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { GameSimulator } from '../components/game/GameSimulator';
import { GameHistory } from '../components/game/GameHistory';
import { GameStats } from '../components/game/GameStats';
import { PlayerStats } from '../components/player/PlayerStats';
import { gameApi, leagueApi, teamApi } from '../services/api';
import type { Team, Player, League, Game, CreateGameRequest } from '../types';

type ViewMode = 'simulator' | 'game-detail' | 'player-stats';

/**
 * GamesPage component
 */
export const GamesPage: React.FC = () => {
  const { leagueId } = useParams<{ leagueId: string }>();
  const navigate = useNavigate();

  // State
  const [viewMode, setViewMode] = useState<ViewMode>('simulator');
  const [league, setLeague] = useState<League | null>(null);
  const [teams, setTeams] = useState<Team[]>([]);
  const [playerMap, setPlayerMap] = useState<Record<string, Player>>({});
  const [games, setGames] = useState<Game[]>([]);
  const [selectedGame, setSelectedGame] = useState<Game | null>(null);
  const [selectedPlayer, setSelectedPlayer] = useState<Player | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [simulationError, setSimulationError] = useState<string | null>(null);

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
   * Navigate back to simulator
   */
  const handleBackToSimulator = () => {
    setViewMode('simulator');
    setSelectedGame(null);
    setSelectedPlayer(null);
  };

  // Loading state
  if (loading) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="flex items-center justify-center h-64">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
            <p className="text-gray-600">Loading game data...</p>
          </div>
        </div>
      </div>
    );
  }

  // Error state
  if (error) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="bg-red-50 border border-red-200 rounded-lg p-6">
          <div className="flex items-center gap-3">
            <div className="text-red-600 text-2xl">⚠️</div>
            <div>
              <h3 className="text-lg font-semibold text-red-800 mb-1">Error Loading Data</h3>
              <p className="text-sm text-red-700">{error}</p>
            </div>
          </div>
          <button
            onClick={() => navigate(`/leagues/${leagueId}`)}
            className="mt-4 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700"
          >
            Back to League
          </button>
        </div>
      </div>
    );
  }

  // No league
  if (!league) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6">
          <p className="text-yellow-700">League not found</p>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      {/* Header */}
      <div className="mb-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 mb-2">Game Center</h1>
            <p className="text-gray-600">{league.name}</p>
          </div>
          <button
            onClick={() => navigate(`/leagues/${leagueId}`)}
            className="px-4 py-2 text-gray-700 hover:text-gray-900 font-medium"
          >
            ← Back to League
          </button>
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
                              {game.events?.length || 0} events
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
          {/* Back Button */}
          <button
            onClick={handleBackToSimulator}
            className="text-blue-600 hover:text-blue-800 font-medium flex items-center gap-2"
          >
            ← Back to Game Center
          </button>

          {/* Game Stats */}
          <GameStats
            game={selectedGame}
            team1Name={getTeamName(selectedGame.team1_id)}
            team2Name={getTeamName(selectedGame.team2_id)}
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
          {/* Back Button */}
          <button
            onClick={handleBackToSimulator}
            className="text-blue-600 hover:text-blue-800 font-medium flex items-center gap-2"
          >
            ← Back to Game Center
          </button>

          {/* Player Stats */}
          <PlayerStats player={selectedPlayer} />
        </div>
      )}
    </div>
  );
};

export default GamesPage;
