
import React from 'react';
import SubjectMasteryTag from './SubjectTag';

const SubjectMasteryContainer = () => {
    // TODO: get subjects
    const subjects = [
        {
            subject: "Math",
            masteryLevel: 100
        },
        {
            subject: "CS",
            masteryLevel: 80
        },
        {
            subject: "English",
            masteryLevel: 30
        },
    ]

    return (
      <div className="space-y-4">
        <h2 className="text-xl font-medium mb-2">Subject Mastery Tags</h2>
        <div className="flex flex-wrap gap-3">
            {subjects && subjects.length > 0 && subjects.map(({ subject, masteryLevel }, index) => {
                return (<SubjectMasteryTag key={index} subject={subject} masteryLevel={masteryLevel} />)
            })}
        </div>
      </div>
    );
  };
  
  export default SubjectMasteryContainer;