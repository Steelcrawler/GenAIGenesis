'use client'

import React, { useState, useEffect, useCallback, use } from 'react';
import { useRouter } from 'next/navigation';
import Navbar from '@/components/quiz/Navbar';
import QuizQuestion from '@/components/quiz/QuizQuestion';
import ProgressBar from '@/components/quiz/ProgressBar';
import AnimatedTransition from '@/components/quiz/AnimatedTransition';
import { Clock } from 'lucide-react';
import { useQuestions, Question } from '@/context/QuestionContext';
import { useQuizzes } from '@/context/QuizViewContext';
import { Response, useResponse } from '@/context/ResponseContext';

const Quiz = () => {
  const router = useRouter();
  const [questions, setQuestions] = useState<Question[]>([]);
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState<number>(0);
  const [startTime, setStartTime] = useState<number>(Date.now());
  const [elapsed, setElapsed] = useState<number>(0);
  const [isLoading, setIsLoading] = useState(true);
  const [isAnimating, setIsAnimating] = useState(false);
  const [responses, setResponses] = useState<Response[]>([]);
  const allQuestions = useQuestions().questions;
  const { currentQuiz, submitQuiz } = useQuizzes();

  // Initialize quiz
  useEffect(() => {
    if (!currentQuiz) {
      router.push("/quiz-config")
      return;
    }

    setQuestions(allQuestions ? 
      allQuestions
        .filter(question => question.quiz == currentQuiz.id!)
      : [])

    // Initialize with a small delay for loading animation
    setIsLoading(false);
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
  async function handleAnswerSubmit(index: number) {
    if (currentQuestionIndex + 1 >= questions.length) {
      // Quiz completed, calculate results and navigate
      await submitQuiz({id: currentQuiz!.id!, responses: [...responses, {id: questions[currentQuestionIndex].id!, single_choice: index}]});
      router.push("/quiz-results");
      return currentQuestionIndex;
    } 

    setIsAnimating(true);
    // Animation between questions
    setTimeout(() => {
      setCurrentQuestionIndex(prevIndex => prevIndex + 1);
      setResponses(prevResponses => 
        [
          ...prevResponses, 
          {id: questions[currentQuestionIndex].id!, single_choice: index}
        ]
      );
    }, 500);
    setIsAnimating(false);
  }

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
                    onAnswerSubmit={(index) => handleAnswerSubmit(index)}
                    showFeedback={false}
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
