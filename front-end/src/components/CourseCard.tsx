'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { Calendar, Edit, Trash } from 'lucide-react';
import { format } from 'date-fns';
import { Course } from '@/context/CourseContext';
import { cn } from '@/lib/utils';
import { useRouter } from 'next/navigation';

interface CourseCardProps {
  course: Course;
  onDelete?: (e: React.MouseEvent) => void;
}

const CourseCard: React.FC<CourseCardProps> = ({ course, onDelete }) => {
  const [imageLoaded, setImageLoaded] = useState(false);
  const [imageError, setImageError] = useState(false);

  const router = useRouter();

  const createdDate = new Date(
    typeof course.createdAt === 'string' ? course.createdAt : course.createdAt
  );

  const formattedDate = format(createdDate, 'MMM d, yyyy');

  function handleEditClick(event: React.MouseEvent) {
    event.stopPropagation();
    router.push(`/edit-course/${course.id}`);
  }

  

  return (
    <div
      className="group relative overflow-hidden rounded-lg border bg-card text-card-foreground shadow-sm transition-all duration-300 hover-scale"
    >
      <div 
        className={cn(
          "h-48 w-full overflow-hidden bg-muted", 
          !imageLoaded && !imageError && "image-loading"
        )}
      >
        {course.imageUrl && !imageError ? (
          <img
            src={course.imageUrl}
            alt={course.name}
            className={cn(
              "h-full w-full object-cover object-center transition-transform duration-500 group-hover:scale-105",
              !imageLoaded && "opacity-0"
            )}
            onLoad={() => setImageLoaded(true)}
            onError={() => setImageError(true)}
          />
        ) : (
          <div className="flex h-full w-full items-center justify-center bg-muted">
            <span className="text-4xl font-light text-muted-foreground opacity-50">
              {course.name.charAt(0)}
            </span>
          </div>
        )}
      </div>

      <div className="p-5">
        <h3 className="text-xl font-semibold transition-colors duration-200 group-hover:text-primary">
          {course.name}
        </h3>
        
        <p className="mt-2 line-clamp-2 text-muted-foreground">
          {course.description}
        </p>
        
        <div className="mt-4 flex items-center text-sm text-muted-foreground">
          <Calendar className="mr-1 h-3.5 w-3.5" />
          <span>{formattedDate}</span>
        </div>
      </div>

      {/* Action Buttons */}
      <div className="absolute right-3 top-3 flex gap-2 opacity-0 transition-opacity duration-300 group-hover:opacity-100">
        <button 
           onClick={handleEditClick}
          className="btn-icon bg-background text-foreground hover:bg-muted cursor-pointer"
        >
          <Edit className="h-4 w-4" />
        </button>
        
        {onDelete && (
          <button 
            onClick={onDelete}
            className="btn-icon bg-background text-destructive hover:text-destructive-foreground hover:bg-muted cursor-pointer"
          >
            <Trash className="h-4 w-4" />
          </button>
        )}
      </div>
    </div>
  );
};

export default CourseCard;