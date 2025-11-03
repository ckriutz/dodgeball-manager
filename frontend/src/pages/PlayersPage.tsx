/**
 * PlayersPage Component
 * 
 * Browse all players in a league with filtering and search.
 * Features:
 * - Display all players in the league
 * - Filter by free agents
 * - Search by player name
 * - Sort by various attributes
 * - View player details
 * 
 * This page allows users to explore the complete player pool.
 */

import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { PlayerList } from '../components/player/PlayerList';
import { Breadcrumbs, type BreadcrumbItem } from '../components/common/Breadcrumbs';
import { leagueApi } from '../services/api';
import type { Player, League, Team } from '../types';

/**
 * PlayersPage component
 */
export const PlayersPage: React.FC = () => {
  const { leagueId } = useParams<{ leagueId: string }>();
  const navigate = useNavigate();

  // State
  const [league, setLeague] = useState<League | null>(null);
  const [players, setPlayers] = useState<Player[]>([]);
  const [teams, setTeams] = useState<Team[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  /**
   * Load league and players on mount
   */
  useEffect(() => {
    loadData();
  }, [leagueId]);

  /**
   * Load data function
   */
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
      setLeague(leagueResponse.data as League);

      // Load players
      const playersResponse = await leagueApi.getPlayers(leagueId);
      if (playersResponse.error) {
        throw new Error(playersResponse.error.message);
      }
      setPlayers(playersResponse.data as Player[]);

      // Load teams
      const teamsResponse = await leagueApi.getTeams(leagueId);
      if (teamsResponse.error) {
        throw new Error(teamsResponse.error.message);
      }
      setTeams(teamsResponse.data as Team[]);
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

  /**
   * Handle player click
   */
  const handlePlayerClick = (player: Player) => {
    if (leagueId) {
      navigate(`/leagues/${leagueId}/players/${player.id}`);
    }
  };

  /**
   * Navigate back to league page
   */
  const handleBackToLeague = () => {
    if (leagueId) {
      navigate(`/leagues/${leagueId}`);
    } else {
      navigate('/');
    }
  };

  /**
   * Calculate player statistics
   */
  const getPlayerStats = () => {
    const freeAgents = players.filter((p) => p.team_id === null).length;
    const assigned = players.length - freeAgents;
    const avgValue =
      players.length > 0
        ? Math.round(
            players.reduce((sum, p) => sum + p.value, 0) / players.length
          )
        : 0;

    return { freeAgents, assigned, avgValue };
  };

  const stats = getPlayerStats();

  // Build breadcrumb items
  const getBreadcrumbs = (): BreadcrumbItem[] => {
    const items: BreadcrumbItem[] = [
      { label: 'Leagues', path: '/leagues' },
    ];
    
    if (league) {
      items.push({ label: league.name, path: `/leagues/${league.id}` });
      items.push({ label: 'Players' });
    }
    
    return items;
  };

  // Error state
  if (error) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 py-8">
        <div className="container mx-auto px-4 max-w-7xl">
          <Breadcrumbs items={getBreadcrumbs()} className="mb-6" />
          <div className="bg-white rounded-lg shadow-md border border-gray-200 p-8">
            <div className="text-center">
              <svg
                className="mx-auto h-12 w-12 text-red-400 mb-4"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                />
              </svg>
              <h2 className="text-2xl font-bold text-gray-900 mb-2">Error Loading Data</h2>
              <p className="text-gray-600 mb-6">{error}</p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 py-8">
      <div className="container mx-auto px-4 max-w-7xl">
        {/* Header */}
        <div className="mb-8">
          <Breadcrumbs items={getBreadcrumbs()} className="mb-4" />

          {league && (
            <div>
              <h1 className="text-4xl font-bold text-gray-900 mb-2">
                {league.name} - Players
              </h1>
              <p className="text-lg text-gray-600">
                Browse and search all players in your league
              </p>
            </div>
          )}
        </div>

        {/* Statistics Cards */}
        {!loading && players.length > 0 && (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
            {/* Total Players */}
            <div className="bg-white rounded-lg shadow-md border border-gray-200 p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600 mb-1">Total Players</p>
                  <p className="text-3xl font-bold text-gray-900">{players.length}</p>
                </div>
                <div className="inline-flex items-center justify-center w-12 h-12 rounded-full bg-blue-100">
                  <svg
                    className="h-6 w-6 text-blue-600"
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
              </div>
            </div>

            {/* Free Agents */}
            <div className="bg-white rounded-lg shadow-md border border-gray-200 p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600 mb-1">Free Agents</p>
                  <p className="text-3xl font-bold text-gray-900">{stats.freeAgents}</p>
                  <p className="text-xs text-gray-500 mt-1">{stats.assigned} assigned to teams</p>
                </div>
                <div className="inline-flex items-center justify-center w-12 h-12 rounded-full bg-green-100">
                  <svg
                    className="h-6 w-6 text-green-600"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
                    />
                  </svg>
                </div>
              </div>
            </div>

            {/* Average Value */}
            <div className="bg-white rounded-lg shadow-md border border-gray-200 p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600 mb-1">Average Value</p>
                  <p className="text-3xl font-bold text-gray-900">${stats.avgValue.toLocaleString()}</p>
                  <p className="text-xs text-gray-500 mt-1">per player</p>
                </div>
                <div className="inline-flex items-center justify-center w-12 h-12 rounded-full bg-yellow-100">
                  <svg
                    className="h-6 w-6 text-yellow-600"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                    />
                  </svg>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Player List */}
        <PlayerList
          players={players}
          teams={teams}
          onPlayerClick={handlePlayerClick}
          showStats={true}
          loading={loading}
          emptyMessage="No players have been generated for this league yet."
          leagueId={leagueId}
          onPlayerGenerated={loadData}
        />

        {/* Generate Players CTA - Show if no players */}
        {!loading && players.length === 0 && (
          <div className="bg-white rounded-lg shadow-md border border-gray-200 p-8 mt-8">
            <div className="text-center">
              <p className="text-gray-600 mb-4">
                This league doesn't have any players yet.
              </p>
              <button
                onClick={handleBackToLeague}
                className="inline-flex items-center gap-2 px-6 py-3 text-base font-medium text-white bg-blue-600 rounded-lg hover:bg-blue-700"
              >
                <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M13 10V3L4 14h7v7l9-11h-7z"
                  />
                </svg>
                <span>Go to League to Generate Players</span>
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default PlayersPage;
