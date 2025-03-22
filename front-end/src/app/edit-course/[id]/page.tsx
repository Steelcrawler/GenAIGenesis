'use client';

import React from 'react';
import { useParams } from 'next/navigation';
import Layout from '@/components/Layout';
import CourseForm from '@/components/CourseForm';

export default function EditCoursePage() {
  const params = useParams();
  const id = params.id as string;

  if (!id) {
    return <div>Course ID is required</div>;
  }

  return (
    <Layout>
      <div className="container mx-auto px-4 py-6">
        <CourseForm courseId={id} />
      </div>
    </Layout>
  );
}