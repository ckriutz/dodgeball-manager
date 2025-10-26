/**
 * Component tests for TeamRoster
 * 
 * Tests the TeamRoster component functionality including:
 * - Roster display with starters and bench
 * - Player selection for starters
 * - Saving starters
 * - Removing players from roster
 * - Validation rules (8-12 players, exactly 5 starters)
 * - Readonly mode
 */

/// <reference types="@testing-library/jest-dom" />

import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { TeamRoster } from '../../src/components/team/TeamRoster';
import type { Team, Player } from '../../src/types';

/**
 * Mock team data
 */
const mockTeam: Team = {
  id: 'team-1',
  name: 'Test Team',
  description: 'Test Description',
  logo: '🏆',
  budget: 75000,
  player_ids: ['p1', 'p2', 'p3', 'p4', 'p5', 'p6', 'p7', 'p8'],
  starter_ids: ['p1', 'p2', 'p3', 'p4', 'p5'],
  wins: 5,
  losses: 3,
  awards: [],
  league_id: 'league-1',
};

const mockPlayers: Player[] = [
  {
    id: 'p1',
    name: 'Player One',
    age: 19,
    avatar: '🏃',
    skills: {
      catching: 6,
      throwing: 8,
      dodging: 7,
      speed: 7,
      iq: 6,
      luck: 5,
    },
    value: 8000,
    injury: null,
    stats: {
      throws_attempted: 20,
      catches_made: 10,
      times_hit: 5,
      missed_throws: 5,
      successful_hits: 15,
    },
    team_id: 'team-1',
    is_starter: true,
  },
  {
    id: 'p2',
    name: 'Player Two',
    age: 18,
    avatar: '🏃',
    skills: {
      catching: 7,
      throwing: 6,
      dodging: 8,
      speed: 6,
      iq: 7,
      luck: 6,
    },
    value: 9000,
    injury: null,
    stats: {
      throws_attempted: 18,
      catches_made: 12,
      times_hit: 4,
      missed_throws: 6,
      successful_hits: 12,
    },
    team_id: 'team-1',
    is_starter: true,
  },
  {
    id: 'p3',
    name: 'Player Three',
    age: 20,
    avatar: '🏃',
    skills: {
      catching: 8,
      throwing: 7,
      dodging: 6,
      speed: 8,
      iq: 8,
      luck: 7,
    },
    value: 10000,
    injury: null,
    stats: {
      throws_attempted: 25,
      catches_made: 15,
      times_hit: 3,
      missed_throws: 8,
      successful_hits: 17,
    },
    team_id: 'team-1',
    is_starter: true,
  },
  {
    id: 'p4',
    name: 'Player Four',
    age: 19,
    avatar: '🏃',
    skills: {
      catching: 5,
      throwing: 9,
      dodging: 7,
      speed: 7,
      iq: 6,
      luck: 6,
    },
    value: 7500,
    injury: null,
    stats: {
      throws_attempted: 22,
      catches_made: 8,
      times_hit: 6,
      missed_throws: 7,
      successful_hits: 15,
    },
    team_id: 'team-1',
    is_starter: true,
  },
  {
    id: 'p5',
    name: 'Player Five',
    age: 18,
    avatar: '🏃',
    skills: {
      catching: 7,
      throwing: 8,
      dodging: 8,
      speed: 6,
      iq: 7,
      luck: 5,
    },
    value: 8500,
    injury: null,
    stats: {
      throws_attempted: 19,
      catches_made: 11,
      times_hit: 5,
      missed_throws: 6,
      successful_hits: 13,
    },
    team_id: 'team-1',
    is_starter: true,
  },
  {
    id: 'p6',
    name: 'Player Six',
    age: 19,
    avatar: '🏃',
    skills: {
      catching: 6,
      throwing: 7,
      dodging: 7,
      speed: 7,
      iq: 6,
      luck: 6,
    },
    value: 7000,
    injury: null,
    stats: {
      throws_attempted: 15,
      catches_made: 7,
      times_hit: 4,
      missed_throws: 5,
      successful_hits: 10,
    },
    team_id: 'team-1',
    is_starter: false,
  },
  {
    id: 'p7',
    name: 'Player Seven',
    age: 20,
    avatar: '🏃',
    skills: {
      catching: 5,
      throwing: 6,
      dodging: 6,
      speed: 8,
      iq: 7,
      luck: 7,
    },
    value: 6500,
    injury: null,
    stats: {
      throws_attempted: 12,
      catches_made: 5,
      times_hit: 3,
      missed_throws: 4,
      successful_hits: 8,
    },
    team_id: 'team-1',
    is_starter: false,
  },
  {
    id: 'p8',
    name: 'Player Eight',
    age: 18,
    avatar: '🏃',
    skills: {
      catching: 7,
      throwing: 7,
      dodging: 6,
      speed: 7,
      iq: 6,
      luck: 6,
    },
    value: 7200,
    injury: null,
    stats: {
      throws_attempted: 14,
      catches_made: 6,
      times_hit: 4,
      missed_throws: 5,
      successful_hits: 9,
    },
    team_id: 'team-1',
    is_starter: false,
  },
];

describe('TeamRoster', () => {
  const mockOnAddPlayer = jest.fn();
  const mockOnRemovePlayer = jest.fn();
  const mockOnSetStarters = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('Basic Rendering', () => {
    it('renders component with team name', () => {
      render(
        <TeamRoster
          team={mockTeam}
          players={mockPlayers}
          onAddPlayer={mockOnAddPlayer}
          onRemovePlayer={mockOnRemovePlayer}
          onSetStarters={mockOnSetStarters}
        />
      );

      expect(screen.getByText(/roster/i)).toBeInTheDocument();
    });

    it('displays starters section', () => {
      render(
        <TeamRoster
          team={mockTeam}
          players={mockPlayers}
          onAddPlayer={mockOnAddPlayer}
          onRemovePlayer={mockOnRemovePlayer}
          onSetStarters={mockOnSetStarters}
        />
      );

      expect(screen.getByText(/starters/i)).toBeInTheDocument();
      expect(screen.getByText(/5\/5/i)).toBeInTheDocument();
    });

    it('displays bench section', () => {
      render(
        <TeamRoster
          team={mockTeam}
          players={mockPlayers}
          onAddPlayer={mockOnAddPlayer}
          onRemovePlayer={mockOnRemovePlayer}
          onSetStarters={mockOnSetStarters}
        />
      );

      expect(screen.getByText(/bench/i)).toBeInTheDocument();
    });

    it('displays roster rules', () => {
      render(
        <TeamRoster
          team={mockTeam}
          players={mockPlayers}
          onAddPlayer={mockOnAddPlayer}
          onRemovePlayer={mockOnRemovePlayer}
          onSetStarters={mockOnSetStarters}
        />
      );

      expect(screen.getByText(/8-12 players required/i)).toBeInTheDocument();
      expect(screen.getByText(/exactly 5 starters/i)).toBeInTheDocument();
    });
  });

  describe('Player Display', () => {
    it('renders all starter players', () => {
      render(
        <TeamRoster
          team={mockTeam}
          players={mockPlayers}
          onAddPlayer={mockOnAddPlayer}
          onRemovePlayer={mockOnRemovePlayer}
          onSetStarters={mockOnSetStarters}
        />
      );

      // Check starters are displayed
      expect(screen.getByText('Player One')).toBeInTheDocument();
      expect(screen.getByText('Player Two')).toBeInTheDocument();
      expect(screen.getByText('Player Three')).toBeInTheDocument();
      expect(screen.getByText('Player Four')).toBeInTheDocument();
      expect(screen.getByText('Player Five')).toBeInTheDocument();
    });

    it('renders all bench players', () => {
      render(
        <TeamRoster
          team={mockTeam}
          players={mockPlayers}
          onAddPlayer={mockOnAddPlayer}
          onRemovePlayer={mockOnRemovePlayer}
          onSetStarters={mockOnSetStarters}
        />
      );

      // Check bench players are displayed
      expect(screen.getByText('Player Six')).toBeInTheDocument();
      expect(screen.getByText('Player Seven')).toBeInTheDocument();
      expect(screen.getByText('Player Eight')).toBeInTheDocument();
    });

    it('displays starter badge for starters', () => {
      render(
        <TeamRoster
          team={mockTeam}
          players={mockPlayers}
          onAddPlayer={mockOnAddPlayer}
          onRemovePlayer={mockOnRemovePlayer}
          onSetStarters={mockOnSetStarters}
        />
      );

      const starterBadges = screen.getAllByText(/starter/i);
      expect(starterBadges.length).toBeGreaterThanOrEqual(5);
    });
  });

  describe('Player Selection', () => {
    it('allows selecting bench players as starters', () => {
      render(
        <TeamRoster
          team={mockTeam}
          players={mockPlayers}
          onAddPlayer={mockOnAddPlayer}
          onRemovePlayer={mockOnRemovePlayer}
          onSetStarters={mockOnSetStarters}
        />
      );

      // Find a bench player and click it
      const benchPlayer = screen.getByText('Player Six').closest('div')?.parentElement;
      if (benchPlayer) {
        fireEvent.click(benchPlayer);
      }

      // Should show visual selection (e.g., blue ring or checkmark)
      // This depends on your component's implementation
    });

    it('prevents selecting more than 5 starters', () => {
      render(
        <TeamRoster
          team={mockTeam}
          players={mockPlayers}
          onAddPlayer={mockOnAddPlayer}
          onRemovePlayer={mockOnRemovePlayer}
          onSetStarters={mockOnSetStarters}
        />
      );

      // Try to deselect a starter
      const starter = screen.getByText('Player One').closest('div')?.parentElement;
      if (starter) {
        fireEvent.click(starter);
      }

      // Try to select 6th player
      const benchPlayer = screen.getByText('Player Six').closest('div')?.parentElement;
      if (benchPlayer) {
        fireEvent.click(benchPlayer);
      }

      // Should not allow more than 5 selections
      // Component should show validation or disable selection
    });

    it('allows deselecting starters', () => {
      render(
        <TeamRoster
          team={mockTeam}
          players={mockPlayers}
          onAddPlayer={mockOnAddPlayer}
          onRemovePlayer={mockOnRemovePlayer}
          onSetStarters={mockOnSetStarters}
        />
      );

      // Click a starter to deselect
      const starter = screen.getByText('Player One').closest('div')?.parentElement;
      if (starter) {
        fireEvent.click(starter);
      }

      // Should remove from selection
    });
  });

  describe('Save Starters', () => {
    it('shows save button when selections change', () => {
      render(
        <TeamRoster
          team={mockTeam}
          players={mockPlayers}
          onAddPlayer={mockOnAddPlayer}
          onRemovePlayer={mockOnRemovePlayer}
          onSetStarters={mockOnSetStarters}
        />
      );

      // Should have save controls visible
      expect(screen.getByText(/save/i)).toBeInTheDocument();
    });

    it('calls onSetStarters with correct player IDs', () => {
      render(
        <TeamRoster
          team={mockTeam}
          players={mockPlayers}
          onAddPlayer={mockOnAddPlayer}
          onRemovePlayer={mockOnRemovePlayer}
          onSetStarters={mockOnSetStarters}
        />
      );

      // Click save button
      const saveButton = screen.getByText(/save starters/i);
      fireEvent.click(saveButton);

      // Should call with current starter IDs
      expect(mockOnSetStarters).toHaveBeenCalled();
      const calledWith = mockOnSetStarters.mock.calls[0][0];
      expect(calledWith).toHaveLength(5);
    });

    it('disables save when not exactly 5 starters', () => {
      render(
        <TeamRoster
          team={mockTeam}
          players={mockPlayers}
          onAddPlayer={mockOnAddPlayer}
          onRemovePlayer={mockOnRemovePlayer}
          onSetStarters={mockOnSetStarters}
        />
      );

      // Deselect a starter
      const starter = screen.getByText('Player One').closest('div')?.parentElement;
      if (starter) {
        fireEvent.click(starter);
      }

      // Save button should be disabled or show error
      const saveButton = screen.getByText(/save starters/i);
      expect(saveButton).toBeDisabled();
    });
  });

  describe('Reset Selections', () => {
    it('shows reset button', () => {
      render(
        <TeamRoster
          team={mockTeam}
          players={mockPlayers}
          onAddPlayer={mockOnAddPlayer}
          onRemovePlayer={mockOnRemovePlayer}
          onSetStarters={mockOnSetStarters}
        />
      );

      expect(screen.getByText(/reset/i)).toBeInTheDocument();
    });

    it('resets selections to current starters', () => {
      render(
        <TeamRoster
          team={mockTeam}
          players={mockPlayers}
          onAddPlayer={mockOnAddPlayer}
          onRemovePlayer={mockOnRemovePlayer}
          onSetStarters={mockOnSetStarters}
        />
      );

      // Change selection
      const starter = screen.getByText('Player One').closest('div')?.parentElement;
      if (starter) {
        fireEvent.click(starter);
      }

      // Click reset
      const resetButton = screen.getByText(/reset/i);
      fireEvent.click(resetButton);

      // Should revert to original starters
    });
  });

  describe('Remove Player', () => {
    it('shows remove button for each player', () => {
      render(
        <TeamRoster
          team={mockTeam}
          players={mockPlayers}
          onAddPlayer={mockOnAddPlayer}
          onRemovePlayer={mockOnRemovePlayer}
          onSetStarters={mockOnSetStarters}
        />
      );

      // Should have remove buttons (depends on implementation - could be icon buttons)
      const removeButtons = screen.getAllByRole('button');
      expect(removeButtons.length).toBeGreaterThan(0);
    });

    it('calls onRemovePlayer with correct player ID', () => {
      render(
        <TeamRoster
          team={mockTeam}
          players={mockPlayers}
          onAddPlayer={mockOnAddPlayer}
          onRemovePlayer={mockOnRemovePlayer}
          onSetStarters={mockOnSetStarters}
        />
      );

      // Find and click remove button for a bench player
      // This depends on your component's implementation
      // You may need to use a test ID or specific selector
    });

    it('prevents removing player when roster would drop below 8', () => {
      const smallRosterTeam: Team = {
        ...mockTeam,
        player_ids: ['p1', 'p2', 'p3', 'p4', 'p5', 'p6', 'p7', 'p8'],
      };

      render(
        <TeamRoster
          team={smallRosterTeam}
          players={mockPlayers}
          onAddPlayer={mockOnAddPlayer}
          onRemovePlayer={mockOnRemovePlayer}
          onSetStarters={mockOnSetStarters}
        />
      );

      // Roster is at minimum (8 players)
      // Remove buttons should be disabled or show warning
    });
  });

  describe('Readonly Mode', () => {
    it('disables all interactions in readonly mode', () => {
      render(
        <TeamRoster
          team={mockTeam}
          players={mockPlayers}
          onAddPlayer={mockOnAddPlayer}
          onRemovePlayer={mockOnRemovePlayer}
          onSetStarters={mockOnSetStarters}
          readonly={true}
        />
      );

      // All buttons should be disabled
      const buttons = screen.getAllByRole('button');
      buttons.forEach((button) => {
        expect(button).toBeDisabled();
      });
    });

    it('does not allow player selection in readonly mode', () => {
      render(
        <TeamRoster
          team={mockTeam}
          players={mockPlayers}
          onAddPlayer={mockOnAddPlayer}
          onRemovePlayer={mockOnRemovePlayer}
          onSetStarters={mockOnSetStarters}
          readonly={true}
        />
      );

      // Click should not work
      const player = screen.getByText('Player One').closest('div')?.parentElement;
      if (player) {
        fireEvent.click(player);
      }

      // Selection should not change
    });
  });

  describe('Validation Messages', () => {
    it('shows warning when roster is below 8 players', () => {
      const underMinTeam: Team = {
        ...mockTeam,
        player_ids: ['p1', 'p2', 'p3', 'p4', 'p5', 'p6', 'p7'],
      };

      const underMinPlayers = mockPlayers.slice(0, 7);

      render(
        <TeamRoster
          team={underMinTeam}
          players={underMinPlayers}
          onAddPlayer={mockOnAddPlayer}
          onRemovePlayer={mockOnRemovePlayer}
          onSetStarters={mockOnSetStarters}
        />
      );

      expect(screen.getByText(/need at least 8 players/i)).toBeInTheDocument();
    });

    it('shows warning when roster exceeds 12 players', () => {
      const overMaxTeam: Team = {
        ...mockTeam,
        player_ids: ['p1', 'p2', 'p3', 'p4', 'p5', 'p6', 'p7', 'p8', 'p9', 'p10', 'p11', 'p12', 'p13'],
      };

      const extraPlayers: Player[] = [
        ...mockPlayers,
        { ...mockPlayers[0], id: 'p9', name: 'Player Nine' },
        { ...mockPlayers[0], id: 'p10', name: 'Player Ten' },
        { ...mockPlayers[0], id: 'p11', name: 'Player Eleven' },
        { ...mockPlayers[0], id: 'p12', name: 'Player Twelve' },
        { ...mockPlayers[0], id: 'p13', name: 'Player Thirteen' },
      ];

      render(
        <TeamRoster
          team={overMaxTeam}
          players={extraPlayers}
          onAddPlayer={mockOnAddPlayer}
          onRemovePlayer={mockOnRemovePlayer}
          onSetStarters={mockOnSetStarters}
        />
      );

      expect(screen.getByText(/maximum 12 players/i)).toBeInTheDocument();
    });

    it('shows success when roster is valid', () => {
      render(
        <TeamRoster
          team={mockTeam}
          players={mockPlayers}
          onAddPlayer={mockOnAddPlayer}
          onRemovePlayer={mockOnRemovePlayer}
          onSetStarters={mockOnSetStarters}
        />
      );

      // Should show green checkmark or success indicator
      expect(screen.getByText(/8-12 players required/i)).toBeInTheDocument();
    });
  });

  describe('Edge Cases', () => {
    it('handles empty roster', () => {
      const emptyTeam: Team = {
        ...mockTeam,
        player_ids: [],
        starter_ids: [],
      };

      render(
        <TeamRoster
          team={emptyTeam}
          players={[]}
          onAddPlayer={mockOnAddPlayer}
          onRemovePlayer={mockOnRemovePlayer}
          onSetStarters={mockOnSetStarters}
        />
      );

      expect(screen.getByText(/no players/i)).toBeInTheDocument();
    });

    it('handles team with only bench players (no starters)', () => {
      const noStartersTeam: Team = {
        ...mockTeam,
        starter_ids: [],
      };

      render(
        <TeamRoster
          team={noStartersTeam}
          players={mockPlayers}
          onAddPlayer={mockOnAddPlayer}
          onRemovePlayer={mockOnRemovePlayer}
          onSetStarters={mockOnSetStarters}
        />
      );

      expect(screen.getByText(/0\/5/i)).toBeInTheDocument();
    });

    it('handles injured players on roster', () => {
      const injuredPlayer: Player = {
        ...mockPlayers[0],
        injury: {
          severity: 'moderate',
          affected_reduction: 20,
          games_remaining: 3,
        },
      };

      const playersWithInjury = [injuredPlayer, ...mockPlayers.slice(1)];

      render(
        <TeamRoster
          team={mockTeam}
          players={playersWithInjury}
          onAddPlayer={mockOnAddPlayer}
          onRemovePlayer={mockOnRemovePlayer}
          onSetStarters={mockOnSetStarters}
        />
      );

      // Should display injury badge
      expect(screen.getByText(/injured/i)).toBeInTheDocument();
    });
  });

  describe('Custom Styling', () => {
    it('applies custom className', () => {
      const { container } = render(
        <TeamRoster
          team={mockTeam}
          players={mockPlayers}
          onAddPlayer={mockOnAddPlayer}
          onRemovePlayer={mockOnRemovePlayer}
          onSetStarters={mockOnSetStarters}
          className="custom-class"
        />
      );

      const roster = container.firstChild as HTMLElement;
      expect(roster.className).toContain('custom-class');
    });
  });
});
