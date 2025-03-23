// File: components/OpenQuizList.tsx
import React from "react";
import { useQuizzes } from "@/context/QuizViewContext";
import OpenQuizCard from "./OpenQuizCard";

const OpenQuizList: React.FC = () => {
  const { getOpenQuizzes } = useQuizzes();
  const openQuizzes = getOpenQuizzes();

  if (openQuizzes.length === 0) {
    return <p className="text-muted-foreground">No open quizzes available.</p>;
  }

  return (
    <div className="space-y-4">
      <h2 className="text-xl font-bold mb-2">Open Quizzes</h2>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {openQuizzes.map((quiz) => (
          <OpenQuizCard key={quiz.id} quiz={quiz} />
        ))}
      </div>
    </div>
  );
};

export default OpenQuizList;
