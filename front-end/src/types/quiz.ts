
export interface QuizConfig {
  length: number;
  optionsPerQuestion: number;
  course: string;
  subjects: string[];
  materials: string[];
}

export interface QuizResult {
  totalQuestions: number;
  correctAnswers: number;
  timeTaken: number; // in seconds
}
