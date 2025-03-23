  
  import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
  import { useAuth } from '@/context/AuthContext';
  import { ClassMaterial } from '@/types/classMaterial';
  
  interface ClassMaterialContextType {
    materials: ClassMaterial[];
    courseId: string;
    setCourseId: (value: string) => void;

    addMaterial: (material: Omit<ClassMaterial, 'id' | 'created_at'>) => Promise<ClassMaterial>;
    updateMaterial: (id: string, material: Partial<ClassMaterial>) => Promise<ClassMaterial>;
    deleteMaterial: (id: string) => Promise<void>;
    getMaterialById: (id: string) => ClassMaterial | undefined;
  }
  
  const ClassMaterialContext = createContext<ClassMaterialContextType | undefined>(undefined);
  
  interface ClassMaterialProviderProps {
    children: ReactNode;
    apiUrl?: string;
  }

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
  
  export const ClassMaterialProvider: React.FC<ClassMaterialProviderProps> = ({ 
    children, 
    apiUrl = 'http://localhost:8000/api/' 
  }) => {
    const [materials, setMaterials] = useState<ClassMaterial[]>([]);
    const [courseId, setCourseId] = useState("");
    const authState = useAuth();

    useEffect(() => {
        (async () => {
          try {
            const res = await apiFetch(`${apiUrl}materials/`);
            if (!res.ok) {
              console.log("Failed to fetch course materials");
              return;
            }
            const data = await res.json();
            console.log("course materials", data);
            setMaterials(Array.isArray(data) ? data : data.courses || []);
          } catch (error) {
            console.error("Error fetching course materials:", error);
          }
        })();
      }, []);

        
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

    const addMaterial = async (material: Omit<ClassMaterial, 'id' | 'created_at'>): Promise<ClassMaterial> => {
      try {
        setLoading(true);
        setError(null);
        const response = await axios.post(apiUrl, material);
        const newMaterial = response.data;
        setMaterials(prev => [...prev, newMaterial]);
        return newMaterial;
      } catch (err) {
        setError('Failed to add class material');
        console.error('Error adding material:', err);
        throw err;
      } finally {
        setLoading(false);
      }
    };
  
    const updateMaterial = async (id: string, material: Partial<ClassMaterial>): Promise<ClassMaterial> => {
      try {
        setLoading(true);
        setError(null);
        const response = await axios.patch(`${apiUrl}/${id}`, material);
        const updatedMaterial = response.data;
        setMaterials(prev => 
          prev.map(item => item.id === id ? updatedMaterial : item)
        );
        return updatedMaterial;
      } catch (err) {
        setError('Failed to update class material');
        console.error('Error updating material:', err);
        throw err;
      } finally {
        setLoading(false);
      }
    };
  
    const deleteMaterial = async (id: string): Promise<void> => {
      try {
        setLoading(true);
        setError(null);
        await axios.delete(`${apiUrl}/${id}`);
        setMaterials(prev => prev.filter(item => item.id !== id));
      } catch (err) {
        setError('Failed to delete class material');
        console.error('Error deleting material:', err);
        throw err;
      } finally {
        setLoading(false);
      }
    };
  
    const getMaterialById = (id: string): ClassMaterial | undefined => {
      return materials.find(material => material.id === id);
    };
  
    const value = {
      materials,
      loading,
      error,
      fetchMaterials,
      addMaterial,
      updateMaterial,
      deleteMaterial,
      getMaterialById
    };
  
    return (
      <ClassMaterialContext.Provider value={value}>
        {children}
      </ClassMaterialContext.Provider>
    );
  };
  
  export const useClassMaterial = (): ClassMaterialContextType => {
    const context = useContext(ClassMaterialContext);
    if (context === undefined) {
      throw new Error('useClassMaterial must be used within a ClassMaterialProvider');
    }
    return context;
  };
