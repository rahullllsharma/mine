import type {
  WorkbookData,
  WorkbookDataOptions,
} from "../providers/spreadsheet";
import { useState } from "react";
import { generateDownloadableWorkbook } from "../providers/spreadsheet";

//** Private types */
type GenerateSpreadsheetStatus = "idle" | "loading" | "error" | "complete";
type GenerateSpreadsheetReturnType = {
  generateDocument: (
    data: WorkbookData,
    { fileName, fileType }: WorkbookDataOptions
  ) => Promise<void>;
  isLoading: boolean;
  isCompleted: boolean;
  isError: boolean;
};

//** Public types */
export type SpreadsheetData = WorkbookData;

export default function useGenerateSpreadsheet(): GenerateSpreadsheetReturnType {
  const [status, setStatus] = useState<GenerateSpreadsheetStatus>("idle");

  const generateDocument = async (
    data: WorkbookData,
    { fileName, fileType }: WorkbookDataOptions
  ) => {
    if (status === "loading") {
      console.warn("Another file is already processing ... please wait.");
      return;
    }

    setStatus("loading");

    if (!Array.isArray(data)) {
      setStatus("error");
      // TODO: dispatch to rum/sentry
      throw new Error("invalid data");
    }

    try {
      await generateDownloadableWorkbook(data, {
        fileName,
        fileType,
      });

      setStatus("complete");
    } catch (err) {
      setStatus("error");
      // TODO: dispatch to rum/sentry
      console.error({ err });
      throw new Error("unable to parse the document");
    }
  };

  return {
    generateDocument,
    get isLoading() {
      return status === "loading";
    },
    get isCompleted() {
      return status === "complete";
    },
    get isError() {
      return status === "error";
    },
  };
}
