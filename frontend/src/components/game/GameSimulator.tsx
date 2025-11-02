/**
 * GameSimulator Component
 * 
 * Interface for simulating games between two teams.
 * Allows users to select teams and run the game simulation.
 */

import React, { useState } from 'react';
import type { Team, Game, CreateGameRequest } from '../../types';

interface GameSimulatorProps {
  teams: Team[];
  onSimulate: (request: CreateGameRequest) => Promise<Game>;
  onGameComplete?: (game: Game) => void;
  className?: string;
}

/**
 * GameSimulator component - Clean interface for game simulation
 */
export const GameSimulator: React.FC<GameSimulatorProps> = ({
  teams,
  onSimulate,
  onGameComplete,
  className = '',
}) => {
  const [team1Id, setTeam1Id] = useState<string>('');
  const [team2Id, setTeam2Id] = useState<string>('');
  const [seed, setSeed] = useState<string>('');
  const [isSimulating, setIsSimulating] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Filter teams that are ready to play (have 5 starters)
  const readyTeams = teams.filter(team => team.starter_ids.length === 5);

  // Get available opponent teams (exclude selected team1)
  const availableOpponents = readyTeams.filter(team => team.id !== team1Id);

  const handleTeam1Change = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const newTeam1Id = e.target.value;
    setTeam1Id(newTeam1Id);
    // Reset team2 if it's the same as new team1
    if (team2Id === newTeam1Id) {
      setTeam2Id('');
    }
    setError(null);
  };

  const handleTeam2Change = (e: React.ChangeEvent<HTMLSelectElement>) => {
    setTeam2Id(e.target.value);
    setError(null);
  };

  const handleSeedChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setSeed(e.target.value);
  };

  const handleSimulate = async () => {
    if (!team1Id || !team2Id) {
      setError('Please select both teams');
      return;
    }

    if (team1Id === team2Id) {
      setError('Teams must be different');
      return;
    }

    // Validate teams have starters
    const team1 = teams.find(t => t.id === team1Id);
    const team2 = teams.find(t => t.id === team2Id);

    if (!team1 || team1.starter_ids.length !== 5) {
      setError('Team 1 must have exactly 5 starters');
      return;
    }

    if (!team2 || team2.starter_ids.length !== 5) {
      setError('Team 2 must have exactly 5 starters');
      return;
    }

    setIsSimulating(true);
    setError(null);

    try {
      const request: CreateGameRequest = {
        team1_id: team1Id,
        team2_id: team2Id,
        seed: seed ? parseInt(seed, 10) : undefined,
      };

      const game = await onSimulate(request);
      
      if (onGameComplete) {
        onGameComplete(game);
      }

      // Reset form
      setTeam1Id('');
      setTeam2Id('');
      setSeed('');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to simulate game');
    } finally {
      setIsSimulating(false);
    }
  };

  const canSimulate = team1Id && team2Id && team1Id !== team2Id && !isSimulating;

  if (readyTeams.length < 2) {
    return (
      <div className={`bg-yellow-50 border border-yellow-200 rounded-lg p-6 ${className}`}>
        <div className="flex items-start gap-3">
          <div className="text-yellow-600 text-2xl">⚠️</div>
          <div>
            <h3 className="text-lg font-semibold text-yellow-800 mb-1">
              Not Enough Teams Ready
            </h3>
            <p className="text-sm text-yellow-700">
              You need at least 2 teams with 5 starters each to simulate a game.
            </p>
            <p className="text-sm text-yellow-700 mt-2">
              Ready teams: {readyTeams.length} / {teams.length}
            </p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className={`bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden ${className}`}>
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-600 to-purple-600 px-6 py-4">
        <h2 className="text-xl font-bold text-white">Game Simulator</h2>
        <p className="text-blue-100 text-sm mt-1">
          Select two teams to simulate a dodgeball match
        </p>
      </div>

      {/* Form */}
      <div className="p-6 space-y-4">
        {/* Error Display */}
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4">
            <div className="flex items-center gap-2">
              <span className="text-red-600">❌</span>
              <p className="text-sm text-red-700">{error}</p>
            </div>
          </div>
        )}

        {/* Team 1 Selection */}
        <div>
          <label htmlFor="team1" className="block text-sm font-medium text-gray-700 mb-2">
            Home Team
          </label>
          <select
            id="team1"
            value={team1Id}
            onChange={handleTeam1Change}
            disabled={isSimulating}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:bg-gray-100 disabled:cursor-not-allowed"
          >
            <option value="">Select home team...</option>
            {readyTeams.map(team => (
              <option key={team.id} value={team.id}>
                {team.name} ({team.wins}W-{team.losses}L)
              </option>
            ))}
          </select>
        </div>

        {/* Team 2 Selection */}
        <div>
          <label htmlFor="team2" className="block text-sm font-medium text-gray-700 mb-2">
            Away Team
          </label>
          <select
            id="team2"
            value={team2Id}
            onChange={handleTeam2Change}
            disabled={isSimulating || !team1Id}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:bg-gray-100 disabled:cursor-not-allowed"
          >
            <option value="">Select away team...</option>
            {availableOpponents.map(team => (
              <option key={team.id} value={team.id}>
                {team.name} ({team.wins}W-{team.losses}L)
              </option>
            ))}
          </select>
        </div>

        {/* Optional Seed Input */}
        <div>
          <label htmlFor="seed" className="block text-sm font-medium text-gray-700 mb-2">
            Random Seed <span className="text-gray-500 text-xs">(optional, for reproducible games)</span>
          </label>
          <input
            id="seed"
            type="number"
            value={seed}
            onChange={handleSeedChange}
            placeholder="Leave blank for random"
            disabled={isSimulating}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:bg-gray-100 disabled:cursor-not-allowed"
          />
          <p className="text-xs text-gray-500 mt-1">
            Use a seed number to get the same result when simulating with the same teams
          </p>
        </div>

        {/* Simulate Button */}
        <button
          onClick={handleSimulate}
          disabled={!canSimulate}
          className={`
            w-full px-6 py-3 rounded-lg font-semibold text-white transition-all duration-200
            ${canSimulate
              ? 'bg-gradient-to-r from-green-600 to-green-700 hover:from-green-700 hover:to-green-800 shadow-md hover:shadow-lg'
              : 'bg-gray-300 cursor-not-allowed'
            }
          `}
        >
          {isSimulating ? (
            <span className="flex items-center justify-center gap-2">
              <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
                <circle
                  className="opacity-25"
                  cx="12"
                  cy="12"
                  r="10"
                  stroke="currentColor"
                  strokeWidth="4"
                  fill="none"
                />
                <path
                  className="opacity-75"
                  fill="currentColor"
                  d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                />
              </svg>
              Simulating Game...
            </span>
          ) : (
            '🎯 Simulate Game'
          )}
        </button>

        {/* Info Box */}
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <div className="flex items-start gap-3">
            <div className="text-blue-600 text-xl">ℹ️</div>
            <div className="text-sm text-blue-700">
              <p className="font-medium mb-1">How it works:</p>
              <ul className="list-disc list-inside space-y-1 text-xs">
                <li>Each team starts with 5 players on the court</li>
                <li>Players take turns throwing dodgeballs</li>
                <li>Hits eliminate players, catches bring teammates back</li>
                <li>First team to eliminate all opponents wins</li>
                <li>Player skills (throwing, catching, dodging) determine outcomes</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default GameSimulator;
