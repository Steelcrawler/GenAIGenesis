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

export type QuestionType = "SHORT_ANSWER" | "MULTIPLE_ANSWER" | "MULTIPLE_CHOICE";

export type Question = {
  id: string;
  quiz: string;
  question: string;
  type: QuestionType;
  choices: string[];
  single_correct_choice: number | null;
  correct_choices: number | null;
  correct_short_answer: string | null;
  attempted_single_choice: number | null;
  attempted_choices: string | null;
  attempted_short_answer: string | null;
  is_correct: boolean | null;
  snippet_id: string | null;
};

type QuestionContextType = {
  questions: Question[] | null;
  
  getQuestion: (id: string) => Question | undefined;
  updateQuestions: (questions: Question[]) => void;
};

const QuestionContext = createContext<QuestionContextType | undefined>(undefined);

export const QuestionProvider: React.FC<{ children: ReactNode }> = ({
  children,
}) => {
  const [questions, setQuestions] = useState<Question[] | null>(null);
  const authState = useAuth();

  const refreshQuestions = async () => {
    if (!authState.loggedIn) return;
  
    try {
      const { data } = await apiService.get(`${API_URL}/questions/`);
      setQuestions(Array.isArray(data.questions) ? data.questions : []);
    } catch (err) {
      console.error("Error fetching questions:", err);
      setQuestions([]);  // Explicitly reset on error
    }
  };

  useEffect(() => {
    refreshQuestions();
  }, [authState.loggedIn]);

  const getQuestion = (id: string) => questions ? questions.find((q) => q.id === id) :  undefined;

  const updateQuestions = (questions: Question[]) => {
    setQuestions(prevQuestions => {
      const filterIds = questions.map(question => question.id!);
      const filteredQuestions = prevQuestions?.filter(question => !filterIds.includes(question.id!));
      return filteredQuestions ? [...filteredQuestions, ...questions] : [...questions];
    });
  }

  return (
    <QuestionContext.Provider
      value={{
        questions,
        getQuestion,
        updateQuestions,
      }}
    >
      {children}
    </QuestionContext.Provider>
  );
};

export const useQuestions = () => {
  const context = useContext(QuestionContext);
  if (!context) {
    throw new Error("useQuestions must be used within a QuestionProvider");
  }
  return context;
};
