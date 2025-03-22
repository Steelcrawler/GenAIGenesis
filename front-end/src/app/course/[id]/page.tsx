"use client";

import React, { useState } from "react";
import Link from "next/link";
import { useParams, useRouter } from "next/navigation";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog";
import { Button } from "@/components/ui/button";
import { useCourses } from "@/context/CourseContext";
import Layout from "@/components/Layout";
import { ArrowLeft, Calendar, Clock, Edit, Trash } from "lucide-react";
import { format } from "date-fns";
import { toast } from "sonner";
import QuizPopup from "@/components/quiz-popup";

export default function CourseDetail() {
  const params = useParams();
  const id = params.id as string;
  const router = useRouter();
  const { getCourse, deleteCourse } = useCourses();
  const [confirmDelete, setConfirmDelete] = useState(false);
  const [imageLoaded, setImageLoaded] = useState(false);
  const [imageError, setImageError] = useState(false);
  const [showQuizPopup, setShowQuizPopup] = useState(false);


  const course = getCourse(id);

  if (!course) {
    return (
      <Layout>
        <div className="container mx-auto px-4 py-12 text-center">
          <h1 className="text-2xl font-semibold mb-4">Course not found</h1>
          <p className="text-muted-foreground mb-6">
            The course you're looking for doesn't exist or has been removed.
          </p>
          <Link href="/courses">
            <Button>Go back to all courses</Button>
          </Link>
        </div>
      </Layout>
    );
  }

  const createdDate = new Date(
    typeof course.createdAt === "string" ? course.createdAt : course.createdAt
  );

  const updatedDate = new Date(
    typeof course.updatedAt === "string" ? course.updatedAt : course.updatedAt
  );

  const handleDelete = () => {
    deleteCourse(id);
    toast.success("Course deleted successfully");
    router.push("/courses");
  };

  return (
    <Layout>
      <div className="container mx-auto px-4 pb-12 animate-fade-in">
        <Button
          variant="ghost"
          className="mb-6 gap-2 cursor-pointer"
          onClick={() => router.push("/courses")}
        >
          <ArrowLeft className="h-4 w-4" />
          <span>Back</span>
        </Button>

        <div className="flex flex-col lg:flex-row gap-8">
          <div className="lg:w-1/3">
            <div
              className={`rounded-lg overflow-hidden border ${
                !imageLoaded && !imageError ? "image-loading" : ""
              } h-64 lg:h-auto lg:aspect-square`}
            >
              {course.imageUrl && !imageError ? (
                <img
                  src={course.imageUrl}
                  alt={course.name}
                  className={`w-full h-full object-cover transition-opacity duration-500 ${
                    !imageLoaded ? "opacity-0" : "opacity-100"
                  }`}
                  onLoad={() => setImageLoaded(true)}
                  onError={() => setImageError(true)}
                />
              ) : (
                <div className="flex h-full items-center justify-center bg-muted">
                  <span className="text-8xl font-light text-muted-foreground opacity-50">
                    {course.name.charAt(0)}
                  </span>
                </div>
              )}
            </div>

            <div className="mt-6 flex space-x-4">
              <Link href={`/edit-course/${id}`} className="flex-1">
                <Button
                  className="w-full gap-2 cursor-pointer"
                  variant="outline"
                >
                  <Edit className="h-4 w-4" />
                  <span>Edit</span>
                </Button>
              </Link>
              <Button
                variant="outline"
                className="flex-1 gap-2 text-destructive hover:bg-destructive hover:text-white cursor-pointer"
                onClick={() => setConfirmDelete(true)}
              >
                <Trash className="h-4 w-4" />
                <span>Delete</span>
              </Button>
            </div>
            <Button
            className="mt-15 w-full gap-2 cursor-pointer bg-blue-600 hover:bg-blue-600/80 text-white"
            onClick={() => setShowQuizPopup(true)}
          >
            <span role="img" aria-label="play">►</span> Start Quiz
          </Button>
          </div>

         

          <div className="lg:w-2/3">
            <div className="glass rounded-lg p-8">
              <h1 className="text-3xl font-semibold mb-4">{course.name}</h1>

              <div className="flex flex-wrap gap-x-6 gap-y-2 mb-8 text-sm text-muted-foreground">
                <div className="flex items-center">
                  <Calendar className="mr-2 h-4 w-4" />
                  <span>Created: {format(createdDate, "MMM d, yyyy")}</span>
                </div>
                <div className="flex items-center">
                  <Clock className="mr-2 h-4 w-4" />
                  <span>Updated: {format(updatedDate, "MMM d, yyyy")}</span>
                </div>
              </div>

              <div className="space-y-6">
                <div>
                  <h2 className="text-xl font-medium mb-2">Description</h2>
                  <p className="text-muted-foreground whitespace-pre-line">
                    {course.description}
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>

        <AlertDialog open={confirmDelete} onOpenChange={setConfirmDelete}>
          <AlertDialogContent>
            <AlertDialogHeader>
              <AlertDialogTitle>Are you sure?</AlertDialogTitle>
              <AlertDialogDescription>
                This action cannot be undone. This will permanently delete the
                course.
              </AlertDialogDescription>
            </AlertDialogHeader>
            <AlertDialogFooter>
              <AlertDialogCancel className="cursor-pointer">
                Cancel
              </AlertDialogCancel>
              <AlertDialogAction
                onClick={handleDelete}
                className="cursor-pointer bg-destructive text-destructive-foreground hover:bg-destructive/80"
              >
                Delete
              </AlertDialogAction>
            </AlertDialogFooter>
          </AlertDialogContent>
        </AlertDialog>
      </div>

      {showQuizPopup && (
  <QuizPopup
    handleCancel={() => setShowQuizPopup(false)}
    courses={[
      {
        id: course.id,
        label: course.name,
        pdfs: [{ id: '1', label: 'PDF 1' }]
      },
    ]}
  />
)}
    </Layout>
  );
}
