/**
 * Component tests for GameSimulator
 * 
 * Tests the GameSimulator component functionality including:
 * - Team selection
 * - Validation rules
 * - Simulation trigger
 * - Error handling
 * - Ready teams filtering
 * - Seed input
 */

/// <reference types="@testing-library/jest-dom" />

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { GameSimulator } from '../../src/components/game/GameSimulator';
import type { Team, Game, CreateGameRequest } from '../../src/types';

/**
 * Mock team data
 */
const mockTeamReady1: Team = {
  id: 'team-1',
  name: 'Red Dragons',
  description: 'A fierce team',
  logo: 'logo-1',
  budget: 25000,
  player_ids: ['p1', 'p2', 'p3', 'p4', 'p5', 'p6', 'p7', 'p8'],
  starter_ids: ['p1', 'p2', 'p3', 'p4', 'p5'],
  wins: 3,
  losses: 1,
  awards: [],
  league_id: 'league-1',
};

const mockTeamReady2: Team = {
  id: 'team-2',
  name: 'Blue Sharks',
  description: 'Fast and agile',
  logo: 'logo-2',
  budget: 30000,
  player_ids: ['p9', 'p10', 'p11', 'p12', 'p13', 'p14', 'p15', 'p16'],
  starter_ids: ['p9', 'p10', 'p11', 'p12', 'p13'],
  wins: 2,
  losses: 2,
  awards: [],
  league_id: 'league-1',
};

const mockTeamReady3: Team = {
  id: 'team-3',
  name: 'Green Turtles',
  description: 'Steady and strong',
  logo: 'logo-3',
  budget: 20000,
  player_ids: ['p17', 'p18', 'p19', 'p20', 'p21', 'p22', 'p23', 'p24'],
  starter_ids: ['p17', 'p18', 'p19', 'p20', 'p21'],
  wins: 1,
  losses: 3,
  awards: [],
  league_id: 'league-1',
};

const mockTeamNotReady: Team = {
  id: 'team-4',
  name: 'Yellow Eagles',
  description: 'Building team',
  logo: 'logo-4',
  budget: 50000,
  player_ids: ['p25', 'p26', 'p27'],
  starter_ids: ['p25', 'p26'], // Only 2 starters - not ready!
  wins: 0,
  losses: 0,
  awards: [],
  league_id: 'league-1',
};

const mockGame: Game = {
  id: 'game-1',
  league_id: 'league-1',
  team1_id: 'team-1',
  team2_id: 'team-2',
  team1_starters: ['p1', 'p2', 'p3', 'p4', 'p5'],
  team2_starters: ['p9', 'p10', 'p11', 'p12', 'p13'],
  events: [],
  winner_id: 'team-1',
  completed_at: '2025-10-25T14:30:00Z',
  seed: 42,
};

describe('GameSimulator', () => {
  const mockOnSimulate = vi.fn();
  const mockOnGameComplete = vi.fn();

  beforeEach(() => {
    mockOnSimulate.mockClear();
    mockOnGameComplete.mockClear();
  });

  describe('Initial Render', () => {
    it('renders the component title', () => {
      render(
        <GameSimulator
          teams={[mockTeamReady1, mockTeamReady2]}
          onSimulate={mockOnSimulate}
        />
      );

      expect(screen.getByText('Game Simulator')).toBeInTheDocument();
    });

    it('displays description text', () => {
      render(
        <GameSimulator
          teams={[mockTeamReady1, mockTeamReady2]}
          onSimulate={mockOnSimulate}
        />
      );

      expect(screen.getByText(/Select two teams to simulate a dodgeball match/i)).toBeInTheDocument();
    });

    it('shows team selection dropdowns', () => {
      render(
        <GameSimulator
          teams={[mockTeamReady1, mockTeamReady2]}
          onSimulate={mockOnSimulate}
        />
      );

      expect(screen.getByLabelText(/Home Team/i)).toBeInTheDocument();
      expect(screen.getByLabelText(/Away Team/i)).toBeInTheDocument();
    });

    it('shows seed input field', () => {
      render(
        <GameSimulator
          teams={[mockTeamReady1, mockTeamReady2]}
          onSimulate={mockOnSimulate}
        />
      );

      expect(screen.getByLabelText(/Random Seed/i)).toBeInTheDocument();
    });

    it('shows simulate button', () => {
      render(
        <GameSimulator
          teams={[mockTeamReady1, mockTeamReady2]}
          onSimulate={mockOnSimulate}
        />
      );

      expect(screen.getByText(/Simulate Game/i)).toBeInTheDocument();
    });

    it('displays how it works info box', () => {
      render(
        <GameSimulator
          teams={[mockTeamReady1, mockTeamReady2]}
          onSimulate={mockOnSimulate}
        />
      );

      expect(screen.getByText(/How it works:/i)).toBeInTheDocument();
    });
  });

  describe('Ready Teams Filtering', () => {
    it('only shows teams with 5 starters in dropdowns', () => {
      render(
        <GameSimulator
          teams={[mockTeamReady1, mockTeamReady2, mockTeamNotReady]}
          onSimulate={mockOnSimulate}
        />
      );

      const team1Select = screen.getByLabelText(/Home Team/i);
      fireEvent.click(team1Select);

      // Should show ready teams
      expect(screen.getByText(/Red Dragons/)).toBeInTheDocument();
      expect(screen.getByText(/Blue Sharks/)).toBeInTheDocument();
      
      // Should not show team without 5 starters
      expect(screen.queryByText(/Yellow Eagles/)).not.toBeInTheDocument();
    });

    it('displays warning when less than 2 teams are ready', () => {
      render(
        <GameSimulator
          teams={[mockTeamReady1, mockTeamNotReady]}
          onSimulate={mockOnSimulate}
        />
      );

      expect(screen.getByText(/Not Enough Teams Ready/i)).toBeInTheDocument();
      expect(screen.getByText(/You need at least 2 teams with 5 starters/i)).toBeInTheDocument();
    });

    it('shows ready team count in warning message', () => {
      render(
        <GameSimulator
          teams={[mockTeamReady1, mockTeamNotReady]}
          onSimulate={mockOnSimulate}
        />
      );

      expect(screen.getByText(/Ready teams: 1 \/ 2/i)).toBeInTheDocument();
    });

    it('does not show simulator when insufficient teams', () => {
      render(
        <GameSimulator
          teams={[mockTeamReady1]}
          onSimulate={mockOnSimulate}
        />
      );

      expect(screen.queryByLabelText(/Home Team/i)).not.toBeInTheDocument();
      expect(screen.queryByText(/Simulate Game/i)).not.toBeInTheDocument();
    });
  });

  describe('Team Selection', () => {
    it('allows selecting team 1', () => {
      render(
        <GameSimulator
          teams={[mockTeamReady1, mockTeamReady2]}
          onSimulate={mockOnSimulate}
        />
      );

      const team1Select = screen.getByLabelText(/Home Team/i) as HTMLSelectElement;
      fireEvent.change(team1Select, { target: { value: 'team-1' } });

      expect(team1Select.value).toBe('team-1');
    });

    it('allows selecting team 2', () => {
      render(
        <GameSimulator
          teams={[mockTeamReady1, mockTeamReady2]}
          onSimulate={mockOnSimulate}
        />
      );

      const team2Select = screen.getByLabelText(/Away Team/i) as HTMLSelectElement;
      fireEvent.change(team2Select, { target: { value: 'team-2' } });

      expect(team2Select.value).toBe('team-2');
    });

    it('displays team records in dropdown', () => {
      render(
        <GameSimulator
          teams={[mockTeamReady1, mockTeamReady2]}
          onSimulate={mockOnSimulate}
        />
      );

      expect(screen.getByText(/Red Dragons \(3W-1L\)/i)).toBeInTheDocument();
      expect(screen.getByText(/Blue Sharks \(2W-2L\)/i)).toBeInTheDocument();
    });

    it('excludes selected team1 from team2 dropdown', () => {
      render(
        <GameSimulator
          teams={[mockTeamReady1, mockTeamReady2, mockTeamReady3]}
          onSimulate={mockOnSimulate}
        />
      );

      // Select team 1
      const team1Select = screen.getByLabelText(/Home Team/i);
      fireEvent.change(team1Select, { target: { value: 'team-1' } });

      // Team 2 dropdown should not include team 1
      const team2Select = screen.getByLabelText(/Away Team/i);
      fireEvent.click(team2Select);

      const team2Options = team2Select.querySelectorAll('option');
      const team2Values = Array.from(team2Options).map(opt => opt.getAttribute('value'));
      
      expect(team2Values).not.toContain('team-1');
      expect(team2Values).toContain('team-2');
      expect(team2Values).toContain('team-3');
    });

    it('resets team2 when team1 is changed to match team2', () => {
      render(
        <GameSimulator
          teams={[mockTeamReady1, mockTeamReady2, mockTeamReady3]}
          onSimulate={mockOnSimulate}
        />
      );

      // Select team2 first
      const team2Select = screen.getByLabelText(/Away Team/i) as HTMLSelectElement;
      fireEvent.change(team2Select, { target: { value: 'team-2' } });
      expect(team2Select.value).toBe('team-2');

      // Now select same team for team1
      const team1Select = screen.getByLabelText(/Home Team/i);
      fireEvent.change(team1Select, { target: { value: 'team-2' } });

      // Team2 should be reset
      expect(team2Select.value).toBe('');
    });

    it('disables team2 dropdown when team1 not selected', () => {
      render(
        <GameSimulator
          teams={[mockTeamReady1, mockTeamReady2]}
          onSimulate={mockOnSimulate}
        />
      );

      const team2Select = screen.getByLabelText(/Away Team/i);
      expect(team2Select).toBeDisabled();
    });

    it('enables team2 dropdown when team1 is selected', () => {
      render(
        <GameSimulator
          teams={[mockTeamReady1, mockTeamReady2]}
          onSimulate={mockOnSimulate}
        />
      );

      const team1Select = screen.getByLabelText(/Home Team/i);
      fireEvent.change(team1Select, { target: { value: 'team-1' } });

      const team2Select = screen.getByLabelText(/Away Team/i);
      expect(team2Select).not.toBeDisabled();
    });
  });

  describe('Seed Input', () => {
    it('allows entering a seed number', () => {
      render(
        <GameSimulator
          teams={[mockTeamReady1, mockTeamReady2]}
          onSimulate={mockOnSimulate}
        />
      );

      const seedInput = screen.getByLabelText(/Random Seed/i) as HTMLInputElement;
      fireEvent.change(seedInput, { target: { value: '42' } });

      expect(seedInput.value).toBe('42');
    });

    it('shows seed placeholder text', () => {
      render(
        <GameSimulator
          teams={[mockTeamReady1, mockTeamReady2]}
          onSimulate={mockOnSimulate}
        />
      );

      const seedInput = screen.getByLabelText(/Random Seed/i);
      expect(seedInput).toHaveAttribute('placeholder', 'Leave blank for random');
    });

    it('displays seed help text', () => {
      render(
        <GameSimulator
          teams={[mockTeamReady1, mockTeamReady2]}
          onSimulate={mockOnSimulate}
        />
      );

      expect(screen.getByText(/Use a seed number to get the same result/i)).toBeInTheDocument();
    });
  });

  describe('Simulate Button State', () => {
    it('is disabled when no teams selected', () => {
      render(
        <GameSimulator
          teams={[mockTeamReady1, mockTeamReady2]}
          onSimulate={mockOnSimulate}
        />
      );

      const simulateButton = screen.getByText(/Simulate Game/i);
      expect(simulateButton).toBeDisabled();
    });

    it('is disabled when only team1 selected', () => {
      render(
        <GameSimulator
          teams={[mockTeamReady1, mockTeamReady2]}
          onSimulate={mockOnSimulate}
        />
      );

      const team1Select = screen.getByLabelText(/Home Team/i);
      fireEvent.change(team1Select, { target: { value: 'team-1' } });

      const simulateButton = screen.getByText(/Simulate Game/i);
      expect(simulateButton).toBeDisabled();
    });

    it('is enabled when both teams selected', () => {
      render(
        <GameSimulator
          teams={[mockTeamReady1, mockTeamReady2]}
          onSimulate={mockOnSimulate}
        />
      );

      const team1Select = screen.getByLabelText(/Home Team/i);
      const team2Select = screen.getByLabelText(/Away Team/i);

      fireEvent.change(team1Select, { target: { value: 'team-1' } });
      fireEvent.change(team2Select, { target: { value: 'team-2' } });

      const simulateButton = screen.getByText(/Simulate Game/i);
      expect(simulateButton).not.toBeDisabled();
    });
  });

  describe('Validation', () => {
    it('shows error when simulating without teams', async () => {
      render(
        <GameSimulator
          teams={[mockTeamReady1, mockTeamReady2]}
          onSimulate={mockOnSimulate}
        />
      );

      // Manually trigger simulate (button should be disabled, but testing the handler)
      const form = screen.getByText('Game Simulator').closest('div');
      const simulateButton = screen.getByText(/Simulate Game/i);
      
      // Force click even though disabled
      fireEvent.click(simulateButton);

      await waitFor(() => {
        expect(screen.getByText(/Please select both teams/i)).toBeInTheDocument();
      });
    });

    it('clears error when team1 is selected', () => {
      render(
        <GameSimulator
          teams={[mockTeamReady1, mockTeamReady2]}
          onSimulate={mockOnSimulate}
        />
      );

      // First trigger an error
      const simulateButton = screen.getByText(/Simulate Game/i);
      fireEvent.click(simulateButton);

      // Then select a team
      const team1Select = screen.getByLabelText(/Home Team/i);
      fireEvent.change(team1Select, { target: { value: 'team-1' } });

      // Error should be cleared
      expect(screen.queryByText(/Please select both teams/i)).not.toBeInTheDocument();
    });

    it('clears error when team2 is selected', async () => {
      render(
        <GameSimulator
          teams={[mockTeamReady1, mockTeamReady2]}
          onSimulate={mockOnSimulate}
        />
      );

      const team1Select = screen.getByLabelText(/Home Team/i);
      fireEvent.change(team1Select, { target: { value: 'team-1' } });

      // Trigger error by clicking simulate
      const simulateButton = screen.getByText(/Simulate Game/i);
      fireEvent.click(simulateButton);

      // Select team2
      const team2Select = screen.getByLabelText(/Away Team/i);
      fireEvent.change(team2Select, { target: { value: 'team-2' } });

      // Error should be cleared
      await waitFor(() => {
        expect(screen.queryByText(/Please select both teams/i)).not.toBeInTheDocument();
      });
    });
  });

  describe('Game Simulation', () => {
    it('calls onSimulate with correct parameters', async () => {
      mockOnSimulate.mockResolvedValue(mockGame);

      render(
        <GameSimulator
          teams={[mockTeamReady1, mockTeamReady2]}
          onSimulate={mockOnSimulate}
        />
      );

      const team1Select = screen.getByLabelText(/Home Team/i);
      const team2Select = screen.getByLabelText(/Away Team/i);

      fireEvent.change(team1Select, { target: { value: 'team-1' } });
      fireEvent.change(team2Select, { target: { value: 'team-2' } });

      const simulateButton = screen.getByText(/Simulate Game/i);
      fireEvent.click(simulateButton);

      await waitFor(() => {
        expect(mockOnSimulate).toHaveBeenCalledWith({
          team1_id: 'team-1',
          team2_id: 'team-2',
          seed: undefined,
        });
      });
    });

    it('includes seed in simulation request when provided', async () => {
      mockOnSimulate.mockResolvedValue(mockGame);

      render(
        <GameSimulator
          teams={[mockTeamReady1, mockTeamReady2]}
          onSimulate={mockOnSimulate}
        />
      );

      const team1Select = screen.getByLabelText(/Home Team/i);
      const team2Select = screen.getByLabelText(/Away Team/i);
      const seedInput = screen.getByLabelText(/Random Seed/i);

      fireEvent.change(team1Select, { target: { value: 'team-1' } });
      fireEvent.change(team2Select, { target: { value: 'team-2' } });
      fireEvent.change(seedInput, { target: { value: '42' } });

      const simulateButton = screen.getByText(/Simulate Game/i);
      fireEvent.click(simulateButton);

      await waitFor(() => {
        expect(mockOnSimulate).toHaveBeenCalledWith({
          team1_id: 'team-1',
          team2_id: 'team-2',
          seed: 42,
        });
      });
    });

    it('shows loading state during simulation', async () => {
      let resolveSimulation: (value: Game) => void;
      const simulationPromise = new Promise<Game>((resolve) => {
        resolveSimulation = resolve;
      });
      mockOnSimulate.mockReturnValue(simulationPromise);

      render(
        <GameSimulator
          teams={[mockTeamReady1, mockTeamReady2]}
          onSimulate={mockOnSimulate}
        />
      );

      const team1Select = screen.getByLabelText(/Home Team/i);
      const team2Select = screen.getByLabelText(/Away Team/i);

      fireEvent.change(team1Select, { target: { value: 'team-1' } });
      fireEvent.change(team2Select, { target: { value: 'team-2' } });

      const simulateButton = screen.getByText(/Simulate Game/i);
      fireEvent.click(simulateButton);

      await waitFor(() => {
        expect(screen.getByText(/Simulating Game.../i)).toBeInTheDocument();
      });

      // Resolve the promise
      resolveSimulation!(mockGame);
    });

    it('calls onGameComplete after successful simulation', async () => {
      mockOnSimulate.mockResolvedValue(mockGame);

      render(
        <GameSimulator
          teams={[mockTeamReady1, mockTeamReady2]}
          onSimulate={mockOnSimulate}
          onGameComplete={mockOnGameComplete}
        />
      );

      const team1Select = screen.getByLabelText(/Home Team/i);
      const team2Select = screen.getByLabelText(/Away Team/i);

      fireEvent.change(team1Select, { target: { value: 'team-1' } });
      fireEvent.change(team2Select, { target: { value: 'team-2' } });

      const simulateButton = screen.getByText(/Simulate Game/i);
      fireEvent.click(simulateButton);

      await waitFor(() => {
        expect(mockOnGameComplete).toHaveBeenCalledWith(mockGame);
      });
    });

    it('resets form after successful simulation', async () => {
      mockOnSimulate.mockResolvedValue(mockGame);

      render(
        <GameSimulator
          teams={[mockTeamReady1, mockTeamReady2]}
          onSimulate={mockOnSimulate}
        />
      );

      const team1Select = screen.getByLabelText(/Home Team/i) as HTMLSelectElement;
      const team2Select = screen.getByLabelText(/Away Team/i) as HTMLSelectElement;
      const seedInput = screen.getByLabelText(/Random Seed/i) as HTMLInputElement;

      fireEvent.change(team1Select, { target: { value: 'team-1' } });
      fireEvent.change(team2Select, { target: { value: 'team-2' } });
      fireEvent.change(seedInput, { target: { value: '42' } });

      const simulateButton = screen.getByText(/Simulate Game/i);
      fireEvent.click(simulateButton);

      await waitFor(() => {
        expect(team1Select.value).toBe('');
        expect(team2Select.value).toBe('');
        expect(seedInput.value).toBe('');
      });
    });
  });

  describe('Error Handling', () => {
    it('displays error when simulation fails', async () => {
      mockOnSimulate.mockRejectedValue(new Error('Simulation failed'));

      render(
        <GameSimulator
          teams={[mockTeamReady1, mockTeamReady2]}
          onSimulate={mockOnSimulate}
        />
      );

      const team1Select = screen.getByLabelText(/Home Team/i);
      const team2Select = screen.getByLabelText(/Away Team/i);

      fireEvent.change(team1Select, { target: { value: 'team-1' } });
      fireEvent.change(team2Select, { target: { value: 'team-2' } });

      const simulateButton = screen.getByText(/Simulate Game/i);
      fireEvent.click(simulateButton);

      await waitFor(() => {
        expect(screen.getByText(/Simulation failed/i)).toBeInTheDocument();
      });
    });

    it('shows generic error message for unknown errors', async () => {
      mockOnSimulate.mockRejectedValue('Unknown error');

      render(
        <GameSimulator
          teams={[mockTeamReady1, mockTeamReady2]}
          onSimulate={mockOnSimulate}
        />
      );

      const team1Select = screen.getByLabelText(/Home Team/i);
      const team2Select = screen.getByLabelText(/Away Team/i);

      fireEvent.change(team1Select, { target: { value: 'team-1' } });
      fireEvent.change(team2Select, { target: { value: 'team-2' } });

      const simulateButton = screen.getByText(/Simulate Game/i);
      fireEvent.click(simulateButton);

      await waitFor(() => {
        expect(screen.getByText(/Failed to simulate game/i)).toBeInTheDocument();
      });
    });
  });

  describe('Custom Styling', () => {
    it('applies custom className', () => {
      const { container } = render(
        <GameSimulator
          teams={[mockTeamReady1, mockTeamReady2]}
          onSimulate={mockOnSimulate}
          className="custom-class"
        />
      );

      const component = container.firstChild as HTMLElement;
      expect(component.className).toContain('custom-class');
    });
  });

  describe('Edge Cases', () => {
    it('handles empty teams array', () => {
      render(
        <GameSimulator
          teams={[]}
          onSimulate={mockOnSimulate}
        />
      );

      expect(screen.getByText(/Not Enough Teams Ready/i)).toBeInTheDocument();
    });

    it('handles single ready team', () => {
      render(
        <GameSimulator
          teams={[mockTeamReady1]}
          onSimulate={mockOnSimulate}
        />
      );

      expect(screen.getByText(/Ready teams: 1/i)).toBeInTheDocument();
    });

    it('handles seed value of 0', async () => {
      mockOnSimulate.mockResolvedValue(mockGame);

      render(
        <GameSimulator
          teams={[mockTeamReady1, mockTeamReady2]}
          onSimulate={mockOnSimulate}
        />
      );

      const team1Select = screen.getByLabelText(/Home Team/i);
      const team2Select = screen.getByLabelText(/Away Team/i);
      const seedInput = screen.getByLabelText(/Random Seed/i);

      fireEvent.change(team1Select, { target: { value: 'team-1' } });
      fireEvent.change(team2Select, { target: { value: 'team-2' } });
      fireEvent.change(seedInput, { target: { value: '0' } });

      const simulateButton = screen.getByText(/Simulate Game/i);
      fireEvent.click(simulateButton);

      await waitFor(() => {
        expect(mockOnSimulate).toHaveBeenCalledWith({
          team1_id: 'team-1',
          team2_id: 'team-2',
          seed: 0,
        });
      });
    });
  });

  describe('Accessibility', () => {
    it('has proper form labels', () => {
      render(
        <GameSimulator
          teams={[mockTeamReady1, mockTeamReady2]}
          onSimulate={mockOnSimulate}
        />
      );

      expect(screen.getByLabelText(/Home Team/i)).toBeInTheDocument();
      expect(screen.getByLabelText(/Away Team/i)).toBeInTheDocument();
      expect(screen.getByLabelText(/Random Seed/i)).toBeInTheDocument();
    });

    it('maintains semantic structure', () => {
      const { container } = render(
        <GameSimulator
          teams={[mockTeamReady1, mockTeamReady2]}
          onSimulate={mockOnSimulate}
        />
      );

      expect(container.firstChild).toBeInTheDocument();
    });
  });
});
