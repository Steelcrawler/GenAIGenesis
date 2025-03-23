'use client';

import React from 'react';
import PDFViewer from '../../components/pdf-viewer'

export default function TempPage() {
    return (
        <div className="h-screen p-4">
            <PDFViewer 
                pdfUrl='https://pdfobject.com/pdf/sample.pdf' 
                title='random pdf'
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
    )
}