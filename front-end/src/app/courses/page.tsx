'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { AlertDialog, AlertDialogAction, AlertDialogCancel, AlertDialogContent, AlertDialogDescription, AlertDialogFooter, AlertDialogHeader, AlertDialogTitle } from '@/components/ui/alert-dialog';
import { Button } from '@/components/ui/button';
import { Plus } from 'lucide-react';
import { useCourses } from '@/context/CourseContext';
import Layout from '@/components/Layout';
import CourseCard from '@/components/CourseCard';
import { toast } from 'sonner';

export default function CoursesPage() {
  const { filteredCourses, deleteCourse, searchTerm } = useCourses();
  const [courseToDelete, setCourseToDelete] = useState<string | null>(null);

  const handleDelete = () => {
    if (courseToDelete) {
      deleteCourse(courseToDelete);
      toast.success('Course deleted successfully');
      setCourseToDelete(null);
    }
  };

  return (
    <Layout>
      <div className="container mx-auto px-4 py-6">
        <div className="mb-8 flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
          <div>
            <h1 className="text-3xl font-semibold">Your Courses</h1>
            {searchTerm && (
              <p className="text-muted-foreground mt-1">
                Showing results for "{searchTerm}"
              </p>
            )}
          </div>
          <Link href="/new-course">
            <Button className="gap-2 cursor-pointer">
              <Plus className="h-4 w-4" />
              <span>New Course</span>
            </Button>
          </Link>
        </div>

        {filteredCourses.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredCourses.map((course) => (
              <Link key={course.id} href={`/course/${course.id}`} className="block no-underline">
                <CourseCard 
                  course={course} 
                  onDelete={(e) => {
                    e.preventDefault();
                    setCourseToDelete(course.id);
                  }}
                />
              </Link>
            ))}
          </div>
        ) : (
          <div className="p-12 text-center bg-muted/50 rounded-lg">
            <h3 className="text-xl font-medium mb-2">
              {searchTerm ? 'No courses found' : 'No courses yet'}
            </h3>
            <p className="text-muted-foreground mb-6">
              {searchTerm 
                ? `Try adjusting your search term or clear it to see all courses.` 
                : `Let's create your first course to get started.`}
            </p>
            {!searchTerm && (
              <Link href="/new-course">
                <Button className="gap-2 cursor-pointer">
                  <Plus className="h-4 w-4" />
                  <span>New Course</span>
                </Button>
              </Link>
            )}
          </div>
        )}

        <AlertDialog open={!!courseToDelete} onOpenChange={(open) => !open && setCourseToDelete(null)}>
          <AlertDialogContent>
            <AlertDialogHeader>
              <AlertDialogTitle>Are you sure?</AlertDialogTitle>
              <AlertDialogDescription>
                This action cannot be undone. This will permanently delete the course.
              </AlertDialogDescription>
            </AlertDialogHeader>
            <AlertDialogFooter>
              <AlertDialogCancel className='cursor-pointer'>Cancel</AlertDialogCancel>
              <AlertDialogAction onClick={handleDelete} className="cursor-pointer bg-destructive text-destructive-foreground hover:bg-destructive/80">
                Delete
              </AlertDialogAction>
            </AlertDialogFooter>
          </AlertDialogContent>
        </AlertDialog>
      </div>
    </Layout>
  );
}