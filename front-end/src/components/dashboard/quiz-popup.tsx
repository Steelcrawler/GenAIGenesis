import React, { useState } from 'react';

interface OptionObject {
  label: string;
  value: number;
}

interface QuizPopupProps {
  handleCancel: () => void;
  courseOptions: OptionObject[];
  pdfOptions: OptionObject[];
}


export default function QuizPopup({ handleCancel, courseOptions, pdfOptions } : QuizPopupProps ) {
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null);
  const [selectedOption, setSelectedOption] = useState<string>('');

  const handleSubmit = () => {
    if (!selectedCategory || !selectedOption) {
      alert('Please select both a category and the material before submitting.');
      return;
    }
  };

  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-gray-100 p-4">
      <div className="fixed inset-0 flex items-center justify-center z-50">
        {/* Backdrop */}
        <div 
          className="absolute inset-0 bg-black bg-opacity-50"
          onClick={() => handleCancel()}
        ></div>
        
        {/* Modal content */}
        <div className="bg-white rounded-lg shadow-lg p-6 max-w-md w-full z-10">
          <h2 className="text-xl font-bold mb-4">Select Quiz Category</h2>
          
          {/* Options selection */}
          <div className="mb-6">
            <p className="font-medium mb-2">Please select one quiz category:</p>
            <div className="flex space-x-4">
              <label className="flex items-center space-x-2 cursor-pointer">
                <input 
                  type="radio" 
                  name="quizOption" 
                  checked={selectedCategory === 'course'}
                  onChange={() => setSelectedCategory('course')}
                  className="h-4 w-4 text-blue-600"
                />
                <span>Course</span>
              </label>
              <label className="flex items-center space-x-2 cursor-pointer">
                <input 
                  type="radio" 
                  name="quizOption" 
                  checked={selectedCategory === 'pdf'}
                  onChange={() => setSelectedCategory('pdf')}
                  className="h-4 w-4 text-blue-600"
                />
                <span>PDF</span>
              </label>
            </div>
          </div>
          
          {/* Class dropdown */}
          <div className="mb-6">
            <label className="block font-medium mb-2">Select your material:</label>
            <select 
              value={selectedOption} 
              onChange={(e) => setSelectedOption(e.target.value)}
              className="w-full p-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="">-- Select a class --</option>
              {pdfOptions && selectedCategory === "pdf" && pdfOptions.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
              {courseOptions && selectedCategory === "course" && courseOptions.map((option) => (
                <option key={option.value} value={option.value}>
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