/**
 * TeamForm Component
 * 
 * Form for creating a new team:
 * - Team name (required)
 * - Description (optional)
 * - Logo (optional)
 * - League selection (required)
 * - Form validation
 * - Error handling
 * 
 * Used in team creation interfaces.
 */

import React, { useState } from 'react';
import type { CreateTeamRequest, League } from '../../types';

interface TeamFormProps {
  leagues: League[];
  onSubmit: (teamData: CreateTeamRequest) => void;
  onCancel?: () => void;
  isLoading?: boolean;
  error?: string | null;
  className?: string;
}

interface FormData {
  name: string;
  description: string;
  logo: string;
  league_id: string;
}

interface FormErrors {
  name?: string;
  description?: string;
  league_id?: string;
  general?: string;
}

/**
 * TeamForm component
 */
export const TeamForm: React.FC<TeamFormProps> = ({
  leagues,
  onSubmit,
  onCancel,
  isLoading = false,
  error = null,
  className = '',
}) => {
  const [formData, setFormData] = useState<FormData>({
    name: '',
    description: '',
    logo: '',
    league_id: leagues.length === 1 ? leagues[0].id : '',
  });

  const [errors, setErrors] = useState<FormErrors>({});
  const [touched, setTouched] = useState<Set<string>>(new Set());

  /**
   * Validate form field
   */
  const validateField = (name: keyof FormData, value: string): string | undefined => {
    switch (name) {
      case 'name':
        if (!value.trim()) {
          return 'Team name is required';
        }
        if (value.trim().length < 3) {
          return 'Team name must be at least 3 characters';
        }
        if (value.trim().length > 50) {
          return 'Team name must be less than 50 characters';
        }
        break;
      
      case 'league_id':
        if (!value) {
          return 'Please select a league';
        }
        break;
      
      case 'description':
        if (value && value.length > 200) {
          return 'Description must be less than 200 characters';
        }
        break;
    }
    return undefined;
  };

  /**
   * Validate entire form
   */
  const validateForm = (): boolean => {
    const newErrors: FormErrors = {};
    
    const nameError = validateField('name', formData.name);
    if (nameError) newErrors.name = nameError;
    
    const leagueError = validateField('league_id', formData.league_id);
    if (leagueError) newErrors.league_id = leagueError;

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  /**
   * Handle field change
   */
  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
    
    // Clear error for this field
    if (errors[name as keyof FormErrors]) {
      setErrors((prev) => ({ ...prev, [name]: undefined }));
    }
  };

  /**
   * Handle field blur
   */
  const handleBlur = (e: React.FocusEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name } = e.target;
    setTouched((prev) => new Set(prev).add(name));
    
    // Validate field on blur
    const fieldError = validateField(name as keyof FormData, formData[name as keyof FormData]);
    if (fieldError) {
      setErrors((prev) => ({ ...prev, [name]: fieldError }));
    }
  };

  /**
   * Handle form submission
   */
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    // Mark all fields as touched
    setTouched(new Set(['name', 'league_id']));
    
    if (!validateForm()) {
      return;
    }

    // Create the request object
    const teamRequest: CreateTeamRequest = {
      name: formData.name.trim(),
      league_id: formData.league_id,
      ...(formData.description && { description: formData.description.trim() }),
      ...(formData.logo && { logo: formData.logo.trim() }),
    };

    onSubmit(teamRequest);
  };

  const showNameError = touched.has('name') && errors.name;
  const showLeagueError = touched.has('league_id') && errors.league_id;

  return (
    <form onSubmit={handleSubmit} className={`bg-white rounded-lg shadow-md border border-gray-200 p-6 ${className}`}>
      <h2 className="text-2xl font-bold text-gray-900 mb-6">Create New Team</h2>

      {/* General Error */}
      {error && (
        <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
          <div className="flex items-start gap-2">
            <span className="text-lg">⚠️</span>
            <div>
              <div className="font-semibold">Error Creating Team</div>
              <div className="mt-1">{error}</div>
            </div>
          </div>
        </div>
      )}

      {/* Team Name */}
      <div className="mb-4">
        <label htmlFor="name" className="block text-sm font-medium text-gray-700 mb-2">
          Team Name <span className="text-red-500">*</span>
        </label>
        <input
          type="text"
          id="name"
          name="name"
          value={formData.name}
          onChange={handleChange}
          onBlur={handleBlur}
          disabled={isLoading}
          placeholder="Enter team name"
          className={`w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 transition-colors ${
            showNameError
              ? 'border-red-300 focus:ring-red-500 focus:border-red-500'
              : 'border-gray-300 focus:ring-blue-500 focus:border-blue-500'
          } ${isLoading ? 'bg-gray-100 cursor-not-allowed' : 'bg-white'}`}
        />
        {showNameError && (
          <p className="mt-1 text-sm text-red-600">{errors.name}</p>
        )}
        <p className="mt-1 text-xs text-gray-500">
          {formData.name.length}/50 characters
        </p>
      </div>

      {/* League Selection */}
      <div className="mb-4">
        <label htmlFor="league_id" className="block text-sm font-medium text-gray-700 mb-2">
          League <span className="text-red-500">*</span>
        </label>
        <select
          id="league_id"
          name="league_id"
          value={formData.league_id}
          onChange={handleChange}
          onBlur={handleBlur}
          disabled={isLoading || leagues.length === 0}
          className={`w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 transition-colors ${
            showLeagueError
              ? 'border-red-300 focus:ring-red-500 focus:border-red-500'
              : 'border-gray-300 focus:ring-blue-500 focus:border-blue-500'
          } ${isLoading || leagues.length === 0 ? 'bg-gray-100 cursor-not-allowed' : 'bg-white'}`}
        >
          <option value="">Select a league</option>
          {leagues.map((league) => (
            <option key={league.id} value={league.id}>
              {league.name} ({league.team_ids.length} teams)
            </option>
          ))}
        </select>
        {showLeagueError && (
          <p className="mt-1 text-sm text-red-600">{errors.league_id}</p>
        )}
        {leagues.length === 0 && (
          <p className="mt-1 text-sm text-yellow-600">
            ⚠️ No leagues available. Create a league first.
          </p>
        )}
      </div>

      {/* Description */}
      <div className="mb-4">
        <label htmlFor="description" className="block text-sm font-medium text-gray-700 mb-2">
          Description <span className="text-gray-400 text-xs">(optional)</span>
        </label>
        <textarea
          id="description"
          name="description"
          value={formData.description}
          onChange={handleChange}
          onBlur={handleBlur}
          disabled={isLoading}
          placeholder="Enter team description"
          rows={3}
          className={`w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 transition-colors ${
            errors.description
              ? 'border-red-300 focus:ring-red-500 focus:border-red-500'
              : 'border-gray-300 focus:ring-blue-500 focus:border-blue-500'
          } ${isLoading ? 'bg-gray-100 cursor-not-allowed' : 'bg-white'}`}
        />
        {errors.description && (
          <p className="mt-1 text-sm text-red-600">{errors.description}</p>
        )}
        <p className="mt-1 text-xs text-gray-500">
          {formData.description.length}/200 characters
        </p>
      </div>

      {/* Logo URL */}
      <div className="mb-6">
        <label htmlFor="logo" className="block text-sm font-medium text-gray-700 mb-2">
          Logo URL <span className="text-gray-400 text-xs">(optional)</span>
        </label>
        <input
          type="url"
          id="logo"
          name="logo"
          value={formData.logo}
          onChange={handleChange}
          onBlur={handleBlur}
          disabled={isLoading}
          placeholder="https://example.com/logo.png"
          className={`w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors ${
            isLoading ? 'bg-gray-100 cursor-not-allowed' : 'bg-white'
          }`}
        />
        <p className="mt-1 text-xs text-gray-500">
          Enter a URL to an image for your team logo
        </p>
      </div>

      {/* Info Box */}
      <div className="mb-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
        <h4 className="text-sm font-semibold text-blue-900 mb-2">Team Setup</h4>
        <ul className="text-sm text-blue-800 space-y-1">
          <li>• Teams start with a $100,000 budget</li>
          <li>• Draft 8-12 players from the free agent pool</li>
          <li>• Designate exactly 5 starters before competing</li>
          <li>• Player values range from $1,000 to $50,000</li>
        </ul>
      </div>

      {/* Form Actions */}
      <div className="flex gap-3">
        {onCancel && (
          <button
            type="button"
            onClick={onCancel}
            disabled={isLoading}
            className="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Cancel
          </button>
        )}
        <button
          type="submit"
          disabled={isLoading || leagues.length === 0}
          className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
        >
          {isLoading ? (
            <>
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
              Creating...
            </>
          ) : (
            'Create Team'
          )}
        </button>
      </div>
    </form>
  );
};

export default TeamForm;
