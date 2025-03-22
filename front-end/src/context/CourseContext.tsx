"use client";

import React, { createContext, useContext, useState, useEffect } from "react";
import { v4 as uuidv4 } from "uuid";

export type CourseFile = {
  id: string;
  fileName: string;
  dataUrl: string;
}


export type Course = {
  id: string;
  name: string;
  description: string;
  imageUrl?: string;
  files?: CourseFile[];
  createdAt: Date;
  updatedAt: Date;
};

type CourseContextType = {
  courses: Course[];
  searchTerm: string;
  setSearchTerm: (term: string) => void;
  filteredCourses: Course[];
  getCourse: (id: string) => Course | undefined;
  addCourse: (course: Omit<Course, "id" | "createdAt" | "updatedAt">) => void;
  updateCourse: (
    id: string,
    courseData: Partial<Omit<Course, "id" | "createdAt" | "updatedAt">>
  ) => void;
  deleteCourse: (id: string) => void;
};

const CourseContext = createContext<CourseContextType | undefined>(undefined);

/**
 * Stable "seed" data for initial SSR render
 * (Use consistent IDs to avoid mismatches)
 */
const initialCourses: Course[] = [
  {
    id: "intro-design",
    name: "Introduction to Design Principles",
    description:
      "Learn the foundational principles of design thinking and application.",
    imageUrl:
      "https://images.unsplash.com/photo-1516383740770-fbcc5ccbece0?q=80&w=1974&auto=format&fit=crop",
    createdAt: new Date(),
    updatedAt: new Date(),
  },
  {
    id: "js-concepts",
    name: "Advanced JavaScript Concepts",
    description:
      "Dive deep into JavaScript with topics like closures, prototypes, and async programming.",
    imageUrl:
      "https://images.unsplash.com/photo-1627398242454-45a1465c2479?q=80&w=2074&auto=format&fit=crop",
    createdAt: new Date(),
    updatedAt: new Date(),
  },
  {
    id: "typography",
    name: "Mastering Typography",
    description: "Explore the art and science of typography for digital and print media.",
    imageUrl:
      "https://images.unsplash.com/photo-1523726491678-bf852e717f6a?q=80&w=1170&auto=format&fit=crop",
    createdAt: new Date(),
    updatedAt: new Date(),
  },
];

export const CourseProvider: React.FC<{ children: React.ReactNode }> = ({
  children,
}) => {
  /**
   * 1) Initialize state with stable `initialCourses` for SSR.
   *    This ensures the server always renders the same IDs.
   */
  const [courses, setCourses] = useState<Course[]>(initialCourses);

  /**
   * 2) Once on the client, load from localStorage if available
   *    and replace the default state.
   */
  useEffect(() => {
    const saved = localStorage.getItem("courses");
    if (saved) {
      try {
        const parsed = JSON.parse(saved) as Course[];
        setCourses(parsed);
      } catch {
        // If parsing fails, just keep initialCourses
      }
    }
  }, []);

  // Search term for filtering
  const [searchTerm, setSearchTerm] = useState("");

  /**
   * 3) Whenever `courses` changes, save to localStorage
   *    (client-only; won't run on the server).
   */
  useEffect(() => {
    localStorage.setItem("courses", JSON.stringify(courses));
  }, [courses]);

  // Filter courses based on search term
  const filteredCourses = courses.filter(
    (course) =>
      course.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      course.description.toLowerCase().includes(searchTerm.toLowerCase())
  );

  // Get a single course by ID
  const getCourse = (id: string) => courses.find((course) => course.id === id);

  // Add a new course (generates a UUID only on the client)
  const addCourse = (
    courseData: Omit<Course, "id" | "createdAt" | "updatedAt">
  ) => {
    const newCourse: Course = {
      ...courseData,
      id: uuidv4(),
      createdAt: new Date(),
      updatedAt: new Date(),
    };
    setCourses((prev) => [newCourse, ...prev]);
  };

  // Update an existing course
  const updateCourse = (
    id: string,
    partialData: Partial<Omit<Course, "id" | "createdAt" | "updatedAt">>
  ) => {
    setCourses((prev) =>
      prev.map((course) =>
        course.id === id
          ? { ...course, ...partialData, updatedAt: new Date() }
          : course
      )
    );
  };

  // Delete a course
  const deleteCourse = (id: string) => {
    setCourses((prev) => prev.filter((course) => course.id !== id));
  };

  return (
    <CourseContext.Provider
      value={{
        courses,
        searchTerm,
        setSearchTerm,
        filteredCourses,
        getCourse,
        addCourse,
        updateCourse,
        deleteCourse,
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

export const getFile = (fileId: string) => {
  const { courses } = useCourses();
  for (const course of courses) {
    if (course.files && course.files.length > 0) {
      const foundFile = course.files.find(file => file.id === fileId);
      if (foundFile) {
        return foundFile;
      }
    }
  }

  return undefined;
}

export const getCourseId = (fileId: string) => {
  const { courses } = useCourses();
  const course = courses.find(course => course.files && course.files.find((file) => file.id == fileId))
  if (course) {
    return course.id;
  }

  return undefined;
}
