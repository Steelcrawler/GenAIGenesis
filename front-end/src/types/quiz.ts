
import { v4 as uuidv4 } from 'uuid';

type QuestionType = 'SHORT_ANSWER' | 'MULTIPLE_ANSWER' | 'MULTIPLE_CHOICE';

interface Question {
  id: string;
  question: string;
  type: QuestionType;
  choices?: string[];
  correctChoices?: number[];
  correctShortAnswer?: string;
  attemptedChoices?: number[];
  attemptedShortAnswer?: string;
  isCorrect?: boolean;
  quizId: string;
  snippetId?: string;
}

// Utility functions

/**
 * Converts a JSON object to a Question object.
 */
const fromJson = (json: any): Question => {
  return {
    id: json.id || uuidv4(),
    question: json.question,
    type: json.type as QuestionType,
    choices: json.choices ? json.choices.split(';;/;;') : undefined,
    correctChoices: json.correct_choices ? json.correct_choices.split(',').map(Number) : undefined,
    correctShortAnswer: json.correct_short_answer,
    attemptedChoices: json.attempted_choices ? json.attempted_choices.split(',').map(Number) : undefined,
    attemptedShortAnswer: json.attempted_short_answer,
    isCorrect: json.is_correct ?? null,
    quizId: json.quiz,
    snippetId: json.snippet || undefined,
  };
};

/**
 * Converts a Question object to a JSON-compatible format.
 */
const toJson = (question: Question): any => {
  return {
    id: question.id,
    question: question.question,
    type: question.type,
    choices: question.choices ? question.choices.join(';;/;;') : null,
    correct_choices: question.correctChoices ? question.correctChoices.join(',') : null,
    correct_short_answer: question.correctShortAnswer || null,
    attempted_choices: question.attemptedChoices ? question.attemptedChoices.join(',') : null,
    attempted_short_answer: question.attemptedShortAnswer || null,
    is_correct: question.isCorrect ?? null,
    quiz: question.quizId,
    snippet: question.snippetId || null,
  };
};

export { type Question, fromJson, toJson };


export interface QuizConfig {
  length: number;
  optionsPerQuestion: number;
}

export interface QuizResult {
  totalQuestions: number;
  correctAnswers: number;
  timeTaken: number; // in seconds
}
