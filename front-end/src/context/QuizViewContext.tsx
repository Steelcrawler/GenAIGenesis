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
import { QuestionType, useQuestions } from "@/context/QuestionContext";
import { Response } from "./ResponseContext";

type QuizSubmission = {
  id: string;
  responses: Response[];
};

type FakeQuestion = {
  id: string;
  quiz_id: string;
  question: string;
  type: QuestionType;
  choices: string;
  single_correct_choice: number | null;
  correct_choices: number | null;
  correct_short_answer: string | null;
  attempted_single_choice: number | null;
  attempted_choices: string | null;
  attempted_short_answer: string | null;
  is_correct: boolean | null;
  snippet_id: string | null;
};

const API_URL = "http://localhost:8000/api";

export type Quiz = {
  id?: string;
  user?: string;
  name?: string;
  course: string;
  subjects: string[];
  materials: string[];
  completed_at?: string | null;
  created_at?: string;
  optimize_learning?: boolean;
  optionsPerQuestion: number;
  quiz_length: number;
};

type QuizContextType = {
  quizzes: Quiz[] | null;

  currentQuiz: Quiz | null;
  setCurrentQuiz: (quiz: Quiz) => void;
  
  getQuiz: (id: string) => Quiz | undefined;
  createQuiz: (quizData: Omit<Quiz, "id">) => Promise<Quiz | null>;
  submitQuiz: ({id, responses}: QuizSubmission) => Promise<Quiz | null>;
  
  getOpenQuizzes: () => Quiz[];
};

const QuizContext = createContext<QuizContextType | undefined>(undefined);

export const QuizProvider: React.FC<{ children: ReactNode }> = ({
  children,
}) => {
  const [quizzes, setQuizzes] = useState<Quiz[] | null>(null);
  const [currentQuiz, setCurrentQuiz] = useState<Quiz | null>(null);
  const authState = useAuth();
  const { updateQuestions } = useQuestions();

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
      const questions = data.questions.map((question: FakeQuestion) => {
        return ({ 
          ...question, 
          choices: question.choices.split(';;/;;')
        })
      });
      updateQuestions(questions);
      setCurrentQuiz(newQuiz);

      setQuizzes((prev) => Array.isArray(prev) ? [newQuiz, ...prev] : [newQuiz]);

      return newQuiz;
    } catch (err) {
      console.error("Error creating quiz:", err);
      return null;
    }
  };

  const submitQuiz = async ({id, responses}: QuizSubmission) => {
    try {
      const finalData = authState.userId
        ? { questions: [...responses] }
        : responses;
      console.log(responses)
        
      const { data } = await apiService.patch(`${API_URL}/quizzes/${id}/submit/`, finalData);
      const updatedQuiz: Quiz = data.quiz;
      const questions = data.questions.map((question: FakeQuestion) => {
        return ({ 
          ...question, 
          choices: question.choices.split(';;/;;')
        })
      });
      updateQuestions(questions);
      setCurrentQuiz(updatedQuiz);
      setQuizzes(prevQuizzes => {
        const filteredQuizzes = prevQuizzes?.filter(quiz => quiz.id! !== updatedQuiz.id!);
        return filteredQuizzes ? [...filteredQuizzes, updatedQuiz] : [updatedQuiz];
      })
      return updatedQuiz;
    } catch (err) {
      console.error("Error updating quiz:", err);
      return null;
    }
  }

  const getOpenQuizzes = () => {
    return quizzes ? quizzes.filter(q => !q.completed_at) : [];
  };

  return (
    <QuizContext.Provider
      value={{
        quizzes,
        currentQuiz,
        setCurrentQuiz,
        getQuiz,
        createQuiz,
        submitQuiz,
        getOpenQuizzes,
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
