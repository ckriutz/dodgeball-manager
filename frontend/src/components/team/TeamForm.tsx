/**
 * TeamForm Component
 * 
 * Form for creating a new team:
 * - Team name (required)
 * - Description (optional)
 * - Logo selection from available avatars (required)
 * - League is implicit from context (no dropdown)
 * - Form validation
 * - Error handling
 * 
 * Used in team creation interfaces.
 */

import React, { useState } from 'react';
import type { CreateTeamRequest } from '../../types';

interface TeamFormProps {
  leagueId: string;
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
}

interface FormErrors {
  name?: string;
  description?: string;
  logo?: string;
  general?: string;
}

// Available team avatars
const TEAM_AVATARS = [
  'team-avatar-1.png',
  'team-avatar-2.png',
  'team-avatar-3.png',
  'team-avatar-4.png',
  'team-avatar-5.png',
  'team-avatar-6.png',
  'team-avatar-7.png',
  'team-avatar-8.png',
];

/**
 * TeamForm component
 */
export const TeamForm: React.FC<TeamFormProps> = ({
  leagueId,
  onSubmit,
  onCancel,
  isLoading = false,
  error = null,
  className = '',
}) => {
  const [formData, setFormData] = useState<FormData>({
    name: '',
    description: '',
    logo: TEAM_AVATARS[0], // Default to first avatar
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
      
      case 'description':
        if (value && value.length > 200) {
          return 'Description must be less than 200 characters';
        }
        break;

      case 'logo':
        if (!value) {
          return 'Please select a team avatar';
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
    
    const logoError = validateField('logo', formData.logo);
    if (logoError) newErrors.logo = logoError;

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
    setTouched(new Set(['name', 'logo']));
    
    if (!validateForm()) {
      return;
    }

    // Create the request object
    const teamRequest: CreateTeamRequest = {
      name: formData.name.trim(),
      league_id: leagueId,
      logo: formData.logo,
      ...(formData.description && { description: formData.description.trim() }),
    };

    onSubmit(teamRequest);
  };

  const showNameError = touched.has('name') && errors.name;
  const showLogoError = touched.has('logo') && errors.logo;

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

      {/* Team Logo Selection */}
      <div className="mb-4">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Team Avatar <span className="text-red-500">*</span>
        </label>
        <div className="grid grid-cols-4 gap-3">
          {TEAM_AVATARS.map((avatar) => (
            <button
              key={avatar}
              type="button"
              onClick={() => {
                setFormData((prev) => ({ ...prev, logo: avatar }));
                if (errors.logo) {
                  setErrors((prev) => ({ ...prev, logo: undefined }));
                }
              }}
              disabled={isLoading}
              className={`relative aspect-square rounded-lg border-2 transition-all duration-200 overflow-hidden ${
                formData.logo === avatar
                  ? 'border-blue-500 ring-2 ring-blue-200'
                  : 'border-gray-300 hover:border-blue-400'
              } ${isLoading ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}`}
            >
              <img
                src={`/images/team_avatars/${avatar}`}
                alt={`Team avatar ${avatar}`}
                className="w-full h-full object-cover"
              />
              {formData.logo === avatar && (
                <div className="absolute top-1 right-1 bg-blue-500 text-white rounded-full p-1">
                  <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
                    <path
                      fillRule="evenodd"
                      d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
                      clipRule="evenodd"
                    />
                  </svg>
                </div>
              )}
            </button>
          ))}
        </div>
        {showLogoError && (
          <p className="mt-1 text-sm text-red-600">{errors.logo}</p>
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

      {/* Info Box */}
      <div className="mb-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
        <h4 className="text-sm font-semibold text-blue-900 mb-2">Team Setup</h4>
        <ul className="text-sm text-blue-800 space-y-1">
          <li>• Teams start with a $15,000 budget</li>
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
          disabled={isLoading}
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
