type DownloadResult = "success" | "error" | "aborted";

type FileUploadPolicies = {
  id: string;
  fields: string;
  url: string;
};

export type FileUploadPolicy = {
  id: string;
  fields: string;
  url: string;
  signedUrl: string;
};

type UploadPoliciesQueryParameters = {
  key: string;
  value: string;
};

export const download = async (
  path: string,
  name: string
): Promise<DownloadResult> => {
  let result: DownloadResult = "success";

  try {
    const file = await fetch(path);
    const fileBlob = await file.blob();
    // TODO: create a global `DownloadManager` utils based on this and the `download` helper.
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

export const upload = async (
  url: string,
  payload: FormData,
  abortController?: AbortController
): Promise<DownloadResult> => {
  let result: DownloadResult = "success";

  try {
    const response = await fetch(url, {
      method: "POST",
      body: payload,
      signal: abortController?.signal,
    });

    // Check for non-success status codes
    if (!response.ok) {
      // Log or throw an error for debugging, based on status
      console.error(`Upload failed with status: ${response.status}`);
      result = "error"; // Set result to "error" if the status is not 200
    }
  } catch (error) {
    console.error("Error during upload:", error);
    result = "error";

    // Check if the request was aborted
    if (abortController?.signal.aborted) {
      console.error("Upload aborted");
      result = "aborted";
    }
  }

  return result;
};

export const buildUploadFormData = (
  fileUploadPolicies: FileUploadPolicies,
  fileToUpload: File
): FormData => {
  const formData = new FormData();

  const params: UploadPoliciesQueryParameters = JSON.parse(
    fileUploadPolicies.fields
  );

  Object.entries(params).forEach(([key, value]) => {
    formData.append(key, value);
  });
  formData.append("file", fileToUpload);

  return formData;
};
