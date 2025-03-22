'use client';

import React from 'react';
import { useParams, useRouter } from 'next/navigation';
import PDFViewer from '@/components/pdf-viewer'
import { getFile, getCourseId } from '@/context/CourseContext';
import Layout from '@/components/Layout';

export default function File() {
    const router = useRouter();

    const params = useParams();
    const id = params.id as string;

    const file = getFile(id);
    const courseId = getCourseId(id);

    return (
        <Layout>
            <div className="h-screen p-4">
            <PDFViewer 
                pdfUrl={file?.dataUrl}
                title={file?.fileName}
                onBack={() => {router.push(`/course/${courseId}`)}}
                courses={[
                    {
                        id: "1",
                        label: "class1",
                        pdfs: [
                            {
                                id: "1",
                                label: "pdf1"
                            },
                            {
                                id: "2",
                                label: "pdf2"
                            },
                        ]
                    },
                    {
                        id: "2",
                        label: "class2",
                        pdfs: [
                            {
                                id: "3",
                                label: "pdf3"
                            },
                            {
                                id: "4",
                                label: "pdf4"
                            },
                        ]
                    },
                ]}
            />
        </div>
        </Layout>
    )
}