import React from 'react';
import Link from 'next/link';
import { MaterialSnippet } from '@/context/MaterialSnippetContext';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { X, Copy, Eye } from 'lucide-react';
import { toast } from 'sonner';
import { useMaterials } from '@/context/ClassMaterialContext';

interface SnippetContainerProps {
  snippets: MaterialSnippet[];
  onClose: () => void;
  subjectName: string;
}

const SnippetContainer: React.FC<SnippetContainerProps> = ({ 
  snippets, 
  onClose,
  subjectName
}) => {
  const { getMaterial } = useMaterials();

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
    toast.success('Copied to clipboard');
  };

  if (snippets.length === 0) {
    return (
      <Card className="mt-4">
        <CardHeader className="flex flex-row items-center justify-between pb-2">
          <CardTitle className="text-lg">Snippets for {subjectName}</CardTitle>
          <Button variant="ghost" size="icon" onClick={onClose}>
            <X className="h-4 w-4" />
          </Button>
        </CardHeader>
        <CardContent>
          <p className="text-muted-foreground">No snippets found for this subject.</p>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="mt-4 space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-medium">Snippets for {subjectName}</h3>
        <Button variant="ghost" size="sm" onClick={onClose}>
          <X className="h-4 w-4 mr-2" />
          Close
        </Button>
      </div>
      
      {snippets.map((snippet) => {
        const material = getMaterial(snippet.class_material);
        const materialName = material?.custom_name || material?.file_name || snippet.class_material;

        return (
          <Card key={snippet.id} className="overflow-hidden">
            <CardHeader className="flex flex-row items-center justify-between py-3 px-4 bg-gray-50">
              <CardTitle className="text-sm font-medium">
                {materialName}
              </CardTitle>
              <div className="flex gap-2 items-center">
                <Link href={`/file/${snippet.class_material}`}>
                  <Button
                    variant="ghost"
                    size="icon"
                    className="h-8 w-8 cursor-pointer"
                    title="View file"
                  >
                    <Eye className="h-4 w-4" />
                  </Button>
                </Link>

                <Button 
                  variant="ghost"
                  size="icon" 
                  onClick={() => copyToClipboard(snippet.snippet)}
                  className="h-8 w-8 cursor-pointer"
                  title="Copy snippet"
                >
                  <Copy className="h-4 w-4" />
                </Button>
              </div>
            </CardHeader>
            <CardContent className="p-4 text-sm font-mono bg-gray-50 bg-opacity-30 whitespace-pre-wrap">
              {snippet.snippet}
            </CardContent>
          </Card>
        );
      })}
    </div>
  );
};

export default SnippetContainer;
