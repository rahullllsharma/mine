import type { UploadItem } from "@/components/upload/Upload";
import type { DailyReportInputs } from "@/types/report/DailyReportInputs";
import type { DownloadableMetadata } from "@/utils/files/shared";
import { nanoid } from "nanoid";
import asyncBatch from "async-batch";
import { appendToFilename } from "@/utils/shared";

/** total requests in parallel in batch */
const batchMaxRequests = 1;

const getReportDocuments = (sections: DailyReportInputs): UploadItem[] => {
  const crewDocuments = sections.crew?.documents || [];
  const attachmentDocuments = sections.attachments?.documents || [];
  const attachmentPhotos = sections.attachments?.photos || [];

  return [...crewDocuments, ...attachmentDocuments, ...attachmentPhotos];
};

const getFileName = (
  displayName: string,
  attachments: DownloadableMetadata[]
) => {
  const isDuplicated =
    attachments.filter(attachment => attachment.file === displayName).length !==
    1;

  return `attachments/${
    isDuplicated ? appendToFilename(displayName, `_${nanoid(6)}`) : displayName
  }`;
};

/**
 * Fetches all the daily reports attachments.
 *
 * @param sections
 * @returns
 */
const getDailyReportAttachments = async (
  sections: DailyReportInputs
): Promise<DownloadableMetadata[]> => {
  const attachments: DownloadableMetadata[] = [];

  const documents = getReportDocuments(sections);

  await asyncBatch(
    documents,
    async document => {
      const file = await fetch(document.signedUrl);
      const attach = {
        file: document.displayName,
        content: Buffer.from(await file.arrayBuffer()),
      };

      attachments.push(attach);
    },
    batchMaxRequests
  );

  // since the async batch is async, it will not fill the attachments array in sequence so we need to format after all attachment information is fetched.
  return attachments.map((attachment, index, allAttachments) => ({
    ...attachment,
    file: getFileName(attachment.file, allAttachments),
  }));
};

export { getDailyReportAttachments };
