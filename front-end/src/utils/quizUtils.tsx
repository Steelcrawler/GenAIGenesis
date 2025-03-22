import { QuizConfig, Question, QuizResult } from "@/types/quiz";
  
  // Calculate results
  export const calculateResults = (questions: Question[], timeTaken: number): QuizResult => {
    const correctAnswers = questions.filter(question => {
      return question?.isCorrect;
    }).length;
    
    return {
      totalQuestions: questions.length,
      correctAnswers,
      timeTaken
    };
  };
  
  // Check if an answer is correct
  export const isAnswerCorrect = (question: Question, selectedOptionId: string): boolean => {
    return question.isCorrect || false;
  };
  
  // Get default quiz config
  export const getDefaultQuizConfig = (): QuizConfig => {
    return {
      length: 5,
      optionsPerQuestion: 4
    };
  };
  