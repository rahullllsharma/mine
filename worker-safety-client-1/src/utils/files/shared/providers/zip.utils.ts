import { downloadContentAsFile } from "@/components/fileDownloadDropdown/utils";

type ZipBufferSupportTypes = "base64" | "blob" | "nodebuffer";
type ZipClientContentSupportTypes = "string" | Blob;

export type IsomorphicDownloadableMetadata = {
  file: string;
  content: ZipClientContentSupportTypes | Buffer;
};

export type DownloadableMetadata = {
  file: string;
  content: ZipClientContentSupportTypes | Buffer;
};

/** Creates the buffer with the encoded zip content that can be used across client and server */
async function generateZipFromSource(
  buffer: IsomorphicDownloadableMetadata[],
  type: ZipBufferSupportTypes = "base64"
): Promise<string | Blob | Buffer> {
  const { default: JSZip } = await import(
    /* webpackChunkName: "vendors~jszip" */
    "jszip"
  );

  const jszip = new JSZip();

  buffer.forEach(({ file: currentFileName, content }) => {
    jszip.file(currentFileName, content, {
      binary: true,
    });
  });

  return jszip.generateAsync({ type });
}

/** Generates a encoded base64 string, ready to be downloaded by the browser (potentially node as well) */
async function downloadZipFromBuffers(
  buffer: DownloadableMetadata[],
  fileName = "file-zip",
  type: "base64" | "blob" = "base64"
): Promise<void> {
  if (typeof window === "undefined") {
    throw new Error("Cannot use this function to download on the server");
  }

  const content = (await generateZipFromSource(buffer, type)) as string | Blob;
  return downloadContentAsFile(content, `${fileName}.zip`);
}

export { downloadZipFromBuffers, generateZipFromSource };
