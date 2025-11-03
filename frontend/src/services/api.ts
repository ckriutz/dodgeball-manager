/**
 * API client service for communicating with the Dodgeball Fantasy League backend.
 * 
 * This module provides a centralized service for making HTTP requests to the FastAPI backend.
 * All API calls should go through this service to ensure consistent error handling,
 * request formatting, and response parsing.
 */

// Type definitions for API requests and responses
// These will be replaced with proper TypeScript types from frontend/src/types/index.ts

interface ApiError {
  message: string;
  detail?: string;
}

interface ApiResponse<T> {
  data?: T;
  error?: ApiError;
}

/**
 * API client configuration
 */
const getApiBaseUrl = (): string => {
  // Check if we're in a browser environment with Vite
  if (typeof window !== 'undefined' && import.meta.env) {
    return import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api';
  }
  // Fallback for Node.js/test environments
  return process.env.VITE_API_BASE_URL || 'http://localhost:8000/api';
};

const API_BASE_URL = getApiBaseUrl();

/**
 * API client class for making HTTP requests to the backend
 */
class ApiClient {
  private baseUrl: string;

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl;
  }

  /**
   * Make a GET request to the API
   */
  async get<T>(endpoint: string): Promise<ApiResponse<T>> {
    try {
      const response = await fetch(`${this.baseUrl}${endpoint}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      return await this.handleResponse<T>(response);
    } catch (error) {
      return this.handleError(error);
    }
  }

  /**
   * Make a POST request to the API
   */
  async post<T>(endpoint: string, data?: unknown): Promise<ApiResponse<T>> {
    try {
      const response = await fetch(`${this.baseUrl}${endpoint}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: data ? JSON.stringify(data) : undefined,
      });

      return await this.handleResponse<T>(response);
    } catch (error) {
      return this.handleError(error);
    }
  }

  /**
   * Make a PATCH request to the API
   */
  async patch<T>(endpoint: string, data?: unknown): Promise<ApiResponse<T>> {
    try {
      const response = await fetch(`${this.baseUrl}${endpoint}`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
        },
        body: data ? JSON.stringify(data) : undefined,
      });

      return await this.handleResponse<T>(response);
    } catch (error) {
      return this.handleError(error);
    }
  }

  /**
   * Make a DELETE request to the API
   */
  async delete<T>(endpoint: string): Promise<ApiResponse<T>> {
    try {
      const response = await fetch(`${this.baseUrl}${endpoint}`, {
        method: 'DELETE',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      return await this.handleResponse<T>(response);
    } catch (error) {
      return this.handleError(error);
    }
  }

  /**
   * Handle API response
   */
  private async handleResponse<T>(response: Response): Promise<ApiResponse<T>> {
    if (response.ok) {
      const data = await response.json();
      return { data };
    }

    // Handle error responses
    const errorData = await response.json().catch(() => ({
      message: 'An unexpected error occurred',
      detail: `HTTP ${response.status}: ${response.statusText}`,
    }));

    return {
      error: {
        message: errorData.message || 'Request failed',
        detail: errorData.detail,
      },
    };
  }

  /**
   * Handle network or other errors
   */
  private handleError(error: unknown): ApiResponse<never> {
    console.error('API request failed:', error);
    return {
      error: {
        message: 'Network error',
        detail: error instanceof Error ? error.message : 'An unexpected error occurred',
      },
    };
  }
}

// Create singleton instance
const apiClient = new ApiClient();

/**
 * API service methods
 * These will be expanded as we implement each user story
 */

// League API methods
export const leagueApi = {
  /**
   * Get all leagues
   */
  getLeagues: async () => {
    return apiClient.get('/leagues');
  },

  /**
   * Create a new league
   */
  createLeague: async (data: { name: string; player_count?: number }) => {
    return apiClient.post('/leagues', data);
  },

  /**
   * Get league by ID
   */
  getLeague: async (leagueId: string) => {
    return apiClient.get(`/leagues/${leagueId}`);
  },

  /**
   * Generate players for a league
   */
  generatePlayers: async (leagueId: string, count?: number) => {
    const params = count ? `?count=${count}` : '';
    return apiClient.post(`/leagues/${leagueId}/players${params}`);
  },

  /**
   * Get all players in a league
   */
  getPlayers: async (leagueId: string, freeAgentsOnly?: boolean) => {
    const params = freeAgentsOnly ? '?free_agents_only=true' : '';
    return apiClient.get(`/leagues/${leagueId}/players${params}`);
  },

  /**
   * Get league standings
   */
  getStandings: async (leagueId: string) => {
    return apiClient.get(`/leagues/${leagueId}/standings`);
  },

  /**
   * Create league schedule
   */
  createSchedule: async (leagueId: string) => {
    return apiClient.post(`/leagues/${leagueId}/schedule`);
  },

  /**
   * Get league awards
   */
  getAwards: async (leagueId: string) => {
    return apiClient.get(`/leagues/${leagueId}/awards`);
  },

  /**
   * Get teams in a league
   */
  getTeams: async (leagueId: string) => {
    return apiClient.get(`/leagues/${leagueId}/teams`);
  },
};

// Player API methods
export const playerApi = {
  /**
   * Get player by ID
   */
  getPlayer: async (playerId: string) => {
    return apiClient.get(`/players/${playerId}`);
  },
};

// Team API methods
export const teamApi = {
  /**
   * Create a new team
   */
  createTeam: async (data: { name: string; description?: string; logo?: string; league_id: string }) => {
    return apiClient.post('/teams', data);
  },

  /**
   * Get team by ID
   */
  getTeam: async (teamId: string) => {
    return apiClient.get(`/teams/${teamId}`);
  },

  /**
   * Add player to team roster
   */
  addPlayerToTeam: async (teamId: string, playerId: string) => {
    return apiClient.post(`/teams/${teamId}/players`, { player_id: playerId });
  },

  /**
   * Remove player from team roster
   */
  removePlayerFromTeam: async (teamId: string, playerId: string) => {
    return apiClient.delete(`/teams/${teamId}/players/${playerId}`);
  },

  /**
   * Update team starters
   */
  updateStarters: async (teamId: string, starterIds: string[]) => {
    return apiClient.patch(`/teams/${teamId}/starters`, { starter_ids: starterIds });
  },
};

// Game API methods
export const gameApi = {
  /**
   * Create and simulate a game
   */
  createGame: async (data: { team1_id: string; team2_id: string; seed?: number }) => {
    return apiClient.post('/games', data);
  },

  /**
   * Get game by ID
   */
  getGame: async (gameId: string) => {
    return apiClient.get(`/games/${gameId}`);
  },

  /**
   * Get all games (optionally filtered by league)
   */
  getGames: async (leagueId?: string) => {
    const params = leagueId ? `?league_id=${leagueId}` : '';
    return apiClient.get(`/games${params}`);
  },
};

// Health check
export const healthApi = {
  /**
   * Check API health
   */
  checkHealth: async () => {
    return apiClient.get('/health');
  },
};

// Export the API client for custom requests if needed
export { apiClient };

// Default export with all API methods
export default {
  league: leagueApi,
  player: playerApi,
  team: teamApi,
  game: gameApi,
  health: healthApi,
};
