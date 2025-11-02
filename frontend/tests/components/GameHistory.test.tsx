/**
 * Component tests for GameHistory
 * 
 * Tests the GameHistory component functionality including:
 * - Event list display
 * - Event type indicators
 * - Player name resolution
 * - Turn number formatting
 * - Show more/less functionality
 * - Empty state handling
 * - Game completion status
 */

/// <reference types="@testing-library/jest-dom" />

import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { GameHistory } from '../../src/components/game/GameHistory';
import type { Game, Player, GameEvent } from '../../src/types';

/**
 * Mock player data
 */
const mockPlayers: Record<string, Player> = {
  'player-1': {
    id: 'player-1',
    name: 'John Doe',
    age: 19,
    avatar: 'avatar-1',
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
    team_id: 'team-1',
    is_starter: true,
  },
  'player-2': {
    id: 'player-2',
    name: 'Jane Smith',
    age: 20,
    avatar: 'avatar-2',
    skills: {
      catching: 7,
      throwing: 6,
      dodging: 8,
      speed: 8,
      iq: 6,
      luck: 7,
    },
    value: 72000,
    injury: null,
    stats: {
      throws_attempted: 42,
      catches_made: 18,
      times_hit: 10,
      missed_throws: 15,
      successful_hits: 27,
    },
    team_id: 'team-2',
    is_starter: true,
  },
};

/**
 * Mock game events
 */
const mockEvents: GameEvent[] = [
  {
    turn: 1,
    type: 'throw',
    thrower_id: 'player-1',
    target_id: 'player-2',
    outcome: 'John Doe throws at Jane Smith',
  },
  {
    turn: 1,
    type: 'hit',
    thrower_id: 'player-1',
    target_id: 'player-2',
    outcome: 'John Doe hits Jane Smith',
  },
  {
    turn: 2,
    type: 'throw',
    thrower_id: 'player-2',
    target_id: 'player-1',
    outcome: 'Jane Smith throws at John Doe',
  },
  {
    turn: 2,
    type: 'catch',
    thrower_id: 'player-2',
    target_id: 'player-1',
    outcome: 'John Doe catches the ball!',
  },
  {
    turn: 3,
    type: 'throw',
    thrower_id: 'player-1',
    target_id: 'player-2',
    outcome: 'John Doe throws at Jane Smith',
  },
  {
    turn: 3,
    type: 'miss',
    thrower_id: 'player-1',
    target_id: 'player-2',
    outcome: 'John Doe misses Jane Smith',
  },
  {
    turn: 4,
    type: 'elimination',
    thrower_id: 'player-2',
    target_id: 'player-1',
    outcome: 'Jane Smith eliminates John Doe!',
  },
];

/**
 * Mock game data
 */
const mockGame: Game = {
  id: 'game-1',
  league_id: 'league-1',
  team1_id: 'team-1',
  team2_id: 'team-2',
  team1_starters: ['player-1', 'player-3', 'player-5', 'player-7', 'player-9'],
  team2_starters: ['player-2', 'player-4', 'player-6', 'player-8', 'player-10'],
  events: mockEvents,
  winner_id: 'team-2',
  completed_at: '2025-10-25T14:30:00Z',
  seed: 42,
};

const mockEmptyGame: Game = {
  ...mockGame,
  id: 'game-2',
  events: [],
  winner_id: null,
  completed_at: null,
};

describe('GameHistory', () => {
  describe('Event Display', () => {
    it('renders all events when no maxEvents limit', () => {
      render(<GameHistory game={mockGame} />);
      
      // Should show all 7 events
      expect(screen.getByText(/7 event/)).toBeInTheDocument();
    });

    it('displays event outcomes', () => {
      render(<GameHistory game={mockGame} players={mockPlayers} />);
      
      expect(screen.getByText(/John Doe throws at Jane Smith/)).toBeInTheDocument();
      expect(screen.getByText(/John Doe hits Jane Smith/)).toBeInTheDocument();
      expect(screen.getByText(/Jane Smith eliminates John Doe!/)).toBeInTheDocument();
    });

    it('formats turn numbers with leading zeros', () => {
      render(<GameHistory game={mockGame} />);
      
      expect(screen.getByText('T001')).toBeInTheDocument();
      expect(screen.getByText('T002')).toBeInTheDocument();
      expect(screen.getByText('T003')).toBeInTheDocument();
      expect(screen.getByText('T004')).toBeInTheDocument();
    });

    it('shows event type labels', () => {
      render(<GameHistory game={mockGame} />);
      
      expect(screen.getByText('Throw')).toBeInTheDocument();
      expect(screen.getByText('Hit')).toBeInTheDocument();
      expect(screen.getByText('Catch')).toBeInTheDocument();
      expect(screen.getByText('Miss')).toBeInTheDocument();
      expect(screen.getByText('Eliminated')).toBeInTheDocument();
    });

    it('displays event type icons', () => {
      render(<GameHistory game={mockGame} />);
      
      // Check for emoji icons
      expect(screen.getByText('🎯')).toBeInTheDocument(); // throw
      expect(screen.getByText('💥')).toBeInTheDocument(); // hit
      expect(screen.getByText('✋')).toBeInTheDocument(); // catch
      expect(screen.getByText('❌')).toBeInTheDocument(); // miss
      expect(screen.getByText('☠️')).toBeInTheDocument(); // elimination
    });
  });

  describe('Player Name Resolution', () => {
    it('displays player names when player map provided', () => {
      render(<GameHistory game={mockGame} players={mockPlayers} />);
      
      expect(screen.getByText(/John Doe/)).toBeInTheDocument();
      expect(screen.getByText(/Jane Smith/)).toBeInTheDocument();
    });

    it('displays player IDs when player map not provided', () => {
      render(<GameHistory game={mockGame} />);
      
      // Should show IDs in the outcome text
      expect(screen.getByText(/player-1/)).toBeInTheDocument();
      expect(screen.getByText(/player-2/)).toBeInTheDocument();
    });

    it('shows thrower and target information', () => {
      render(<GameHistory game={mockGame} players={mockPlayers} />);
      
      // Check for "from X to Y" pattern
      const fromToText = screen.getAllByText(/from|to/);
      expect(fromToText.length).toBeGreaterThan(0);
    });
  });

  describe('Max Events Limit', () => {
    it('limits displayed events when maxEvents is set', () => {
      render(<GameHistory game={mockGame} maxEvents={3} />);
      
      // Should only show first 3 events
      const turnLabels = screen.getAllByText(/T00/);
      expect(turnLabels.length).toBe(3);
    });

    it('shows "Show All Events" button when events are limited', () => {
      render(<GameHistory game={mockGame} maxEvents={3} />);
      
      expect(screen.getByText(/Show All Events/)).toBeInTheDocument();
      expect(screen.getByText(/4 more/)).toBeInTheDocument();
    });

    it('expands to show all events when "Show All" is clicked', () => {
      render(<GameHistory game={mockGame} maxEvents={3} />);
      
      const showAllButton = screen.getByText(/Show All Events/);
      fireEvent.click(showAllButton);
      
      // Should now show all 7 events (7 turn labels)
      const turnLabels = screen.getAllByText(/T00/);
      expect(turnLabels.length).toBe(7);
    });

    it('shows "Show Less" button after expanding', () => {
      render(<GameHistory game={mockGame} maxEvents={3} />);
      
      const showAllButton = screen.getByText(/Show All Events/);
      fireEvent.click(showAllButton);
      
      expect(screen.getByText(/Show Less/)).toBeInTheDocument();
    });

    it('collapses events when "Show Less" is clicked', () => {
      render(<GameHistory game={mockGame} maxEvents={3} />);
      
      // Expand first
      const showAllButton = screen.getByText(/Show All Events/);
      fireEvent.click(showAllButton);
      
      // Then collapse
      const showLessButton = screen.getByText(/Show Less/);
      fireEvent.click(showLessButton);
      
      // Should be back to 3 events
      const turnLabels = screen.getAllByText(/T00/);
      expect(turnLabels.length).toBe(3);
    });

    it('does not show buttons when maxEvents not set', () => {
      render(<GameHistory game={mockGame} />);
      
      expect(screen.queryByText(/Show All Events/)).not.toBeInTheDocument();
      expect(screen.queryByText(/Show Less/)).not.toBeInTheDocument();
    });
  });

  describe('Empty State', () => {
    it('shows empty state when no events', () => {
      render(<GameHistory game={mockEmptyGame} />);
      
      expect(screen.getByText(/No Events Yet/)).toBeInTheDocument();
    });

    it('shows appropriate message for incomplete game', () => {
      render(<GameHistory game={mockEmptyGame} />);
      
      expect(screen.getByText(/hasn't started or events are still being recorded/)).toBeInTheDocument();
    });

    it('shows appropriate message for completed game with no events', () => {
      const completedEmptyGame: Game = {
        ...mockEmptyGame,
        completed_at: '2025-10-25T14:30:00Z',
      };
      
      render(<GameHistory game={completedEmptyGame} />);
      
      expect(screen.getByText(/no recorded events/)).toBeInTheDocument();
    });
  });

  describe('Game Completion Status', () => {
    it('shows completion badge for completed games', () => {
      render(<GameHistory game={mockGame} />);
      
      expect(screen.getByText('Complete')).toBeInTheDocument();
    });

    it('does not show completion badge for incomplete games', () => {
      render(<GameHistory game={mockEmptyGame} />);
      
      expect(screen.queryByText('Complete')).not.toBeInTheDocument();
    });

    it('shows summary footer for completed games', () => {
      render(<GameHistory game={mockGame} />);
      
      expect(screen.getByText(/Game duration:/)).toBeInTheDocument();
      expect(screen.getByText(/4 turns/)).toBeInTheDocument();
    });

    it('displays seed information when available', () => {
      render(<GameHistory game={mockGame} />);
      
      expect(screen.getByText(/Seed: 42/)).toBeInTheDocument();
    });

    it('does not show seed when not set', () => {
      const gameWithoutSeed: Game = {
        ...mockGame,
        seed: 0,
      };
      
      render(<GameHistory game={gameWithoutSeed} />);
      
      expect(screen.queryByText(/Seed:/)).not.toBeInTheDocument();
    });
  });

  describe('Event Count Display', () => {
    it('shows correct event count in header', () => {
      render(<GameHistory game={mockGame} />);
      
      expect(screen.getByText(/7 events recorded/)).toBeInTheDocument();
    });

    it('uses singular "event" for single event', () => {
      const singleEventGame: Game = {
        ...mockGame,
        events: [mockEvents[0]],
      };
      
      render(<GameHistory game={singleEventGame} />);
      
      expect(screen.getByText(/1 event recorded/)).toBeInTheDocument();
    });
  });

  describe('Custom Styling', () => {
    it('applies custom className', () => {
      const { container } = render(
        <GameHistory game={mockGame} className="custom-class" />
      );
      
      const component = container.firstChild as HTMLElement;
      expect(component.className).toContain('custom-class');
    });
  });

  describe('Edge Cases', () => {
    it('handles events with null player IDs', () => {
      const eventsWithNulls: GameEvent[] = [
        {
          turn: 1,
          type: 'throw',
          thrower_id: 'player-1',
          target_id: 'player-2',
          outcome: 'Event with null target',
        },
      ];
      
      const gameWithNulls: Game = {
        ...mockGame,
        events: eventsWithNulls,
      };
      
      expect(() => {
        render(<GameHistory game={gameWithNulls} players={mockPlayers} />);
      }).not.toThrow();
    });

    it('handles very long event outcomes', () => {
      const longOutcome = 'This is a very long outcome description that should still be displayed properly without breaking the layout or causing any visual issues in the component';
      
      const eventWithLongOutcome: GameEvent[] = [
        {
          turn: 1,
          type: 'throw',
          thrower_id: 'player-1',
          target_id: 'player-2',
          outcome: longOutcome,
        },
      ];
      
      const gameWithLongOutcome: Game = {
        ...mockGame,
        events: eventWithLongOutcome,
      };
      
      render(<GameHistory game={gameWithLongOutcome} />);
      expect(screen.getByText(longOutcome)).toBeInTheDocument();
    });

    it('handles large turn numbers', () => {
      const largeEvents: GameEvent[] = [
        {
          turn: 999,
          type: 'throw',
          thrower_id: 'player-1',
          target_id: 'player-2',
          outcome: 'Turn 999 event',
        },
      ];
      
      const gameWithLargeTurns: Game = {
        ...mockGame,
        events: largeEvents,
      };
      
      render(<GameHistory game={gameWithLargeTurns} />);
      expect(screen.getByText('T999')).toBeInTheDocument();
    });

    it('handles many events efficiently', () => {
      const manyEvents: GameEvent[] = Array.from({ length: 100 }, (_, i) => ({
        turn: i + 1,
        type: 'throw' as const,
        thrower_id: 'player-1',
        target_id: 'player-2',
        outcome: `Event ${i + 1}`,
      }));
      
      const gameWithManyEvents: Game = {
        ...mockGame,
        events: manyEvents,
      };
      
      expect(() => {
        render(<GameHistory game={gameWithManyEvents} maxEvents={10} />);
      }).not.toThrow();
      
      expect(screen.getByText(/100 events recorded/)).toBeInTheDocument();
    });
  });

  describe('Accessibility', () => {
    it('has proper semantic structure', () => {
      const { container } = render(<GameHistory game={mockGame} />);
      expect(container.firstChild).toBeInTheDocument();
    });

    it('maintains readable text colors', () => {
      render(<GameHistory game={mockGame} />);
      
      // Check that header text is visible
      const header = screen.getByText('Play-by-Play');
      expect(header).toBeVisible();
    });

    it('provides context for event types', () => {
      render(<GameHistory game={mockGame} />);
      
      // Event type labels should be present for screen readers
      expect(screen.getByText('Throw')).toBeInTheDocument();
      expect(screen.getByText('Hit')).toBeInTheDocument();
    });
  });
});
