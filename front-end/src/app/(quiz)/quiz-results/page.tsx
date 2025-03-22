'use client'

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Navbar from '@/components/quiz/Navbar';
import ResultsSummary from '@/components/quiz/ResultsSummary';
import AnimatedTransition from '@/components/quiz/AnimatedTransition';
import { QuizResult } from '@/types/quiz';
import { getDefaultQuizConfig } from '@/utils/quizUtils';

const Results = () => {
  const router = useRouter();
  const [result, setResult] = useState<QuizResult | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const loadResults = () => {
      try {
        // Get result from backend
        const savedResult = {
            totalQuestions: 10,
            correctAnswers: 8,
            timeTaken: 100,
        }; // TODO
        if (!savedResult) {
          // No results found, redirect to home
          router.push("/courses")
          return;
        }
        
        setResult(savedResult);
        setIsLoading(false);
      } catch (error) {
        console.error('Error loading results:', error);
        router.push("/courses")
      }
    };

    // Load with small delay for animation
    const timer = setTimeout(loadResults, 500);
    return () => clearTimeout(timer);
  }, []);

  const handleRetry = () => {
    // Navigate to quiz page
    router.push('/quiz-config');
  };

  return (
    <div className="min-h-screen flex flex-col">
      <Navbar />
      
      <main className="flex-1 py-10">
        <div className="container-fluid">
          {isLoading ? (
            <div className="flex items-center justify-center h-64">
              <div className="animate-pulse text-center">
                <p className="text-muted-foreground">Loading results...</p>
              </div>
            </div>
          ) : (
            <AnimatedTransition show={true} animation="scale">
              {result && <ResultsSummary result={result} onRetry={handleRetry} />}
            </AnimatedTransition>
          )}
        </div>
      </main>
    </div>
  );
};

export default Results;
