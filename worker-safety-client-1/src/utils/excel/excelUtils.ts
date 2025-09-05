import * as XLSX from "xlsx";

export type ExcelMetaOnly = {
  rowCount: number;
  columns: string[];
  allData: any[]; // we return this so you can get first row in the component
};

export function parseExcelMetadata(file: File): Promise<ExcelMetaOnly> {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();

    reader.onload = evt => {
      try {
        const binaryStr = evt.target?.result;
        const workbook = XLSX.read(binaryStr, { type: "binary" });
        const sheet = workbook.Sheets[workbook.SheetNames[0]];
        const jsonData = XLSX.utils.sheet_to_json(sheet, { defval: "" });

        const rowCount = jsonData.length;
        const columns =
          rowCount > 0 &&
          typeof jsonData[0] === "object" &&
          jsonData[0] !== null
            ? Object.keys(jsonData[0] as object)
            : [];

        const updatedColumns = columns.map(column => {
          if (column.toString().indexOf("__EMPTY") !== -1) {
            return "NO_COLUMN";
          }
          return column;
        });

        resolve({ rowCount, columns: updatedColumns, allData: jsonData });
      } catch (err) {
        reject(err);
      }
    };

    reader.onerror = reject;
    reader.readAsBinaryString(file);
  });
}
