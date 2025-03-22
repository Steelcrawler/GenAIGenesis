'use client';

import React, { useState, useRef } from 'react';
import { ClipboardCheck, Search } from 'lucide-react';
import QuizPopup from './quiz-popup';
import { courseObject } from './quiz-popup';
import { useRouter } from 'next/navigation';

interface PDFViewerProps {
  pdfUrl?: string;
  title?: string;
  courses: courseObject[];
  onBack: () => void;
  textToHighlight?: string[]; // Array of strings to highlight
  highlightColor?: string; // Optional color for highlights
}

export default function PDFViewer({ 
  pdfUrl, 
  title, 
  courses, 
  onBack,
  textToHighlight = [], 
  highlightColor = 'rgba(255, 235, 59, 0.5)' // Default yellow highlight with transparency
}: PDFViewerProps) {
  const [isQuizOpen, setIsQuizOpen] = useState<boolean>(false);
  const [isSearchOpen, setIsSearchOpen] = useState<boolean>(false);
  const [searchTerm, setSearchTerm] = useState<string>('');
  const [scale, setScale] = useState<number>(1);
  const containerRef = useRef<HTMLDivElement>(null);
  const [activeHighlights, setActiveHighlights] = useState<string[]>(textToHighlight);
  const router = useRouter();

  const handleQuiz = () => {
    router.push("/quiz-config")
  };

  const toggleSearch = () => {
    setIsSearchOpen(!isSearchOpen);
  };

  // Function to add a new highlight
  const addHighlight = () => {
    if (searchTerm && !activeHighlights.includes(searchTerm)) {
      setActiveHighlights([...activeHighlights, searchTerm]);
    }
  };

  // Function to remove a highlight
  const removeHighlight = (text: string) => {
    setActiveHighlights(activeHighlights.filter(item => item !== text));
  };

  return (
    <div className="flex flex-col h-full w-full bg-gray-100 rounded-lg overflow-hidden">
      {/* Header */}
      <div className="flex justify-between items-center p-4 bg-white border-b border-gray-200">
        <div className="flex items-center gap-3">
          <button 
            onClick={onBack} 
            className="p-2 rounded-full hover:bg-gray-100 transition-colors"
            aria-label="Go back"
          >
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="lucide-arrow-left">
              <path d="m12 19-7-7 7-7"/>
              <path d="M19 12H5"/>
            </svg>
          </button>
          <div className="mx-3 h-6 w-px bg-gray-300"></div>
          <h2 className="text-xl font-semibold truncate">
            {title || 'PDF Document'}
          </h2>
        </div>
        <div className="flex items-center gap-2">
          <button 
            onClick={toggleSearch}
            className="p-2 rounded-full hover:bg-gray-100 transition-colors"
            aria-label="Search in document"
          >
            <Search size={20} />
          </button>
        </div>
      </div>

      {/* Search bar */}
      {isSearchOpen && (
        <div className="p-2 bg-white border-b border-gray-200">
          <div className="flex items-center gap-2">
            <input
              type="text"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder="Enter text to highlight..."
              className="flex-grow p-2 border border-gray-300 rounded"
            />
            <button
              onClick={addHighlight}
              className="px-3 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
            >
              Highlight
            </button>
          </div>
          {activeHighlights.length > 0 && (
            <div className="mt-2">
              <p className="text-sm text-gray-600 mb-1">Active highlights:</p>
              <div className="flex flex-wrap gap-2">
                {activeHighlights.map((text, index) => (
                  <div 
                    key={index} 
                    className="flex items-center gap-1 px-2 py-1 bg-gray-100 rounded"
                    style={{ backgroundColor: highlightColor }}
                  >
                    <span className="text-sm">{text}</span>
                    <button 
                      onClick={() => removeHighlight(text)}
                      className="text-gray-500 hover:text-gray-700"
                    >
                      ×
                    </button>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* PDF Viewer */}
      <div className="relative flex-grow overflow-auto h-full" ref={containerRef}>
        <div 
          className="w-full flex justify-center p-4 h-full"
          style={{
            height: 'calc(100vh - 140px)'
          }}
        >
          {pdfUrl ? (
            <div className="relative w-full h-full">
              <iframe
                src={`${pdfUrl}#view=FitH`}
                className="w-full h-full border-none bg-white shadow-lg"
                title={title || "PDF Viewer"}
                style={{ height: '100%' }}
              />
              {/* Note: The text highlighting would require a PDF.js implementation for actual text selection */}
              {/* This is a simplified approach to demonstrate the UI */}
            </div>
          ) : (
            <div>Could not load PDF</div>
          )}
        </div>
        
        {/* Quiz Button */}
        <button
          onClick={handleQuiz}
          className="absolute bottom-6 right-6 bg-blue-600 text-white p-3 rounded-full shadow-lg hover:bg-blue-700 transition-colors z-10"
          aria-label="Open Quiz"
        >
          <ClipboardCheck size={24} />
        </button>
      </div>

      {isQuizOpen && 
        <QuizPopup 
          handleCancel={() => setIsQuizOpen(false)}
          courses={courses}
        />
      }
    </div>
  );
};