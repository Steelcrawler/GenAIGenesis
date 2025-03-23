import { createContext, useContext, useState } from 'react';
import { useSession } from 'next-auth/react';

const QuizContext = createContext();

export const QuizProvider = ({ children }) => {
    const { data: session } = useSession();
    const [quizzes, setQuizzes] = useState([]);
    const [questions, setQuestions] = useState([]);
    const [loading, setLoading] = useState(false);
    const API_URL = '/api/quizzes';

    const fetchQuizzes = async (courseId = null) => {
        setLoading(true);
        try {
            const response = await axios.get(API_URL, {
                headers: { Authorization: `Bearer ${session?.user?.token}` },
                params: courseId ? { course_id: courseId } : {},
            });
            setQuizzes(response.data.quizzes);
        } catch (error) {
            console.error('Error fetching quizzes:', error);
        }
        setLoading(false);
    };

    const fetchQuizById = async (quizId) => {
        setLoading(true);
        try {
            const response = await axios.get(`${API_URL}/${quizId}`, {
                headers: { Authorization: `Bearer ${session?.user?.token}` },
            });
            setQuestions(response.data.questions);
            return response.data;
        } catch (error) {
            console.error('Error fetching quiz:', error);
        }
        setLoading(false);
    };

    const createQuiz = async (quizData) => {
        setLoading(true);
        try {
            const response = await axios.post(API_URL, quizData, {
                headers: { Authorization: `Bearer ${session?.user?.token}` },
            });
            setQuizzes([...quizzes, response.data.quiz]);
            return response.data;
        } catch (error) {
            console.error('Error creating quiz:', error);
        }
        setLoading(false);
    };

    return (
        <QuizContext.Provider value={{ quizzes, questions, loading, fetchQuizzes, fetchQuizById, createQuiz }}>
            {children}
        </QuizContext.Provider>
    );
};

export const useQuiz = () => {
    return useContext(QuizContext);
};
