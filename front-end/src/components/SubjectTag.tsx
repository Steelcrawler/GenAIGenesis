import React from 'react';

export default function SubjectMasteryTag({ subject = "Mathematics", masteryLevel = 75 }) {

  // Ensure mastery level is between 0 and 100
  const normalizedMasteryLevel = Math.max(0, Math.min(100, masteryLevel));
  
  // Calculate color based on mastery level (red to yellow to green)
  const getColor = (level: number) => {
    if (level < 50) {
      // Red (0%) to Yellow (50%)
      const g = Math.floor((level / 50) * 255);
      return `rgb(255, ${g}, 0)`;
    } else {
      // Yellow (50%) to Green (100%)
      const r = Math.floor(255 - ((level - 50) / 50) * 255);
      return `rgb(${r}, 255, 0)`;
    }
  };

  const wheelColor = getColor(normalizedMasteryLevel);
  
  return (
    <div className="flex items-center bg-gray-100 rounded-full px-3 py-2 w-36">
      {/* Subject name */}
      <span className="text-gray-800 font-medium mr-2 w-full">{subject}</span>
      
      {/* Mastery wheel */}
      <div className="relative flex-shrink-0 w-10 h-10">
        {/* Background circle (empty) */}
        <svg className="w-10 h-10" viewBox="0 0 24 24">
          <circle
            cx="12"
            cy="12"
            r="10"
            fill="none"
            stroke="#e5e7eb"
            strokeWidth="3"
          />
        </svg>
        
        {/* Foreground circle (filled based on mastery) */}
        <svg className="absolute top-0 left-0 w-10 h-10" viewBox="0 0 24 24">
          <circle
            cx="12"
            cy="12"
            r="10"
            fill="none"
            stroke={wheelColor}
            strokeWidth="3"
            strokeDasharray={`${normalizedMasteryLevel * 0.628} 100`}
            transform="rotate(-90 12 12)"
          />
        </svg>
        
        {/* Percentage text */}
        <div className="absolute inset-0 flex items-center justify-center">
          <span className="text-xs font-bold text-gray-800">
            {normalizedMasteryLevel}
          </span>
        </div>
      </div>
    </div>
  );
};