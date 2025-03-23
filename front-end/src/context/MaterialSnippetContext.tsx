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

export type MaterialSnippet = {
  id: string;
  class_material: string;
  subject: string | null;
  snippet: string;
};

type MaterialSnippetContextType = {
  snippets: MaterialSnippet[];
  loading: boolean;
  error: string | null;

refreshSnippets: () => Promise<void>;
getSnippet: (id: string) => MaterialSnippet | undefined;
getSnippetsByMaterial: (materialId: string) => MaterialSnippet[];
getSnippetsBySubject: (subjectId: string) => MaterialSnippet[];
  
};

const MaterialSnippetContext = createContext<MaterialSnippetContextType | undefined>(undefined);

export const MaterialSnippetProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [snippets, setSnippets] = useState<MaterialSnippet[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const refreshSnippets = async () => {
    setLoading(true);
    setError(null);

    try {
      const { data } = await apiService.get(`${API_URL}/snippets/`);
      if (Array.isArray(data.material_snippets)) {
        console.log("FETCH SNIPPETS !!!! : ", data.material_snippets);
        setSnippets(data.material_snippets);
      } else {
        setSnippets([]);
      }

      console.log("SNIPPET DATA : ", data);


    } catch (err) {
      setError("Failed to fetch material snippets.");
      console.error("Error fetching material snippets:", err);
    } finally {
      setLoading(false);
    }
  };


  const getSnippet = (id: string) => snippets.find((snip) => snip.id === id);

  const getSnippetsByMaterial = (materialId: string) =>
    snippets.filter((snip) => snip.class_material === materialId);

  const getSnippetsBySubject = (subjectId: string) =>
    snippets.filter((snip) => snip.subject === subjectId);

  useEffect(() => {
    refreshSnippets();
  }, []);

  return (
    <MaterialSnippetContext.Provider
      value={{
        snippets,
        loading,
        error,
        refreshSnippets,
        getSnippet,
        getSnippetsByMaterial,
        getSnippetsBySubject
      }}
    >
      {children}
    </MaterialSnippetContext.Provider>
  );
};

export const useMaterialSnippets = () => {
  const context = useContext(MaterialSnippetContext);
  if (!context) {
    throw new Error("useMaterialSnippets must be used within a MaterialSnippetProvider");
  }
  return context;
};
