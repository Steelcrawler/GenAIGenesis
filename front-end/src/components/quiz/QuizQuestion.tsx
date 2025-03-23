
import React, { use, useState } from 'react';
import type { Question } from '@/context/QuestionContext';
import Button from './Button';
import AnimatedTransition from './AnimatedTransition';
import { cn } from '@/lib/utils';

interface QuizQuestionProps {
  question: Question;
  onAnswerSubmit: (index: number) => void;
  showFeedback?: boolean;
}

const QuizQuestion: React.FC<QuizQuestionProps> = ({ 
  question, 
  onAnswerSubmit,
  showFeedback = false,
}) => {
  const [selectedOption, setSelectedOption] = useState<string | null>(null);
  const [correctOption, setCorrectOption] = useState<string | null>(null);
  const [isSubmitted, setIsSubmitted] = useState(false);

  const handleOptionSelect = (optionId: string) => {
    if (isSubmitted) return;
    setSelectedOption(optionId);
  };

  const isCorrectOption = (optionId: string, question: Question): boolean => {
    if (!selectedOption || !correctOption) {
      return false;
    }

    return selectedOption === correctOption;
  }

  const handleSubmit = () => {
    if (!selectedOption || isSubmitted) return;
    
    setIsSubmitted(true);
    const index = question.choices.indexOf(selectedOption);
    
    // Wait for animation if showing feedback
    setTimeout(() => {
      onAnswerSubmit(index);
    }, showFeedback ? 1000 : 0);
    setIsSubmitted(false)
  };

  const getOptionClassName = (optionId: string) => {
    const baseClasses = "flex items-center p-4 border rounded-xl transition-all duration-200";
    
    if (!isSubmitted) {
      return cn(
        baseClasses,
        selectedOption === optionId 
          ? "border-primary bg-primary/5" 
          : "border-border hover:border-primary/30 hover:bg-secondary"
      );
    }
    
    if (showFeedback) {
      if (isCorrectOption(optionId, question)) {
        return cn(baseClasses, "border-green-500 bg-green-50 text-green-700");
      }
      if (optionId === selectedOption) {
        return cn(baseClasses, "border-red-500 bg-red-50 text-red-700");
      }
    }
    
    return cn(baseClasses, "border-border opacity-50");
  };

  return (
    <div className="w-full max-w-lg mx-auto space-y-6">
      <h3 className="text-xl font-medium text-center leading-tight tracking-tight">
        {question.question}
      </h3>
      
      <div className="space-y-3 mt-6">
        {question.choices && question.choices.map((option) => (
          <AnimatedTransition
            key={option}
            show={true}
            animation="scale"
            className="w-full"
          >
            <button
              type="button"
              onClick={() => handleOptionSelect(option)}
              className={getOptionClassName(option)}
              disabled={isSubmitted}
            >
              <div className="mr-3 flex-shrink-0 w-5 h-5 rounded-full border border-current flex items-center justify-center">
                {selectedOption === option && (
                  <div className="w-3 h-3 rounded-full bg-primary" />
                )}
                {isSubmitted && showFeedback && isCorrectOption(option, question) && (
                  <div className="w-3 h-3 rounded-full bg-green-500" />
                )}
              </div>
              <span className="flex-1 text-left">{option}</span>
            </button>
          </AnimatedTransition>
        ))}
      </div>
      
      <div className="pt-4">
        <Button
          onClick={handleSubmit}
          disabled={!selectedOption || isSubmitted}
          className="w-full"
        >
          {isSubmitted ? "Next Question" : "Submit Answer"}
        </Button>
      </div>
    </div>
  );
};

export default QuizQuestion;
