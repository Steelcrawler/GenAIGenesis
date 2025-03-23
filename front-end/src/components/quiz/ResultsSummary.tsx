
import React from 'react';
import { QuizResult } from '@/types/quiz';
import Button from './Button';
import Link from 'next/link';
import { ArrowLeft, Award } from 'lucide-react';

interface ResultsSummaryProps {
  result: QuizResult;
  onRetry: () => void;
}

const ResultsSummary: React.FC<ResultsSummaryProps> = ({ result, onRetry }) => {
  const percentage = Math.round((result.correctAnswers / result.totalQuestions) * 100);
  
  let performance = "Try again!";
  let color = "text-red-500";
  
  if (percentage >= 80) {
    performance = "Excellent!";
    color = "text-green-500";
  } else if (percentage >= 60) {
    performance = "Good job!";
    color = "text-blue-500";
  } else if (percentage >= 40) {
    performance = "Keep practicing!";
    color = "text-amber-500";
  }

  return (
    <div className="w-full max-w-md mx-auto">
      <div className="text-center">
        <div className="mb-6 flex justify-center">
          <div className="rounded-full p-4 bg-primary/10 text-primary">
            <Award size={40} />
          </div>
        </div>
        
        <h2 className="text-2xl font-semibold mb-1">Quiz Completed!</h2>
        <p className={`text-lg font-medium ${color} mb-6`}>{performance}</p>
        
        <div className="glass rounded-2xl p-6 mb-8">
          <div className="flex justify-between mb-4">
            <div className="text-left">
              <p className="text-sm text-muted-foreground">Score</p>
              <p className="text-2xl font-semibold">{percentage}%</p>
            </div>
          </div>
          
          <div className="bg-secondary rounded-lg p-4 flex justify-between">
            <p className="text-sm">Correct answers</p>
            <p className="text-sm font-medium">{result.correctAnswers} / {result.totalQuestions}</p>
          </div>
        </div>
        
        <div className="flex flex-col gap-3">
          <Button onClick={onRetry}>Try Again</Button>
          <Link href="/courses">
            <Button variant="outline" className="w-full" icon={<ArrowLeft size={16} />}>
              Back to Home
            </Button>
          </Link>
        </div>
      </div>
    </div>
  );
};

export default ResultsSummary;
