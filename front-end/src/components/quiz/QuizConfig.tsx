
import React, { useState } from 'react';
import type { QuizConfig } from '@/types/quiz';
import Button from './Button';

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
    courses: courseObject[];
}

const QuizConfig: React.FC<QuizConfigProps> = ({ defaultConfig, onConfigSubmit, handleCancel, courses }) => {
  const [config, setConfig] = useState<QuizConfig>(defaultConfig);
  const [selectedCourse, setSelectedCourse] = useState<string | null>(null);
  const [selectedOption, setSelectedOption] = useState<string>('');

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setConfig(prev => ({
      ...prev,
      [name]: parseInt(value, 10)
    }));
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onConfigSubmit(config);
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
                    value={selectedCourse || ''} 
                    onChange={(e) => setSelectedCourse(e.target.value)}
                    className="w-full p-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                    <option value="">-- Select a course --</option>
                    {courses && courses.map((option) => (
                    <option key={option.id} value={option.id}>
                        {option.label}
                    </option>
                    ))}
                </select>
                </div>
            </div>
          
            {/* Document dropdown */}
            <div className="mb-6">
                <label className="block text-sm font-medium mb-1">Select your material:</label>
                <select 
                value={selectedOption} 
                onChange={(e) => setSelectedOption(e.target.value)}
                className="w-full p-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                <option value="all">All course documents</option>
                {selectedCourse && courses && courses.filter((option) => option.id === selectedCourse)[0].pdfs?.map((option) => (
                    <option key={option.id} value={option.id}>
                    {option.label}
                    </option>
                ))}
                </select>
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

        <div className="flex gap-8 pt-4">
          <Button 
            type="submit" 
            className="w-full"
            onClick={handleCancel}
          >
            Cancel
          </Button>
          <Button 
            type="submit" 
            className="w-full"
            onClick={handleSubmit}
          >
            Start Quiz
          </Button>
        </div>
      </div>
    </div>
    </div>
  );
};

export default QuizConfig;
