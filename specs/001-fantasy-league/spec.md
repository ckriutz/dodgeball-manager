# Feature Specification: Dodgeball Fantasy League Core System

**Feature Branch**: `001-fantasy-league`  
**Created**: October 24, 2025  
**Status**: Draft  
**Input**: User description: "I am going to build a fun webapp that acts as a dodgeball fantasy league"

## Clarifications

### Session 2025-10-24

- Q: What happens when a team attempts to add a player whose value exactly equals their remaining budget? → A: When this happens, the budget goes to zero and the player gets added.
- Q: How should the system handle a game when a team has fewer than 5 healthy (non-injured) players available to start? → A: Injured players play with reduced stats instead of sitting out.
- Q: When aging reduces a player's maximum skill level below their current skill value, what happens to the current skill value? → A: Skills are automatically reduced to match the new maximum.
- Q: How many players should be generated when a league is first created? → A: Generate 50-100 players (ample variety for drafting).
- Q: Should we address concurrent access scenarios for this milestone? → A: Not applicable; single-user system (remove edge case).
- Q: Should player values include cents (decimal precision) or be whole dollar amounts only? → A: Integer values only (no cents).
- Q: What is the age range for newly generated players and when does aging affect stats? → A: Players are generated with ages between 18-20, and aging does not affect maximum skill levels until the player reaches age 30.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - League Setup and Player Generation (Priority: P1)

A league administrator can create a new league and populate it with randomly generated players. This establishes the foundation of the fantasy league by creating the player pool from which teams will be built.

**Why this priority**: Without players, there is no league. This is the foundational data that everything else depends on. This story delivers immediate value by providing a viewable roster of players with stats and calculated values.

**Independent Test**: Can be fully tested by creating a league, generating players, and viewing the player pool with all attributes (name, age, avatar, skills, calculated value). Delivers a browsable player database with meaningful stats.

**Acceptance Scenarios**:

1. **Given** no league exists, **When** administrator creates a new league with a name, **Then** a league is created with default settings and zero teams
2. **Given** a league exists, **When** administrator generates players, **Then** each player has a placeholder name, age, avatar, and 10 skill points randomly distributed across catching, throwing, dodging, speed, IQ, and luck (all skills 0-100 range)
3. **Given** players are generated, **When** viewing player details, **Then** each player displays their calculated value based on age and skill stats
4. **Given** multiple players exist, **When** viewing the player pool, **Then** all available free agent players are listed with their key stats and values

---

### User Story 2 - Team Creation and Player Draft (Priority: P2)

A team owner can create a team and build their roster by selecting 8-12 players from the available free agent pool, staying within their $100,000 budget. This allows users to strategize and build their ideal team composition.

**Why this priority**: Teams are essential for competition but depend on having a player pool. This story delivers the core fantasy experience of building your dream team within budget constraints.

**Independent Test**: Can be fully tested by creating a team, viewing available players sorted by position/value, selecting players within budget, and confirming the final roster. Delivers a complete team management experience.

**Acceptance Scenarios**:

1. **Given** a league with available players, **When** user creates a team with name, description, and logo, **Then** team is created with $100,000 budget and empty roster
2. **Given** a team with available budget, **When** user selects a player from the free agent pool, **Then** player is added to roster and their value is deducted from team budget
3. **Given** a team roster, **When** viewing team details, **Then** team shows 5 designated starters and remaining players as bench (8-12 total players)
4. **Given** a player is added to a team, **When** viewing the player pool, **Then** that player is no longer available as a free agent
5. **Given** a team has insufficient budget, **When** user attempts to add a player whose value exceeds remaining budget, **Then** system prevents the addition and shows budget constraint message
6. **Given** a team has 12 players, **When** user attempts to add another player, **Then** system prevents the addition and shows roster limit message

---

### User Story 3 - Game Simulation and Stats Tracking (Priority: P3)

The league can simulate games between teams where player skills determine outcomes through dodgeball mechanics. The simulation updates player stats and team records, creating an evolving competitive landscape.

**Why this priority**: Game simulation is the entertainment payoff but requires teams and players to be fully set up. This delivers the "action" that makes the league dynamic and engaging.

**Independent Test**: Can be fully tested by selecting two teams, simulating a game, viewing the play-by-play results, and confirming updated stats and win/loss records. Delivers the core entertainment value of watching your team compete.

**Acceptance Scenarios**:

1. **Given** two teams with complete rosters, **When** league initiates game simulation, **Then** game proceeds with 5 starters per team following dodgeball elimination rules
2. **Given** a game in progress, **When** a player throws at an opponent, **Then** outcome (hit, miss, or catch) is determined by throwing player's stats (throwing, IQ) vs defending player's stats (catching, dodging, IQ) plus randomness influenced by luck
3. **Given** a player is hit or their throw is caught, **When** elimination occurs, **Then** that player is removed from active play for remainder of game
4. **Given** all players on one team are eliminated, **When** game ends, **Then** winning team is declared and game result is recorded
5. **Given** a game completes, **When** viewing player stats, **Then** each player's performance stats are updated (throws, catches, hits taken, misses, successful hits)
6. **Given** a game completes, **When** viewing team records, **Then** winner gains a win and loser gains a loss

---

### User Story 4 - League Schedule and Season Management (Priority: P4)

The league can create a schedule of games between teams and track season-long performance including standings, MVPs, and awards.

**Why this priority**: Schedules and season structure add depth but require working game simulation. This delivers the long-term engagement of a competitive season.

**Independent Test**: Can be fully tested by creating a schedule for all teams, simulating multiple games in sequence, and viewing updated standings and cumulative stats. Delivers a complete season experience.

**Acceptance Scenarios**:

1. **Given** a league with multiple teams, **When** administrator creates a schedule, **Then** games are generated pairing teams in a balanced format
2. **Given** a schedule exists, **When** league simulates next scheduled game, **Then** game proceeds and schedule advances
3. **Given** multiple games completed, **When** viewing league standings, **Then** teams are ranked by wins and losses
4. **Given** a season of games, **When** viewing league awards, **Then** system identifies MVPs and statistical leaders based on player performance

---

### Edge Cases

- When a team attempts to add a player whose value exactly equals their remaining budget, the player is added successfully and the team budget becomes $0
- How does the system handle a game simulation where both teams somehow eliminate each other simultaneously (should not be possible in dodgeball rules)?
- When a player's age increases and reduces their max skill levels below their current skill values, the current skills are automatically reduced to match the new maximum
- How does the system handle injury probability and duration during game simulation?
- When a team has injured players, those injured players participate in games as starters with their reduced (injured) stats rather than sitting out

## Requirements *(mandatory)*

### Functional Requirements

#### Player Management

- **FR-001**: System MUST generate players with placeholder names, randomly assigned ages between 18-20, and placeholder avatars
- **FR-001a**: System MUST generate between 50-100 players when a league is first created to provide ample variety for team drafting
- **FR-002**: System MUST assign each new player exactly 10 total skill points randomly distributed across six skills: catching, throwing, dodging, speed, IQ, and luck
- **FR-003**: System MUST enforce skill level range of 0-100 for each individual skill
- **FR-004**: System MUST calculate player value using a formula that factors in age and skill stats
- **FR-004a**: System MUST represent all player values and team budgets as integer dollar amounts without cents
- **FR-005**: System MUST track player statistics including throws attempted, catches made, times hit, missed throws, successful hits on opponents
- **FR-006**: System MUST support player injury status that affects their stats until injury heals
- **FR-006a**: System MUST allow injured players to participate in games with their reduced stats rather than being unavailable
- **FR-007**: System MUST reduce maximum skill levels as player age increases beyond 30 years old
- **FR-007a**: System MUST automatically reduce current skill values to match new maximum when aging lowers the skill cap below current value
- **FR-008**: System MUST allow player skills to improve over time through gameplay
- **FR-009**: System MUST track whether each player is a free agent or assigned to a team

#### Team Management

- **FR-010**: System MUST allow creation of teams with name, description, and logo
- **FR-011**: System MUST provide each new team with $100,000 starting budget
- **FR-012**: System MUST enforce roster size limits of 8-12 players per team
- **FR-013**: System MUST require teams to designate exactly 5 players as starters
- **FR-014**: System MUST prevent adding players whose value exceeds team's remaining budget
- **FR-014a**: System MUST allow adding players whose value exactly equals team's remaining budget, reducing budget to $0
- **FR-015**: System MUST deduct player value from team budget when player is added to roster
- **FR-016**: System MUST track team wins and losses
- **FR-017**: System MUST track team awards and achievements
- **FR-018**: System MUST prevent adding players who are already on another team

#### League Management

- **FR-019**: System MUST allow creation of leagues with name and settings
- **FR-020**: System MUST manage multiple teams within a league
- **FR-021**: System MUST create and maintain game schedules pairing teams
- **FR-022**: System MUST track league-wide player statistics across all games
- **FR-023**: System MUST maintain historical records of all games played
- **FR-024**: System MUST identify and track MVP awards and statistical leaders
- **FR-025**: System MUST maintain the global pool of free agent players

#### Game Simulation

- **FR-026**: System MUST simulate games between two teams using their designated starter players (5 per team)
- **FR-027**: System MUST determine throw outcomes (hit, miss, catch) based on attacker stats (throwing, IQ), defender stats (catching, dodging, IQ), and randomness influenced by luck
- **FR-028**: System MUST eliminate players who are hit or whose throw is caught
- **FR-029**: System MUST end game when all players on one team are eliminated
- **FR-030**: System MUST update all relevant player performance statistics after each game
- **FR-031**: System MUST update team win/loss records after each game
- **FR-032**: System MUST enforce standard dodgeball elimination rules during simulation

#### Data Storage

- **FR-033**: System MUST store all data in memory for this initial milestone (no database, Redis, or persistent storage)
- **FR-034**: System MUST maintain data consistency across players, teams, and league during gameplay

### Non-Functional Requirements

- **NFR-001**: System is designed for single-user operation without authentication or user management
- **NFR-002**: System has no access restrictions or permission controls in this milestone
- **NFR-003**: Game simulation algorithm must be deterministic given the same player stats and random seed for testing purposes

### Key Entities

- **Player**: Represents an individual dodgeball athlete with name, age, avatar, six skill attributes (catching, throwing, dodging, speed, IQ, luck each 0-100), calculated value, injury status, gameplay statistics (throws, catches, hits taken, misses, successful hits), and team assignment status
- **Team**: Represents a fantasy team with name, description, logo, budget (starting $100,000), roster of 8-12 players, designated 5 starters, win/loss record, and awards/achievements
- **League**: Central management entity containing multiple teams, global player pool, game schedules, historical game records, league settings, and award tracking (MVPs, statistical leaders)
- **Game**: Represents a match between two teams with participating players (starters), play-by-play events (throws, hits, catches, misses), eliminations, final outcome, and updated statistics
- **Injury**: Represents a temporary condition affecting a player with severity, affected stats, and healing timeline

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can create a league and generate a pool of players with complete attributes and calculated values in under 1 minute
- **SC-002**: Users can create a team and draft a full roster of 8-12 players while staying within budget constraints in under 5 minutes
- **SC-003**: Game simulation between two teams completes and produces a winner with updated statistics in under 30 seconds
- **SC-004**: System maintains accurate player statistics across multiple simulated games with zero data inconsistencies
- **SC-005**: 100% of game outcomes are determined by player skill stats combined with randomness, producing varied but logical results
- **SC-006**: Users can view complete league standings, team rosters, player stats, and game history at any time
- **SC-007**: Player value calculation accurately reflects the combined impact of age and skill stats using a consistent formula
- **SC-008**: Team budget constraints are enforced 100% of the time, preventing roster additions that exceed available funds

## Assumptions *(optional)*

- Placeholder names will be simple identifiers (e.g., "Player 1", "Player 2") until more sophisticated name generation is implemented
- Avatar placeholders will be generic images or initials until custom avatar system is built
- New players are generated with ages between 18-20 years old
- Players under age 30 do not experience any age-related stat degradation
- The formula for calculating player value will weight skills equally with age providing a discount factor (specific formula to be determined during implementation planning)
- Injury probability during games will be low (e.g., 5% chance per player per game) to maintain gameplay flow
- Injury effects will reduce affected skills by 20-50% depending on severity
- Injury healing will occur automatically after 1-3 simulated games depending on severity
- Game simulation will process events sequentially (one throw at a time) rather than simultaneously
- Luck stat will influence random outcome variance by ±10% for each action
- The "best" player will throw first in each round of game simulation, determined by a combination of throwing and IQ stats
- Schedule generation will ensure each team plays every other team at least once
- MVP and awards will be determined by statistical formulas (e.g., highest total hits, best catch percentage)

## Dependencies *(optional)*

- None for this initial milestone, as the system is self-contained with in-memory storage

## Out of Scope *(optional)*

The following features are explicitly excluded from this milestone and will be addressed in future iterations:

- User authentication and account management
- Multi-user support and access controls
- Persistent data storage (database, Redis, file system)
- Real-time multiplayer or live game viewing
- Advanced player name generation or customization
- Custom avatar creation or upload
- Trading players between teams
- Salary cap adjustments or dynamic player value changes
- Advanced scheduling algorithms (playoffs, tournaments)
- Detailed injury management system
- Player morale, contracts, or retirement mechanics
- Social features (chat, forums, leaderboards across multiple users)
- Mobile applications or native clients
- API for external integrations
- Advanced analytics or statistical reports beyond basic stats
