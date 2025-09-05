import { convertDateToString } from "@/utils/date/helper";
import type { IconName } from "@urbint/silica";
import { BodyText, CaptionText, Icon } from "@urbint/silica";
import React, { useCallback, useContext, useRef, useState } from "react";
import ButtonSecondary from "../shared/button/secondary/ButtonSecondary";
import ToastContext from "../shared/toast/context/ToastContext";

export interface FileUploaderConfig {
  buttonLabel: string;
  buttonIcon: IconName;
  allowedFormats: string[];
  maxFileSize: number; // in MB
  maxFiles: number;
  allowMultiple?: boolean;
  showPreview?: boolean;
  acceptImages?: boolean;
  acceptDocuments?: boolean;
  onError?: (isError: boolean, message: string) => void;
}

export interface FileUploaderProps {
  config: FileUploaderConfig;
  onUpload: (files: File[]) => void;
  onError?: (isError: boolean, message: string) => void;
  onFileRead?: (file: File, content: string) => void;
  disabled?: boolean;
  loading?: boolean;
  className?: string;
  children?: React.ReactNode;
}

export interface FilePreview {
  file: File;
  id: string;
  preview?: string;
}

const FileUploader: React.FC<FileUploaderProps> = ({
  config,
  onUpload,
  onFileRead,
  onError,
  disabled = false,
  loading = false,
  className = "",
  children,
}) => {
  const [isDragOver, setIsDragOver] = useState(false);
  const [selectedFiles, setSelectedFiles] = useState<FilePreview[]>([]);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const toastCtx = useContext(ToastContext);

  const {
    buttonLabel,
    buttonIcon,
    allowedFormats,
    maxFileSize,
    maxFiles,
    allowMultiple = true,
    showPreview = true,
  } = config;

  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return "0 Bytes";
    const k = 1024;
    const sizes = ["Bytes", "KB", "MB", "GB"];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + " " + sizes[i];
  };

  const validateFile = (file: File): { isValid: boolean; error?: string } => {
    // Check file size
    if (file.size > maxFileSize * 1024 * 1024) {
      return {
        isValid: false,
        error: `${file.name} is too large. Please upload a file smaller than 10 MB.`,
      };
    }

    // Check file type
    const fileExtension = file.name.split(".").pop()?.toLowerCase();
    const isValidType = allowedFormats.some(format =>
      format.toLowerCase().includes(fileExtension || "")
    );

    if (!isValidType) {
      return {
        isValid: false,
        error: `${file.name} has an unsupported file type. Please upload a .csv or .xlsx file.`,
      };
    }

    return { isValid: true };
  };

  const createFilePreview = (file: File): FilePreview => {
    const id = `${file.name}-${Date.now()}-${Math.random()}`;
    const preview: FilePreview = {
      file,
      id,
    };
    return preview;
  };

  const readFileContent = useCallback((file: File): Promise<string> => {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = e => {
        const content = e.target?.result as string;
        resolve(content);
      };
      reader.onerror = () => reject(new Error("Failed to read file"));
      reader.readAsText(file);
    });
  }, []);

  const handleFileSelection = useCallback(
    async (files: FileList | null) => {
      if (!files) return;

      const fileArray = Array.from(files);
      const validFiles: FilePreview[] = [];
      const errors: string[] = [];

      for (const file of fileArray) {
        const validation = validateFile(file);
        if (validation.isValid) {
          const filePreview = createFilePreview(file);
          validFiles.push(filePreview);

          // Read file content if onFileRead callback is provided
          if (onFileRead) {
            try {
              const content = await readFileContent(file);
              onFileRead(file, content);
            } catch (error) {
              console.error("Failed to read file:", error);
            }
          }
        } else {
          onError?.(true, validation.error || "File is not valid");
        }
      }

      if (errors.length > 0) {
        errors.forEach(error => {
          toastCtx?.pushToast("error", error);
        });
      }

      if (validFiles.length > 0) {
        setSelectedFiles(prev => [...prev, ...validFiles]);
        onUpload(validFiles.map(f => f.file));
      }
    },
    [maxFiles, onUpload, onFileRead, readFileContent, toastCtx]
  );

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
    handleFileSelection(e.dataTransfer.files);
  }, []);

  const handleFileInputChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      handleFileSelection(e.target.files);
      // Reset input value to allow selecting the same file again
      if (e.target) {
        e.target.value = "";
      }
    },
    [handleFileSelection]
  );

  const handleUploadClick = useCallback((e?: React.MouseEvent) => {
    // Prevent event bubbling to avoid double file dialog opening
    e?.stopPropagation();
    fileInputRef.current?.click();
  }, []);

  const isDisabled = disabled || loading;

  return (
    <>
      <div className={`file-uploader ${className}`}>
        {/* Upload Area */}
        {selectedFiles.length == 0 && (
          <div className="border-2 border-dotted border-neutral-shade-40 rounded-lg p-8 flex flex-col gap-2 bg-neutral-light-16">
            <div
              className={`
            relative   p-8 text-center transition-all duration-200
            ${
              isDragOver
                ? "border-brand-urbint-50 bg-brand-urbint-5"
                : "border-neutral-shade-25 hover:border-neutral-shade-50 bg-neutral-shade-5"
            }
            ${isDisabled ? "opacity-50 cursor-not-allowed" : "cursor-pointer"}
          `}
              onDragOver={handleDragOver}
              onDragLeave={handleDragLeave}
              onDrop={handleDrop}
              onClick={!isDisabled ? handleUploadClick : undefined}
            >
              <div className="flex flex-col items-center space-y-4">
                <ButtonSecondary
                  className="hidden sm:block"
                  iconStart={buttonIcon}
                  label={buttonLabel}
                  disabled={isDisabled}
                  loading={loading}
                  onClick={e => handleUploadClick(e)}
                />
                <div className="space-y-2">
                  <BodyText className="text-neutral-shade-100">
                    {isDragOver
                      ? "Drop files here"
                      : "or drag & drop a file here to upload"}
                  </BodyText>
                </div>
                <div className="text-xs text-neutral-shade-75 space-y-1">
                  <p>
                    Max file size is 10 mb. Supported file types are .csv, .xlsx
                    and .xls
                  </p>
                </div>
              </div>
            </div>
            <input
              ref={fileInputRef}
              type="file"
              className="hidden"
              multiple={allowMultiple}
              accept={allowedFormats.join(",")}
              onChange={handleFileInputChange}
              disabled={isDisabled}
            />
          </div>
        )}
        {/* File Previews */}
        {showPreview && selectedFiles.length > 0 && (
          <div className=" space-y-4">
            <div className="">
              {selectedFiles.map(filePreview => (
                <FilePreviewCard
                  key={filePreview.id}
                  filePreview={filePreview}
                  formatFileSize={formatFileSize}
                />
              ))}
            </div>
          </div>
        )}
        {/* Children */}
        {children && <div className="mt-6">{children}</div>}
      </div>
    </>
  );
};

// File Preview Card Component
interface FilePreviewCardProps {
  filePreview: FilePreview;
  formatFileSize: (bytes: number) => string;
}

const FilePreviewCard: React.FC<FilePreviewCardProps> = ({
  filePreview,
  formatFileSize,
}) => {
  const { file } = filePreview;

  return (
    <div className="relative border border-neutral-shade-25 rounded-lg p-4 hover:border-neutral-shade-50 transition-colors">
      {/* File Info */}
      <div className="space-y-2">
        <div className="flex items-start justify-between">
          <div className="flex items-center justify-center">
            <Icon
              name="file_blank_outline"
              className="text-xl text-neutral-shade-75 mr-2"
            />
          </div>
          <div className="flex-1 min-w-0">
            <BodyText className="text-neutral-shade-100 truncate">
              {file.name}
            </BodyText>
            <CaptionText className="text-neutral-shade-75">
              <ul className="flex  gap-1">
                <li> {formatFileSize(file.size)}</li>
                <li className="before:content-['•'] before:mr-1">
                  {convertDateToString(new Date())}
                </li>
              </ul>
            </CaptionText>
          </div>
        </div>
      </div>
    </div>
  );
};

export default FileUploader;
