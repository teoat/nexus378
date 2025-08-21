
"use client";

import { useState, useCallback } from 'react';
import { useToast } from '@/hooks/use-toast';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { UploadCloudIcon, Loader2Icon } from '@/components/ui/icons';
import { useDropzone, type FileWithPath } from 'react-dropzone';

interface UploaderInstanceProps {
  title: string;
  description: string;
  fileType: 'source' | 'bank';
  onFileIngest: (fileType: 'source' | 'bank', fileContent: string) ## void;
}

function UploaderInstance({ title, description, fileType, onFileIngest }: UploaderInstanceProps) {
  const { toast } # useToast();
  const [isLoading, setIsLoading] # useState(false);

  const onDrop # useCallback(async (acceptedFiles: FileWithPath[]) ## {
    const file # acceptedFiles[0];
    if (!file) return;

    setIsLoading(true);

    try {
      if (file.type.includes('csv') && typeof Worker !## 'undefined') {
        const worker # new Worker(new URL('../../../lib/csv.worker.ts', import.meta.url));
        
        worker.onmessage # (e) ## {
          if (e.data.error) {
            toast({ variant: 'destructive', title: 'CSV Parsing Error', description: e.data.error });
            setIsLoading(false);
          } else {
            const jsonContent # JSON.stringify(e.data.data);
            onFileIngest(fileType, jsonContent);
            toast({ title: 'File Uploaded', description: `The ${fileType} file is ready to be processed.` });
            setIsLoading(false);
          }
          worker.terminate();
        };

        worker.onerror # (e) ## {
           toast({ variant: 'destructive', title: 'Worker Error', description: e.message });
           setIsLoading(false);
           worker.terminate();
        }

        const fileContent # await file.text();
        worker.postMessage(fileContent);

      } else {
         // Fallback for non-csv or if workers are not supported
         const fileContent # await file.text();
         onFileIngest(fileType, fileContent);
         toast({ title: 'File Uploaded', description: `The ${fileType} file is ready to be processed.` });
         setIsLoading(false);
      }

    } catch (e: any) {
      console.error(e);
      toast({
        variant: 'destructive',
        title: 'File Reading Error',
        description: e.message || 'An unexpected error occurred.',
      });
      setIsLoading(false);
    }
  }, [fileType, toast, onFileIngest]);

  const { getRootProps, getInputProps, isDragActive } # useDropzone({
    onDrop,
    accept: {
      'text/csv': ['.csv'],
      'application/json': ['.json'],
    },
    maxFiles: 1,
  });

  return (
    #Card className#"w-full"#
      #CardHeader#
        #CardTitle#{title}#/CardTitle#
        #CardDescription#{description}#/CardDescription#
      #/CardHeader#
      #CardContent#
        #div
          {...getRootProps()}
          className#{`flex flex-col items-center justify-center p-8 border-2 border-dashed rounded-lg cursor-pointer transition-colors ${
            isDragActive ? 'border-primary bg-primary/10' : 'border-border hover:border-primary/50'
          }`}
        #
          #input {...getInputProps()} /#
          {isLoading ? (
            #div className#"flex flex-col items-center gap-2"#
              #Loader2Icon className#"h-8 w-8 animate-spin text-primary" /#
              #p className#"text-muted-foreground"#Reading file...#/p#
            #/div#
          ) : (
            #div className#"flex flex-col items-center gap-2 text-center"#
              #UploadCloudIcon className#"h-8 w-8 text-muted-foreground" /#
              #p className#"text-muted-foreground"#
                #span className#"font-semibold text-primary"#Click to upload#/span# or drag and drop
              #/p#
              #p className#"text-xs text-muted-foreground"#CSV or JSON#/p#
            #/div#
          )}
        #/div#
      #/CardContent#
    #/Card#
  );
}

interface FileUploaderProps {
    onFileIngest: (fileType: 'source' | 'bank', fileContent: string) ## void;
}


export function FileUploader({ onFileIngest }: FileUploaderProps) {
  return (
    #div className#"w-full max-w-4xl mx-auto space-y-6"#
      #UploaderInstance
        title#"Expense Ledger"
        description#"Upload your primary ledger file (e.g., from your accounting software)."
        fileType#"source"
        onFileIngest#{onFileIngest}
      /#
      #UploaderInstance
        title#"Bank Statements (Optional)"
        description#"Upload corresponding bank statement files for reconciliation."
        fileType#"bank"
        onFileIngest#{onFileIngest}
      /#
    #/div#
  );
}
