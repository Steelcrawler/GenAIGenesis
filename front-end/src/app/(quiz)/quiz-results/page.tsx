'use client'

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Navbar from '@/components/quiz/Navbar';
import ResultsSummary from '@/components/quiz/ResultsSummary';
import AnimatedTransition from '@/components/quiz/AnimatedTransition';
import { QuizResult } from '@/types/quiz';
import { useCurrentCourse } from '@/context/CurrentCourseContext';
import { useQuestions, Question } from '@/context/QuestionContext';
import { useQuizzes } from '@/context/QuizViewContext';

const Results = () => {
  const router = useRouter();

  const [isLoading, setIsLoading] = useState(true);
  const [results, setResults] = useState<QuizResult | null>(null);
  const { currentCourseId } = useCurrentCourse();
  const { questions } = useQuestions();
  const { currentQuiz } = useQuizzes();

  useEffect(() => {
    if (!currentQuiz) {
      // No results found, redirect to home
      router.push("/courses")
      return;
    }

    const filteredQuestions = questions?.filter(question => question.quiz === currentQuiz.id!) || [];
    const newResults: QuizResult = {
      totalQuestions: filteredQuestions.length,
      correctAnswers: filteredQuestions.filter(question => question.is_correct).length
    };
    setResults(newResults);

    setIsLoading(false);
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
              {results && <ResultsSummary result={results!} onRetry={handleRetry} />}
            </AnimatedTransition>
          )}
        </div>
      </main>
    </div>
  );
};

export default Results;
