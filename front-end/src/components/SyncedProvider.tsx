"use client";

import React from "react";
import { MaterialProvider } from "@/context/ClassMaterialContext";
import { CourseProvider } from "@/context/CourseContext";
import { QuizProvider } from "@/context/QuizViewContext";
import { CurrentCourseProvider } from "@/context/CurrentCourseContext";
import { QuestionProvider } from "@/context/QuestionContext";

export const SyncedProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <QuestionProvider>
    <CurrentCourseProvider>
      <QuizProvider>
        <MaterialProvider>
          <CourseProvider>
            {children}
          </CourseProvider>
        </MaterialProvider>
      </QuizProvider>
    </CurrentCourseProvider>
  </QuestionProvider>
);
