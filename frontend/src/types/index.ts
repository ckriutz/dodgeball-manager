/**
 * Common TypeScript type definitions for the Dodgeball Fantasy League frontend.
 * 
 * These types match the backend API schemas and provide type safety throughout
 * the frontend application.
 */

// Base types
export type UUID = string;

// Player types
export interface PlayerSkills {
  catching: number;
  throwing: number;
  dodging: number;
  speed: number;
  iq: number;
  luck: number;
}

export interface PlayerInjury {
  severity: 'minor' | 'moderate' | 'severe';
  affected_reduction: number;
  games_remaining: number;
}

export interface PlayerStats {
  throws_attempted: number;
  catches_made: number;
  times_hit: number;
  missed_throws: number;
  successful_hits: number;
}

export interface Player {
  id: UUID;
  name: string;
  age: number;
  avatar: string;
  skills: PlayerSkills;
  value: number;
  injury: PlayerInjury | null;
  stats: PlayerStats;
  league_id: UUID | null;
  team_id: UUID | null;
  is_starter: boolean;
}

// Team types
export interface Team {
  id: UUID;
  name: string;
  description: string;
  logo: string; // Image filename from public/images/team_avatars/
  budget: number;
  player_ids: UUID[];
  starter_ids: UUID[];
  wins: number;
  losses: number;
  awards: string[];
  league_id: UUID;
}

// League types
export interface LeagueSettings {
  player_count: number;
  season_rounds: number;
}

export interface LeagueScheduleItem {
  game_number: number;
  team1_id: UUID;
  team2_id: UUID;
  completed: boolean;
}

export interface League {
  id: UUID;
  name: string;
  settings: LeagueSettings;
  team_ids: UUID[];
  game_ids: UUID[];
  schedule: LeagueScheduleItem[];
  created_at: string;
}

// Game types
export type GameEventType = 'throw' | 'hit' | 'catch' | 'miss' | 'elimination';

export interface GameEvent {
  turn: number;
  type: GameEventType;
  thrower_id: UUID;
  target_id: UUID;
  outcome: string;
}

export interface Game {
  id: UUID;
  league_id: UUID;
  team1_id: UUID;
  team2_id: UUID;
  team1_starters: UUID[];
  team2_starters: UUID[];
  events?: GameEvent[]; // Optional: only included in full game details, not in summaries
  winner_id: UUID | null;
  completed_at: string | null;
  seed: number;
}

// Request types
export interface CreateLeagueRequest {
  name: string;
  player_count?: number;
}

export interface CreateTeamRequest {
  name: string;
  description?: string;
  logo?: string; // Image filename from available team avatars
  league_id: UUID; // Provided by context, not user input
}

export interface AddPlayerToTeamRequest {
  player_id: UUID;
}

export interface UpdateTeamStartersRequest {
  starter_ids: UUID[];
}

export interface CreateGameRequest {
  league_id: UUID;
  team1_id: UUID;
  team2_id: UUID;
  seed?: number;
}

// Response types
export interface GeneratePlayersResponse {
  count: number;
  players: Player[];
}

export interface LeagueStandingsItem {
  team_id: UUID;
  team_name: string;
  wins: number;
  losses: number;
  win_percentage: number;
}

export interface LeagueStandingsResponse {
  standings: LeagueStandingsItem[];
}

export interface LeagueAwardsResponse {
  awards: Record<string, any>;
}

export interface HealthResponse {
  status: string;
  version: string;
  storage_stats: Record<string, number>;
}

// API error types
export interface ApiError {
  message: string;
  detail?: string;
}

export interface ApiResponse<T> {
  data?: T;
  error?: ApiError;
}

// UI state types
export type LoadingState = 'idle' | 'loading' | 'success' | 'error';

export interface ComponentState<T> {
  data: T | null;
  loading: boolean;
  error: string | null;
}

// Form types
export interface FormErrors {
  [key: string]: string;
}

// Navigation types
export type AppRoute = 
  | '/'
  | '/leagues'
  | '/leagues/:leagueId'
  | '/players'
  | '/teams'
  | '/teams/:teamId'
  | '/games'
  | '/games/:gameId';

// Utility types
export type Optional<T> = T | null | undefined;
export type Nullable<T> = T | null;
export type Maybe<T> = T | undefined;

// Type guards
export function isPlayer(obj: any): obj is Player {
  return (
    obj &&
    typeof obj === 'object' &&
    'id' in obj &&
    'name' in obj &&
    'skills' in obj &&
    'value' in obj
  );
}

export function isTeam(obj: any): obj is Team {
  return (
    obj &&
    typeof obj === 'object' &&
    'id' in obj &&
    'name' in obj &&
    'budget' in obj &&
    'player_ids' in obj
  );
}

export function isLeague(obj: any): obj is League {
  return (
    obj &&
    typeof obj === 'object' &&
    'id' in obj &&
    'name' in obj &&
    'settings' in obj &&
    'team_ids' in obj
  );
}

export function isGame(obj: any): obj is Game {
  return (
    obj &&
    typeof obj === 'object' &&
    'id' in obj &&
    'league_id' in obj &&
    'team1_id' in obj &&
    'team2_id' in obj &&
    'events' in obj
  );
}

export function isApiError(obj: any): obj is ApiError {
  return obj && typeof obj === 'object' && 'message' in obj;
}
