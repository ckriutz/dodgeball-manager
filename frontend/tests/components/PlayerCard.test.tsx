/**
 * Component tests for PlayerCard
 * 
 * Tests the PlayerCard component functionality including:
 * - Player information display
 * - Skill visualization
 * - Injury status display
 * - Statistics display
 * - Team information
 * - Click interactions
 */

/// <reference types="@testing-library/jest-dom" />

import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { PlayerCard } from '../../src/components/player/PlayerCard';
import type { Player } from '../../src/types';

/**
 * Mock player data
 */
const mockPlayer: Player = {
  id: 'player-1',
  name: 'John Doe',
  age: 19,
  avatar: '🏃',
  skills: {
    catching: 6,
    throwing: 8,
    dodging: 9,
    speed: 7,
    iq: 7,
    luck: 5,
  },
  value: 75000,
  injury: null,
  stats: {
    throws_attempted: 38,
    catches_made: 15,
    times_hit: 8,
    missed_throws: 13,
    successful_hits: 25,
  },
  team_id: null,
  is_starter: false,
};

const mockInjuredPlayer: Player = {
  ...mockPlayer,
  id: 'player-2',
  name: 'Jane Smith',
  injury: {
    severity: 'moderate',
    affected_reduction: 20,
    games_remaining: 3,
  },
};

const mockTeamPlayer: Player = {
  ...mockPlayer,
  id: 'player-3',
  name: 'Bob Johnson',
  team_id: 'team-1',
  is_starter: true,
};

describe('PlayerCard', () => {
  describe('Basic Information Display', () => {
    it('renders player name correctly', () => {
      render(<PlayerCard player={mockPlayer} />);
      expect(screen.getByText('John Doe')).toBeInTheDocument();
    });

    it('renders player avatar', () => {
      render(<PlayerCard player={mockPlayer} />);
      expect(screen.getByText('🏃')).toBeInTheDocument();
    });

    it('renders player age', () => {
      render(<PlayerCard player={mockPlayer} />);
      expect(screen.getByText(/19 yrs/i)).toBeInTheDocument();
    });

    it('renders player value correctly formatted', () => {
      render(<PlayerCard player={mockPlayer} />);
      expect(screen.getByText('$75,000')).toBeInTheDocument();
    });
  });

  describe('Skills Display', () => {
    it('renders all six skills', () => {
      render(<PlayerCard player={mockPlayer} />);
      
      expect(screen.getByText(/throwing power/i)).toBeInTheDocument();
      expect(screen.getByText(/throwing accuracy/i)).toBeInTheDocument();
      expect(screen.getByText(/catching/i)).toBeInTheDocument();
      expect(screen.getByText(/dodging/i)).toBeInTheDocument();
      expect(screen.getByText(/speed/i)).toBeInTheDocument();
      expect(screen.getByText(/endurance/i)).toBeInTheDocument();
    });

    it('displays skill values', () => {
      render(<PlayerCard player={mockPlayer} />);
      
      // Check that skill values are displayed
      expect(screen.getByText('8')).toBeInTheDocument(); // throwing_power
      expect(screen.getByText('7')).toBeInTheDocument(); // throwing_accuracy or speed
      expect(screen.getByText('6')).toBeInTheDocument(); // catching
      expect(screen.getByText('9')).toBeInTheDocument(); // dodging
      expect(screen.getByText('5')).toBeInTheDocument(); // endurance
    });
  });

  describe('Injury Status', () => {
    it('does not show injury badge for healthy player', () => {
      render(<PlayerCard player={mockPlayer} />);
      expect(screen.queryByText(/injured/i)).not.toBeInTheDocument();
    });

    it('shows injury badge for injured player', () => {
      render(<PlayerCard player={mockInjuredPlayer} />);
      expect(screen.getByText(/shoulder/i)).toBeInTheDocument();
    });

    it('displays injury severity', () => {
      render(<PlayerCard player={mockInjuredPlayer} />);
      expect(screen.getByText(/moderate/i)).toBeInTheDocument();
    });

    it('displays games remaining for injury', () => {
      render(<PlayerCard player={mockInjuredPlayer} />);
      expect(screen.getByText(/3 games/i)).toBeInTheDocument();
    });
  });

  describe('Statistics Display', () => {
    it('hides statistics by default', () => {
      render(<PlayerCard player={mockPlayer} />);
      expect(screen.queryByText(/eliminations/i)).not.toBeInTheDocument();
    });

    it('shows statistics when showStats is true', () => {
      render(<PlayerCard player={mockPlayer} showStats={true} />);
      
      expect(screen.getByText(/eliminations/i)).toBeInTheDocument();
      expect(screen.getByText('25')).toBeInTheDocument(); // eliminations
      expect(screen.getByText(/catches/i)).toBeInTheDocument();
      expect(screen.getByText('15')).toBeInTheDocument(); // catches
      expect(screen.getByText(/accuracy/i)).toBeInTheDocument();
      expect(screen.getByText(/65\.5%/i)).toBeInTheDocument();
    });

    it('displays games played', () => {
      render(<PlayerCard player={mockPlayer} showStats={true} />);
      expect(screen.getByText(/10 games/i)).toBeInTheDocument();
    });
  });

  describe('Team Information', () => {
    it('shows free agent status by default', () => {
      render(<PlayerCard player={mockPlayer} showTeamInfo={true} />);
      expect(screen.getByText(/free agent/i)).toBeInTheDocument();
    });

    it('hides team info when showTeamInfo is false', () => {
      render(<PlayerCard player={mockPlayer} showTeamInfo={false} />);
      expect(screen.queryByText(/free agent/i)).not.toBeInTheDocument();
    });

    it('displays team ID when player is on a team', () => {
      render(<PlayerCard player={mockTeamPlayer} showTeamInfo={true} />);
      expect(screen.getByText(/team-1/i)).toBeInTheDocument();
    });

    it('shows starter status', () => {
      render(<PlayerCard player={mockTeamPlayer} showTeamInfo={true} />);
      expect(screen.getByText(/starter/i)).toBeInTheDocument();
    });
  });

  describe('Click Interaction', () => {
    it('calls onClick handler when card is clicked', () => {
      const handleClick = vi.fn();
      render(<PlayerCard player={mockPlayer} onClick={handleClick} />);
      
      const card = screen.getByText('John Doe').closest('div')?.parentElement;
      if (card) {
        fireEvent.click(card);
      }
      
      expect(handleClick).toHaveBeenCalledWith(mockPlayer);
      expect(handleClick).toHaveBeenCalledTimes(1);
    });

    it('does not call onClick when handler is not provided', () => {
      // Should not throw error when onClick is undefined
      expect(() => {
        render(<PlayerCard player={mockPlayer} />);
      }).not.toThrow();
    });

    it('applies hover styles when onClick is provided', () => {
      const handleClick = vi.fn();
      const { container } = render(<PlayerCard player={mockPlayer} onClick={handleClick} />);
      
      const card = container.firstChild as HTMLElement;
      expect(card.className).toContain('cursor-pointer');
    });
  });

  describe('Custom Styling', () => {
    it('applies custom className', () => {
      const { container } = render(<PlayerCard player={mockPlayer} className="custom-class" />);
      
      const card = container.firstChild as HTMLElement;
      expect(card.className).toContain('custom-class');
    });
  });

  describe('Edge Cases', () => {
    it('handles player with zero stats', () => {
      const playerWithZeroStats: Player = {
        ...mockPlayer,
        stats: {
          games_played: 0,
          eliminations: 0,
          catches: 0,
          times_eliminated: 0,
          accuracy_percentage: 0,
        },
      };
      
      render(<PlayerCard player={playerWithZeroStats} showStats={true} />);
      expect(screen.getByText('0')).toBeInTheDocument();
    });

    it('handles player with maximum skill values', () => {
      const maxSkillPlayer: Player = {
        ...mockPlayer,
        skills: {
          throwing_power: 10,
          throwing_accuracy: 10,
          catching: 10,
          dodging: 10,
          speed: 10,
          endurance: 10,
        },
      };
      
      render(<PlayerCard player={maxSkillPlayer} />);
      const tens = screen.getAllByText('10');
      expect(tens.length).toBeGreaterThanOrEqual(6);
    });

    it('handles player with minimum skill values', () => {
      const minSkillPlayer: Player = {
        ...mockPlayer,
        skills: {
          throwing_power: 0,
          throwing_accuracy: 0,
          catching: 0,
          dodging: 0,
          speed: 0,
          endurance: 0,
        },
      };
      
      render(<PlayerCard player={minSkillPlayer} />);
      const zeros = screen.getAllByText('0');
      expect(zeros.length).toBeGreaterThanOrEqual(6);
    });

    it('handles very long player names', () => {
      const longNamePlayer: Player = {
        ...mockPlayer,
        name: 'Alexander Bartholomew Christopher Donovan',
      };
      
      render(<PlayerCard player={longNamePlayer} />);
      expect(screen.getByText('Alexander Bartholomew Christopher Donovan')).toBeInTheDocument();
    });

    it('handles high value players', () => {
      const highValuePlayer: Player = {
        ...mockPlayer,
        value: 999999,
      };
      
      render(<PlayerCard player={highValuePlayer} />);
      expect(screen.getByText('$999,999')).toBeInTheDocument();
    });
  });

  describe('Accessibility', () => {
    it('has proper semantic structure', () => {
      const { container } = render(<PlayerCard player={mockPlayer} />);
      expect(container.firstChild).toBeInTheDocument();
    });

    it('maintains readability with injury status', () => {
      render(<PlayerCard player={mockInjuredPlayer} />);
      
      // Should have visible text for injury
      const injuryText = screen.getByText(/shoulder/i);
      expect(injuryText).toBeVisible();
    });
  });
});
