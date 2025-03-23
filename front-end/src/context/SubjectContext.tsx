"use client";

import React, {
  createContext,
  useContext,
  useEffect,
  useState,
  ReactNode,
} from "react";
import { apiService } from "@/services/api";

const API_URL = "http://localhost:8000/api";

export type Subject = {
  id: string;
  name: string;
  course: string;
  mastery: number;
};

type SubjectContextType = {
  subjects: Subject[];
  loading: boolean;
  error: string | null;

  getSubject: (id: string) => Subject | undefined;
  getSubjectsByCourse: (courseId: string) => Subject[];
  refreshSubjects: (courseId?: string) => Promise<void>;
};

const SubjectContext = createContext<SubjectContextType | undefined>(undefined);

export const SubjectProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [subjects, setSubjects] = useState<Subject[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const refreshSubjects = async (courseId?: string) => {
    setLoading(true);
    setError(null);

    try {
      let url = `${API_URL}/subjects/`;
      if (courseId) {
        url += `?course_id=${courseId}`;
      }

      const { data } = await apiService.get(url);
      console.log("Received following subjects: ",data.subjects)
      setSubjects(Array.isArray(data.subjects) ? data.subjects : []);
    } catch (err) {
      setError("Failed to fetch subjects. Please try again.");
      console.error("Error fetching subjects:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    refreshSubjects();
  }, []);

  const getSubject = (id: string) => subjects.find((s) => s.id === id);

  const getSubjectsByCourse = (courseId: string) =>
    subjects.filter((s) => s.course === courseId);

  return (
    <SubjectContext.Provider
      value={{
        subjects,
        loading,
        error,
        getSubject,
        getSubjectsByCourse,
        refreshSubjects,
      }}
    >
      {children}
    </SubjectContext.Provider>
  );
};

export const useSubjects = () => {
  const context = useContext(SubjectContext);
  if (!context) {
    throw new Error("useSubjects must be used within a SubjectProvider");
  }
  return context;
};
