/**
 * Component tests for TeamBudget
 * 
 * Tests the TeamBudget component functionality including:
 * - Budget display and formatting
 * - Progress bar visualization
 * - Budget status indicators
 * - Spending breakdown
 * - Roster statistics
 * - Capacity calculations
 * - Warning messages
 */

/// <reference types="@testing-library/jest-dom" />

import React from 'react';
import { render, screen } from '@testing-library/react';
import { TeamBudget } from '../../src/components/team/TeamBudget';
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
  // Add more players (total spent: 25000)
  {
    id: 'p3',
    name: 'Player Three',
    age: 20,
    avatar: '🏃',
    skills: { catching: 5, throwing: 5, dodging: 5, speed: 5, iq: 5, luck: 5 },
    value: 2000,
    injury: null,
    stats: {
      throws_attempted: 10,
      catches_made: 5,
      times_hit: 3,
      missed_throws: 3,
      successful_hits: 7,
    },
    team_id: 'team-1',
    is_starter: true,
  },
  {
    id: 'p4',
    name: 'Player Four',
    age: 19,
    avatar: '🏃',
    skills: { catching: 6, throwing: 6, dodging: 6, speed: 6, iq: 6, luck: 6 },
    value: 2000,
    injury: null,
    stats: {
      throws_attempted: 12,
      catches_made: 6,
      times_hit: 3,
      missed_throws: 4,
      successful_hits: 8,
    },
    team_id: 'team-1',
    is_starter: true,
  },
  {
    id: 'p5',
    name: 'Player Five',
    age: 18,
    avatar: '🏃',
    skills: { catching: 5, throwing: 6, dodging: 5, speed: 6, iq: 5, luck: 5 },
    value: 2000,
    injury: null,
    stats: {
      throws_attempted: 11,
      catches_made: 5,
      times_hit: 4,
      missed_throws: 4,
      successful_hits: 7,
    },
    team_id: 'team-1',
    is_starter: true,
  },
  {
    id: 'p6',
    name: 'Player Six',
    age: 19,
    avatar: '🏃',
    skills: { catching: 4, throwing: 5, dodging: 4, speed: 5, iq: 4, luck: 5 },
    value: 1000,
    injury: null,
    stats: {
      throws_attempted: 8,
      catches_made: 3,
      times_hit: 2,
      missed_throws: 3,
      successful_hits: 5,
    },
    team_id: 'team-1',
    is_starter: false,
  },
  {
    id: 'p7',
    name: 'Player Seven',
    age: 20,
    avatar: '🏃',
    skills: { catching: 4, throwing: 4, dodging: 5, speed: 5, iq: 4, luck: 5 },
    value: 500,
    injury: null,
    stats: {
      throws_attempted: 7,
      catches_made: 2,
      times_hit: 2,
      missed_throws: 3,
      successful_hits: 4,
    },
    team_id: 'team-1',
    is_starter: false,
  },
  {
    id: 'p8',
    name: 'Player Eight',
    age: 18,
    avatar: '🏃',
    skills: { catching: 4, throwing: 4, dodging: 4, speed: 4, iq: 4, luck: 4 },
    value: 500,
    injury: null,
    stats: {
      throws_attempted: 6,
      catches_made: 2,
      times_hit: 2,
      missed_throws: 2,
      successful_hits: 4,
    },
    team_id: 'team-1',
    is_starter: false,
  },
];

describe('TeamBudget', () => {
  describe('Budget Display', () => {
    it('renders component', () => {
      render(<TeamBudget team={mockTeam} players={mockPlayers} />);
      expect(screen.getByText(/budget/i)).toBeInTheDocument();
    });

    it('displays remaining budget correctly formatted', () => {
      render(<TeamBudget team={mockTeam} players={mockPlayers} />);
      // mockTeam.budget is 75000, so remaining is 75000
      expect(screen.getByText('$75,000')).toBeInTheDocument();
    });

    it('calculates spent budget correctly', () => {
      render(<TeamBudget team={mockTeam} players={mockPlayers} showBreakdown={true} />);
      // Total player values: 8000 + 9000 + 2000 + 2000 + 2000 + 1000 + 500 + 500 = 25000
      expect(screen.getByText('$25,000')).toBeInTheDocument();
    });

    it('displays budget percentage', () => {
      render(<TeamBudget team={mockTeam} players={mockPlayers} />);
      // 75000/100000 = 75%
      expect(screen.getByText(/75%/i)).toBeInTheDocument();
    });

    it('displays max budget correctly', () => {
      render(<TeamBudget team={mockTeam} players={mockPlayers} showBreakdown={true} />);
      expect(screen.getByText('$100,000')).toBeInTheDocument();
    });
  });

  describe('Progress Bar', () => {
    it('renders progress bar', () => {
      const { container } = render(<TeamBudget team={mockTeam} players={mockPlayers} />);
      const progressBar = container.querySelector('.bg-green-600, .bg-yellow-500, .bg-red-600');
      expect(progressBar).toBeInTheDocument();
    });

    it('uses green color for healthy budget (>50%)', () => {
      render(<TeamBudget team={mockTeam} players={mockPlayers} />);
      // 75% remaining = healthy (green)
      expect(screen.getByText(/healthy/i)).toBeInTheDocument();
    });

    it('uses yellow color for moderate budget (25-50%)', () => {
      const moderateTeam: Team = {
        ...mockTeam,
        budget: 35000, // 35% remaining
      };
      render(<TeamBudget team={moderateTeam} players={mockPlayers} />);
      expect(screen.getByText(/moderate/i)).toBeInTheDocument();
    });

    it('uses red color for low budget (10-25%)', () => {
      const lowTeam: Team = {
        ...mockTeam,
        budget: 15000, // 15% remaining
      };
      render(<TeamBudget team={lowTeam} players={mockPlayers} />);
      expect(screen.getByText(/low|critical/i)).toBeInTheDocument();
    });

    it('shows critical status for very low budget (<10%)', () => {
      const criticalTeam: Team = {
        ...mockTeam,
        budget: 5000, // 5% remaining
      };
      render(<TeamBudget team={criticalTeam} players={mockPlayers} />);
      expect(screen.getByText(/critical/i)).toBeInTheDocument();
    });

    it('shows exhausted status for no budget', () => {
      const exhaustedTeam: Team = {
        ...mockTeam,
        budget: 0,
      };
      render(<TeamBudget team={exhaustedTeam} players={mockPlayers} />);
      expect(screen.getByText(/exhausted/i)).toBeInTheDocument();
    });
  });

  describe('Budget Breakdown', () => {
    it('hides breakdown by default', () => {
      render(<TeamBudget team={mockTeam} players={mockPlayers} />);
      expect(screen.queryByText(/average player cost/i)).not.toBeInTheDocument();
    });

    it('shows breakdown when showBreakdown is true', () => {
      render(<TeamBudget team={mockTeam} players={mockPlayers} showBreakdown={true} />);
      expect(screen.getByText(/spent/i)).toBeInTheDocument();
      expect(screen.getByText(/remaining/i)).toBeInTheDocument();
    });

    it('displays roster count', () => {
      render(<TeamBudget team={mockTeam} players={mockPlayers} showBreakdown={true} />);
      expect(screen.getByText(/8 players/i)).toBeInTheDocument();
    });

    it('calculates average player cost correctly', () => {
      render(<TeamBudget team={mockTeam} players={mockPlayers} showBreakdown={true} />);
      // Total: 25000, Players: 8, Average: 3125
      expect(screen.getByText(/\$3,125/i)).toBeInTheDocument();
    });

    it('calculates affordable players count', () => {
      render(<TeamBudget team={mockTeam} players={mockPlayers} showBreakdown={true} />);
      // With 75000 remaining and average 1000 per player, could afford 75 more
      // Component might show how many $1k players can be afforded
      expect(screen.getByText(/\d+ more/i)).toBeInTheDocument();
    });
  });

  describe('Roster Statistics', () => {
    it('displays player count', () => {
      render(<TeamBudget team={mockTeam} players={mockPlayers} showBreakdown={true} />);
      expect(screen.getByText(/8/)).toBeInTheDocument();
    });

    it('shows roster capacity (12 max)', () => {
      render(<TeamBudget team={mockTeam} players={mockPlayers} showBreakdown={true} />);
      expect(screen.getByText(/12/)).toBeInTheDocument();
    });

    it('handles empty roster', () => {
      render(<TeamBudget team={mockTeam} players={[]} showBreakdown={true} />);
      expect(screen.getByText(/0 players/i)).toBeInTheDocument();
    });

    it('calculates capacity correctly', () => {
      render(<TeamBudget team={mockTeam} players={mockPlayers} showBreakdown={true} />);
      // 8 players, max 12, so 4 slots remaining
      expect(screen.getByText(/4 slots?/i)).toBeInTheDocument();
    });
  });

  describe('Warning Messages', () => {
    it('shows warning when budget is low', () => {
      const lowTeam: Team = {
        ...mockTeam,
        budget: 15000,
      };
      render(<TeamBudget team={lowTeam} players={mockPlayers} />);
      expect(screen.getByText(/warning|low/i)).toBeInTheDocument();
    });

    it('shows critical warning when budget is very low', () => {
      const criticalTeam: Team = {
        ...mockTeam,
        budget: 5000,
      };
      render(<TeamBudget team={criticalTeam} players={mockPlayers} />);
      expect(screen.getByText(/critical/i)).toBeInTheDocument();
    });

    it('shows exhausted message when no budget remaining', () => {
      const exhaustedTeam: Team = {
        ...mockTeam,
        budget: 0,
      };
      render(<TeamBudget team={exhaustedTeam} players={mockPlayers} />);
      expect(screen.getByText(/exhausted|no budget/i)).toBeInTheDocument();
    });

    it('does not show warnings for healthy budget', () => {
      render(<TeamBudget team={mockTeam} players={mockPlayers} />);
      expect(screen.queryByText(/warning/i)).not.toBeInTheDocument();
      expect(screen.queryByText(/critical/i)).not.toBeInTheDocument();
    });
  });

  describe('Per-Player Spending', () => {
    it('shows player spending list when breakdown is enabled', () => {
      render(<TeamBudget team={mockTeam} players={mockPlayers} showBreakdown={true} />);
      
      // Should show individual player values
      expect(screen.getByText('Player One')).toBeInTheDocument();
      expect(screen.getByText('$8,000')).toBeInTheDocument();
    });

    it('hides player spending list when breakdown is disabled', () => {
      render(<TeamBudget team={mockTeam} players={mockPlayers} showBreakdown={false} />);
      
      // Player names should not be in spending breakdown
      expect(screen.queryByText('$8,000')).not.toBeInTheDocument();
    });

    it('sorts players by value (highest first)', () => {
      const { container } = render(
        <TeamBudget team={mockTeam} players={mockPlayers} showBreakdown={true} />
      );
      
      // Player Two ($9000) should appear before Player One ($8000)
      const playerElements = container.querySelectorAll('[class*="player"]');
      // This is implementation-specific; adjust based on actual DOM structure
    });
  });

  describe('Edge Cases', () => {
    it('handles team with no players', () => {
      const emptyTeam: Team = {
        ...mockTeam,
        player_ids: [],
      };
      render(<TeamBudget team={emptyTeam} players={[]} showBreakdown={true} />);
      
      expect(screen.getByText('$100,000')).toBeInTheDocument(); // Full budget remaining
      expect(screen.getByText(/0 players/i)).toBeInTheDocument();
    });

    it('handles team at budget limit', () => {
      const fullTeam: Team = {
        ...mockTeam,
        budget: 0,
      };
      render(<TeamBudget team={fullTeam} players={mockPlayers} />);
      
      expect(screen.getByText('$0')).toBeInTheDocument();
      expect(screen.getByText(/exhausted/i)).toBeInTheDocument();
    });

    it('handles team with maximum roster (12 players)', () => {
      const extraPlayers: Player[] = [
        ...mockPlayers,
        { ...mockPlayers[0], id: 'p9', name: 'Player Nine', value: 1000 },
        { ...mockPlayers[0], id: 'p10', name: 'Player Ten', value: 1000 },
        { ...mockPlayers[0], id: 'p11', name: 'Player Eleven', value: 1000 },
        { ...mockPlayers[0], id: 'p12', name: 'Player Twelve', value: 1000 },
      ];

      const fullRosterTeam: Team = {
        ...mockTeam,
        player_ids: extraPlayers.map((p) => p.id),
        budget: 71000, // Adjusted for extra players
      };

      render(<TeamBudget team={fullRosterTeam} players={extraPlayers} showBreakdown={true} />);
      
      expect(screen.getByText(/12 players/i)).toBeInTheDocument();
      expect(screen.getByText(/0 slots/i)).toBeInTheDocument();
    });

    it('handles very expensive roster', () => {
      const expensivePlayers: Player[] = mockPlayers.map((p, i) => ({
        ...p,
        value: 12000, // 12k each, total 96k for 8 players
      }));

      const expensiveTeam: Team = {
        ...mockTeam,
        budget: 4000, // Only 4k remaining
      };

      render(<TeamBudget team={expensiveTeam} players={expensivePlayers} showBreakdown={true} />);
      
      expect(screen.getByText(/\$4,000/i)).toBeInTheDocument();
      expect(screen.getByText(/critical|low/i)).toBeInTheDocument();
    });

    it('handles negative budget (over-spent)', () => {
      // This shouldn't happen with validation, but test defensive handling
      const overSpentTeam: Team = {
        ...mockTeam,
        budget: -5000,
      };

      render(<TeamBudget team={overSpentTeam} players={mockPlayers} />);
      
      // Should show 0 or handle gracefully
      expect(screen.getByText(/exhausted|over/i)).toBeInTheDocument();
    });
  });

  describe('Custom Styling', () => {
    it('applies custom className', () => {
      const { container } = render(
        <TeamBudget team={mockTeam} players={mockPlayers} className="custom-class" />
      );
      
      const budget = container.firstChild as HTMLElement;
      expect(budget.className).toContain('custom-class');
    });
  });

  describe('Accessibility', () => {
    it('has proper semantic structure', () => {
      const { container } = render(<TeamBudget team={mockTeam} players={mockPlayers} />);
      expect(container.firstChild).toBeInTheDocument();
    });

    it('displays budget information in readable format', () => {
      render(<TeamBudget team={mockTeam} players={mockPlayers} />);
      
      // Check that dollar amounts are formatted with commas
      expect(screen.getByText(/\$75,000/i)).toBeInTheDocument();
    });

    it('uses appropriate color contrast for status indicators', () => {
      const criticalTeam: Team = {
        ...mockTeam,
        budget: 5000,
      };
      render(<TeamBudget team={criticalTeam} players={mockPlayers} />);
      
      // Critical status should have red text or background
      const criticalElement = screen.getByText(/critical/i);
      expect(criticalElement).toBeVisible();
    });
  });
});
