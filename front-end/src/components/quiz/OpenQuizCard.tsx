// File: components/quiz/OpenQuizCard.tsx
'use client';

import React from "react";
import { useRouter } from "next/navigation";
import { Quiz } from "@/context/QuizViewContext";
import { useCourses } from "@/context/CourseContext";
import { useQuizzes } from "@/context/QuizViewContext"; // Import the hook for quiz context
import { Card } from "@/components/ui/card"; // assuming you have a Card component
import { cn } from "@/lib/utils";

interface OpenQuizCardProps {
  quiz: Quiz;
}

const OpenQuizCard: React.FC<OpenQuizCardProps> = ({ quiz }) => {
  const router = useRouter();
  const { getCourse } = useCourses();
  const { setCurrentQuiz } = useQuizzes(); // Get setter for current quiz

  // Look up course details using the course id from the quiz.
  const course = getCourse(quiz.course);
  
  // Set the current quiz and navigate to its page.
  const handleClick = () => {
    setCurrentQuiz(quiz); // Set the current quiz in context
    router.push(`/quiz`);
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

export default OpenQuizCard;
