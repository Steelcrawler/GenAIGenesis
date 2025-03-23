"use client";

import React, {
  createContext,
  useContext,
  useState,
  useEffect,
  ReactNode,
} from "react";

import { useAuth } from '@/context/AuthContext';
import { apiService } from '@/services/api';
import { ClassMaterial, useMaterials} from "./ClassMaterialContext";

const API_URL = "http://localhost:8000/api";

export type Course = {
  id: string;
  user?: string;
  name: string;
  description: string;
  icon?: string;
  image_path?: string;
  created_at?: string;
  material?: ClassMaterial[];
};

type CourseContextType = {
  courses: Course[];
  filteredCourses: Course[];
  searchTerm: string;
  loading: boolean;
  error: string | null;
  
  setSearchTerm: (value: string) => void;
  getCourse: (id: string) => Course | undefined;
  addCourse: (courseData: Omit<Course, "id">) => Promise<Course | null>;
  updateCourse: (id: string, courseData: Partial<Course>) => Promise<Course | null>;
  deleteCourse: (id: string) => Promise<boolean>;
  refreshCourses: () => Promise<void>;
};

const CourseContext = createContext<CourseContextType | undefined>(undefined);

export const CourseProvider: React.FC<{ children: ReactNode }> = ({
  children,
}) => {
  const [courses, setCourses] = useState<Course[]>([]);
  const [searchTerm, setSearchTerm] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const authState = useAuth();
  const materialState = useMaterials();

  const refreshCourses = async () => {
    if (!authState.loggedIn) return;
  
    setLoading(true);
    setError(null);
  
    try {
      const { data } = await apiService.get(`${API_URL}/courses/`);
      setCourses(Array.isArray(data.courses) ? data.courses : []);
    } catch (err) {
      setError("Failed to fetch courses. Please try again.");
      console.error("Error fetching courses:", err);
      setCourses([]);  // Explicitly reset on error
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    refreshCourses();
  }, [authState.loggedIn]);

  const filteredCourses = Array.isArray(courses)
  ? courses.filter(
      (c) =>
        c.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        c.description.toLowerCase().includes(searchTerm.toLowerCase())
    )
  : [];

  const getCourse = (id: string) => courses.find((c) => c.id === id);

  const addCourse = async (courseData: Omit<Course, "id">) => {
    setLoading(true);
    setError(null);
    
    try {
      const finalData = authState.userId
        ? { ...courseData, user: String(authState.userId) }
        : courseData;
        
      const { data } = await apiService.post(`${API_URL}/courses/`, finalData);
      const newCourse = data.course;

      const material = courseData.material;
      if (material && material.length > 0) {
        for(const mat of material) {
          materialState.createMaterial(mat, newCourse.id);
          };
        }
      
      
      setCourses((prev) => Array.isArray(prev) ? [newCourse, ...prev] : [newCourse]);

      return newCourse;
    } catch (err) {
      setError("Failed to create course. Please try again.");
      console.error("Error creating course:", err);
      return null;
    } finally {
      setLoading(false);
    }
  };

  const updateCourse = async (id: string, courseData: Partial<Course>) => {
    setLoading(true);
    setError(null);
    
    try {
      const { data } = await apiService.put(`${API_URL}/courses/${id}/`, courseData);
      const updatedCourse = data.course;
      
      setCourses((prev) =>
        prev.map((c) => (c.id === id ? { ...c, ...updatedCourse } : c))
      );
      
      return updatedCourse;
    } catch (err) {
      setError("Failed to update course. Please try again.");
      console.error("Error updating course:", err);
      return null;
    } finally {
      setLoading(false);
    }
  };

  const deleteCourse = async (id: string) => {
    setLoading(true);
    setError(null);
    
    try {
      await apiService.delete(`${API_URL}/courses/${id}/`);
      setCourses((prev) => prev.filter((c) => c.id !== id));
      return true;
    } catch (err) {
      setError("Failed to delete course. Please try again.");
      console.error("Error deleting course:", err);
      return false;
    } finally {
      setLoading(false);
    }
  };

  return (
    <CourseContext.Provider
      value={{
        courses,
        filteredCourses,
        searchTerm,
        loading,
        error,
        setSearchTerm,
        getCourse,
        addCourse,
        updateCourse,
        deleteCourse,
        refreshCourses,
      }}
    >
      {children}
    </CourseContext.Provider>
  );
};

export const useCourses = () => {
  const context = useContext(CourseContext);
  if (!context) {
    throw new Error("useCourses must be used within a CourseProvider");
  }
  return context;
};