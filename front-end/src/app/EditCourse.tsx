import React from 'react';
import { useParams } from 'react-router-dom';
import Layout from '@/components/Layout';
import CourseForm from '@/components/CourseForm';

const EditCourse = () => {
  const { id } = useParams<{ id: string }>();

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
};

export default EditCourse;