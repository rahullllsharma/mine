import type { IngestDataSelectOptionType } from "@/components/shared/inputSelect/InputSelect";
import type { Column } from "react-table";
import Table from "@/components/table/Table";

const CsvMetadata = ({
  selectedOption,
}: {
  selectedOption: IngestDataSelectOptionType;
}) => {
  const columns: Column<{
    attribute: string;
    requiredOnIngest: string;
    ignoreOnIngest: string;
  }>[] = [
    { id: "attribute", Header: "column header", accessor: "attribute" },
    {
      id: "requiredOnIngest",
      Header: "required",
      accessor: "requiredOnIngest",
    },
    { id: "ignoreOnIngest", Header: "ignored", accessor: "ignoreOnIngest" },
  ];

  const data = selectedOption.columns.map(column => {
    return {
      attribute: column.attribute,
      requiredOnIngest: column.requiredOnIngest ? "*" : "",
      ignoreOnIngest: column.ignoreOnIngest ? "*" : "",
    };
  });

  return (
    <div className="mt-20">
      CSV columns
      <Table columns={columns} data={data} />
    </div>
  );
};

export { CsvMetadata };
