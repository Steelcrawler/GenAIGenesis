"use client";

import React from "react";
import { MaterialProvider } from "@/context/ClassMaterialContext";
import { CourseProvider } from "@/context/CourseContext";

export const SyncedProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <MaterialProvider>
    <CourseProvider>
      {children}
    </CourseProvider>
  </MaterialProvider>
);
