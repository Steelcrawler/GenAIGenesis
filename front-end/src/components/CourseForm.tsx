"use client";

import React, { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { z } from "zod";
import { v4 as uuidv4 } from "uuid";
import { useCourses, Course } from "@/context/CourseContext";
import { ClassMaterial } from "@/context/ClassMaterialContext";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { toast } from "sonner";
import { ArrowLeft, Save, Loader2 } from "lucide-react";

const formSchema = z.object({
  name: z.string().min(1, "Course name is required"),
  description: z.string().min(1, "Description is required"),
  image_path: z.string().url("Invalid image URL").optional(),
  material: z
    .array(
      z.object({
        id: z.string(),
        file_name: z.string(),
        local_file: z.instanceof(File),
        course: z.string().default(""),
      })
    )
    .optional(),
});

interface CourseFormProps {
  courseId?: string;
}

const CourseForm: React.FC<CourseFormProps> = ({ courseId }) => {
  const { getCourse, addCourse, updateCourse } = useCourses();
  const router = useRouter();

  const existingCourse = courseId ? getCourse(courseId) : undefined;
  const isEditing = !!existingCourse;

  const [previewImage, setPreviewImage] = useState<string | undefined>(
    existingCourse?.image_path || undefined
  );
  const [imageError, setImageError] = useState(false);

  // État pour stocker les champs du formulaire
  const [formData, setFormData] = useState<Partial<Course>>({
    name: existingCourse?.name || "",
    description: existingCourse?.description || "",
    image_path: existingCourse?.image_path || "",
    material: existingCourse?.material || [],
  });

  useEffect(() => {
    if (formData.image_path) {
      setPreviewImage(formData.image_path);
      setImageError(false);
    } else {
      setPreviewImage(undefined);
    }
  }, [formData.image_path]);

  const handleImageError = () => {
    setImageError(true);
  };

  const [errors, setErrors] = useState<{ [key: string]: string }>({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [showMaterialsLoading, setShowMaterialsLoading] = useState(false);

  // Convertit un fichier en base64 (facultatif selon votre logique)
  const fileToBase64 = (file: File): Promise<string> =>
    new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = () => {
        const result = reader.result as string;
        resolve(result);
      };
      reader.onerror = reject;
      reader.readAsDataURL(file);
    });

  // Gère l'ajout de fichiers
  const handleFilesChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (!e.target.files) return;
    const filesArray = Array.from(e.target.files);

    try {
      const filePromises = filesArray.map(async (file) => {
        await fileToBase64(file); // Conversion en base64 si besoin
        const courseFile: ClassMaterial = {
          id: uuidv4(),
          file_name: file.name,
          local_file: file,
          course: courseId || "",
        };
        return courseFile;
      });

      const uploadedFiles = await Promise.all(filePromises);

      setFormData((prev) => ({
        ...prev,
        material: [...(prev.material || []), ...uploadedFiles],
      }));
    } catch (err) {
      console.error("Error converting file:", err);
      toast.error("Error uploading files");
    }
  };

  // Retire un fichier du tableau
  const handleRemoveFile = (fileId: string) => {
    setFormData((prev) => ({
      ...prev,
      material: prev.material?.filter((f) => f.id !== fileId) ?? [],
    }));
  };

  // Gestion du changement de champ (nom, description, etc.)
  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>
  ) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));

    if (errors[name]) {
      setErrors((prev) => {
        const newErrors = { ...prev };
        delete newErrors[name];
        return newErrors;
      });
    }
  };

  // Soumission du formulaire
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);

    try {
      // Validation via Zod
      const validatedData = formSchema.parse(formData);

      if (isEditing && courseId) {
        // Cas d'édition : on update le cours
        await updateCourse(courseId, validatedData);
        toast.success("Course updated successfully");
        router.push(`/course/${courseId}`);
      } else {
        await addCourse(
          validatedData as Omit<Course, "id" | "created_at">,
          () => setShowMaterialsLoading(true),
          () => setShowMaterialsLoading(false)
        );
        toast.success("Course created successfully");
        router.push("/courses");
      }
    } catch (error) {
      if (error instanceof z.ZodError) {
        const newErrors: { [key: string]: string } = {};
        error.errors.forEach((err) => {
          if (err.path[0]) {
            newErrors[err.path[0] as string] = err.message;
          }
        });
        setErrors(newErrors);
        toast.error("Please correct the form errors");
      } else {
        toast.error("An unexpected error occurred");
        console.error("Form submission error:", error);
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto">
      {/* Bouton "Back" */}
      <Button
        variant="ghost"
        className="mb-6 gap-2"
        onClick={() => router.push("/courses")}
      >
        <ArrowLeft className="h-4 w-4" />
        <span>Back</span>
      </Button>

      <div className="glass p-6 rounded-lg">
        <h1 className="text-2xl font-semibold mb-6">
          {isEditing ? "Edit Course" : "Create New Course"}
        </h1>

        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Nom du cours */}
          <div className="space-y-2">
            <Label htmlFor="name">Course Name</Label>
            <Input
              id="name"
              name="name"
              value={formData.name}
              onChange={handleChange}
              className={errors.name ? "border-destructive" : ""}
              disabled={isSubmitting}
            />
            {errors.name && (
              <p className="text-sm text-destructive">{errors.name}</p>
            )}
          </div>

          {/* Description */}
          <div className="space-y-2">
            <Label htmlFor="description">Description</Label>
            <Textarea
              id="description"
              name="description"
              value={formData.description}
              onChange={handleChange}
              className={errors.description ? "border-destructive" : ""}
              disabled={isSubmitting}
              rows={4}
            />
            {errors.description && (
              <p className="text-sm text-destructive">{errors.description}</p>
            )}
          </div>

          <div className="flex-1 space-y-2">
            <Label htmlFor="image_path">Image URL (Optional)</Label>
            <Input
              id="image_path"
              name="image_path"
              value={formData.image_path || ""}
              onChange={handleChange}
              placeholder="https://example.com/image.jpg"
              disabled={isSubmitting}
            />
            {errors.image_path && (
              <p className="text-sm text-destructive">{errors.image_path}</p>
            )}

            {previewImage && !imageError && (
              <div className="mt-4">
                <p className="text-sm text-muted-foreground mb-2">
                  Image Preview
                </p>
                <div className="relative w-full h-48 rounded-md overflow-hidden border bg-background">
                  <img
                    src={previewImage}
                    alt="Course preview"
                    className="w-full h-full object-cover"
                    onError={handleImageError}
                  />
                </div>
              </div>
            )}
            {imageError && previewImage && (
              <p className="text-sm text-destructive mt-2">
                Failed to load image. Please check the URL and try again.
              </p>
            )}
          </div>

          {!isEditing && (
            <div className="space-y-2">
              <Label htmlFor="files">Upload Files (PDF, images, etc.)</Label>
              <Input
                id="files"
                type="file"
                multiple
                onChange={handleFilesChange}
                disabled={isSubmitting}
              />
              {errors.files && (
                <p className="text-sm text-destructive">{errors.files}</p>
              )}

              {formData.material && formData.material.length > 0 && (
                <ul className="mt-4 space-y-1 text-sm">
                  {formData.material.map((file) => (
                    <li key={file.id} className="flex items-center gap-2">
                      • {file.file_name}
                      <button
                        type="button"
                        onClick={() => handleRemoveFile(file.id!)}
                        className="text-destructive text-xs hover:underline"
                      >
                        Remove
                      </button>
                    </li>
                  ))}
                </ul>
              )}
            </div>
          )}

          <div className="flex justify-end">
            <Button type="submit" disabled={isSubmitting} className="gap-2">
              <Save className="h-4 w-4" />
              <span>{isEditing ? "Update Course" : "Create Course"}</span>
            </Button>
          </div>
        </form>
      </div>

      {showMaterialsLoading && (
        <div className="fixed inset-0 flex items-center justify-center bg-gray-600 bg-opacity-10 z-50">
          <div className="bg-white p-6 rounded shadow-lg flex flex-col items-center gap-4">
            <Loader2 className="animate-spin h-6 w-6" />
            <p className="text-lg font-medium">Uploading files...</p>
          </div>
        </div>
      )}
    </div>
  );
};

export default CourseForm;
