'use client';

import React, { useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import PDFViewer from '@/components/pdf-viewer';
import { useCourses } from '@/context/CourseContext';
import { useMaterials } from '@/context/ClassMaterialContext';
import Layout from '@/components/Layout';

type ClassMaterial = {
  id?: string;
  file_name: string;
  local_file?: File;
  custom_name?: string;
  course: string;
  weight?: number;
  created_at?: string;
};

export default function File() {
  const router = useRouter();
  const params = useParams();
  const id = params.id as string;

  const { getCourse } = useCourses();
  const { getMaterialRequest } = useMaterials();

  const [currentMaterial, setCurrentMaterial] = useState<ClassMaterial | null>(null);
  const [fileUrl, setFileUrl] = useState('');
  const [loading, setLoading] = useState(true);

  async function fetchMaterialAndFile() {
    setLoading(true);
    try {
      const data: { class_material: ClassMaterial; file: string } | null = await getMaterialRequest(id);
      if (!data) {
        throw new Error("Aucune donnée reçue via getMaterialRequest");
      }

      setCurrentMaterial(data.class_material);

      const pdfBase64 = data.file;
      const pdfBytes = Uint8Array.from(atob(pdfBase64), c => c.charCodeAt(0));
      const blob = new Blob([pdfBytes], { type: 'application/pdf' });
      const url = URL.createObjectURL(blob);
      setFileUrl(url);
    } catch (error) {
      console.error('Erreur lors de la récupération du fichier :', error);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    fetchMaterialAndFile();

    return () => {
      if (fileUrl) URL.revokeObjectURL(fileUrl);
    };
  }, [id]);

  if (loading || !currentMaterial || !fileUrl) {
    return (
      <Layout>
        <div className="p-4">Loading...</div>
      </Layout>
    );
  }

  const course = getCourse(currentMaterial.course);

  return (
    <Layout>
      <div className="h-screen p-4">
        <PDFViewer
          pdfUrl={fileUrl}
          title={currentMaterial.file_name.split('/').pop()}
          onBack={() => router.push(`/course/${currentMaterial.course}`)}
          courses={[
            {
              id: course?.id || '',
              label: course?.name || '',
              pdfs: [
                {
                  id: currentMaterial.id || '',
                  label:
                    currentMaterial.custom_name ||
                    currentMaterial.file_name.split('/').pop() ||
                    'Material',
                },
              ],
            },
          ]}
        />
      </div>
    </Layout>
  );
}
