import type { IngestDataSelectOptionType } from "@/components/shared/inputSelect/InputSelect";
import { useContext } from "react";
import ButtonSecondary from "@/components/shared/button/secondary/ButtonSecondary";
import EmptyContent from "@/components/emptyContent/EmptyContent";
import Table from "@/components/table/Table";
import ToastContext from "@/components/shared/toast/context/ToastContext";

const CsvItems = ({
  selectedOption,
  items,
  delimiter = ",",
}: {
  selectedOption: IngestDataSelectOptionType;
  items: Array<Record<string, unknown>>;
  delimiter: string;
}) => {
  const toastCtx = useContext(ToastContext);
  const columns = selectedOption.columns.map(column => {
    return {
      id: column.attribute,
      Header: column.attribute,
      accessor: column.attribute,
    };
  });

  async function toClipboard(text: string) {
    navigator.clipboard.writeText(text).then(
      () => {
        toastCtx?.pushToast("success", "Data Copied");
      },
      () => {
        toastCtx?.pushToast("error", "Copy Failed");
      }
    );
  }

  function copyToClipboard() {
    const headers = selectedOption.columns.map(column => column.attribute);
    const csvHeaders = headers.join(delimiter);
    const dataRows = items.map((item: Record<string, unknown>) =>
      headers.map(header => item[header]).join(delimiter)
    );
    const csvRows = [csvHeaders].concat(dataRows);
    toClipboard(csvRows.join("\n"));
  }

  return (
    <div>
      {items.length === 0 ? (
        <div>
          <ButtonSecondary onClick={copyToClipboard} label="Copy CSV Headers" />
          <EmptyContent
            title="There is currently no data for this tenant"
            description="If you believe this is an error, please contact the engineering team to help troubleshoot the issues"
          />
        </div>
      ) : (
        <div>
          <ButtonSecondary onClick={copyToClipboard} label={"Copy Data"} />
          <Table columns={columns} data={items} />
        </div>
      )}
    </div>
  );
};

export { CsvItems };
