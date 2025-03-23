'use client';

import React, { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import Navbar from '@/components/quiz/Navbar';
import QuizConfig from '@/components/quiz/QuizConfig';
import { QuizConfig as QuizConfigType } from '@/types/quiz';
import { getDefaultQuizConfig } from '@/utils/quizUtils';
import { Brain } from 'lucide-react';
import { courseObject } from "@/components/quiz-popup"
import AnimatedTransition from '@/components/quiz/AnimatedTransition';

const Index = () => {
  const router = useRouter();
  const [course, setCourse] = useState<string | undefined>();
  const [courses, setCourses] = useState<courseObject[]>([]);

  useEffect(() => {
    const getCourses = () => {
      try {
        // TODO: Make API call
        setCourses([])
        // TODO: Get default course if any
      } catch (error) {
        console.error('Error initializing quiz:', error);
        // Handle error
      }
    };

    // Initialize with a small delay for loading animation
    const timer = setTimeout(getCourses, 500);
    return () => clearTimeout(timer);
  }, [])

  const handleCancel = () => {
    router.back()
  }
  
  const handleStartQuiz = (config: QuizConfigType) => {
    // TODO: push quiz config

    router.push('/quiz');
  };

  return (
    <div className="min-h-screen flex flex-col">
      <Navbar />
      
      <main className="flex-1 py-10">
        <div className="container-fluid max-w-3xl mx-auto">
          <AnimatedTransition show={true} animation="slide">
            <div className="text-center mb-10">
              <div className="inline-flex rounded-full bg-primary/10 p-2 mb-4">
                <div className="rounded-full bg-primary/20 p-2 text-primary">
                  <Brain size={24} />
                </div>
              </div>
              <h1 className="text-4xl font-bold mb-3 tracking-tight">QuizCraft</h1>
              <p className="text-lg text-muted-foreground max-w-xl mx-auto text-balance">
                Create and take personalized quizzes with customizable length and options. 
                Test your knowledge on a variety of topics.
              </p>
            </div>
          </AnimatedTransition>

          <AnimatedTransition show={true} animation="scale" className="mt-6">
            <div className="glass rounded-2xl p-8 shadow-sm">
              <h2 className="text-xl font-semibold mb-6 text-center">Customize Your Quiz</h2>
              <QuizConfig 
                defaultConfig={getDefaultQuizConfig()} 
                onConfigSubmit={handleStartQuiz} 
                handleCancel={handleCancel}
              />
            </div>
          </AnimatedTransition>
        </div>
      </main>
    </div>
  );
};

export default Index;
