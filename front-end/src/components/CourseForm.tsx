"use client";

import React, { useState } from "react";
import { useRouter } from "next/navigation";
import { z } from "zod";
import { v4 as uuidv4 } from "uuid";
import { useCourses, Course, ClassMaterial } from "@/context/CourseContext";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { toast } from "sonner";
import { ArrowLeft, Save } from "lucide-react";

const formSchema = z.object({
  name: z.string().min(1, "Course name is required"),
  description: z.string().min(1, "Description is required"),
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

  const [formData, setFormData] = useState<Partial<Course>>({
    name: existingCourse?.name || "",
    description: existingCourse?.description || "",
    material: existingCourse?.material || [],
  });

  const [errors, setErrors] = useState<{ [key: string]: string }>({});
  const [isSubmitting, setIsSubmitting] = useState(false);

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

  const handleFilesChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (!e.target.files) return;
    const filesArray = Array.from(e.target.files);

    try {
      const filePromises = filesArray.map(async (file) => {
        const dataUrl = await fileToBase64(file);
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

  const handleRemoveFile = (fileId: string) => {
    setFormData((prev) => ({
      ...prev,
      material: prev.material?.filter((f) => f.id !== fileId) ?? [],
    }));
  };

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

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);

    try {
      const validatedData = formSchema.parse(formData);

      if (isEditing && courseId) {
        await updateCourse(courseId, validatedData);
        toast.success("Course updated successfully");
        router.push(`/course/${courseId}`);
      }
      else {
        await addCourse(validatedData as Omit<Course, "id" | "created_at">);
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
      <Button variant="ghost" className="mb-6 gap-2" onClick={() => router.push("/courses")}>
        <ArrowLeft className="h-4 w-4" />
        <span>Back</span>
      </Button>

      <div className="glass p-6 rounded-lg">
        <h1 className="text-2xl font-semibold mb-6">
          {isEditing ? "Edit Course" : "Create New Course"}
        </h1>

        <form onSubmit={handleSubmit} className="space-y-6">
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
            {errors.name && <p className="text-sm text-destructive">{errors.name}</p>}
          </div>

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

          <div className="flex justify-end">
            <Button type="submit" disabled={isSubmitting} className="gap-2">
              <Save className="h-4 w-4" />
              <span>{isEditing ? "Update Course" : "Create Course"}</span>
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default CourseForm;
