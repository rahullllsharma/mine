import type * as xlsx from "xlsx";
import type { DownloadableMetadata } from "@/utils/files/shared";
import { downloadZipFromBuffers } from "@/utils/files/shared";

// internal SheetJs helper types
type SheetJs = typeof xlsx;
type SheetJsUtils = SheetJs["utils"];
type SheetJsWriteFn = SheetJs["write"];

type SheetJsBookType = Parameters<SheetJsWriteFn>[1]["bookType"];
type SheetJsWorkBook = Parameters<SheetJsUtils["book_append_sheet"]>[0];

type SheetJsActions = {
  write: SheetJsWriteFn;
  book_new: SheetJsUtils["book_new"];
  json_to_sheet: SheetJsUtils["json_to_sheet"];
  book_append_sheet: SheetJsUtils["book_append_sheet"];
};

type WorkbookCellValue = string | number | undefined;
type WorkbookCell = { [k: string]: WorkbookCellValue } | WorkbookCellValue;

export type WorkbookSupportedFileTypes = "csv" | "xlsx" | "xls";
export type WorkbookData = [string, WorkbookCell[]][];
export type WorkbookDataOptions = {
  fileName: string;
  fileType: WorkbookSupportedFileTypes;
};

type CreateWorkbookReturnType = (DownloadableMetadata | SheetJsWorkBook)[];

type CreateWorkbookArgs = {
  multiple: boolean;
  bookType: SheetJsBookType;
};

/**
 * Trim the worksheet title to just 30 chars
 *
 * Known limitation by the spreadsheets formats.
 * @see https://stackoverflow.com/questions/70065014/xlsx-sheetname-exceeding-31-characters-in-length-in-react
 */
const trimWorksheetTitle = (title: string) =>
  title.length < 30 ? title : `${title.substr(0, 27)}...`;

/** Create a workbook in memory. Returns an array of workbooks */
const createWorkbook = (
  data: WorkbookData,
  { book_new, json_to_sheet, book_append_sheet, write }: SheetJsActions,
  { multiple = false, bookType = "csv" }: CreateWorkbookArgs
) => {
  let workbook = book_new();
  return data.reduce((workbooks, [sheet, sheetData]) => {
    book_append_sheet(
      workbook,
      json_to_sheet(sheetData),
      trimWorksheetTitle(sheet)
    );

    if (multiple) {
      workbooks.push({
        file: `${sheet}.${bookType}`,
        content: write(workbook, {
          type: "binary",
          bookType,
        }),
      });

      // restart workbook to create a new file
      workbook = book_new();
    } else {
      workbooks.push(workbook);
    }

    return workbooks;
  }, [] as CreateWorkbookReturnType);
};

/**
 * Generate the workbook(s) and download them.
 * If the format doesn't support multiple worksheets, it will compress all files to a single zip.
 */
const generateDownloadableWorkbook = async (
  data: WorkbookData,
  { fileName, fileType }: WorkbookDataOptions
): Promise<void> => {
  const {
    utils: { book_new, json_to_sheet, book_append_sheet },
    writeFile,
    write,
  } = await import(
    /* webpackChunkName: "vendors~sheetjs-ce" */
    "xlsx"
  );

  const shouldDownloadAsZip = fileType === "csv" && data.length > 1;

  // Generate the workbook ready for download or an array of buffer with multiple files to download.
  const workbooks = createWorkbook(
    data,
    { book_new, json_to_sheet, book_append_sheet, write },
    {
      bookType: fileType,
      multiple: shouldDownloadAsZip,
    }
  );

  // Download the file(s)
  if (!shouldDownloadAsZip || workbooks.length === 1) {
    writeFile(workbooks[0] as SheetJsWorkBook, `${fileName}.${fileType}`, {
      type: "binary",
      bookType: fileType,
    });
  } else {
    await downloadZipFromBuffers(workbooks as DownloadableMetadata[], fileName);
  }
};

export { generateDownloadableWorkbook };
