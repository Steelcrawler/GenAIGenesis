// File: app/quiz-history/[id]/page.tsx
'use client';

import React, { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import Layout from '@/components/Layout';
import Link from 'next/link';
import { format } from 'date-fns';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Info } from 'lucide-react';
import { useQuizzes } from '@/context/QuizViewContext';
import { useQuestions } from '@/context/QuestionContext';
import SnippetContainer from '@/components/SnippetContainer';

// Helper: Determine performance message and color based on percentage.
const getPerformanceInfo = (percentage: number) => {
  if (percentage >= 80) {
    return { message: "Excellent!", color: "text-green-500" };
  } else if (percentage >= 60) {
    return { message: "Good job!", color: "text-blue-500" };
  } else if (percentage >= 40) {
    return { message: "Keep practicing!", color: "text-amber-500" };
  } else {
    return { message: "Try again!", color: "text-red-500" };
  }
};

// Component to render a single question result.
type QuestionResultItemProps = {
  question: any; // Replace with your proper Question type if available.
  // If the question is linked to a snippet, we simulate a snippet object.
  snippet?: { id: string; class_material: string; subject: string; snippet: string };
};

const QuestionResultItem: React.FC<QuestionResultItemProps> = ({ question, snippet }) => {
  const [showSnippet, setShowSnippet] = useState(false);

  return (
    <Card className="mb-4 p-4">
      <div className="flex justify-between items-center">
        <h4 className="font-semibold">{question.question}</h4>
        {snippet && (
          <div className="relative">
            <button
              onMouseEnter={() => setShowSnippet(true)}
              onMouseLeave={() => setShowSnippet(false)}
              className="text-muted-foreground"
              title="View snippet"
            >
              <Info size={20} />
            </button>
            {showSnippet && (
              <div className="absolute z-10 top-full left-0 mt-2 w-64">
                <SnippetContainer
                  snippets={[snippet]}
                  subjectName={snippet.subject} // Pass the subject as the title.
                  onClose={() => setShowSnippet(false)}
                />
              </div>
            )}
          </div>
        )}
      </div>
      <div className="mt-2">
        <p>
          <span className="font-medium">Your answer: </span>
          {question.attempted_single_choice !== null ? question.attempted_single_choice : "No answer"}
        </p>
        <p>
          <span className="font-medium">Correct answer: </span>
          {question.single_correct_choice !== null ? question.single_correct_choice : "N/A"}
        </p>
      </div>
    </Card>
  );
};

export default function QuizHistoryPage() {
  const params = useParams();
  const router = useRouter();
  const { id } = params as { id: string };
  const { getQuiz } = useQuizzes();
  const { questions } = useQuestions();

  // Retrieve the quiz from the Quiz context.
  const quiz = getQuiz(id);

  // Fallback: Quiz not found.
  if (!quiz) {
    return (
      <Layout>
        <div className="container mx-auto px-4 py-12 text-center">
          <h2>Quiz not found.</h2>
          <Link href="/courses">
            <Button>Back to Courses</Button>
          </Link>
        </div>
      </Layout>
    );
  }

  // Redirect to /courses if quiz is incomplete.
  useEffect(() => {
    if (!quiz.completed_at) {
      router.push("/courses");
    }
  }, [quiz, router]);

  // Filter questions belonging to this quiz.
  // Note: Make sure the filtering field matches your Question model. (I adjusted it from q.quiz to q.quiz_id if needed.)
  const quizQuestions = questions ? questions.filter(q => q.quiz === quiz.id) : [];
  const totalQuestions = quizQuestions.length;
  const correctAnswers = quizQuestions.filter(q => q.is_correct).length;
  const percentage = totalQuestions > 0 ? Math.round((correctAnswers / totalQuestions) * 100) : 0;
  const { message, color } = getPerformanceInfo(percentage);

  return (
    <Layout>
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="mb-8 text-center">
          <h1 className="text-4xl font-bold">{quiz.name || "Untitled Quiz"}</h1>
          <p className="mt-2 text-muted-foreground">
            Created: {quiz.created_at ? format(new Date(quiz.created_at), "MMM d, yyyy") : "N/A"} | Completed: {quiz.completed_at ? format(new Date(quiz.completed_at), "MMM d, yyyy") : "N/A"}
          </p>
        </div>
        
        {/* Grade Section */}
        <div className="mb-8 text-center">
          <div className={`text-6xl font-extrabold ${color}`}>{percentage}%</div>
          <div className="mt-2 text-xl font-semibold">{message}</div>
        </div>

        {/* Questions List */}
        <div className="space-y-4">
          {quizQuestions.map((question) => {
            // If the question has a snippet, simulate a snippet object matching MaterialSnippet.
            const snippet = question.snippet_id
              ? { 
                  id: question.snippet_id, 
                  class_material: "dummy_material", // Replace with actual material ID if available.
                  subject: "Example Subject",         // Replace with actual subject name if available.
                  snippet: "This is the snippet content for the question." 
                }
              : undefined;
            return (
              <QuestionResultItem key={question.id} question={question} snippet={snippet} />
            );
          })}
        </div>

        {/* Back Button */}
        <div className="mt-8 text-center">
          <Link href="/courses">
            <Button>Back to Courses</Button>
          </Link>
        </div>
      </div>
    </Layout>
  );
}
