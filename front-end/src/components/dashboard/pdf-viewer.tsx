'use client';

import React, { useState, useRef } from 'react';
import { ClipboardCheck } from 'lucide-react';
import QuizPopup from './quiz-popup';

interface OptionObject {
    label: string;
    value: number;
}

interface PDFViewerProps {
  pdfUrl: string;
  title?: string;
  courseOptions: OptionObject[];
  pdfOptions: OptionObject[];
}

export default function PDFViewer({ pdfUrl, title, courseOptions, pdfOptions } : PDFViewerProps) {
  const [isQuizOpen, setIsQuizOpen] = useState<boolean>(false);
  const [selectedCategory, setSelectedCategory] = useState('');
  const [selectedOption, setSelectedOption] = useState('');
  const containerRef = useRef<HTMLDivElement>(null);

  const handleQuizSubmit = () => {
    if (selectedOption) {
      console.log('Submitted option:', selectedOption);
      // Process submission logic here
      setIsQuizOpen(false);
    }
  };

  const handleCategoryChange = (e: any) => {
    setSelectedCategory(e.target.value);
    setSelectedOption('');
  };

  const handleQuiz = () => {
    setIsQuizOpen(!isQuizOpen);
  };

  return (
    <div className="flex flex-col h-full w-full bg-gray-100 rounded-lg overflow-hidden">
      {/* Header */}
      <div className="flex justify-between items-center p-4 bg-white border-b border-gray-200">
        <h2 className="text-xl font-semibold truncate">
          {title || 'PDF Document'}
        </h2>   
      </div>

      {/* PDF Viewer */}
      <div className="relative flex-grow overflow-auto h-full" ref={containerRef}>
        <div 
            className="min-h-full w-full flex justify-center p-4 h-full"
            style={{
                height: 'calc(100vh - 100px)' // Subtract header height (adjust as needed)
            }}
        >
            <iframe
                src={`${pdfUrl}#view=FitH`}
                className="w-full h-full border-none bg-white shadow-lg"
                title={title || "PDF Viewer"}
                style={{ height: '100%' }}
            />
        </div>
        
        {/* Quiz Button (Bottom Right) */}
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
            courseOptions={courseOptions}
            pdfOptions={pdfOptions}
        />
      }
    </div>
  );
};

// Usage example:
// import PDFViewer from '@/components/PDFViewer';
//
// export default function Page() {
//   return (
//     <div className="h-screen p-4">
//       <PDFViewer 
//         pdfUrl="/path-to-your-pdf.pdf" 
//         title="Document Title" 
//       />
//     </div>
//   );
// }