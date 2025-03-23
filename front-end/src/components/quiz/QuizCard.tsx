// File: components/quiz/QuizCard.tsx
'use client';

import React from "react";
import { useRouter } from "next/navigation";
import { Quiz } from "@/context/QuizViewContext";
import { useCourses } from "@/context/CourseContext";
import { useQuizzes } from "@/context/QuizViewContext"; // Hook for quiz context
import { Card } from "@/components/ui/card"; // Your card component
import { cn } from "@/lib/utils";

interface QuizCardProps {
  quiz: Quiz;
  courseOverride?: any; // Optionally pass a course directly (or type as Course if available)
}

const QuizCard: React.FC<QuizCardProps> = ({ quiz, courseOverride }) => {
  const router = useRouter();
  const { getCourse } = useCourses();
  const { setCurrentQuiz } = useQuizzes();

  // Use the override if provided; otherwise, lookup using quiz.course.
  const course = courseOverride || getCourse(quiz.course);

  // Determine if the quiz is completed (e.g. by checking if completed_at is set)
  const isCompleted = !!quiz.completed_at;

  const handleClick = () => {
    if (isCompleted) {
      // For completed quizzes, navigate to a view quiz page (placeholder)
      router.push(`/view-quiz/${quiz.id}`);
    } else {
      // For open quizzes, set as current and navigate to active quiz page
      setCurrentQuiz(quiz);
      router.push(`/quiz`);
    }
  };

  return (
    <Card
      onClick={handleClick}
      className={cn("cursor-pointer p-4 hover:shadow-lg transition-shadow")}
    >
      <div className="flex justify-between items-center mb-2">
        <strong className="text-sm">
          Class: {course ? course.name : "Unknown"}
        </strong>
        <span className="text-xs text-muted-foreground">
          {quiz.quiz_length} Questions
        </span>
      </div>
      <h3 className="text-lg font-medium">
        {quiz.name || "Untitled Quiz"}
      </h3>
    </Card>
  );
};

export default QuizCard;
