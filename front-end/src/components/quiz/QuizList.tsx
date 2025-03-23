// File: components/quiz/QuizList.tsx
'use client';

import React from "react";
import { useQuizzes } from "@/context/QuizViewContext";
import QuizCard from "./QuizCard";

interface QuizListProps {
  courseId?: string;        // Only show quizzes for a given course (if provided)
  isCompleted?: boolean;    // Filter by completed (true) or open (false) quizzes
  horizontalScroll?: boolean; // If true, render as a horizontally scrollable list
}

const QuizList: React.FC<QuizListProps> = ({ courseId, isCompleted, horizontalScroll = false }) => {
  const { quizzes } = useQuizzes();

  // Start with all quizzes (or empty array)
  let filteredQuizzes = quizzes ? quizzes : [];

  // Filter by course if provided
  if (courseId) {
    filteredQuizzes = filteredQuizzes.filter(q => q.course === courseId);
  }

  // Filter by completion status if provided
  if (typeof isCompleted === "boolean") {
    filteredQuizzes = filteredQuizzes.filter(q => isCompleted ? !!q.completed_at : !q.completed_at);
  }

  if (filteredQuizzes.length === 0) {
    return (
      <div className="p-4 bg-muted rounded-lg">
        <p className="text-muted-foreground">
          {isCompleted ? "No completed quizzes available." : "No open quizzes available."}
        </p>
      </div>
    );
  }

  const containerClasses = horizontalScroll
    ? "flex space-x-4 overflow-x-auto pb-4"
    : "grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4";

  return (
    <div className={containerClasses}>
      {filteredQuizzes.map((quiz) => (
        <div key={quiz.id} className={horizontalScroll ? "min-w-[250px]" : ""}>
          <QuizCard quiz={quiz} />
        </div>
      ))}
    </div>
  );
};

export default QuizList;
