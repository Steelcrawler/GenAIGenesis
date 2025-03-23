"use client";

import React from "react";
import { MaterialProvider } from "@/context/ClassMaterialContext";
import { CourseProvider } from "@/context/CourseContext";
import { QuizProvider } from "@/context/QuizViewContext";
import { CurrentCourseProvider } from "@/context/CurrentCourseContext";
import { QuestionProvider } from "@/context/QuestionContext";
import { SubjectProvider } from "@/context/SubjectContext";
import { ResponseProvider } from "@/context/ResponseContext"

export const SyncedProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <ResponseProvider>
    <QuestionProvider>
      <CurrentCourseProvider>
        <QuizProvider>
          <MaterialProvider>
            <CourseProvider>
              <SubjectProvider>
                {children}
              </SubjectProvider>
            </CourseProvider>
          </MaterialProvider>
        </QuizProvider>
      </CurrentCourseProvider>
    </QuestionProvider>
  </ResponseProvider>
);
