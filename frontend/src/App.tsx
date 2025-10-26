/**
 * Main App component with routing configuration for the Dodgeball Fantasy League.
 * 
 * This component sets up the application structure, routing, and context providers.
 */

import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { LeagueProvider } from './contexts/LeagueContext';
import { LeaguePage } from './pages/LeaguePage';
import { PlayersPage } from './pages/PlayersPage';
import { TeamsPage } from './pages/TeamsPage';

// Home page component
const HomePage: React.FC = () => (
  <div className="min-h-screen bg-gray-100 flex items-center justify-center">
    <div className="text-center">
      <h1 className="text-4xl font-bold text-gray-900 mb-4">
        Dodgeball Fantasy League
      </h1>
      <p className="text-xl text-gray-600 mb-8">
        Create leagues, draft teams, and simulate epic dodgeball battles!
      </p>
      <div className="space-x-4">
        <a
          href="/leagues"
          className="inline-block px-6 py-3 bg-blue-600 text-white font-semibold rounded-lg hover:bg-blue-700 transition"
        >
          Get Started
        </a>
        <a
          href="/docs"
          className="inline-block px-6 py-3 bg-gray-200 text-gray-800 font-semibold rounded-lg hover:bg-gray-300 transition"
        >
          API Docs
        </a>
      </div>
    </div>
  </div>
);

const GamesPage: React.FC = () => (
  <div className="min-h-screen bg-gray-100 p-8">
    <div className="max-w-7xl mx-auto">
      <h1 className="text-3xl font-bold text-gray-900 mb-6">Games</h1>
      <p className="text-gray-600">Game simulation will be implemented in User Story 3</p>
    </div>
  </div>
);

const NotFoundPage: React.FC = () => (
  <div className="min-h-screen bg-gray-100 flex items-center justify-center">
    <div className="text-center">
      <h1 className="text-6xl font-bold text-gray-900 mb-4">404</h1>
      <p className="text-xl text-gray-600 mb-8">Page not found</p>
      <a
        href="/"
        className="inline-block px-6 py-3 bg-blue-600 text-white font-semibold rounded-lg hover:bg-blue-700 transition"
      >
        Go Home
      </a>
    </div>
  </div>
);

/**
 * Main App component
 */
const App: React.FC = () => {
  return (
    <LeagueProvider>
      <BrowserRouter>
        <div className="min-h-screen">
          {/* Navigation will be added in user stories */}
          <Routes>
            {/* Home route */}
            <Route path="/" element={<HomePage />} />
            
            {/* League routes */}
            <Route path="/leagues" element={<LeaguePage />} />
            <Route path="/leagues/:leagueId" element={<LeaguePage />} />
            <Route path="/leagues/:leagueId/players" element={<PlayersPage />} />
            
            {/* Player routes */}
            <Route path="/players" element={<PlayersPage />} />
            
            {/* Team routes */}
            <Route path="/leagues/:leagueId/teams" element={<TeamsPage />} />
            <Route path="/teams/:teamId" element={<TeamsPage />} />
            
            {/* Game routes */}
            <Route path="/games" element={<GamesPage />} />
            <Route path="/games/:gameId" element={<GamesPage />} />
            
            {/* API documentation redirect */}
            <Route path="/docs" element={<Navigate to="http://localhost:8000/docs" replace />} />
            
            {/* 404 catch-all */}
            <Route path="*" element={<NotFoundPage />} />
          </Routes>
        </div>
      </BrowserRouter>
    </LeagueProvider>
  );
};

export default App;
