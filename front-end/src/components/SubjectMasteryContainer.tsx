
import React, {useEffect, useState} from 'react';
import SubjectMasteryTag from './SubjectTag';
import { useSubjects } from '@/context/SubjectContext';

interface SubjectMasteryContainerProps {
    courseId: string;
  }



const SubjectMasteryContainer: React.FC<SubjectMasteryContainerProps> = ({ courseId }) => {
    const { loading, error, getSubjectsByCourse } = useSubjects();
    const [masteryData, setMasteryData] = useState<
    { subject: string; masteryLevel: number }[]
  >([]);

    useEffect(() => {
    const subjects = getSubjectsByCourse(courseId);
    if (subjects.length > 0) {
      const mockData = subjects.map((s) => ({
        subject: s.name,
        masteryLevel: Math.floor(Math.random() * 101),
      }));
      setMasteryData(mockData);
    }
  }, [courseId, getSubjectsByCourse]);

  if (loading) return <p>Loading subjects...</p>;
  if (error) return <p className="text-destructive">{error}</p>;

  return (
    <div className="space-y-4">
      <h2 className="text-xl font-medium mb-2">Subject Mastery Tags</h2>
      <div className="flex flex-wrap gap-3">
        {masteryData.map(({ subject, masteryLevel }, index) => (
          <SubjectMasteryTag
            key={index}
            subject={subject}
            masteryLevel={masteryLevel}
          />
        ))}
      </div>
    </div>
  );
  };
  
  export default SubjectMasteryContainer;