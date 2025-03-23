// File: app/quiz-history/[id]/page.tsx
'use client';

import React, { useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import Layout from '@/components/Layout';
import Link from 'next/link';
import { format } from 'date-fns';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { useQuizzes } from '@/context/QuizViewContext';
import { useQuestions } from '@/context/QuestionContext';
import { MaterialSnippet, useMaterialSnippets } from '@/context/MaterialSnippetContext';
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

type QuestionResultItemProps = {
  question: any; // Replace with your proper Question type if available.
  snippet?: MaterialSnippet;
};

const QuestionResultItem: React.FC<QuestionResultItemProps> = ({ question, snippet }) => {
  // Convert choices to an array if needed.
  const choices = Array.isArray(question.choices)
    ? question.choices
    : typeof question.choices === 'string'
      ? question.choices.split(';;/;;')
      : [];

  // Force the snippet: if getSnippet returned nothing, provide a fallback.
  const forcedSnippet: MaterialSnippet | undefined = question.snippet_id
    ? snippet || {
        id: question.snippet_id,
        class_material: "dummy_material",
        subject: "Forced Subject",
        snippet: "Forced snippet content: snippet not available from provider.",
      }
    : undefined;

  return (
    <Card className="mb-4 p-4">
      <h4 className="font-semibold">{question.question}</h4>
      <div className="mt-2">
        <ul className="space-y-2">
          {choices.map((choice: string, index: number) => {
            const isCorrect = question.single_correct_choice === index;
            const isSelected = question.attempted_single_choice === index;
            let choiceClasses = "p-2 border rounded";
            if (isCorrect) choiceClasses += " border-green-500 bg-green-100";
            if (isSelected && !isCorrect) choiceClasses += " border-red-500";
            return (
              <li key={index} className={choiceClasses}>
                {choice}
                {isSelected && (
                  <span className="ml-2 text-sm font-medium text-blue-500">
                    {isCorrect ? "(Your selection, correct)" : "(Your selection)"}
                  </span>
                )}
                {!isSelected && isCorrect && (
                  <span className="ml-2 text-sm font-medium text-green-500">
                    (Correct answer)
                  </span>
                )}
              </li>
            );
          })}
        </ul>
      </div>
      {question.snippet_id && (
        <div className="mt-4">
          <h5 className="text-md font-semibold">Question's source:</h5>
          <SnippetContainer
            snippets={[forcedSnippet!]}
            subjectName={forcedSnippet?.subject || "Source"}
            onClose={() => {}}
          />
        </div>
      )}
    </Card>
  );
};

export default function QuizHistoryPage() {
  const { id } = useParams() as { id: string };
  const router = useRouter();
  const { getQuiz } = useQuizzes();
  const { questions } = useQuestions();
  const { getSnippet } = useMaterialSnippets();

  const quiz = getQuiz(id);
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

  useEffect(() => {
    if (!quiz.completed_at) {
      router.push("/courses");
    }
  }, [quiz, router]);

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
          {quizQuestions.map(question => {
            // Retrieve snippet from provider; if it returns nothing, our fallback in QuestionResultItem will kick in.
            const snippet = question.snippet_id ? getSnippet(question.snippet_id) : undefined;
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
