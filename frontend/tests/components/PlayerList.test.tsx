/**
 * Component tests for PlayerList
 * 
 * Tests the PlayerList component functionality including:
 * - Player filtering and search
 * - Sorting functionality
 * - View mode toggle (grid/list)
 * - Loading and empty states
 * - Player click interactions
 */

/// <reference types="@testing-library/jest-dom" />

import React from 'react';
import { render, screen, fireEvent, within } from '@testing-library/react';
import { PlayerList } from '../../src/components/player/PlayerList';
import type { Player } from '../../src/types';

/**
 * Mock player data
 */
const mockPlayers: Player[] = [
  {
    id: 'player-1',
    name: 'Alice Johnson',
    age: 18,
    avatar: '👩',
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
  },
  {
    id: 'player-2',
    name: 'Bob Smith',
    age: 19,
    avatar: '👨',
    skills: {
      catching: 5,
      throwing: 6,
      dodging: 7,
      speed: 8,
      iq: 6,
      luck: 4,
    },
    value: 60000,
    injury: null,
    stats: {
      throws_attempted: 30,
      catches_made: 12,
      times_hit: 10,
      missed_throws: 10,
      successful_hits: 20,
    },
    team_id: 'team-1',
    is_starter: true,
  },
  {
    id: 'player-3',
    name: 'Charlie Brown',
    age: 20,
    avatar: '🧑',
    skills: {
      catching: 7,
      throwing: 7,
      dodging: 6,
      speed: 6,
      iq: 8,
      luck: 6,
    },
    value: 85000,
    injury: {
      severity: 'minor',
      affected_reduction: 10,
      games_remaining: 1,
    },
    stats: {
      throws_attempted: 45,
      catches_made: 20,
      times_hit: 5,
      missed_throws: 15,
      successful_hits: 30,
    },
    team_id: null,
    is_starter: false,
  },
];

describe('PlayerList', () => {
  describe('Basic Rendering', () => {
    test('renders player cards for all players', () => {
      render(<PlayerList players={mockPlayers} />);
      
      expect(screen.getByText('Alice Johnson')).toBeInTheDocument();
      expect(screen.getByText('Bob Smith')).toBeInTheDocument();
      expect(screen.getByText('Charlie Brown')).toBeInTheDocument();
    });

    test('renders showing count message', () => {
      render(<PlayerList players={mockPlayers} />);
      
      expect(screen.getByText(/Showing 3 of 3 players/i)).toBeInTheDocument();
    });

    test('renders all control elements', () => {
      render(<PlayerList players={mockPlayers} />);
      
      // Search input
      expect(screen.getByPlaceholderText(/search players by name/i)).toBeInTheDocument();
      
      // Free agents filter
      expect(screen.getByLabelText(/free agents only/i)).toBeInTheDocument();
      
      // View mode buttons
      expect(screen.getByText('Grid')).toBeInTheDocument();
      expect(screen.getByText('List')).toBeInTheDocument();
      
      // Sort buttons
      expect(screen.getByText(/Name/)).toBeInTheDocument();
      expect(screen.getByText(/Age/)).toBeInTheDocument();
      expect(screen.getByText(/Value/)).toBeInTheDocument();
      expect(screen.getByText(/Skills/)).toBeInTheDocument();
    });
  });

  describe('Search Functionality', () => {
    test('filters players by name', () => {
      render(<PlayerList players={mockPlayers} />);
      
      const searchInput = screen.getByPlaceholderText(/search players by name/i);
      fireEvent.change(searchInput, { target: { value: 'Alice' } });
      
      expect(screen.getByText('Alice Johnson')).toBeInTheDocument();
      expect(screen.queryByText('Bob Smith')).not.toBeInTheDocument();
      expect(screen.queryByText('Charlie Brown')).not.toBeInTheDocument();
    });

    test('search is case insensitive', () => {
      render(<PlayerList players={mockPlayers} />);
      
      const searchInput = screen.getByPlaceholderText(/search players by name/i);
      fireEvent.change(searchInput, { target: { value: 'alice' } });
      
      expect(screen.getByText('Alice Johnson')).toBeInTheDocument();
    });

    test('shows "no players match" message when search has no results', () => {
      render(<PlayerList players={mockPlayers} />);
      
      const searchInput = screen.getByPlaceholderText(/search players by name/i);
      fireEvent.change(searchInput, { target: { value: 'Nonexistent' } });
      
      expect(screen.getByText(/No players match your filters/i)).toBeInTheDocument();
    });

    test('clears search filter when clicking clear filters', () => {
      render(<PlayerList players={mockPlayers} />);
      
      const searchInput = screen.getByPlaceholderText(/search players by name/i);
      fireEvent.change(searchInput, { target: { value: 'Alice' } });
      
      expect(screen.queryByText('Bob Smith')).not.toBeInTheDocument();
      
      const clearButton = screen.getByText(/Clear Filters/i);
      fireEvent.click(clearButton);
      
      expect(screen.getByText('Bob Smith')).toBeInTheDocument();
    });
  });

  describe('Free Agents Filter', () => {
    test('filters to show only free agents', () => {
      render(<PlayerList players={mockPlayers} />);
      
      const freeAgentsCheckbox = screen.getByLabelText(/free agents only/i);
      fireEvent.click(freeAgentsCheckbox);
      
      // Alice and Charlie are free agents (team_id === null)
      expect(screen.getByText('Alice Johnson')).toBeInTheDocument();
      expect(screen.getByText('Charlie Brown')).toBeInTheDocument();
      
      // Bob is on a team
      expect(screen.queryByText('Bob Smith')).not.toBeInTheDocument();
    });

    test('updates count message when filtering free agents', () => {
      render(<PlayerList players={mockPlayers} />);
      
      const freeAgentsCheckbox = screen.getByLabelText(/free agents only/i);
      fireEvent.click(freeAgentsCheckbox);
      
      expect(screen.getByText(/Showing 2 of 3 players.*free agents only/i)).toBeInTheDocument();
    });
  });

  describe('Sorting', () => {
    test('sorts players by name ascending by default', () => {
      render(<PlayerList players={mockPlayers} />);
      
      const playerNames = screen.getAllByRole('heading', { level: 3 });
      expect(playerNames[0]).toHaveTextContent('Alice Johnson');
      expect(playerNames[1]).toHaveTextContent('Bob Smith');
      expect(playerNames[2]).toHaveTextContent('Charlie Brown');
    });

    test('toggles sort direction when clicking same field', () => {
      render(<PlayerList players={mockPlayers} />);
      
      const nameButton = screen.getByRole('button', { name: /Name/i });
      
      // First click: descending (reverse alphabetical)
      fireEvent.click(nameButton);
      
      const playerNamesDesc = screen.getAllByRole('heading', { level: 3 });
      expect(playerNamesDesc[0]).toHaveTextContent('Charlie Brown');
      
      // Second click: ascending again
      fireEvent.click(nameButton);
      
      const playerNamesAsc = screen.getAllByRole('heading', { level: 3 });
      expect(playerNamesAsc[0]).toHaveTextContent('Alice Johnson');
    });

    test('sorts players by age', () => {
      render(<PlayerList players={mockPlayers} />);
      
      const ageButton = screen.getByRole('button', { name: /Age/i });
      fireEvent.click(ageButton);
      
      const playerNames = screen.getAllByRole('heading', { level: 3 });
      expect(playerNames[0]).toHaveTextContent('Alice Johnson'); // age 18
      expect(playerNames[1]).toHaveTextContent('Bob Smith'); // age 19
      expect(playerNames[2]).toHaveTextContent('Charlie Brown'); // age 20
    });

    test('sorts players by value', () => {
      render(<PlayerList players={mockPlayers} />);
      
      const valueButton = screen.getByRole('button', { name: /Value/i });
      fireEvent.click(valueButton);
      
      const playerNames = screen.getAllByRole('heading', { level: 3 });
      expect(playerNames[0]).toHaveTextContent('Bob Smith'); // $60,000
      expect(playerNames[1]).toHaveTextContent('Alice Johnson'); // $75,000
      expect(playerNames[2]).toHaveTextContent('Charlie Brown'); // $85,000
    });

    test('sorts players by total skills', () => {
      render(<PlayerList players={mockPlayers} />);
      
      const skillsButton = screen.getByRole('button', { name: /Skills/i });
      fireEvent.click(skillsButton);
      
      // Bob has 36 total, Alice has 42 total, Charlie has 40 total
      const playerNames = screen.getAllByRole('heading', { level: 3 });
      expect(playerNames[0]).toHaveTextContent('Bob Smith');
      expect(playerNames[1]).toHaveTextContent('Charlie Brown');
      expect(playerNames[2]).toHaveTextContent('Alice Johnson');
    });

    test('shows sort direction indicator', () => {
      render(<PlayerList players={mockPlayers} />);
      
      const nameButton = screen.getByRole('button', { name: /Name/i });
      
      // Should show ascending indicator initially
      expect(nameButton).toHaveTextContent('↑');
      
      // Click to toggle
      fireEvent.click(nameButton);
      expect(nameButton).toHaveTextContent('↓');
    });
  });

  describe('View Mode Toggle', () => {
    test('switches between grid and list view', () => {
      const { container } = render(<PlayerList players={mockPlayers} />);
      
      // Default is grid view
      const gridContainer = container.querySelector('.grid');
      expect(gridContainer).toBeInTheDocument();
      
      // Switch to list view
      const listButton = screen.getByText('List');
      fireEvent.click(listButton);
      
      const listContainer = container.querySelector('.space-y-4');
      expect(listContainer).toBeInTheDocument();
    });

    test('highlights active view mode button', () => {
      render(<PlayerList players={mockPlayers} />);
      
      const gridButton = screen.getByText('Grid');
      const listButton = screen.getByText('List');
      
      // Grid is active by default
      expect(gridButton).toHaveClass('bg-blue-600');
      expect(listButton).not.toHaveClass('bg-blue-600');
      
      // Click list
      fireEvent.click(listButton);
      
      expect(listButton).toHaveClass('bg-blue-600');
      expect(gridButton).not.toHaveClass('bg-blue-600');
    });
  });

  describe('Loading State', () => {
    test('shows loading spinner when loading', () => {
      render(<PlayerList players={[]} loading={true} />);
      
      expect(screen.getByText(/Loading players.../i)).toBeInTheDocument();
      
      // Should show spinner
      const spinner = document.querySelector('.animate-spin');
      expect(spinner).toBeInTheDocument();
    });

    test('does not show players when loading', () => {
      render(<PlayerList players={mockPlayers} loading={true} />);
      
      expect(screen.queryByText('Alice Johnson')).not.toBeInTheDocument();
    });
  });

  describe('Empty State', () => {
    test('shows empty state when no players provided', () => {
      render(<PlayerList players={[]} />);
      
      expect(screen.getByText(/No players found/i)).toBeInTheDocument();
    });

    test('shows custom empty message', () => {
      render(<PlayerList players={[]} emptyMessage="Custom empty message" />);
      
      expect(screen.getByText('Custom empty message')).toBeInTheDocument();
    });

    test('shows empty state icon', () => {
      render(<PlayerList players={[]} />);
      
      // SVG icon should be present
      const icon = document.querySelector('svg');
      expect(icon).toBeInTheDocument();
    });
  });

  describe('Click Interaction', () => {
    test('calls onPlayerClick when player card is clicked', () => {
      const handlePlayerClick = jest.fn();
      render(<PlayerList players={mockPlayers} onPlayerClick={handlePlayerClick} />);
      
      const aliceCard = screen.getByText('Alice Johnson');
      fireEvent.click(aliceCard.closest('div')!);
      
      expect(handlePlayerClick).toHaveBeenCalledWith(mockPlayers[0]);
    });

    test('does not throw error when onPlayerClick is not provided', () => {
      expect(() => {
        render(<PlayerList players={mockPlayers} />);
      }).not.toThrow();
    });
  });

  describe('Props: showStats', () => {
    test('passes showStats to PlayerCard components', () => {
      render(<PlayerList players={mockPlayers} showStats={true} />);
      
      // Statistics should be visible (PlayerCard shows stats when showStats is true)
      expect(screen.getAllByText(/Eliminations:/i).length).toBeGreaterThan(0);
    });

    test('hides stats by default', () => {
      render(<PlayerList players={mockPlayers} showStats={false} />);
      
      // Statistics should not be visible
      expect(screen.queryByText(/Eliminations:/i)).not.toBeInTheDocument();
    });
  });

  describe('Props: showTeamInfo', () => {
    test('passes showTeamInfo to PlayerCard components', () => {
      render(<PlayerList players={mockPlayers} showTeamInfo={true} />);
      
      // Team info should be visible
      expect(screen.getByText(/Free Agent/i)).toBeInTheDocument();
    });

    test('hides team info when prop is false', () => {
      render(<PlayerList players={mockPlayers} showTeamInfo={false} />);
      
      // Team info should not be visible
      expect(screen.queryByText(/Free Agent/i)).not.toBeInTheDocument();
    });
  });

  describe('Combined Filtering', () => {
    test('combines search and free agents filter', () => {
      render(<PlayerList players={mockPlayers} />);
      
      // Enable free agents filter
      const freeAgentsCheckbox = screen.getByLabelText(/free agents only/i);
      fireEvent.click(freeAgentsCheckbox);
      
      // Search for Alice
      const searchInput = screen.getByPlaceholderText(/search players by name/i);
      fireEvent.change(searchInput, { target: { value: 'Alice' } });
      
      // Only Alice should be visible (she is a free agent)
      expect(screen.getByText('Alice Johnson')).toBeInTheDocument();
      expect(screen.queryByText('Charlie Brown')).not.toBeInTheDocument();
      expect(screen.queryByText('Bob Smith')).not.toBeInTheDocument();
      
      expect(screen.getByText(/Showing 1 of 3 players.*free agents only/i)).toBeInTheDocument();
    });
  });

  describe('Edge Cases', () => {
    test('handles single player', () => {
      render(<PlayerList players={[mockPlayers[0]]} />);
      
      expect(screen.getByText('Alice Johnson')).toBeInTheDocument();
      expect(screen.getByText(/Showing 1 of 1 players/i)).toBeInTheDocument();
    });

    test('handles large number of players', () => {
      const manyPlayers = Array.from({ length: 100 }, (_, i) => ({
        ...mockPlayers[0],
        id: `player-${i}`,
        name: `Player ${i}`,
      }));
      
      render(<PlayerList players={manyPlayers} />);
      
      expect(screen.getByText(/Showing 100 of 100 players/i)).toBeInTheDocument();
    });

    test('applies custom className', () => {
      const { container } = render(<PlayerList players={mockPlayers} className="custom-class" />);
      
      expect(container.firstChild).toHaveClass('custom-class');
    });
  });
});
