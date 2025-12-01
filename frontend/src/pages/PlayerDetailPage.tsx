/**
 * PlayerDetailPage Component
 * 
 * Detailed view of a single player showing:
 * - Full player information
 * - All skills with visual bars
 * - Complete performance statistics
 * - Player progression (level, XP, skill points)
 * - Skill point allocation when available
 * - Game history
 * - Injury status
 */

import React, { useEffect, useState, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import type { Player, Team, PlayerSkills } from '../types';
import api from '../services/api';
import { Breadcrumbs } from '../components/common/Breadcrumbs';
import { ProgressionBadge } from '../components/player/ProgressionBadge';
import { SkillPointAllocator } from '../components/player/SkillPointAllocator';

/**
 * Format dollar value with comma separators
 */
const formatValue = (value: number): string => {
  return `$${value.toLocaleString()}`;
};

/**
 * Get skill color based on value
 */
const getSkillColor = (value: number): string => {
  if (value >= 8) return 'bg-green-500';
  if (value >= 6) return 'bg-blue-500';
  if (value >= 4) return 'bg-yellow-500';
  return 'bg-gray-400';
};

/**
 * PlayerDetailPage component
 */
export const PlayerDetailPage: React.FC = () => {
  const { leagueId, playerId } = useParams<{ leagueId: string; playerId: string }>();
  const navigate = useNavigate();
  const [player, setPlayer] = useState<Player | null>(null);
  const [team, setTeam] = useState<Team | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showSkillAllocator, setShowSkillAllocator] = useState(false);

  const fetchPlayerData = useCallback(async () => {
    if (!leagueId || !playerId) return;

    try {
      setLoading(true);
      setError(null);

      // Fetch all players to find the one we need
      const playersResponse = await api.league.getPlayers(leagueId);
      if (playersResponse.error) {
        throw new Error(playersResponse.error.message);
      }
      
      const playersData = playersResponse.data as Player[];
      const foundPlayer = playersData.find((p: Player) => p.id === playerId);

      if (!foundPlayer) {
        setError('Player not found');
        return;
      }

      setPlayer(foundPlayer);

      // If player is on a team, fetch team details
      if (foundPlayer.team_id) {
        try {
          const teamResponse = await api.team.getTeam(foundPlayer.team_id);
          if (teamResponse.error) {
            console.error('Error fetching team:', teamResponse.error);
          } else {
            setTeam(teamResponse.data as Team);
          }
        } catch (err) {
          console.error('Error fetching team:', err);
        }
      }
    } catch (err) {
      console.error('Error fetching player:', err);
      setError('Failed to load player data');
    } finally {
      setLoading(false);
    }
  }, [leagueId, playerId]);

  useEffect(() => {
    fetchPlayerData();
  }, [fetchPlayerData]);

  /**
   * Handle skill point allocation
   */
  const handleAllocateSkillPoints = async (allocations: Record<string, number>) => {
    if (!playerId) return;
    
    try {
      const response = await api.player.spendSkillPoints(playerId, allocations);
      if (response.error) {
        throw new Error(response.error.message);
      }
      
      // Refresh player data to get updated stats
      await fetchPlayerData();
      setShowSkillAllocator(false);
    } catch (err) {
      throw err; // Let the SkillPointAllocator handle the error display
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading player details...</p>
        </div>
      </div>
    );
  }

  if (error || !player) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-8">
        <div className="bg-red-50 border border-red-200 rounded-lg p-6 text-center">
          <p className="text-red-800 font-semibold mb-2">Error</p>
          <p className="text-red-600">{error || 'Player not found'}</p>
          <button
            onClick={() => navigate(`/leagues/${leagueId}/players`)}
            className="mt-4 px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700"
          >
            Back to Players
          </button>
        </div>
      </div>
    );
  }

  const { name, age, avatar, skills, value, injury, stats, team_id, is_starter } = player;

  const breadcrumbItems = [
    { label: 'League', path: `/leagues/${leagueId}` },
    { label: 'Players', path: `/leagues/${leagueId}/players` },
    { label: name },
  ];

  const allSkills = [
    { name: 'Throwing', key: 'throwing' as keyof PlayerSkills },
    { name: 'Catching', key: 'catching' as keyof PlayerSkills },
    { name: 'Dodging', key: 'dodging' as keyof PlayerSkills },
    { name: 'Speed', key: 'speed' as keyof PlayerSkills },
    { name: 'IQ', key: 'iq' as keyof PlayerSkills },
    { name: 'Luck', key: 'luck' as keyof PlayerSkills },
  ];

  const totalSkillPoints = Object.values(skills).reduce((sum, val) => sum + val, 0);
  const accuracyPercent = stats.throws_attempted > 0
    ? ((stats.successful_hits / stats.throws_attempted) * 100).toFixed(1)
    : '0.0';

  return (
    <div className="max-w-6xl mx-auto px-4 py-8">
      <Breadcrumbs items={breadcrumbItems} />

      {/* Player Header Card */}
      <div className="bg-white rounded-xl shadow-lg border border-gray-200 overflow-hidden mb-6">
        <div className="relative bg-gradient-to-br from-slate-100 via-blue-50 to-purple-50 p-8">
          {injury && (
            <div className="absolute top-4 right-4">
              <div className="bg-red-100 border-2 border-red-300 rounded-lg px-4 py-2">
                <div className="flex items-center gap-2">
                  <span className="text-2xl">🤕</span>
                  <div>
                    <p className="text-red-800 font-bold text-sm">INJURED</p>
                    <p className="text-red-600 text-xs">{injury.games_remaining} games remaining</p>
                  </div>
                </div>
              </div>
            </div>
          )}

          <div className="flex items-start gap-6">
            {/* Large Avatar */}
            <div className="relative">
              <div className="w-32 h-32 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center text-white font-bold text-4xl shadow-xl border-4 border-white">
                <img 
                  src={`/images/avatars/${avatar}.png`} 
                  alt={name} 
                  className="w-full h-full rounded-full object-cover" 
                />
              </div>
              {is_starter && (
                <div className="absolute -bottom-2 -right-2 w-10 h-10 bg-yellow-400 rounded-full border-4 border-white flex items-center justify-center shadow-lg">
                  <span className="text-xl">⭐</span>
                </div>
              )}
            </div>

            {/* Player Info */}
            <div className="flex-1">
              <div className="flex items-center gap-4 mb-2">
                <h1 className="text-4xl font-bold text-gray-900">{name}</h1>
                <ProgressionBadge 
                  player={player} 
                  mode="badge-only" 
                  onClick={stats.available_skill_points > 0 ? () => setShowSkillAllocator(true) : undefined}
                />
              </div>
              <div className="flex items-center gap-4 text-lg text-gray-600 mb-4">
                <span>Age {age}</span>
                <span>•</span>
                <span className="text-green-600 font-bold">{formatValue(value)}</span>
                {is_starter && (
                  <>
                    <span>•</span>
                    <span className="px-3 py-1 bg-yellow-100 text-yellow-800 rounded-full font-semibold text-sm">
                      Starter
                    </span>
                  </>
                )}
              </div>
              
              {team && (
                <div className="flex items-center gap-3 mb-4">
                  <img 
                    src={`/images/team_avatars/${team.logo}`}
                    alt={team.name}
                    className="w-10 h-10 rounded-full border-2 border-gray-300"
                  />
                  <div>
                    <p className="text-sm text-gray-500">Current Team</p>
                    <button
                      onClick={() => navigate(`/leagues/${leagueId}/teams/${team.id}`)}
                      className="text-blue-600 hover:text-blue-800 font-semibold hover:underline"
                    >
                      {team.name}
                    </button>
                  </div>
                </div>
              )}
              
              {!team_id && (
                <div className="inline-flex items-center gap-2 px-4 py-2 bg-blue-100 text-blue-800 rounded-lg">
                  <span className="text-xl">🆓</span>
                  <span className="font-semibold">Free Agent</span>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Skill Point Allocator Modal/Section */}
      {showSkillAllocator && stats.available_skill_points > 0 && (
        <div className="mb-6">
          <SkillPointAllocator
            player={player}
            availablePoints={stats.available_skill_points}
            onAllocate={handleAllocateSkillPoints}
            onCancel={() => setShowSkillAllocator(false)}
          />
        </div>
      )}

      {/* Progression Section */}
      <div className="bg-white rounded-xl shadow-lg border border-gray-200 p-6 mb-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-2xl font-bold text-gray-900">Player Progression</h2>
          {stats.available_skill_points > 0 && !showSkillAllocator && (
            <button
              onClick={() => setShowSkillAllocator(true)}
              className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors font-semibold flex items-center gap-2"
            >
              <span>✨</span>
              Allocate {stats.available_skill_points} Skill Point{stats.available_skill_points > 1 ? 's' : ''}
            </button>
          )}
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {/* Level Display */}
          <div className="bg-gradient-to-br from-purple-50 to-indigo-100 rounded-lg p-4 border border-purple-200">
            <div className="flex items-center gap-3">
              <ProgressionBadge player={player} mode="full" />
            </div>
          </div>
          
          {/* Games Played for XP context */}
          <div className="bg-gradient-to-br from-blue-50 to-blue-100 rounded-lg p-4 border border-blue-200">
            <p className="text-sm text-blue-600 font-medium mb-1">Games Played</p>
            <p className="text-3xl font-bold text-blue-900">{stats.games_played}</p>
            <p className="text-xs text-blue-600 mt-1">
              XP earned through gameplay
            </p>
          </div>
          
          {/* Skill Points Info */}
          <div className="bg-gradient-to-br from-amber-50 to-amber-100 rounded-lg p-4 border border-amber-200">
            <p className="text-sm text-amber-600 font-medium mb-1">Available Skill Points</p>
            <p className="text-3xl font-bold text-amber-900">{stats.available_skill_points}</p>
            <p className="text-xs text-amber-600 mt-1">
              {stats.available_skill_points > 0 ? 'Ready to allocate!' : 'Level up to earn more'}
            </p>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Skills Section */}
        <div className="bg-white rounded-xl shadow-lg border border-gray-200 p-6">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-2xl font-bold text-gray-900">Skills</h2>
            <div className="text-right">
              <p className="text-sm text-gray-500">Total Points</p>
              <p className="text-2xl font-bold text-blue-600">{totalSkillPoints}/60</p>
            </div>
          </div>

          <div className="space-y-4">
            {allSkills.map(({ name, key }) => {
              const skillValue = skills[key];
              const percentage = (skillValue / 10) * 100;

              return (
                <div key={key}>
                  <div className="flex justify-between items-center mb-2">
                    <span className="font-semibold text-gray-900">{name}</span>
                    <span className="text-lg font-bold text-gray-900">{skillValue}/10</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-3 overflow-hidden">
                    <div
                      className={`h-full ${getSkillColor(skillValue)} transition-all duration-500 rounded-full`}
                      style={{ width: `${percentage}%` }}
                    />
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Statistics Section */}
        <div className="bg-white rounded-xl shadow-lg border border-gray-200 p-6">
          <h2 className="text-2xl font-bold text-gray-900 mb-6">Career Statistics</h2>

          <div className="grid grid-cols-2 gap-4">
            {/* Games Played */}
            <div className="bg-gradient-to-br from-blue-50 to-blue-100 rounded-lg p-4 border border-blue-200">
              <p className="text-sm text-blue-600 font-medium mb-1">Games Played</p>
              <p className="text-3xl font-bold text-blue-900">{stats.games_played}</p>
            </div>

            {/* Eliminations */}
            <div className="bg-gradient-to-br from-red-50 to-red-100 rounded-lg p-4 border border-red-200">
              <p className="text-sm text-red-600 font-medium mb-1">Eliminations</p>
              <p className="text-3xl font-bold text-red-900">{stats.successful_hits}</p>
            </div>

            {/* Catches */}
            <div className="bg-gradient-to-br from-green-50 to-green-100 rounded-lg p-4 border border-green-200">
              <p className="text-sm text-green-600 font-medium mb-1">Catches Made</p>
              <p className="text-3xl font-bold text-green-900">{stats.catches_made}</p>
            </div>

            {/* Times Hit */}
            <div className="bg-gradient-to-br from-orange-50 to-orange-100 rounded-lg p-4 border border-orange-200">
              <p className="text-sm text-orange-600 font-medium mb-1">Times Hit</p>
              <p className="text-3xl font-bold text-orange-900">{stats.times_hit}</p>
            </div>

            {/* Throws Attempted */}
            <div className="bg-gradient-to-br from-purple-50 to-purple-100 rounded-lg p-4 border border-purple-200">
              <p className="text-sm text-purple-600 font-medium mb-1">Throws Attempted</p>
              <p className="text-3xl font-bold text-purple-900">{stats.throws_attempted}</p>
            </div>

            {/* Missed Throws */}
            <div className="bg-gradient-to-br from-yellow-50 to-yellow-100 rounded-lg p-4 border border-yellow-200">
              <p className="text-sm text-yellow-600 font-medium mb-1">Missed Throws</p>
              <p className="text-3xl font-bold text-yellow-900">{stats.missed_throws}</p>
            </div>
          </div>

          {/* Additional Stats */}
          <div className="mt-6 pt-6 border-t border-gray-200 space-y-3">
            <div className="flex justify-between items-center">
              <span className="text-gray-600">Hit Accuracy</span>
              <span className="font-bold text-gray-900">{accuracyPercent}%</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-gray-600">Avg Eliminations per Game</span>
              <span className="font-bold text-gray-900">
                {stats.games_played > 0 ? (stats.successful_hits / stats.games_played).toFixed(2) : '0.00'}
              </span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-gray-600">Avg Catches per Game</span>
              <span className="font-bold text-gray-900">
                {stats.games_played > 0 ? (stats.catches_made / stats.games_played).toFixed(2) : '0.00'}
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Back Button */}
      <div className="mt-6 flex justify-center">
        <button
          onClick={() => navigate(-1)}
          className="px-6 py-3 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors font-semibold"
        >
          ← Back
        </button>
      </div>
    </div>
  );
};

export default PlayerDetailPage;
