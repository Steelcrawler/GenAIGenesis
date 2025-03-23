
"use client";

import React, {
  createContext,
  useContext,
  useState,
  useEffect,
  ReactNode,
} from "react";

import { apiService } from '@/services/api';

const API_URL = "http://localhost:8000/api";

export type ClassMaterial = {
  id?: string;
  file_name: string;
  local_file?: File;
  custom_name?: string;
  course: string;
  weight?: number;
  created_at?: string;
};

type MaterialContextType = {
  materials: ClassMaterial[];
  searchTerm: string;
  loading: boolean;
  error: string | null;
  
  setSearchTerm: (value: string) => void;
  getMaterial: (id: string) => ClassMaterial | undefined;
  getMaterialsByCourse: (courseId: string) => ClassMaterial[];
  createMaterial: (materialData: ClassMaterial, courseId: string) => Promise<ClassMaterial | null>;
  deleteMaterial: (id: string) => Promise<boolean>;
  refreshMaterials: () => Promise<void>;
};

const MaterialContext = createContext<MaterialContextType | undefined>(undefined);

export const MaterialProvider: React.FC<{ children: ReactNode, onMaterialChange?:() => void }> = ({
  children, onMaterialChange
}) => {
  const [materials, setMaterials] = useState<ClassMaterial[]>([]);
  const [materialTest, setMaterialTest] = useState<ClassMaterial>();
  const [searchTerm, setSearchTerm] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  //const { refreshCourses } = useCourses();


  const refreshMaterials = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const { data } = await apiService.get(`${API_URL}/materials/`);
      console.log('materialTest: ', data);
      setMaterials(Array.isArray(data['class_materials']) ? data['class_materials'] : []);
      //const response = await apiService.get(`${API_URL}/materials/b65b6f8177da4d128668210f6b4b1cb6/`);
      //console.log('materialTest: ', response.data);
    } catch (err) {
      setError("Failed to fetch materials. Please try again.");
      console.error("Error fetching materials:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    refreshMaterials();
  }, []);

  

  const getMaterial = (id: string) => materials.find((m) => m.id === id);
  
  const getMaterialsByCourse = (courseId: string) => 
    materials.filter(m => m.course === courseId);

  const createMaterial = async (
    materialData: ClassMaterial, courseId: string
  ): Promise<ClassMaterial | null> => {
    setLoading(true);
    setError(null);
    
    try {
      const formData = new FormData();
      formData.append("material", JSON.stringify(materialData));
      formData.append("course_id", courseId);
      
      if (materialData.local_file) {
        formData.append("file", materialData.local_file);
      }
      
      const { data } = await apiService.uploadFile(`${API_URL}/materials/`, formData);
      const newMaterial: ClassMaterial = data.class_material;
      
      setMaterials(prev => Array.isArray(prev) ? [...prev, newMaterial] : [newMaterial]);
      
      //await refreshCourses();
      
      return newMaterial;
    } catch (err) {
      setError("Failed to create material. Please try again.");
      console.error("Error creating material:", err);
      return null;
    } finally {
      setLoading(false);
    }
  };

  const deleteMaterial = async (id: string): Promise<boolean> => {
    setLoading(true);
    setError(null);
    
    try {
      await apiService.delete(`${API_URL}/materials/${id}/`);
      
      setMaterials(prev => prev.filter(m => m.id !== id));
      
      //await refreshCourses();
      
      return true;
    } catch (err) {
      setError("Failed to delete material. Please try again.");
      console.error("Error deleting material:", err);
      return false;
    } finally {
      setLoading(false);
    }
  };

  return (
    <MaterialContext.Provider
      value={{
        materials,
        
        searchTerm,
        loading,
        error,
        setSearchTerm,
        getMaterial,
        getMaterialsByCourse,
        createMaterial,
        deleteMaterial,
        refreshMaterials,
      }}
    >
      {children}
    </MaterialContext.Provider>
  );
};

export const useMaterials = () => {
  const context = useContext(MaterialContext);
  if (!context) {
    throw new Error("useMaterials must be used within a MaterialProvider");
  }
  return context;
};
