import React, { useState, useEffect } from 'react';
import type { QuizConfig } from '@/types/quiz';
import Button from './Button';
import { useCourses, ClassMaterial } from '@/context/CourseContext';
import { useCurrentCourse } from '@/context/CurrentCourseContext';

interface pdfObject {
    label: string;
    id: string;
}

export interface courseObject {
    label: string;
    id: string;
    pdfs: pdfObject[]
}

interface QuizConfigProps {
    defaultConfig: QuizConfig;
    onConfigSubmit: (config: QuizConfig) => void;
    handleCancel: () => void;
}

const QuizConfig: React.FC<QuizConfigProps> = ({ defaultConfig, onConfigSubmit, handleCancel }) => {
  const { getCourse, courses } = useCourses();
  const { currentCourseId } = useCurrentCourse();
  const [config, setConfig] = useState<QuizConfig>(defaultConfig);
  const [selectedCourseId, setSelectedCourseId] = useState<string | null>(null);
  const [options, setOptions] = useState<ClassMaterial[]>([]);
  const [selectedDocumentIds, setSelectedDocumentIds] = useState<string[]>([]);

  useEffect(() => {
    if (!currentCourseId) {
      return;
    }

    setSelectedCourseId(currentCourseId);
    console.log(selectedCourseId)
    const courseDocs = selectedCourseId ? getCourse(selectedCourseId)?.material || [] : []
    console.log(getCourse(selectedCourseId || ""))
    setOptions(courseDocs);
    setSelectedDocumentIds([]);
  }, [])

  const handleSelectedCourseChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    setSelectedCourseId(e.target.value);
    const courseDocs = selectedCourseId ? getCourse(selectedCourseId)?.material || [] : []
    setOptions(courseDocs);
    setSelectedDocumentIds([]);
  };

  const handleDocumentChange = (documentId: string) => {
    setSelectedDocumentIds(prev => {
      if (prev.includes(documentId)) {
        // Remove if already selected
        return prev.filter(id => id !== documentId);
      } else {
        // Add if not selected
        return [...prev, documentId];
      }
    });
  };

  const handleSelectAllDocuments = () => {
    if (options.length > 0 && selectedDocumentIds.length === options.length) {
      // If all are selected, deselect all
      setSelectedDocumentIds([]);
    } else {
      // Otherwise select all
      setSelectedDocumentIds(options?.map(doc => doc.id!) || []);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setConfig(prev => ({
      ...prev,
      [name]: parseInt(value, 10)
    }));
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    // Update config with selected documents before submitting
    const updatedConfig = {
      ...config,
      selectedCourse: selectedCourseId,
      selectedDocuments: selectedDocumentIds
    };
    onConfigSubmit(updatedConfig);
  };

  return (
    <div className="w-full max-w-md mx-auto">
      <div className="space-y-6">
        <div className="space-y-4">
          <div>
            <label htmlFor="length" className="block text-sm font-medium mb-1">
              Number of Questions
            </label>
            <div className="mt-1">
              <input
                id="length"
                name="length"
                type="range"
                min="3"
                max="10"
                value={config.length}
                onChange={handleChange}
                className="w-full h-2 bg-secondary rounded-lg appearance-none cursor-pointer"
              />
              <div className="flex justify-between mt-2 text-xs text-muted-foreground">
                <span>3</span>
                <span>{config.length}</span>
                <span>10</span>
              </div>
            </div>
          </div>

          {/* Course dropdown */}
          <div className="mb-6">
            <p className="block text-sm font-medium mb-1">Please select a course:</p>
            <div className="flex space-x-4">
              <select 
                value={selectedCourseId || ''} 
                onChange={handleSelectedCourseChange}
                className="w-full p-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="">-- Select a course --</option>
                {courses && courses.map((option) => (
                  <option key={option.id} value={option.id}>
                    {option.name}
                  </option>
                ))}
              </select>
            </div>
          </div>
          
          {/* Document selection with checkboxes */}
          <div className="mb-6">
            <label className="block text-sm font-medium mb-1">Select your materials:</label>
            {selectedCourseId && (
              <div className="border rounded-md p-3 max-h-60 overflow-y-auto">
                <div className="mb-2 flex items-center">
                  <input
                    type="checkbox"
                    id="select-all-documents"
                    checked={options.length > 0 && selectedDocumentIds.length === options.length}
                    onChange={handleSelectAllDocuments}
                    className="mr-2 h-4 w-4"
                  />
                  <label htmlFor="select-all-documents" className="text-sm">
                    Select All
                  </label>
                </div>
                
                {options.length > 0 ? (
                  options.map((doc) => (
                    <div key={doc.id} className="flex items-center mb-2">
                      <input
                        type="checkbox"
                        id={`doc-${doc.id}`}
                        checked={selectedDocumentIds.includes(doc.id!)}
                        onChange={() => handleDocumentChange(doc.id!)}
                        className="mr-2 h-4 w-4"
                      />
                      <label htmlFor={`doc-${doc.id}`} className="text-sm">
                        {doc.file_name}
                      </label>
                    </div>
                  ))
                ) : (
                  selectedCourseId && <p className="text-sm text-gray-500">No documents available for this course</p>
                )}
                
                {!selectedCourseId && <p className="text-sm text-gray-500">Please select a course first</p>}
              </div>
            )}
            {selectedDocumentIds.length > 0 && (
              <p className="mt-2 text-sm text-green-600">
                {selectedDocumentIds.length} document{selectedDocumentIds.length !== 1 ? 's' : ''} selected
              </p>
            )}
          </div>

          <div>
            <label htmlFor="optionsPerQuestion" className="block text-sm font-medium mb-1">
              Options per Question
            </label>
            <div className="mt-1">
              <input
                id="optionsPerQuestion"
                name="optionsPerQuestion"
                type="range"
                min="2"
                max="4"
                value={config.optionsPerQuestion}
                onChange={handleChange}
                className="w-full h-2 bg-secondary rounded-lg appearance-none cursor-pointer"
              />
              <div className="flex justify-between mt-2 text-xs text-muted-foreground">
                <span>2</span>
                <span>{config.optionsPerQuestion}</span>
                <span>4</span>
              </div>
            </div>
          </div>
        </div>

        <div className="flex gap-8 pt-4">
          <Button 
            type="button" 
            className="w-full"
            onClick={handleCancel}
          >
            Cancel
          </Button>
          <Button 
            type="submit" 
            className="w-full"
            onClick={handleSubmit}
            disabled={!selectedCourseId || selectedDocumentIds.length === 0}
          >
            Start Quiz
          </Button>
        </div>
      </div>
    </div>
  );
};

export default QuizConfig;