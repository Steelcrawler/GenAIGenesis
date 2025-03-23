"use client";

import React, {
  createContext,
  useContext,
  useState,
  useEffect,
  ReactNode,
} from "react";

import { useAuth } from '@/context/AuthContext';
import { apiService } from '@/services/api';

const API_URL = "http://localhost:8000/api";

export type Quiz = {
  id: string;
  user: string;
  name: string;
  course_id: string;
  subjects: string[];
  materials: string[];
  completed_at: string | null;
  created_at: string;
  optimize_learning: boolean;
  quiz_length: number;
};

type QuizContextType = {
  quizzes: Quiz[] | null;

  currentQuiz: Quiz | null;
  setCurrentQuiz: (quiz: Quiz) => void;
  
  getQuiz: (id: string) => Quiz | undefined;
  createQuiz: (quizData: Omit<Quiz, "id">) => Promise<Quiz | null>;
};

const QuizContext = createContext<QuizContextType | undefined>(undefined);

export const QuizProvider: React.FC<{ children: ReactNode }> = ({
  children,
}) => {
  const [quizzes, setQuizzes] = useState<Quiz[] | null>(null);
  const [currentQuiz, setCurrentQuiz] = useState<Quiz | null>(null);
  const authState = useAuth();

  const refreshQuizzes = async () => {
    if (!authState.loggedIn) return;
  
    try {
      const { data } = await apiService.get(`${API_URL}/quizzes/`);
      setQuizzes(Array.isArray(data.quizzes) ? data.quizzes : []);
    } catch (err) {
      console.error("Error fetching quizzes:", err);
      setQuizzes([]);  // Explicitly reset on error
    }
  };

  useEffect(() => {
    refreshQuizzes();
  }, [authState.loggedIn]);

  const getQuiz = (id: string) => quizzes ? quizzes.find((q) => q.id === id) : undefined;

  const createQuiz = async (quizData: Omit<Quiz, "id">) => {
    try {
      const finalData = authState.userId
        ? { ...quizData, user: String(authState.userId) }
        : quizData;
        
      const { data } = await apiService.post(`${API_URL}/quizzes/`, finalData);
      const newQuiz: Quiz = data.quiz;
      const questions: Question[] = data.questions;
      udpateQuestions(questions);
      setCurrentQuiz(newQuiz);

      setQuizzes((prev) => Array.isArray(prev) ? [newQuiz, ...prev] : [newQuiz]);

      return newQuiz;
    } catch (err) {
      console.error("Error creating quiz:", err);
      return null;
    }
  };

  return (
    <QuizContext.Provider
      value={{
        quizzes,
        currentQuiz,
        setCurrentQuiz,
        getQuiz,
        createQuiz,
      }}
    >
      {children}
    </QuizContext.Provider>
  );
};

export const useQuizzes = () => {
  const context = useContext(QuizContext);
  if (!context) {
    throw new Error("useQuizzes must be used within a QuizProvider");
  }
  return context;
};