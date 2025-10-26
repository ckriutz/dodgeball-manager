/**
 * LeagueForm Component
 * 
 * Form for creating a new fantasy dodgeball league.
 * Features:
 * - League name input with validation
 * - Player count slider (50-100)
 * - Submit handler with loading state
 * - Error display
 * - Reset functionality
 * 
 * Used on the league creation page.
 */

import React, { useState, FormEvent } from 'react';
import type { CreateLeagueRequest } from '../../types';

interface LeagueFormProps {
  onSubmit: (data: CreateLeagueRequest) => Promise<void>;
  loading?: boolean;
  error?: string | null;
  className?: string;
}

/**
 * LeagueForm component
 */
export const LeagueForm: React.FC<LeagueFormProps> = ({
  onSubmit,
  loading = false,
  error = null,
  className = '',
}) => {
  // Form state
  const [name, setName] = useState('');
  const [playerCount, setPlayerCount] = useState(75);
  const [validationError, setValidationError] = useState<string | null>(null);

  // Min/max player counts
  const MIN_PLAYERS = 50;
  const MAX_PLAYERS = 100;

  /**
   * Validate form data
   */
  const validateForm = (): boolean => {
    // Validate name
    if (!name.trim()) {
      setValidationError('League name is required');
      return false;
    }

    if (name.trim().length < 3) {
      setValidationError('League name must be at least 3 characters');
      return false;
    }

    if (name.trim().length > 50) {
      setValidationError('League name must be less than 50 characters');
      return false;
    }

    // Validate player count
    if (playerCount < MIN_PLAYERS || playerCount > MAX_PLAYERS) {
      setValidationError(`Player count must be between ${MIN_PLAYERS} and ${MAX_PLAYERS}`);
      return false;
    }

    setValidationError(null);
    return true;
  };

  /**
   * Handle form submission
   */
  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();

    if (!validateForm()) {
      return;
    }

    const data: CreateLeagueRequest = {
      name: name.trim(),
      player_count: playerCount,
    };

    await onSubmit(data);
  };

  /**
   * Handle reset
   */
  const handleReset = () => {
    setName('');
    setPlayerCount(75);
    setValidationError(null);
  };

  /**
   * Handle name change
   */
  const handleNameChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setName(e.target.value);
    // Clear validation error when user starts typing
    if (validationError) {
      setValidationError(null);
    }
  };

  /**
   * Handle player count change
   */
  const handlePlayerCountChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setPlayerCount(parseInt(e.target.value, 10));
    // Clear validation error when user changes value
    if (validationError) {
      setValidationError(null);
    }
  };

  return (
    <form onSubmit={handleSubmit} className={`bg-white rounded-lg shadow-md border border-gray-200 ${className}`}>
      {/* Header */}
      <div className="px-6 py-4 border-b border-gray-200">
        <h2 className="text-2xl font-bold text-gray-900">Create New League</h2>
        <p className="text-sm text-gray-600 mt-1">
          Set up your fantasy dodgeball league with custom settings
        </p>
      </div>

      {/* Form Content */}
      <div className="px-6 py-6 space-y-6">
        {/* Error Display */}
        {(error || validationError) && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4">
            <div className="flex">
              <div className="flex-shrink-0">
                <svg
                  className="h-5 w-5 text-red-400"
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
              <div className="ml-3">
                <p className="text-sm text-red-800">
                  {validationError || error}
                </p>
              </div>
            </div>
          </div>
        )}

        {/* League Name Input */}
        <div>
          <label htmlFor="league-name" className="block text-sm font-medium text-gray-700 mb-2">
            League Name <span className="text-red-500">*</span>
          </label>
          <input
            type="text"
            id="league-name"
            value={name}
            onChange={handleNameChange}
            disabled={loading}
            placeholder="e.g., Summer 2024 Championship"
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:bg-gray-100 disabled:cursor-not-allowed"
            maxLength={50}
            required
          />
          <p className="text-xs text-gray-500 mt-1">
            {name.length}/50 characters
          </p>
        </div>

        {/* Player Count Slider */}
        <div>
          <label htmlFor="player-count" className="block text-sm font-medium text-gray-700 mb-2">
            Player Pool Size: <span className="font-bold text-blue-600">{playerCount}</span> players
          </label>
          <input
            type="range"
            id="player-count"
            min={MIN_PLAYERS}
            max={MAX_PLAYERS}
            step={5}
            value={playerCount}
            onChange={handlePlayerCountChange}
            disabled={loading}
            className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer disabled:cursor-not-allowed"
          />
          <div className="flex justify-between text-xs text-gray-500 mt-1">
            <span>{MIN_PLAYERS} min</span>
            <span>{MAX_PLAYERS} max</span>
          </div>
          <p className="text-xs text-gray-500 mt-2">
            More players provide greater variety for team drafting and trading
          </p>
        </div>

        {/* Info Box */}
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <div className="flex">
            <div className="flex-shrink-0">
              <svg
                className="h-5 w-5 text-blue-400"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                />
              </svg>
            </div>
            <div className="ml-3">
              <p className="text-sm text-blue-800">
                After creating your league, you'll be able to generate the player pool with randomized skills and values.
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Form Actions */}
      <div className="px-6 py-4 bg-gray-50 border-t border-gray-200 rounded-b-lg flex justify-end gap-3">
        <button
          type="button"
          onClick={handleReset}
          disabled={loading}
          className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          Reset
        </button>
        <button
          type="submit"
          disabled={loading || !name.trim()}
          className="px-6 py-2 text-sm font-medium text-white bg-blue-600 rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
        >
          {loading ? (
            <>
              <svg className="animate-spin h-4 w-4" fill="none" viewBox="0 0 24 24">
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
              <span>Creating...</span>
            </>
          ) : (
            <span>Create League</span>
          )}
        </button>
      </div>
    </form>
  );
};

export default LeagueForm;
