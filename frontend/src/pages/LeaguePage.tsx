/**
 * LeaguePage Component
 * 
 * Main page for league setup and management.
 * Features:
 * - Create new league with LeagueForm
 * - Generate player pool for the league
 * - Display league information
 * - View generated players with PlayerList
 * - Navigate to player browsing
 * - Tabs for Standings, Schedule, Awards, and Season History
 * 
 * This is the main entry point for User Story 1: League Setup and Player Generation.
 * Enhanced for User Story 4: Season Management.
 */

import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { LeagueForm } from '../components/league/LeagueForm';
import { Breadcrumbs, type BreadcrumbItem } from '../components/common/Breadcrumbs';
import { LeagueStandings, type StandingsEntry } from '../components/league/LeagueStandings';
import { LeagueSchedule } from '../components/league/LeagueSchedule';
import { LeagueAwards, type AwardsData } from '../components/league/LeagueAwards';
import { SeasonHistory, type SeasonArchiveData } from '../components/league/SeasonHistory';
import { leagueApi, gameApi } from '../services/api';
import type { League, Player, Team, Game, CreateLeagueRequest, LeagueScheduleItem } from '../types';

/**
 * Tab type for navigation
 */
type LeagueTab = 'overview' | 'standings' | 'schedule' | 'awards' | 'history';

/**
 * Extended schedule item with game_id
 */
interface ScheduleGame extends LeagueScheduleItem {
  game_id?: string | null;
}

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
  const [teams, setTeams] = useState<Team[]>([]);
  const [games, setGames] = useState<Game[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [playersLoading, setPlayersLoading] = useState(false);
  const [playersError, setPlayersError] = useState<string | null>(null);
  const [leaguesLoading, setLeaguesLoading] = useState(true);
  
  // Tab state
  const [activeTab, setActiveTab] = useState<LeagueTab>('overview');
  
  // Standings state
  const [standings, setStandings] = useState<StandingsEntry[]>([]);
  const [standingsLoading, setStandingsLoading] = useState(false);
  const [standingsError, setStandingsError] = useState<string | null>(null);
  
  // Schedule state
  const [schedule, setSchedule] = useState<ScheduleGame[]>([]);
  const [scheduleLoading, setScheduleLoading] = useState(false);
  const [scheduleError, setScheduleError] = useState<string | null>(null);
  const [seasonNumber, setSeasonNumber] = useState<number>(1);
  const [seasonStatus, setSeasonStatus] = useState<string>('not_started');
  
  // Awards state
  const [awards, setAwards] = useState<AwardsData | null>(null);
  const [awardsLoading, setAwardsLoading] = useState(false);
  const [awardsError, setAwardsError] = useState<string | null>(null);
  
  // Season history state
  const [seasonHistory, setSeasonHistory] = useState<SeasonArchiveData[]>([]);
  const [historyLoading, setHistoryLoading] = useState(false);
  const [historyError, setHistoryError] = useState<string | null>(null);

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
        setTeams([]);
        setGames([]);
        setSchedule([]);
        setStandings([]);
        setAwards(null);
        setSeasonHistory([]);
        setError(null);
        setPlayersError(null);
        setActiveTab('overview');
        return;
      }

      try {
        const leagueResponse = await leagueApi.getLeague(leagueId);
        if (leagueResponse.error) {
          throw new Error(leagueResponse.error.message);
        }
        setLeague(leagueResponse.data as League);

        // Load players for this league
        const playersResponse = await leagueApi.getPlayers(leagueId);
        if (playersResponse.error) {
          throw new Error(playersResponse.error.message);
        }
        setPlayers(playersResponse.data as Player[]);
        
        // Load teams for this league
        const teamsResponse = await leagueApi.getTeams(leagueId);
        if (!teamsResponse.error) {
          setTeams(teamsResponse.data as Team[]);
        }
        
        // Load games for this league
        const gamesResponse = await gameApi.getGames(leagueId);
        if (!gamesResponse.error) {
          setGames(gamesResponse.data as Game[]);
        }
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
   * Load standings data
   */
  const loadStandings = useCallback(async () => {
    if (!leagueId) return;
    
    setStandingsLoading(true);
    setStandingsError(null);
    
    try {
      const response = await leagueApi.getStandings(leagueId);
      if (response.error) {
        throw new Error(response.error.message);
      }
      const data = response.data as { standings: StandingsEntry[] };
      setStandings(data.standings || []);
    } catch (err) {
      console.error('Failed to load standings:', err);
      setStandingsError(err instanceof Error ? err.message : 'Failed to load standings');
    } finally {
      setStandingsLoading(false);
    }
  }, [leagueId]);

  /**
   * Load schedule data
   */
  const loadSchedule = useCallback(async () => {
    if (!leagueId) return;
    
    setScheduleLoading(true);
    setScheduleError(null);
    
    try {
      const response = await leagueApi.getSchedule(leagueId);
      if (response.error) {
        throw new Error(response.error.message);
      }
      const data = response.data as { 
        schedule: ScheduleGame[]; 
        season_number?: number;
        season_status?: string;
      };
      setSchedule(data.schedule || []);
      if (data.season_number) setSeasonNumber(data.season_number);
      if (data.season_status) setSeasonStatus(data.season_status);
    } catch (err) {
      console.error('Failed to load schedule:', err);
      setScheduleError(err instanceof Error ? err.message : 'Failed to load schedule');
    } finally {
      setScheduleLoading(false);
    }
  }, [leagueId]);

  /**
   * Load awards data
   */
  const loadAwards = useCallback(async () => {
    if (!leagueId) return;
    
    setAwardsLoading(true);
    setAwardsError(null);
    
    try {
      const response = await leagueApi.getAwards(leagueId);
      if (response.error) {
        throw new Error(response.error.message);
      }
      setAwards(response.data as AwardsData);
    } catch (err) {
      console.error('Failed to load awards:', err);
      setAwardsError(err instanceof Error ? err.message : 'Failed to load awards');
    } finally {
      setAwardsLoading(false);
    }
  }, [leagueId]);

  /**
   * Load season history data
   */
  const loadSeasonHistory = useCallback(async () => {
    if (!leagueId) return;
    
    setHistoryLoading(true);
    setHistoryError(null);
    
    try {
      const response = await leagueApi.getSeasonHistory(leagueId);
      if (response.error) {
        throw new Error(response.error.message);
      }
      const data = response.data as { seasons: SeasonArchiveData[] };
      setSeasonHistory(data.seasons || []);
    } catch (err) {
      console.error('Failed to load season history:', err);
      setHistoryError(err instanceof Error ? err.message : 'Failed to load season history');
    } finally {
      setHistoryLoading(false);
    }
  }, [leagueId]);

  /**
   * Load data when tab changes
   */
  useEffect(() => {
    if (!leagueId) return;
    
    switch (activeTab) {
      case 'standings':
        loadStandings();
        break;
      case 'schedule':
        loadSchedule();
        break;
      case 'awards':
        loadAwards();
        break;
      case 'history':
        loadSeasonHistory();
        break;
    }
  }, [activeTab, leagueId, loadStandings, loadSchedule, loadAwards, loadSeasonHistory]);

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
      const newLeague = response.data as League;
      setLeague(newLeague);
      
      // Automatically generate players for the new league
      setPlayersLoading(true);
      try {
        const playersResponse = await leagueApi.generatePlayers(newLeague.id);
        if (playersResponse.error) {
          throw new Error(playersResponse.error.message);
        }
        setPlayers(playersResponse.data as Player[]);
      } catch (playerErr) {
        console.error('Failed to generate players:', playerErr);
        setPlayersError(
          playerErr instanceof Error
            ? playerErr.message
            : 'Failed to generate players. Please try again.'
        );
      } finally {
        setPlayersLoading(false);
      }
      
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

  // Build breadcrumb items
  const getBreadcrumbs = (): BreadcrumbItem[] => {
    const items: BreadcrumbItem[] = [
      { label: 'Leagues', path: '/leagues' },
    ];
    
    if (league) {
      items.push({ label: league.name });
    }
    
    return items;
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 py-8">
      <div className="container mx-auto px-4 max-w-7xl">
        {/* Breadcrumbs */}
        {league && <Breadcrumbs items={getBreadcrumbs()} className="mb-6" />}
        
        {/* Page Header - Only show when no league is selected */}
        {!league && (
          <div className="mb-8">
            <h1 className="text-4xl font-bold text-gray-900 mb-2">
              League Setup
            </h1>
            <p className="text-lg text-gray-600">
              Create your fantasy dodgeball league and generate the player pool
            </p>
          </div>
        )}

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
                </div>
              </div>
            </div>

            {/* Tab Navigation */}
            <div className="bg-white rounded-lg shadow-md border border-gray-200 overflow-hidden">
              <div className="border-b border-gray-200">
                <nav className="flex -mb-px" aria-label="Tabs">
                  <button
                    onClick={() => setActiveTab('overview')}
                    className={`px-6 py-4 text-sm font-medium border-b-2 ${
                      activeTab === 'overview'
                        ? 'border-blue-500 text-blue-600'
                        : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                    }`}
                  >
                    <span className="flex items-center gap-2">
                      <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2V6zM14 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V6zM4 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2v-2zM14 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z" />
                      </svg>
                      Overview
                    </span>
                  </button>
                  <button
                    onClick={() => setActiveTab('standings')}
                    className={`px-6 py-4 text-sm font-medium border-b-2 ${
                      activeTab === 'standings'
                        ? 'border-blue-500 text-blue-600'
                        : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                    }`}
                  >
                    <span className="flex items-center gap-2">
                      <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                      </svg>
                      Standings
                    </span>
                  </button>
                  <button
                    onClick={() => setActiveTab('schedule')}
                    className={`px-6 py-4 text-sm font-medium border-b-2 ${
                      activeTab === 'schedule'
                        ? 'border-blue-500 text-blue-600'
                        : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                    }`}
                  >
                    <span className="flex items-center gap-2">
                      <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                      </svg>
                      Schedule
                    </span>
                  </button>
                  <button
                    onClick={() => setActiveTab('awards')}
                    className={`px-6 py-4 text-sm font-medium border-b-2 ${
                      activeTab === 'awards'
                        ? 'border-blue-500 text-blue-600'
                        : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                    }`}
                  >
                    <span className="flex items-center gap-2">
                      <span className="text-lg">🏆</span>
                      Awards
                    </span>
                  </button>
                  <button
                    onClick={() => setActiveTab('history')}
                    className={`px-6 py-4 text-sm font-medium border-b-2 ${
                      activeTab === 'history'
                        ? 'border-blue-500 text-blue-600'
                        : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                    }`}
                  >
                    <span className="flex items-center gap-2">
                      <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                      History
                    </span>
                  </button>
                </nav>
              </div>

              {/* Tab Content */}
              <div className="p-6">
                {/* Overview Tab */}
                {activeTab === 'overview' && (
                  <div className="space-y-6">
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
                onClick={() => navigate(`/leagues/${league.id}/games`)}
                disabled={league.team_ids.length < 2}
                className="flex items-center gap-3 p-4 bg-white rounded-lg shadow-md border border-gray-200 hover:border-purple-300 hover:shadow-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <div className="inline-flex items-center justify-center w-10 h-10 rounded-full bg-purple-100">
                  <svg className="h-6 w-6 text-purple-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M13 10V3L4 14h7v7l9-11h-7z"
                    />
                  </svg>
                </div>
                <div className="text-left">
                  <p className="text-sm font-medium text-gray-900">Simulate Games</p>
                  <p className="text-xs text-gray-500">
                    {league.team_ids.length < 2 ? 'Need 2+ teams' : 'Battle it out!'}
                  </p>
                </div>
              </button>
                    </div>

                    {/* Player Generation/Loading Section */}
                    {players.length === 0 && playersLoading ? (
                      <div className="bg-gray-50 rounded-lg border border-gray-200 p-8">
                        <div className="text-center">
                          <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-blue-100 mb-4">
                            <svg
                              className="animate-spin h-8 w-8 text-blue-600"
                              fill="none"
                              viewBox="0 0 24 24"
                            >
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
                          </div>
                          <h3 className="text-xl font-bold text-gray-900 mb-2">
                            Generating Player Pool
                          </h3>
                          <p className="text-gray-600 max-w-md mx-auto">
                            Creating {league.settings.player_count} players with randomized skills, attributes, and values...
                          </p>
                        </div>
                      </div>
                    ) : players.length === 0 && playersError ? (
                      <div className="bg-gray-50 rounded-lg border border-gray-200 p-8">
                        <div className="text-center">
                          <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-red-100 mb-4">
                            <svg
                              className="h-8 w-8 text-red-600"
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
                          </div>
                          <h3 className="text-xl font-bold text-gray-900 mb-2">
                            Player Generation Failed
                          </h3>
                          <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-4 max-w-md mx-auto">
                            <p className="text-sm text-red-800">{playersError}</p>
                          </div>
                          <button
                            onClick={handleGeneratePlayers}
                            className="inline-flex items-center gap-2 px-6 py-3 text-base font-medium text-white bg-blue-600 rounded-lg hover:bg-blue-700"
                          >
                            <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                              <path
                                strokeLinecap="round"
                                strokeLinejoin="round"
                                strokeWidth={2}
                                d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
                              />
                            </svg>
                            <span>Retry Player Generation</span>
                          </button>
                        </div>
                      </div>
                    ) : (
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div className="bg-blue-50 rounded-lg p-4 border border-blue-200">
                          <h4 className="text-sm font-semibold text-blue-900 mb-1">Players</h4>
                          <p className="text-2xl font-bold text-blue-700">{players.length}</p>
                          <p className="text-xs text-blue-600">Generated players in pool</p>
                        </div>
                        <div className="bg-green-50 rounded-lg p-4 border border-green-200">
                          <h4 className="text-sm font-semibold text-green-900 mb-1">Teams</h4>
                          <p className="text-2xl font-bold text-green-700">{teams.length}</p>
                          <p className="text-xs text-green-600">Active teams in league</p>
                        </div>
                      </div>
                    )}
                  </div>
                )}

                {/* Standings Tab */}
                {activeTab === 'standings' && (
                  <LeagueStandings
                    standings={standings}
                    loading={standingsLoading}
                    error={standingsError}
                    onTeamClick={(teamId) => navigate(`/leagues/${league.id}/teams/${teamId}`)}
                  />
                )}

                {/* Schedule Tab */}
                {activeTab === 'schedule' && (
                  <div className="space-y-4">
                    {schedule.length === 0 && !scheduleLoading && !scheduleError && (
                      <div className="text-center py-8">
                        <p className="text-gray-500 mb-4">No schedule generated yet.</p>
                        <button
                          onClick={async () => {
                            try {
                              setScheduleLoading(true);
                              await leagueApi.createSchedule(league.id);
                              await loadSchedule();
                            } catch (err) {
                              setScheduleError(err instanceof Error ? err.message : 'Failed to create schedule');
                            }
                          }}
                          disabled={teams.length < 2}
                          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                          {teams.length < 2 ? 'Need at least 2 teams' : 'Generate Schedule'}
                        </button>
                      </div>
                    )}
                    <LeagueSchedule
                      schedule={schedule}
                      teams={teams}
                      games={games}
                      isLoading={scheduleLoading}
                      seasonNumber={seasonNumber}
                      seasonStatus={seasonStatus}
                      onPlayGame={(gameNumber) => {
                        navigate(`/leagues/${league.id}/games?game=${gameNumber}`);
                      }}
                    />
                  </div>
                )}

                {/* Awards Tab */}
                {activeTab === 'awards' && (
                  <LeagueAwards
                    awards={awards}
                    loading={awardsLoading}
                    error={awardsError}
                    onPlayerClick={(playerId) => navigate(`/leagues/${league.id}/players/${playerId}`)}
                  />
                )}

                {/* History Tab */}
                {activeTab === 'history' && (
                  <SeasonHistory
                    seasons={seasonHistory}
                    loading={historyLoading}
                    error={historyError}
                    onTeamClick={(teamId) => navigate(`/leagues/${league.id}/teams/${teamId}`)}
                    onPlayerClick={(playerId) => navigate(`/leagues/${league.id}/players/${playerId}`)}
                    teamNames={teams.reduce((acc, team) => ({ ...acc, [team.id]: team.name }), {})}
                    playerNames={players.reduce((acc, player) => ({ ...acc, [player.id]: player.name }), {})}
                  />
                )}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default LeaguePage;
