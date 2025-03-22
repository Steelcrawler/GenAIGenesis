import React, { useState } from 'react';
import { useRouter } from 'next/navigation';

interface pdfObject {
  label: string;
  id: string;
}

export interface courseObject {
  label: string;
  id: string;
  pdfs: pdfObject[]
}

export interface QuizPopupProps {
  handleCancel: () => void;
  courses: courseObject[];
}

export default function QuizPopup({ handleCancel, courses } : QuizPopupProps ) {
  const [selectedCourse, setSelectedCourse] = useState<string | null>(null);
  const [selectedOption, setSelectedOption] = useState<string>('');
  const router = useRouter();

  const handleSubmit = () => {
    if (!selectedCourse || !selectedOption) {
      alert('Please select both a category and the material before submitting.');
      return;
    }

    router.push("/quiz/0")
  };

  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-gray-100 p-4">
      <div className="fixed inset-0 flex items-center justify-center z-50">
        {/* Backdrop */}
        <div 
          className="absolute inset-0 bg-black bg-opacity-50"
          onClick={() => handleCancel()}
        ></div>
        
        <div className="bg-white rounded-lg shadow-lg p-6 max-w-md w-full z-10">
          <h2 className="text-xl font-bold mb-4">Select Course</h2>
          
          {/* Course dropdown */}
          <div className="mb-6">
            <p className="font-medium mb-2">Please select a course:</p>
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
            <label className="block font-medium mb-2">Select your material:</label>
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
          
          {/* Buttons */}
          <div className="flex justify-end space-x-3">
            <button 
              onClick={() => handleCancel()}
              className="px-4 py-2 border border-gray-300 rounded-md hover:bg-gray-100"
            >
              Cancel
            </button>
            <button 
              onClick={handleSubmit}
              className="px-4 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              Submit
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};