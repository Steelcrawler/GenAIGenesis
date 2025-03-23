import React from 'react';

interface SubjectMasteryTagProps {
  subject: string;
  subjectId: string;
  masteryLevel: number;
  onClick: (subjectId: string) => void;
}


export default function SubjectMasteryTag({ subject = "Mathematics", subjectId, masteryLevel = 75, onClick }: SubjectMasteryTagProps) {

  const normalizedMasteryLevel = Math.max(0, Math.min(100, masteryLevel));
  
  const getColor = (level: number) => {
    if (level < 50) {
      const g = Math.floor((level / 50) * 255);
      return `rgb(255, ${g}, 0)`;
    } else {
      const r = Math.floor(255 - ((level - 50) / 50) * 255);
      return `rgb(${r}, 255, 0)`;
    }
  };

  const wheelColor = getColor(normalizedMasteryLevel);
  
  return (
    <div 
      className="flex items-center bg-gray-100 rounded-full px-3 py-2 w-36 hover:bg-gray-200 cursor-pointer transition-colors"
      onClick={() => onClick(subjectId)}
    >
      <span className="text-gray-800 font-medium mr-2 w-full">{subject}</span>
      
      <div className="relative flex-shrink-0 w-10 h-10">
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
        
        <div className="absolute inset-0 flex items-center justify-center">
          <span className="text-xs font-bold text-gray-800">
            {normalizedMasteryLevel}
          </span>
        </div>
      </div>
    </div>
  );
};