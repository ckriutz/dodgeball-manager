/**
 * TeamsPage Component
 * 
 * Manage teams in a league - create teams, view team rosters, and manage players.
 * Features:
 * - Create new teams
 * - View all teams in a league
 * - Select team to view/edit roster
 * - Add/remove players from roster
 * - Designate starters
 * - View budget and spending
 * 
 * This page integrates TeamForm, TeamCard, TeamRoster, and TeamBudget components.
 */

import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { TeamForm } from '../components/team/TeamForm';
import { TeamCard } from '../components/team/TeamCard';
import { TeamRoster } from '../components/team/TeamRoster';
import { PlayerList } from '../components/player/PlayerList';
import { teamApi, leagueApi } from '../services/api';
import type { Team, Player, League, CreateTeamRequest } from '../types';

type ViewMode = 'list' | 'create' | 'roster';

/**
 * TeamsPage component
 */
export const TeamsPage: React.FC = () => {
  const { leagueId } = useParams<{ leagueId: string }>();
  const navigate = useNavigate();

  // State
  const [viewMode, setViewMode] = useState<ViewMode>('list');
  const [league, setLeague] = useState<League | null>(null);
  const [teams, setTeams] = useState<Team[]>([]);
  const [selectedTeam, setSelectedTeam] = useState<Team | null>(null);
  const [allPlayers, setAllPlayers] = useState<Player[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [actionLoading, setActionLoading] = useState(false);
  const [actionError, setActionError] = useState<string | null>(null);

  /**
   * Load league, teams, and players on mount
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
        setAllPlayers(playersResponse.data as Player[]);
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
   * Reload selected team
   */
  const reloadSelectedTeam = async () => {
    if (!selectedTeam) return;

    try {
      const response = await teamApi.getTeam(selectedTeam.id);
      if (!response.error) {
        const updatedTeam = response.data as Team;
        setSelectedTeam(updatedTeam);
        
        // Update in teams list
        setTeams((prev) =>
          prev.map((t) => (t.id === updatedTeam.id ? updatedTeam : t))
        );

        // Reload players
        if (league) {
          const playersResponse = await leagueApi.getPlayers(league.id);
          if (!playersResponse.error) {
            setAllPlayers(playersResponse.data as Player[]);
          }
        }
      }
    } catch (err) {
      console.error('Failed to reload team:', err);
    }
  };

  /**
   * Handle create team
   */
  const handleCreateTeam = async (data: CreateTeamRequest) => {
    setActionLoading(true);
    setActionError(null);

    try {
      const response = await teamApi.createTeam(data);
      if (response.error) {
        throw new Error(response.error.message);
      }

      // Reload league data first to get updated team_ids
      if (leagueId) {
        const leagueResponse = await leagueApi.getLeague(leagueId);
        if (!leagueResponse.error) {
          const updatedLeague = leagueResponse.data as League;
          setLeague(updatedLeague);
          
          // Now reload teams with the updated league data
          const teamsPromises = updatedLeague.team_ids.map((teamId) =>
            teamApi.getTeam(teamId)
          );
          const teamsResponses = await Promise.all(teamsPromises);
          const teamsData = teamsResponses
            .filter((r) => !r.error)
            .map((r) => r.data as Team);
          setTeams(teamsData);
        }
      }

      // Switch back to list view
      setViewMode('list');
    } catch (err) {
      console.error('Failed to create team:', err);
      setActionError(
        err instanceof Error ? err.message : 'Failed to create team'
      );
      throw err; // Re-throw so form can handle it
    } finally {
      setActionLoading(false);
    }
  };

  /**
   * Handle team click
   */
  const handleTeamClick = (team: Team) => {
    setSelectedTeam(team);
    setViewMode('roster');
  };

  /**
   * Handle add player to team
   */
  const handleAddPlayer = async (player: Player) => {
    if (!selectedTeam) return;

    setActionLoading(true);
    setActionError(null);

    try {
      const response = await teamApi.addPlayerToTeam(selectedTeam.id, player.id);
      if (response.error) {
        throw new Error(response.error.message);
      }

      // Reload team and players
      await reloadSelectedTeam();
    } catch (err) {
      console.error('Failed to add player:', err);
      setActionError(
        err instanceof Error ? err.message : 'Failed to add player to roster'
      );
    } finally {
      setActionLoading(false);
    }
  };

  /**
   * Handle remove player from team
   */
  const handleRemovePlayer = async (playerId: string) => {
    if (!selectedTeam) return;

    setActionLoading(true);
    setActionError(null);

    try {
      const response = await teamApi.removePlayerFromTeam(selectedTeam.id, playerId);
      if (response.error) {
        throw new Error(response.error.message);
      }

      // Reload team and players
      await reloadSelectedTeam();
    } catch (err) {
      console.error('Failed to remove player:', err);
      setActionError(
        err instanceof Error ? err.message : 'Failed to remove player from roster'
      );
    } finally {
      setActionLoading(false);
    }
  };

  /**
   * Handle set starters
   */
  const handleSetStarters = async (starterIds: string[]) => {
    if (!selectedTeam) return;

    setActionLoading(true);
    setActionError(null);

    try {
      const response = await teamApi.updateStarters(selectedTeam.id, starterIds);
      if (response.error) {
        throw new Error(response.error.message);
      }

      // Reload team and players
      await reloadSelectedTeam();
    } catch (err) {
      console.error('Failed to update starters:', err);
      setActionError(
        err instanceof Error ? err.message : 'Failed to update starters'
      );
    } finally {
      setActionLoading(false);
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
   * Get players for selected team
   */
  const getTeamPlayers = (): Player[] => {
    if (!selectedTeam) return [];
    return allPlayers.filter((p) => selectedTeam.player_ids.includes(p.id));
  };

  /**
   * Get free agent players
   */
  const getFreeAgents = (): Player[] => {
    return allPlayers.filter((p) => p.team_id === null);
  };

  /**
   * Calculate team statistics
   */
  const getTeamStats = () => {
    const totalTeams = teams.length;
    const totalPlayers = allPlayers.filter((p) => p.team_id !== null).length;
    const freeAgents = allPlayers.length - totalPlayers;

    return { totalTeams, totalPlayers, freeAgents };
  };

  const stats = getTeamStats();

  // Error state
  if (error) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 py-8">
        <div className="container mx-auto px-4 max-w-7xl">
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
              <button
                onClick={handleBackToLeague}
                className="px-6 py-3 text-base font-medium text-white bg-blue-600 rounded-lg hover:bg-blue-700"
              >
                Back to League
              </button>
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
          <button
            onClick={handleBackToLeague}
            className="flex items-center gap-2 text-blue-600 hover:text-blue-700 font-medium mb-4"
          >
            <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M10 19l-7-7m0 0l7-7m-7 7h18"
              />
            </svg>
            <span>Back to League</span>
          </button>

          {league && (
            <div className="flex items-center justify-between">
              <div>
                <h1 className="text-4xl font-bold text-gray-900 mb-2">
                  {league.name} - Teams
                </h1>
                <p className="text-lg text-gray-600">
                  Create teams and build your roster
                </p>
              </div>
              {viewMode === 'list' && (
                <button
                  onClick={() => setViewMode('create')}
                  className="inline-flex items-center gap-2 px-6 py-3 text-base font-medium text-white bg-blue-600 rounded-lg hover:bg-blue-700"
                >
                  <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M12 4v16m8-8H4"
                    />
                  </svg>
                  <span>Create Team</span>
                </button>
              )}
            </div>
          )}
        </div>

        {/* Statistics Cards - Show in list view */}
        {!loading && viewMode === 'list' && (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
            {/* Total Teams */}
            <div className="bg-white rounded-lg shadow-md border border-gray-200 p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600 mb-1">Total Teams</p>
                  <p className="text-3xl font-bold text-gray-900">{stats.totalTeams}</p>
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
                      d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"
                    />
                  </svg>
                </div>
              </div>
            </div>

            {/* Assigned Players */}
            <div className="bg-white rounded-lg shadow-md border border-gray-200 p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600 mb-1">Assigned Players</p>
                  <p className="text-3xl font-bold text-gray-900">{stats.totalPlayers}</p>
                  <p className="text-xs text-gray-500 mt-1">
                    {stats.freeAgents} free agents available
                  </p>
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
                      d="M18 9v3m0 0v3m0-3h3m-3 0h-3m-2-5a4 4 0 11-8 0 4 4 0 018 0zM3 20a6 6 0 0112 0v1H3v-1z"
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
                  <p className="text-xs text-gray-500 mt-1">Available to draft</p>
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
                      d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z"
                    />
                  </svg>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Content based on view mode */}
        {loading ? (
          <div className="bg-white rounded-lg shadow-md border border-gray-200 p-12">
            <div className="flex items-center justify-center">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
              <span className="ml-4 text-gray-600">Loading teams...</span>
            </div>
          </div>
        ) : viewMode === 'create' ? (
          <div className="bg-white rounded-lg shadow-md border border-gray-200 p-8">
            <div className="max-w-2xl mx-auto">
              <h2 className="text-2xl font-bold text-gray-900 mb-6">Create New Team</h2>
              <TeamForm
                leagues={league ? [league] : []}
                onSubmit={handleCreateTeam}
                onCancel={() => setViewMode('list')}
                isLoading={actionLoading}
                error={actionError}
              />
            </div>
          </div>
        ) : viewMode === 'roster' && selectedTeam ? (
          <div className="space-y-6">
            {/* Team Header */}
            <div className="flex items-start gap-6">
              <button
                onClick={() => {
                  setSelectedTeam(null);
                  setViewMode('list');
                }}
                className="inline-flex items-center gap-2 px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50"
              >
                <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M10 19l-7-7m0 0l7-7m-7 7h18"
                  />
                </svg>
                <span>Back to Teams</span>
              </button>
              <div className="flex-1">
                <TeamCard team={selectedTeam} showDetails={true} />
              </div>
            </div>

            {/* Action Error */}
            {actionError && (
              <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                <div className="flex items-start gap-3">
                  <svg
                    className="h-5 w-5 text-red-400 mt-0.5"
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
                  <div className="flex-1">
                    <p className="text-sm font-medium text-red-800">{actionError}</p>
                  </div>
                  <button
                    onClick={() => setActionError(null)}
                    className="text-red-400 hover:text-red-500"
                  >
                    <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M6 18L18 6M6 6l12 12"
                      />
                    </svg>
                  </button>
                </div>
              </div>
            )}

            {/* Roster Management */}
            <TeamRoster
              team={selectedTeam}
              players={getTeamPlayers()}
              onAddPlayer={() => {}} // Opens player selection modal (not implemented yet)
              onRemovePlayer={handleRemovePlayer}
              onSetStarters={handleSetStarters}
              readonly={actionLoading}
            />

            {/* Free Agents Section */}
            <div className="bg-white rounded-lg shadow-md border border-gray-200 p-6">
              <h3 className="text-xl font-bold text-gray-900 mb-4">
                Available Free Agents ({getFreeAgents().length})
              </h3>
              <PlayerList
                players={getFreeAgents()}
                showStats={true}
                loading={false}
                emptyMessage="No free agents available."
                actionButton={{
                  label: '+ Add to Team',
                  onClick: handleAddPlayer,
                  variant: 'success',
                  isDisabled: (player) => {
                    // Disable if team is at max capacity or over budget
                    if (!selectedTeam) return true;
                    const currentRoster = allPlayers.filter(p => p.team_id === selectedTeam.id);
                    if (currentRoster.length >= 10) return true; // Max roster size
                    const remainingBudget = selectedTeam.budget - currentRoster.reduce((sum, p) => sum + p.value, 0);
                    return player.value > remainingBudget;
                  },
                }}
              />
            </div>
          </div>
        ) : (
          /* Team List View */
          <div>
            {teams.length === 0 ? (
              <div className="bg-white rounded-lg shadow-md border border-gray-200 p-12">
                <div className="text-center">
                  <svg
                    className="mx-auto h-12 w-12 text-gray-400 mb-4"
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
                  <h3 className="text-lg font-medium text-gray-900 mb-2">No Teams Yet</h3>
                  <p className="text-gray-600 mb-6">
                    Create your first team to start building your roster and competing in the league.
                  </p>
                  <button
                    onClick={() => setViewMode('create')}
                    className="inline-flex items-center gap-2 px-6 py-3 text-base font-medium text-white bg-blue-600 rounded-lg hover:bg-blue-700"
                  >
                    <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M12 4v16m8-8H4"
                      />
                    </svg>
                    <span>Create Team</span>
                  </button>
                </div>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {teams.map((team) => (
                  <TeamCard
                    key={team.id}
                    team={team}
                    onClick={() => handleTeamClick(team)}
                    showDetails={false}
                  />
                ))}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default TeamsPage;
