// File: app/course/[id]/page.tsx
'use client';

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
import { ArrowLeft, Calendar, Edit, Trash } from "lucide-react";
import { format } from "date-fns";
import { toast } from "sonner";
import SubjectMasteryContainer from "@/components/SubjectMasteryContainer";
import { useCurrentCourse } from "@/context/CurrentCourseContext";
import QuizList from "@/components/quiz/QuizList";

export default function CourseDetail() {
  const params = useParams();
  const id = params.id as string;
  const router = useRouter();
  const { getCourse, deleteCourse } = useCourses();
  const { setCurrentCourseId } = useCurrentCourse();
  const [confirmDelete, setConfirmDelete] = useState(false);
  const [imageLoaded, setImageLoaded] = useState(false);
  const [imageError, setImageError] = useState(false);

  const handleQuizStart = () => {
    setCurrentCourseId(id);
    router.push("/quiz-config");
  };

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
    typeof course.created_at === "string" ? course.created_at : Date.now()
  );

  const handleDelete = () => {
    deleteCourse(id);
    toast.success("Course deleted successfully");
    router.push("/courses");
  };

  return (
    <Layout>
      <div className="container mx-auto px-4 pb-12 animate-fade-in">
        {/* Back Button */}
        <Button
          variant="ghost"
          className="mb-6 gap-2 cursor-pointer"
          onClick={() => router.push("/courses")}
        >
          <ArrowLeft className="h-4 w-4" />
          <span>Back</span>
        </Button>

        {/* Top Section: Two Columns */}
        <div className="flex flex-col lg:flex-row gap-8">
          {/* Left Column: Image & Actions */}
          <div className="lg:w-1/3">
            <div
              className={`rounded-lg overflow-hidden border ${
                !imageLoaded && !imageError ? "image-loading" : ""
              } h-64 lg:h-auto lg:aspect-square`}
            >
              {course.image_path && !imageError ? (
                <img
                  src={course.image_path}
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

            {/* Action Buttons: Edit, Delete & Start Quiz */}
            <div className="mt-6 flex flex-col gap-2">
              <div className="flex space-x-4">
                <Link href={`/edit-course/${id}`} className="flex-1">
                  <Button className="w-full gap-2 cursor-pointer" variant="outline">
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
                className="w-full gap-2 cursor-pointer bg-blue-600 hover:bg-blue-600/80 text-white"
                onClick={handleQuizStart}
              >
                <span role="img" aria-label="play">►</span> Start Quiz
              </Button>
            </div>
          </div>

          {/* Right Column: Course Details */}
          <div className="lg:w-2/3">
            <div className="glass rounded-lg p-8">
              <h1 className="text-3xl font-semibold mb-4">{course.name}</h1>
              <div className="flex flex-wrap gap-x-6 gap-y-2 mb-8 text-sm text-muted-foreground">
                <div className="flex items-center">
                  <Calendar className="mr-2 h-4 w-4" />
                  <span>Created: {format(createdDate, "MMM d, yyyy")}</span>
                </div>
              </div>
              <div className="space-y-6">
                <div>
                  <h2 className="text-xl font-medium mb-2">Description</h2>
                  <p className="text-muted-foreground whitespace-pre-line">
                    {course.description}
                  </p>
                  <div className="mt-4">
                    <SubjectMasteryContainer courseId={id} />
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Quiz Lists Section: Full Width Under Top Section */}
        <div className="mt-12">
          <div className="mb-8">
            <h2 className="text-2xl font-bold mb-4">
              Open Quizzes for this Course
            </h2>
            <QuizList courseId={id} isCompleted={false} horizontalScroll={false} />
          </div>
          <div>
            <h2 className="text-2xl font-bold mb-4">
              Completed Quizzes for this Course
            </h2>
            <QuizList courseId={id} isCompleted={true} horizontalScroll={false} />
          </div>
        </div>

        {/* Delete Confirmation Dialog */}
        <AlertDialog open={confirmDelete} onOpenChange={(open) => !open && setConfirmDelete(false)}>
          <AlertDialogContent>
            <AlertDialogHeader>
              <AlertDialogTitle>Are you sure?</AlertDialogTitle>
              <AlertDialogDescription>
                This action cannot be undone. This will permanently delete the course.
              </AlertDialogDescription>
            </AlertDialogHeader>
            <AlertDialogFooter>
              <AlertDialogCancel className="cursor-pointer">Cancel</AlertDialogCancel>
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
    </Layout>
  );
}
