import React, { useCallback, useMemo } from "react";
import type { Column } from "react-table";

import Table from "@/components/table/Table";

type ExcelColumnData = {
  column: string;
  exampleData: string;
};

type DataImportPreviewTableProps = {
  data: ExcelColumnData[];
};

export default function DataImportPreviewTable({
  data,
}: DataImportPreviewTableProps) {
  // Helper function to check if a value is empty or invalid
  const isEmptyValue = useCallback(
    (value: string | null | undefined): boolean => {
      return (
        !value ||
        value === "" ||
        value === null ||
        value.toString().indexOf("__EMPTY") > -1 ||
        value.toString().indexOf("NO_COLUMN") > -1
      );
    },
    []
  );

  // Helper function to format display value
  const formatDisplayValue = useCallback(
    (
      value: string | null | undefined,
      fallbackText: string
    ): React.ReactNode => {
      if (isEmptyValue(value)) {
        return <span className="text-red-500 font-medium">{fallbackText}</span>;
      }
      return value?.toString() || fallbackText;
    },
    [isEmptyValue]
  );
  const columns: Column<ExcelColumnData>[] = useMemo(
    () => [
      {
        Header: "Column Header Name",
        width: 150,
        accessor: (previewData: ExcelColumnData) =>
          formatDisplayValue(previewData.column, "NO COLUMN DATA"),
      },
      {
        Header: "Example Data",
        width: 150,
        accessor: (previewData: ExcelColumnData) =>
          formatDisplayValue(previewData.exampleData, "NO ROW DATA"),
      },
    ],
    [formatDisplayValue]
  );

  return <Table columns={columns} data={data} isLoading={false} />;
}
