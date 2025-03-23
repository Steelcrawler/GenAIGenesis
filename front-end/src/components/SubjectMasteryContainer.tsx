import React, { useEffect, useState } from 'react';
import SubjectMasteryTag from './SubjectTag';
import SnippetContainer from './SnippetContainer';
import { useSubjects, Subject } from '@/context/SubjectContext';
import { useMaterialSnippets, MaterialSnippet } from '@/context/MaterialSnippetContext';

interface SubjectMasteryContainerProps {
    courseId: string;
  }



const SubjectMasteryContainer: React.FC<SubjectMasteryContainerProps> = ({ courseId }) => {
    const { loading, error, getSubjectsByCourse } = useSubjects();
    const { getSnippetsBySubject } = useMaterialSnippets();
    
  const [masteryData, setMasteryData] = useState<
    { subject: string; subjectId: string; masteryLevel: number }[]
  >([]);

  const [selectedSubjectId, setSelectedSubjectId] = useState<string | null>(null);
  const [selectedSubjectName, setSelectedSubjectName] = useState<string>('');
  const [snippets, setSnippets] = useState<MaterialSnippet[]>([]);

    useEffect(() => {
    const subjects = getSubjectsByCourse(courseId);
    if (subjects.length > 0) {
      const mockData = subjects.map((s) => ({
        subject: s.name,
        subjectId: s.id,
        masteryLevel: s.mastery,
      }));
      setMasteryData(mockData);
    }
  }, [courseId, getSubjectsByCourse]);

  if (loading) return <p>Loading subjects...</p>;
  if (error) return <p className="text-destructive">{error}</p>;

  const handleSubjectClick = (subjectId: string) => {
    const subject = masteryData.find(item => item.subjectId === subjectId);
    
    if (selectedSubjectId === subjectId) {
      setSelectedSubjectId(null);
      setSnippets([]);
    } else {
      setSelectedSubjectId(subjectId);
      if (subject) {
        setSelectedSubjectName(subject.subject);
      }
      const subjectSnippets = getSnippetsBySubject(subjectId);
      console.log("SNIPPETS : ", subjectSnippets);
      setSnippets(subjectSnippets);
    }
  };

  const handleCloseSnippets = () => {
    setSelectedSubjectId(null);
    setSnippets([]);
  };

  return (
    <div className="space-y-4">
      <h2 className="text-xl font-medium mb-2">Subject Mastery Tags</h2>
      <div className="flex flex-wrap gap-3">
        {masteryData.map(({ subject, subjectId ,masteryLevel }, index) => (
          <SubjectMasteryTag
            key={index}
            subject={subject}
            subjectId={subjectId}
            onClick={handleSubjectClick}
            masteryLevel={masteryLevel}
          />
        ))}
      </div>

      {selectedSubjectId && snippets.length > 0 && (
      <SnippetContainer 
        snippets={snippets}
        onClose={handleCloseSnippets}
        subjectName={selectedSubjectName}
      />
    )}
    </div>

    
  );
  };
  
  export default SubjectMasteryContainer;