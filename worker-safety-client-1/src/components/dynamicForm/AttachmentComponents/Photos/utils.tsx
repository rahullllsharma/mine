import type {
  DownloadResult,
  PhotoUploadItem,
  SubmissionPhotoType,
  UploadItem,
} from "@/components/templatesComponents/customisedForm.types";
import { messages } from "@/locales/messages";
import {
  ALLOWED_DOCUMENTS_FORMATS,
  ALLOWED_IMAGE_FORMATS,
  maxFiles,
} from "@/utils/customisedFormUtils/customisedForm.constants";

const BlankField = () => {
  return (
    <div className="flex flex-col sm:flex-row gap-2 sm:gap-4 p-2 sm:p-4 bg-gray-100 h-24 sm:h-32 w-full" />
  );
};

const photosFormatsText = ALLOWED_IMAGE_FORMATS.join(",")
  .replace(/\,/g, ", ")
  .toUpperCase();

const documentFormatsText = ALLOWED_DOCUMENTS_FORMATS.join(",")
  .replace(/\,/g, ", ")
  .toUpperCase();

const getMaxFilesErrorMessage = (isPhoto: boolean): string => {
  const contentType = isPhoto ? "images" : "documents";
  return `Maximum of ${maxFiles} ${contentType} can be uploaded at once.`;
};
const convertToPhotoUploadItem = (
  submissionPhotos: SubmissionPhotoType[]
): PhotoUploadItem[] => {
  return submissionPhotos.map(photo => {
    const {
      id,
      url,
      date,
      name,
      size,
      time,
      last_modified: lastModified,
      signed_url: signedUrl,
      display_name: displayName,
      description = "",
    } = photo;
    return {
      id: id,
      url: url,
      date: date,
      name: name,
      size: size,
      time: time,
      signedUrl: signedUrl,
      lastModified: lastModified,
      displayName: displayName,
      description: description || "",
    };
  });
};

const convertToSubmissionPhotoType = (
  uploadedFiles: PhotoUploadItem[]
): SubmissionPhotoType[] => {
  return uploadedFiles.map(file => {
    const {
      id,
      url,
      date,
      name,
      size,
      time,
      signedUrl,
      lastModified,
      displayName,
      description = "",
    } = file;
    return {
      id: id,
      md5: null,
      url: url,
      date: date,
      name: name,
      size: size,
      time: time,
      crc32c: null,
      category: null,
      mimetype: null,
      signed_url: signedUrl,
      last_modified: lastModified,
      display_name: displayName,
      description: description || "",
    };
  });
};

const timeoutPromise = (ms: number) =>
  new Promise((_, reject) => {
    setTimeout(() => reject(new Error(messages.requestTimedOut)), ms);
  });

const download = async (
  path: string,
  name: string
): Promise<DownloadResult> => {
  let result: DownloadResult = "success";
  try {
    const file = await fetch(path);
    const fileBlob = await file.blob();
    const url = URL.createObjectURL(fileBlob);
    const link = document.createElement("a");
    link.href = url;
    link.download = name;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  } catch (error) {
    result = "error";
  }
  return result;
};

const downloadDocumentHandler = async (
  event: React.MouseEvent<HTMLButtonElement>,
  file: UploadItem
) => {
  event.preventDefault();
  await download(file.signedUrl, file.name);
};

const isImage = (fileName: string): boolean => {
  const imageExtensions = ALLOWED_IMAGE_FORMATS;
  const ext = fileName.split(".").pop()?.toLowerCase();
  return ext ? imageExtensions.includes(ext) : false;
};

export {
  BlankField,
  photosFormatsText,
  documentFormatsText,
  getMaxFilesErrorMessage,
  convertToPhotoUploadItem,
  convertToSubmissionPhotoType,
  timeoutPromise,
  download,
  downloadDocumentHandler,
  isImage,
};
