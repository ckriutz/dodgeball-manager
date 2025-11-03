/**
 * Breadcrumbs Component
 * 
 * Consistent navigation breadcrumbs used across all pages.
 * Shows the hierarchical path and allows navigation back through levels.
 */

import React from 'react';
import { Link } from 'react-router-dom';

export interface BreadcrumbItem {
  label: string;
  path?: string;
  onClick?: () => void;
}

interface BreadcrumbsProps {
  items: BreadcrumbItem[];
  className?: string;
}

/**
 * Breadcrumbs component
 */
export const Breadcrumbs: React.FC<BreadcrumbsProps> = ({ items, className = '' }) => {
  return (
    <nav className={`flex items-center gap-2 text-sm ${className}`} aria-label="Breadcrumb">
      {items.map((item, index) => {
        const isLast = index === items.length - 1;

        return (
          <React.Fragment key={index}>
            {index > 0 && (
              <svg
                className="h-4 w-4 text-gray-400"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M9 5l7 7-7 7"
                />
              </svg>
            )}
            {isLast ? (
              <span className="font-medium text-gray-900">{item.label}</span>
            ) : item.onClick ? (
              <button
                onClick={item.onClick}
                className="font-medium text-blue-600 hover:text-blue-700 transition-colors"
              >
                {item.label}
              </button>
            ) : item.path ? (
              <Link
                to={item.path}
                className="font-medium text-blue-600 hover:text-blue-700 transition-colors"
              >
                {item.label}
              </Link>
            ) : (
              <span className="font-medium text-gray-600">{item.label}</span>
            )}
          </React.Fragment>
        );
      })}
    </nav>
  );
};

export default Breadcrumbs;
