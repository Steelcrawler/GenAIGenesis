"use client";

import React, {
  createContext,
  useContext,
  useState,
  useEffect,
  ReactNode,
} from "react";

import { useAuth } from '@/context/AuthContext';

export type ClassMaterial = {
  id?: string;
  file_name: string;
  local_file?: File;
  custom_name?: string;
  course: string;
  weight?: number;
  created_at?: string;
};

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
  setSearchTerm: (value: string) => void;

  getCourse: (id: string) => Course | undefined;
  addCourse: (courseData: Omit<Course, "id">) => Promise<Course | null>;
  updateCourse: (id: string, courseData: Partial<Course>) => Promise<void>;
  deleteCourse: (id: string) => Promise<void>;

  createMaterial: (materialData: ClassMaterial, courseId: string) => Promise<void>;
};

const CourseContext = createContext<CourseContextType | undefined>(undefined);

async function apiFetch(url: string, options: RequestInit = {}) {
  const finalOptions: RequestInit = {
    ...options,
    credentials: "include",
    headers: {
      "Content-Type": "application/json",
      ...(options.headers || {}),
    },
  };
  return fetch(url, finalOptions);
}

export const CourseProvider: React.FC<{ children: ReactNode }> = ({
  children,
}) => {
  const [courses, setCourses] = useState<Course[]>([]);
  const [searchTerm, setSearchTerm] = useState("");
  const authState = useAuth();

  useEffect(() => {
    (async () => {
      try {
        const res = await apiFetch("http://localhost:8000/api/courses/");
        if (!res.ok) {
          console.log("Failed to fetch courses");
          return;
        }
        const data = await res.json();
        console.log("courses", data);
        setCourses(Array.isArray(data) ? data : data.courses || []);
      } catch (error) {
        console.error("Error fetching courses:", error);
      }
    })();
  }, []);

  const filteredCourses = courses.filter(
    (c) =>
      c.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      c.description.toLowerCase().includes(searchTerm.
      toLowerCase())
  );

  const getCourse = (id: string) => courses.find((c) => c.id === id);


  const addCourse = async (courseData: Omit<Course, "id">) => {
    
    const material = courseData.material;
    if(authState.userId){
      courseData = {
        ...courseData,
        user: String(authState.userId),
      };
    }
    console.log("courseData", courseData);

    try {
      const res = await apiFetch("http://localhost:8000/api/courses/", {
        method: "POST",
        body: JSON.stringify(courseData),
      });
      if (!res.ok) {
        console.error("Failed to create course");
        return null;
      }
      const data = await res.json();
      const newCourse: Course = data.course;

      console.log("new course", newCourse);
      console.log("material", material);

      if (material && material.length > 0) {
        for (const mat of material) {
          console.log("creating material", mat);

          await createMaterial(
            mat,
            newCourse.id
          );
        }
      }

      setCourses((prev) => [newCourse, ...prev]);
      return newCourse;
    } catch (error) {
      console.error("Error creating course:", error);
      return null;
    }
  };

  const updateCourse = async (id: string, courseData: Partial<Course>) => {
    const material = courseData.material;
    try {
      const res = await apiFetch(`http://localhost:8000/api/courses/${id}/`, {
        method: "PUT",
        body: JSON.stringify(courseData),
      });
      if (!res.ok) {
        console.log("Failed to update course");
        return;
      }
      const data = await res.json();
      console.log("updated course", data);
      const updated: Course = data.course;

      if (material && material.length > 0) {
        for (const mat of material) {
          console.log("creating material", mat);

          await createMaterial(
            mat,
            updated.id
          );
        }
      }

      setCourses((prev) =>
        prev.map((c) => (c.id === id ? { ...c, ...updated } : c))
      );
    } catch (error) {
      console.error("Error updating course:", error);
    }
  };

  const deleteCourse = async (id: string) => {
    try {
      const res = await apiFetch(`http://localhost:8000/api/courses/${id}/`, {
        method: "DELETE",
      });
      if (!res.ok) {
        console.error("Failed to delete course");
        return;
      }
      setCourses((prev) => prev.filter((c) => c.id !== id));
    } catch (error) {
      console.error("Error deleting course:", error);
    }
  };

  const createMaterial = async (
    materialData: ClassMaterial, course: string
  ) => {
    try {
      const formData = new FormData();
      formData.append("material", JSON.stringify(materialData));
      formData.append("course_id", course);
      formData.append("file", materialData.local_file!);
      console.log("creating material", materialData);
      const res = await fetch("http://localhost:8000/api/materials/", {
        method: "POST",
        credentials: "include",
        body: formData,
      });      
      if (!res.ok) {
        const body = await res.json()
        console.error("Failed to create material: ", body);	
        return;
      }
      const data = await res.json();
      const newMaterial: ClassMaterial = data.class_material;
      const courseId = newMaterial.course;

      setCourses((prev) =>
        prev.map((course) => {
          if (course.id === courseId) {
            const oldMats = course.material || [];
            return {
              ...course,
              material: [...oldMats, newMaterial],
            };
          }
          return course;
        })
      );
    } catch (error) {
      console.error("Error creating material:", error);
    }
  };

  return (
    <CourseContext.Provider
      value={{
        courses,
        filteredCourses,
        searchTerm,
        setSearchTerm,
        getCourse,
        addCourse,
        updateCourse,
        deleteCourse,
        createMaterial,
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
