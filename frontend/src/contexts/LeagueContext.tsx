/**
 * LeagueContext - React Context for managing league state across the application.
 * 
 * This context provides centralized state management for the current league,
 * including players, teams, and related data. Components can access and update
 * league state without prop drilling.
 */

import React, { createContext, useContext, useState, useCallback, ReactNode } from 'react';
import { League, Player, Team, Game, ApiError } from '../types';

// Context state interface
interface LeagueState {
  // Current league data
  currentLeague: League | null;
  players: Player[];
  teams: Team[];
  games: Game[];
  
  // Loading states
  isLoadingLeague: boolean;
  isLoadingPlayers: boolean;
  isLoadingTeams: boolean;
  isLoadingGames: boolean;
  
  // Error states
  leagueError: ApiError | null;
  playersError: ApiError | null;
  teamsError: ApiError | null;
  gamesError: ApiError | null;
}

// Context actions interface
interface LeagueActions {
  // League actions
  setCurrentLeague: (league: League | null) => void;
  updateLeague: (league: Partial<League>) => void;
  clearLeague: () => void;
  
  // Player actions
  setPlayers: (players: Player[]) => void;
  addPlayer: (player: Player) => void;
  updatePlayer: (playerId: string, updates: Partial<Player>) => void;
  removePlayer: (playerId: string) => void;
  
  // Team actions
  setTeams: (teams: Team[]) => void;
  addTeam: (team: Team) => void;
  updateTeam: (teamId: string, updates: Partial<Team>) => void;
  removeTeam: (teamId: string) => void;
  
  // Game actions
  setGames: (games: Game[]) => void;
  addGame: (game: Game) => void;
  
  // Loading state actions
  setLoadingLeague: (loading: boolean) => void;
  setLoadingPlayers: (loading: boolean) => void;
  setLoadingTeams: (loading: boolean) => void;
  setLoadingGames: (loading: boolean) => void;
  
  // Error state actions
  setLeagueError: (error: ApiError | null) => void;
  setPlayersError: (error: ApiError | null) => void;
  setTeamsError: (error: ApiError | null) => void;
  setGamesError: (error: ApiError | null) => void;
  
  // Utility actions
  resetState: () => void;
}

// Combined context interface
interface LeagueContextValue extends LeagueState, LeagueActions {}

// Initial state
const initialState: LeagueState = {
  currentLeague: null,
  players: [],
  teams: [],
  games: [],
  isLoadingLeague: false,
  isLoadingPlayers: false,
  isLoadingTeams: false,
  isLoadingGames: false,
  leagueError: null,
  playersError: null,
  teamsError: null,
  gamesError: null,
};

// Create context with undefined as default (will be provided by provider)
const LeagueContext = createContext<LeagueContextValue | undefined>(undefined);

// Provider props
interface LeagueProviderProps {
  children: ReactNode;
}

/**
 * LeagueProvider - Provides league state and actions to child components
 */
export const LeagueProvider: React.FC<LeagueProviderProps> = ({ children }) => {
  // State
  const [currentLeague, setCurrentLeague] = useState<League | null>(initialState.currentLeague);
  const [players, setPlayersState] = useState<Player[]>(initialState.players);
  const [teams, setTeamsState] = useState<Team[]>(initialState.teams);
  const [games, setGamesState] = useState<Game[]>(initialState.games);
  
  const [isLoadingLeague, setIsLoadingLeague] = useState(initialState.isLoadingLeague);
  const [isLoadingPlayers, setIsLoadingPlayers] = useState(initialState.isLoadingPlayers);
  const [isLoadingTeams, setIsLoadingTeams] = useState(initialState.isLoadingTeams);
  const [isLoadingGames, setIsLoadingGames] = useState(initialState.isLoadingGames);
  
  const [leagueError, setLeagueError] = useState<ApiError | null>(initialState.leagueError);
  const [playersError, setPlayersError] = useState<ApiError | null>(initialState.playersError);
  const [teamsError, setTeamsError] = useState<ApiError | null>(initialState.teamsError);
  const [gamesError, setGamesError] = useState<ApiError | null>(initialState.gamesError);

  // League actions
  const updateLeague = useCallback((updates: Partial<League>) => {
    setCurrentLeague(prev => prev ? { ...prev, ...updates } : null);
  }, []);

  const clearLeague = useCallback(() => {
    setCurrentLeague(null);
    setPlayersState([]);
    setTeamsState([]);
    setGamesState([]);
    setLeagueError(null);
    setPlayersError(null);
    setTeamsError(null);
    setGamesError(null);
  }, []);

  // Player actions
  const setPlayers = useCallback((newPlayers: Player[]) => {
    setPlayersState(newPlayers);
  }, []);

  const addPlayer = useCallback((player: Player) => {
    setPlayersState(prev => [...prev, player]);
  }, []);

  const updatePlayer = useCallback((playerId: string, updates: Partial<Player>) => {
    setPlayersState(prev =>
      prev.map(player =>
        player.id === playerId ? { ...player, ...updates } : player
      )
    );
  }, []);

  const removePlayer = useCallback((playerId: string) => {
    setPlayersState(prev => prev.filter(player => player.id !== playerId));
  }, []);

  // Team actions
  const setTeams = useCallback((newTeams: Team[]) => {
    setTeamsState(newTeams);
  }, []);

  const addTeam = useCallback((team: Team) => {
    setTeamsState(prev => [...prev, team]);
  }, []);

  const updateTeam = useCallback((teamId: string, updates: Partial<Team>) => {
    setTeamsState(prev =>
      prev.map(team =>
        team.id === teamId ? { ...team, ...updates } : team
      )
    );
  }, []);

  const removeTeam = useCallback((teamId: string) => {
    setTeamsState(prev => prev.filter(team => team.id !== teamId));
  }, []);

  // Game actions
  const setGames = useCallback((newGames: Game[]) => {
    setGamesState(newGames);
  }, []);

  const addGame = useCallback((game: Game) => {
    setGamesState(prev => [...prev, game]);
  }, []);

  // Loading state actions
  const setLoadingLeague = useCallback((loading: boolean) => {
    setIsLoadingLeague(loading);
  }, []);

  const setLoadingPlayers = useCallback((loading: boolean) => {
    setIsLoadingPlayers(loading);
  }, []);

  const setLoadingTeams = useCallback((loading: boolean) => {
    setIsLoadingTeams(loading);
  }, []);

  const setLoadingGames = useCallback((loading: boolean) => {
    setIsLoadingGames(loading);
  }, []);

  // Reset state
  const resetState = useCallback(() => {
    setCurrentLeague(initialState.currentLeague);
    setPlayersState(initialState.players);
    setTeamsState(initialState.teams);
    setGamesState(initialState.games);
    setIsLoadingLeague(initialState.isLoadingLeague);
    setIsLoadingPlayers(initialState.isLoadingPlayers);
    setIsLoadingTeams(initialState.isLoadingTeams);
    setIsLoadingGames(initialState.isLoadingGames);
    setLeagueError(initialState.leagueError);
    setPlayersError(initialState.playersError);
    setTeamsError(initialState.teamsError);
    setGamesError(initialState.gamesError);
  }, []);

  // Context value
  const value: LeagueContextValue = {
    // State
    currentLeague,
    players,
    teams,
    games,
    isLoadingLeague,
    isLoadingPlayers,
    isLoadingTeams,
    isLoadingGames,
    leagueError,
    playersError,
    teamsError,
    gamesError,
    
    // Actions
    setCurrentLeague,
    updateLeague,
    clearLeague,
    setPlayers,
    addPlayer,
    updatePlayer,
    removePlayer,
    setTeams,
    addTeam,
    updateTeam,
    removeTeam,
    setGames,
    addGame,
    setLoadingLeague,
    setLoadingPlayers,
    setLoadingTeams,
    setLoadingGames,
    setLeagueError,
    setPlayersError,
    setTeamsError,
    setGamesError,
    resetState,
  };

  return (
    <LeagueContext.Provider value={value}>
      {children}
    </LeagueContext.Provider>
  );
};

/**
 * useLeague - Hook to access league context
 * 
 * @throws Error if used outside of LeagueProvider
 */
export const useLeague = (): LeagueContextValue => {
  const context = useContext(LeagueContext);
  
  if (context === undefined) {
    throw new Error('useLeague must be used within a LeagueProvider');
  }
  
  return context;
};

/**
 * Utility hooks for specific parts of league state
 */

// Hook to get only players
export const usePlayers = () => {
  const { players, isLoadingPlayers, playersError, setPlayers, addPlayer, updatePlayer, removePlayer } = useLeague();
  return { players, isLoadingPlayers, playersError, setPlayers, addPlayer, updatePlayer, removePlayer };
};

// Hook to get only teams
export const useTeams = () => {
  const { teams, isLoadingTeams, teamsError, setTeams, addTeam, updateTeam, removeTeam } = useLeague();
  return { teams, isLoadingTeams, teamsError, setTeams, addTeam, updateTeam, removeTeam };
};

// Hook to get only games
export const useGames = () => {
  const { games, isLoadingGames, gamesError, setGames, addGame } = useLeague();
  return { games, isLoadingGames, gamesError, setGames, addGame };
};

// Hook to get only current league
export const useCurrentLeague = () => {
  const { currentLeague, isLoadingLeague, leagueError, setCurrentLeague, updateLeague, clearLeague } = useLeague();
  return { currentLeague, isLoadingLeague, leagueError, setCurrentLeague, updateLeague, clearLeague };
};

// Export context for testing purposes
export { LeagueContext };
