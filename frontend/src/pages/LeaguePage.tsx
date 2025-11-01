/**
 * LeaguePage Component
 * 
 * Main page for league setup and player generation.
 * Features:
 * - Create new league with LeagueForm
 * - Generate player pool for the league
 * - Display league information
 * - View generated players with PlayerList
 * - Navigate to player browsing
 * 
 * This is the main entry point for User Story 1: League Setup and Player Generation.
 */

import React, { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { LeagueForm } from '../components/league/LeagueForm';
import { PlayerList } from '../components/player/PlayerList';
import { leagueApi } from '../services/api';
import type { League, Player, CreateLeagueRequest } from '../types';

/**
 * LeaguePage component
 */
export const LeaguePage: React.FC = () => {
  const navigate = useNavigate();
  const { leagueId } = useParams<{ leagueId: string }>();

  // State
  const [allLeagues, setAllLeagues] = useState<League[]>([]);
  const [league, setLeague] = useState<League | null>(null);
  const [players, setPlayers] = useState<Player[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [playersLoading, setPlayersLoading] = useState(false);
  const [playersError, setPlayersError] = useState<string | null>(null);
  const [leaguesLoading, setLeaguesLoading] = useState(true);

  /**
   * Load all leagues on mount
   */
  useEffect(() => {
    const loadLeagues = async () => {
      setLeaguesLoading(true);
      try {
        const response = await leagueApi.getLeagues();
        if (response.error) {
          console.error('Failed to load leagues:', response.error);
        } else {
          setAllLeagues(response.data as League[]);
        }
      } catch (err) {
        console.error('Failed to load leagues:', err);
      } finally {
        setLeaguesLoading(false);
      }
    };

    loadLeagues();
  }, []);

  /**
   * Load specific league if leagueId is in URL, clear league if not
   */
  useEffect(() => {
    const loadLeague = async () => {
      if (!leagueId) {
        // Clear league state when navigating back to leagues list
        setLeague(null);
        setPlayers([]);
        setError(null);
        setPlayersError(null);
        return;
      }

      try {
        const leagueResponse = await leagueApi.getLeague(leagueId);
        if (leagueResponse.error) {
          throw new Error(leagueResponse.error.message);
        }
        setLeague(leagueResponse.data as League);

        // Also load players for this league
        const playersResponse = await leagueApi.getPlayers(leagueId);
        if (playersResponse.error) {
          throw new Error(playersResponse.error.message);
        }
        setPlayers(playersResponse.data as Player[]);
      } catch (err) {
        console.error('Failed to load league:', err);
        setError(
          err instanceof Error
            ? err.message
            : 'Failed to load league. Please try again.'
        );
      }
    };

    loadLeague();
  }, [leagueId]);

  /**
   * Handle league creation
   */
  const handleCreateLeague = async (data: CreateLeagueRequest) => {
    setLoading(true);
    setError(null);

    try {
      const response = await leagueApi.createLeague(data);
      if (response.error) {
        throw new Error(response.error.message);
      }
      setLeague(response.data as League);
      
      // Reload leagues list
      await reloadLeagues();
    } catch (err) {
      console.error('Failed to create league:', err);
      setError(
        err instanceof Error
          ? err.message
          : 'Failed to create league. Please try again.'
      );
    } finally {
      setLoading(false);
    }
  };

  /**
   * Reload leagues list
   */
  const reloadLeagues = async () => {
    try {
      const response = await leagueApi.getLeagues();
      if (!response.error) {
        setAllLeagues(response.data as League[]);
      }
    } catch (err) {
      console.error('Failed to reload leagues:', err);
    }
  };

  /**
   * Handle selecting an existing league
   */
  const handleSelectLeague = (selectedLeague: League) => {
    navigate(`/leagues/${selectedLeague.id}`);
  };

  /**
   * Handle player generation
   */
  const handleGeneratePlayers = async () => {
    if (!league) return;

    setPlayersLoading(true);
    setPlayersError(null);

    try {
      const response = await leagueApi.generatePlayers(league.id);
      if (response.error) {
        throw new Error(response.error.message);
      }
      setPlayers(response.data as Player[]);
    } catch (err) {
      console.error('Failed to generate players:', err);
      setPlayersError(
        err instanceof Error
          ? err.message
          : 'Failed to generate players. Please try again.'
      );
    } finally {
      setPlayersLoading(false);
    }
  };

  /**
   * Handle player click
   */
  const handlePlayerClick = (player: Player) => {
    // Navigate to player detail page (not yet implemented)
    console.log('Player clicked:', player);
  };

  /**
   * Navigate to all players page
   */
  const handleViewAllPlayers = () => {
    if (!league) return;
    navigate(`/leagues/${league.id}/players`);
  };

  /**
   * Navigate to teams page
   */
  const handleManageTeams = () => {
    if (!league) return;
    navigate(`/leagues/${league.id}/teams`);
  };

  /**
   * Reset and create new league
   */
  const handleCreateNewLeague = () => {
    setLeague(null);
    setPlayers([]);
    setError(null);
    setPlayersError(null);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 py-8">
      <div className="container mx-auto px-4 max-w-7xl">
        {/* Page Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">
            League Setup
          </h1>
          <p className="text-lg text-gray-600">
            Create your fantasy dodgeball league and generate the player pool
          </p>
        </div>

        {/* Existing Leagues List - Show if no league selected and leagues exist */}
        {!league && leaguesLoading && (
          <div className="mb-8">
            <div className="bg-white rounded-lg shadow-md border border-gray-200 p-12">
              <div className="flex items-center justify-center">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
                <span className="ml-4 text-gray-600">Loading leagues...</span>
              </div>
            </div>
          </div>
        )}

        {!league && !leaguesLoading && allLeagues.length > 0 && (
          <div className="mb-8">
            <div className="bg-white rounded-lg shadow-md border border-gray-200 p-6">
              <h2 className="text-2xl font-bold text-gray-900 mb-4">Your Leagues</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {allLeagues.map((existingLeague) => (
                  <button
                    key={existingLeague.id}
                    onClick={() => handleSelectLeague(existingLeague)}
                    className="flex items-center gap-4 p-4 text-left border-2 border-gray-200 rounded-lg hover:border-blue-400 hover:shadow-lg transition-all"
                  >
                    <div className="inline-flex items-center justify-center w-12 h-12 rounded-full bg-gradient-to-br from-blue-500 to-indigo-600 text-white font-bold text-xl">
                      {existingLeague.name.charAt(0).toUpperCase()}
                    </div>
                    <div className="flex-1 min-w-0">
                      <h3 className="text-lg font-bold text-gray-900 truncate">
                        {existingLeague.name}
                      </h3>
                      <div className="flex items-center gap-3 text-sm text-gray-600 mt-1">
                        <span className="flex items-center gap-1">
                          <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path
                              strokeLinecap="round"
                              strokeLinejoin="round"
                              strokeWidth={2}
                              d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z"
                            />
                          </svg>
                          {existingLeague.settings.player_count} players
                        </span>
                        <span className="flex items-center gap-1">
                          <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path
                              strokeLinecap="round"
                              strokeLinejoin="round"
                              strokeWidth={2}
                              d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"
                            />
                          </svg>
                          {existingLeague.team_ids.length} teams
                        </span>
                      </div>
                    </div>
                    <svg className="h-6 w-6 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M9 5l7 7-7 7"
                      />
                    </svg>
                  </button>
                ))}
              </div>
              <div className="mt-6 pt-6 border-t border-gray-200">
                <p className="text-sm text-gray-600 text-center">
                  Want to start fresh?{' '}
                  <span className="text-blue-600 font-medium">Create a new league below</span>
                </p>
              </div>
            </div>
          </div>
        )}

        {/* League Form - Show if no league created yet */}
        {!league && (
          <div className="mb-8">
            <LeagueForm
              onSubmit={handleCreateLeague}
              loading={loading}
              error={error}
            />
          </div>
        )}

        {/* League Info - Show after league created */}
        {league && (
          <div className="space-y-8">
            {/* Back to Leagues Button */}
            <div>
              <button
                onClick={() => {
                  setLeague(null);
                  setPlayers([]);
                  setError(null);
                  setPlayersError(null);
                  navigate('/leagues', { replace: true });
                }}
                className="flex items-center gap-2 text-blue-600 hover:text-blue-700 font-medium"
              >
                <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M10 19l-7-7m0 0l7-7m-7 7h18"
                  />
                </svg>
                <span>Back to All Leagues</span>
              </button>
            </div>

            {/* League Details Card */}
            <div className="bg-white rounded-lg shadow-md border border-gray-200 p-6">
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <h2 className="text-2xl font-bold text-gray-900 mb-2">
                    {league.name}
                  </h2>
                  <div className="flex items-center gap-6 text-sm text-gray-600">
                    <div className="flex items-center gap-2">
                      <svg
                        className="h-5 w-5 text-gray-400"
                        fill="none"
                        viewBox="0 0 24 24"
                        stroke="currentColor"
                      >
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth={2}
                          d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z"
                        />
                      </svg>
                      <span>
                        <span className="font-medium">{league.settings.player_count}</span> player pool
                      </span>
                    </div>
                    <div className="flex items-center gap-2">
                      <svg
                        className="h-5 w-5 text-gray-400"
                        fill="none"
                        viewBox="0 0 24 24"
                        stroke="currentColor"
                      >
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth={2}
                          d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"
                        />
                      </svg>
                      <span>
                        <span className="font-medium">{players.length}</span> players generated
                      </span>
                    </div>
                    <div className="flex items-center gap-2">
                      <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                        ID: {league.id}
                      </span>
                    </div>
                  </div>
                </div>
                <div className="flex gap-2">
                  <button
                    onClick={handleManageTeams}
                    className="inline-flex items-center gap-2 px-4 py-2 text-sm font-medium text-white bg-green-600 rounded-lg hover:bg-green-700"
                  >
                    <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"
                      />
                    </svg>
                    <span>Manage Teams</span>
                  </button>
                  <button
                    onClick={handleCreateNewLeague}
                    className="px-4 py-2 text-sm text-gray-600 hover:text-gray-900 font-medium border border-gray-300 rounded-lg hover:bg-gray-50"
                  >
                    Create New League
                  </button>
                </div>
              </div>
            </div>

            {/* Quick Actions */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <button
                onClick={handleViewAllPlayers}
                disabled={players.length === 0}
                className="flex items-center gap-3 p-4 bg-white rounded-lg shadow-md border border-gray-200 hover:border-blue-300 hover:shadow-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <div className="inline-flex items-center justify-center w-10 h-10 rounded-full bg-blue-100">
                  <svg className="h-6 w-6 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z"
                    />
                  </svg>
                </div>
                <div className="text-left">
                  <p className="text-sm font-medium text-gray-900">Browse Players</p>
                  <p className="text-xs text-gray-500">View all players in the league</p>
                </div>
              </button>

              <button
                onClick={handleManageTeams}
                disabled={players.length === 0}
                className="flex items-center gap-3 p-4 bg-white rounded-lg shadow-md border border-gray-200 hover:border-green-300 hover:shadow-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <div className="inline-flex items-center justify-center w-10 h-10 rounded-full bg-green-100">
                  <svg className="h-6 w-6 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"
                    />
                  </svg>
                </div>
                <div className="text-left">
                  <p className="text-sm font-medium text-gray-900">Manage Teams</p>
                  <p className="text-xs text-gray-500">Create teams and draft players</p>
                </div>
              </button>

              <button
                disabled={true}
                className="flex items-center gap-3 p-4 bg-white rounded-lg shadow-md border border-gray-200 opacity-50 cursor-not-allowed"
              >
                <div className="inline-flex items-center justify-center w-10 h-10 rounded-full bg-purple-100">
                  <svg className="h-6 w-6 text-purple-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M9 12l2 2 4-4M7.835 4.697a3.42 3.42 0 001.946-.806 3.42 3.42 0 014.438 0 3.42 3.42 0 001.946.806 3.42 3.42 0 013.138 3.138 3.42 3.42 0 00.806 1.946 3.42 3.42 0 010 4.438 3.42 3.42 0 00-.806 1.946 3.42 3.42 0 01-3.138 3.138 3.42 3.42 0 00-1.946.806 3.42 3.42 0 01-4.438 0 3.42 3.42 0 00-1.946-.806 3.42 3.42 0 01-3.138-3.138 3.42 3.42 0 00-.806-1.946 3.42 3.42 0 010-4.438 3.42 3.42 0 00.806-1.946 3.42 3.42 0 013.138-3.138z"
                    />
                  </svg>
                </div>
                <div className="text-left">
                  <p className="text-sm font-medium text-gray-900">Simulate Games</p>
                  <p className="text-xs text-gray-500">Coming in User Story 3</p>
                </div>
              </button>
            </div>

            {/* Player Generation Section */}
            {players.length === 0 ? (
              <div className="bg-white rounded-lg shadow-md border border-gray-200 p-8">
                <div className="text-center">
                  <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-blue-100 mb-4">
                    <svg
                      className="h-8 w-8 text-blue-600"
                      fill="none"
                      viewBox="0 0 24 24"
                      stroke="currentColor"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z"
                      />
                    </svg>
                  </div>
                  <h3 className="text-xl font-bold text-gray-900 mb-2">
                    Generate Player Pool
                  </h3>
                  <p className="text-gray-600 mb-6 max-w-md mx-auto">
                    Generate {league.settings.player_count} players with randomized skills, attributes, and values for your league.
                  </p>
                  {playersError && (
                    <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-4 max-w-md mx-auto">
                      <p className="text-sm text-red-800">{playersError}</p>
                    </div>
                  )}
                  <button
                    onClick={handleGeneratePlayers}
                    disabled={playersLoading}
                    className="inline-flex items-center gap-2 px-6 py-3 text-base font-medium text-white bg-blue-600 rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {playersLoading ? (
                      <>
                        <svg className="animate-spin h-5 w-5" fill="none" viewBox="0 0 24 24">
                          <circle
                            className="opacity-25"
                            cx="12"
                            cy="12"
                            r="10"
                            stroke="currentColor"
                            strokeWidth="4"
                          />
                          <path
                            className="opacity-75"
                            fill="currentColor"
                            d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                          />
                        </svg>
                        <span>Generating Players...</span>
                      </>
                    ) : (
                      <>
                        <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            strokeWidth={2}
                            d="M13 10V3L4 14h7v7l9-11h-7z"
                          />
                        </svg>
                        <span>Generate Players</span>
                      </>
                    )}
                  </button>
                </div>
              </div>
            ) : (
              /* Player List Section */
              <div>
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-2xl font-bold text-gray-900">Generated Players</h3>
                  <button
                    onClick={handleViewAllPlayers}
                    className="text-sm text-blue-600 hover:text-blue-700 font-medium"
                  >
                    View All Players →
                  </button>
                </div>
                <PlayerList
                  players={players}
                  onPlayerClick={handlePlayerClick}
                  showStats={true}
                />
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default LeaguePage;
