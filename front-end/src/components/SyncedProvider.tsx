"use client";

import React from "react";
import { MaterialProvider } from "@/context/ClassMaterialContext";
import { CourseProvider } from "@/context/CourseContext";
import { QuizProvider } from "@/context/QuizViewContext";
import { CurrentCourseProvider } from "@/context/CurrentCourseContext";
import { QuestionProvider } from "@/context/QuestionContext";
import { SubjectProvider } from "@/context/SubjectContext";
<<<<<<< HEAD
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
=======
import {MaterialSnippetProvider} from "@/context/MaterialSnippetContext";

export const SyncedProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <QuestionProvider>
    <CurrentCourseProvider>
      <QuizProvider>
        <MaterialProvider>
          <CourseProvider>
            <SubjectProvider>
              <MaterialSnippetProvider>
                {children}
              </MaterialSnippetProvider>
            </SubjectProvider>
          </CourseProvider>
        </MaterialProvider>
      </QuizProvider>
    </CurrentCourseProvider>
  </QuestionProvider>
>>>>>>> 86d97c45ea815b7bf51b62b423299e9d1bf1af16
);
