import { QuizConfig, QuizResult } from "@/types/quiz";
import { Question } from "@/context/QuestionContext";
  
  // Calculate results
  export const calculateResults = (questions: Question[], timeTaken: number): QuizResult => {
    const correctAnswers = questions.filter(question => {
      return question?.is_correct!;
    }).length;
    
    return {
      totalQuestions: questions.length,
      correctAnswers,
      timeTaken
    };
  };
  
  // Check if an answer is correct
  export const isAnswerCorrect = (question: Question, selectedOptionId: string): boolean => {
    return question.is_correct || false;
  };
  
  // Get default quiz config
  export const getDefaultQuizConfig = (): QuizConfig => {
    return {
      length: 20,
      optionsPerQuestion: 4,
      course: "",
      subjects: [],
      materials: [],
    };
  };
  