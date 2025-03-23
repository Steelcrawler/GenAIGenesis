"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import {
  ChevronLeft,
  FolderOpen,
  Loader2,
  Plus,
  Search,
  Trash,
  Upload,
} from "lucide-react";
import { useCourses } from "@/context/CourseContext";
import { useMaterials } from "@/context/ClassMaterialContext";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { cn } from "@/lib/utils";

interface SidebarProps {
  isOpen: boolean;
  setIsOpen: (isOpen: boolean) => void;
}

export default function Sidebar({ isOpen, setIsOpen }: SidebarProps) {
  const { filteredCourses, searchTerm, setSearchTerm } = useCourses();
  const { getMaterialsByCourse, createMaterial, deleteMaterial } = useMaterials();


  const pathname = usePathname();
  const [mounted, setMounted] = useState(false);
  const router = useRouter();

  const [uploadingCourseId, setUploadingCourseId] = useState<string | null>(
    null
  );
  const [expandedCourseId, setExpandedCourseId] = useState<string | null>(null);

  useEffect(() => {
    setMounted(true);
  }, []);

  // MOVE handleFileUpload OUTSIDE of .map
  const handleFileUpload = async (
    e: React.ChangeEvent<HTMLInputElement>,
    courseId: string
  ) => {
    if (!e.target.files || e.target.files.length === 0) return;

    const file = e.target.files[0];
    setUploadingCourseId(courseId);

    try {
      const newMaterial = {
        id: "",
        file_name: file.name,
        local_file: file,
        course: courseId,
      };

      // Now we can use createMaterial without re-calling the hook
      await createMaterial(newMaterial, courseId);
    } catch (error) {
      console.error("Failed to upload material:", error);
    } finally {
      setUploadingCourseId(null);
    }
  };

  return (
    <>
      {isOpen && (
        <div
          className="md:hidden fixed inset-0 bg-black/20 backdrop-blur-sm z-40"
          onClick={() => setIsOpen(false)}
        />
      )}

      <aside
        className={cn(
          "fixed md:sticky top-0 bottom-0 left-0 z-50 md:z-0 h-screen w-[280px] flex flex-col",
          "bg-sidebar backdrop-blur-lg border-r border-sidebar-border transition-transform duration-300 ease-in-out",
          isOpen
            ? "translate-x-0 shadow-lg md:shadow-none"
            : "-translate-x-full md:translate-x-0",
          !mounted && "!transform-none"
        )}
      >
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-sidebar-border">
          <Link href="/courses" className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-md bg-primary flex items-center justify-center">
              <FolderOpen className="text-white h-4 w-4" />
            </div>
            <h1 className="font-semibold text-lg text-sidebar-foreground">
              Courses
            </h1>
          </Link>
          <Button
            variant="ghost"
            size="icon"
            className="md:hidden"
            onClick={() => setIsOpen(false)}
          >
            <ChevronLeft className="h-4 w-4" />
          </Button>
        </div>

        {/* Search Bar */}
        <div className="p-4">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
            <Input
              placeholder="Search courses..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-9 bg-sidebar-accent border-sidebar-border"
            />
          </div>
        </div>

        {/* Courses */}
        <nav className="flex-1 overflow-y-auto p-2">
          {filteredCourses.length > 0 ? (
            <ul className="space-y-1">
              {filteredCourses.map((course) => {
                const isActive =
                  pathname === `/course/${course.id}` ||
                  pathname === `/edit-course/${course.id}`;
                const isExpanded = expandedCourseId === course.id;
                const courseMaterials = getMaterialsByCourse(course.id);

                return (
                  <li key={course.id}>
                    <div
                      className={cn(
                        "flex items-center justify-between gap-2 p-2 rounded-md hover:bg-sidebar-accent cursor-pointer",
                        isActive && "border-l-4 border-black",
                        isExpanded && "bg-sidebar-accent"
                      )}
                      onClick={() => {
                        setExpandedCourseId(isExpanded ? null : course.id);
                        router.push(`/course/${course.id}`)
                      }}
                    >
                      <ChevronLeft
                        className={cn(
                          "h-4 w-4 transition-transform -rotate-180",
                          isExpanded && "-rotate-90"
                        )}
                      />
                      <span className="flex-1 truncate pr-2">
                        {course.name}
                      </span>

                      {/* Upload icon + hidden input */}
                      <label className="cursor-pointer">
                        <Upload className="h-4 w-4 text-muted-foreground hover:text-primary" />
                        <input
                          type="file"
                          hidden
                          onChange={(e) => handleFileUpload(e, course.id)}
                        />
                      </label>

                      {/* Spinner if uploading */}
                      {uploadingCourseId === course.id && (
                        <Loader2 className="h-4 w-4 animate-spin text-primary" />
                      )}
                    </div>

                    {isExpanded && courseMaterials.length > 0 && (
                      <ul className="ml-6 mt-1 space-y-1 text-sm">
                      {courseMaterials.map((material) => (
                        <li key={material.id} className="flex items-center justify-between group">
                          <Link
                            href={`/file/${material.id}`}
                            className="text-foreground hover:underline truncate max-w-[170px]"
                          >
                            {material.file_name.split("/").pop()}
                          </Link>
                    
                          <button
                            onClick={() => deleteMaterial(material.id!)}
                            className="cursor-pointer text-muted-foreground hover:text-red-500 opacity-0 group-hover:opacity-100 transition"
                            title="Delete file"
                          >
                            <Trash className="h-4 w-4" />
                          </button>
                        </li>
                      ))}
                    </ul>
                    )}
                    {isExpanded && courseMaterials.length === 0 && (
                      <p className="ml-6 mt-1 text-xs text-muted-foreground">
                        No files uploaded
                      </p>
                    )}
                  </li>
                );
              })}
            </ul>
          ) : (
            <div className="text-center text-muted-foreground py-8">
              {searchTerm ? "No courses found" : "No courses yet"}
            </div>
          )}
        </nav>

        <div className="border-t border-sidebar-border p-4">
          <Link href="/new-course">
            <Button className="w-full gap-2 cursor-pointer">
              <Plus className="h-4 w-4" />
              <span>New Course</span>
            </Button>
          </Link>
        </div>
      </aside>
    </>
  );
}
