
'use client'

import React, { useState, createContext, ReactNode, useContext } from "react";

type CurrentCourseContextType = {
    currentCourseId: string | null;
    setCurrentCourseId: (id: string) => void 
};

const CurrentCourseContext = createContext<CurrentCourseContextType | undefined>(undefined);

export const CurrentCourseProvider: React.FC<{ children: ReactNode }> = ({
    children,
}) => {
    const [currentCourseId, setCurrentCourseId] = useState<string | null>(null);

    return (
        <CurrentCourseContext.Provider
          value={{
            currentCourseId,
            setCurrentCourseId
          }}
        >
          {children}
        </CurrentCourseContext.Provider>
      );
}

export const useCurrentCourse = () => {
  const context = useContext(CurrentCourseContext);
  if (!context) {
    throw new Error("useCourses must be used within a CourseProvider");
  }
  return context;
};
