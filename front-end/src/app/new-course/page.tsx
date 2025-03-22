'use client';

import React from 'react';
import Layout from '@/components/Layout';
import CourseForm from '@/components/CourseForm';

export default function NewCoursePage() {
  return (
    <Layout>
      <div className="container mx-auto px-4 py-6">
        <CourseForm />
      </div>
    </Layout>
  );
}