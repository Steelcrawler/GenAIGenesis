'use client'

import React, { useState, useEffect, useCallback, use } from 'react';
import { useRouter } from 'next/navigation';
import Navbar from '@/components/quiz/Navbar';
import QuizQuestion from '@/components/quiz/QuizQuestion';
import ProgressBar from '@/components/quiz/ProgressBar';
import AnimatedTransition from '@/components/quiz/AnimatedTransition';
import { QuizResult } from '@/types/quiz';
import { calculateResults } from '@/utils/quizUtils';
import { Clock } from 'lucide-react';
import { useQuestions, Question } from '@/context/QuestionContext';
import { useQuizzes } from '@/context/QuizViewContext';

const Quiz = () => {
  const router = useRouter();
  const [questions, setQuestions] = useState<Question[]>([]);
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [startTime, setStartTime] = useState<number>(Date.now());
  const [elapsed, setElapsed] = useState<number>(0);
  const [isLoading, setIsLoading] = useState(true);
  const [isAnimating, setIsAnimating] = useState(false);
  const allQuestions = useQuestions().questions;
  const { currentQuiz } = useQuizzes();

  // Initialize quiz
  useEffect(() => {
    const initQuiz = () => {
      console.log(currentQuiz);
      if (!currentQuiz) {
        console.log("Current quiz is not set!");
        return;
      }

      setQuestions(allQuestions ? 
        allQuestions
          .filter(question => question.quiz_id == currentQuiz.id!)
        : [])
      console.log(allQuestions && allQuestions
        .filter(question => question.quiz_id == currentQuiz.id!))
    };

    // Initialize with a small delay for loading animation
    const timer = setTimeout(initQuiz, 500);
    setIsLoading(false);
    return () => clearTimeout(timer);
  }, []);

  // Timer effect
  useEffect(() => {
    if (isLoading) return;
    
    const timer = setInterval(() => {
      setElapsed(Math.floor((Date.now() - startTime) / 1000));
    }, 1000);
    
    return () => clearInterval(timer);
  }, [startTime, isLoading]);

  // Handle answer submission
  const handleAnswerSubmit = useCallback(() => {
    
    // Animation between questions
    setIsAnimating(true);
    setTimeout(() => {
      setCurrentQuestionIndex(prevIndex => {
        if (prevIndex + 1 >= questions.length) {
          // Quiz completed, calculate results and navigate
          const totalTime = Math.floor((Date.now() - startTime) / 1000);
          const result: QuizResult = calculateResults(questions, totalTime);
          // TODO save result in backend
          router.push("/quiz-results");
          return prevIndex;
        }
        return prevIndex + 1;
      });
      setIsAnimating(false);
    }, 500);
  }, [questions, router, startTime]);

  // Format time
  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  return (
    <div className="min-h-screen flex flex-col">
      <Navbar />
      
      <main className="flex-1 py-6">
        <div className="container-fluid">
          {isLoading ? (
            <div className="flex items-center justify-center h-64">
              <div className="animate-pulse text-center">
                <p className="text-muted-foreground">Loading quiz...</p>
              </div>
            </div>
          ) : (
            <>
              <div className="mb-8">
                <div className="flex justify-between items-center mb-4">
                  <div>
                    <span className="text-xs font-medium text-muted-foreground">
                      Question {currentQuestionIndex + 1} of {questions.length}
                    </span>
                  </div>
                  <div className="flex items-center">
                    <Clock size={14} className="mr-1 text-muted-foreground" />
                    <span className="text-xs font-medium text-muted-foreground">
                      {formatTime(elapsed)}
                    </span>
                  </div>
                </div>
                <ProgressBar 
                  value={currentQuestionIndex + 1} 
                  max={questions.length} 
                />
              </div>
              
              <AnimatedTransition 
                show={!isAnimating} 
                animation="fade" 
                duration={400}
              >
                {questions.length > 0 && currentQuestionIndex < questions.length && (
                  <QuizQuestion 
                    question={questions[currentQuestionIndex]}
                    onAnswerSubmit={handleAnswerSubmit}
                    showFeedback={true}
                  />
                )}
              </AnimatedTransition>
            </>
          )}
        </div>
      </main>
    </div>
  );
};

export default Quiz;
