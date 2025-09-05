import type { WorkbookData } from "@/components/fileDownloadDropdown/providers/spreadsheet";

import FilesDownloadDropdown from "@/components/fileDownloadDropdown/FileDownloadDropdown";

type ChartHeaderFileDownloadDropdownProps = {
  chartFilename: string;
  chartData: WorkbookData;
  downloadable?: boolean;
  actionTitle?: string;
};

function HeaderDownloadComponent({
  chartData,
  downloadable = true,
  actionTitle = "",
  chartFilename,
}: ChartHeaderFileDownloadDropdownProps) {
  return (
    <FilesDownloadDropdown
      className="flex-0"
      fileName={chartFilename}
      data={chartData}
      action={{
        title: actionTitle,
        disabled: !downloadable || chartData.length === 0,
      }}
    />
  );
}

type ChartHeaderProps = {
  title: string;
  chartData?: WorkbookData;
  downloadable?: boolean;
  actionTitle?: string;
  chartFilename: string;
};

export default function ChartHeader({
  title,
  ...headerDropdownProps
}: ChartHeaderProps): JSX.Element {
  return (
    <header className="flex flex-nowrap items-center justify-around">
      <h2 className="text-center font-semibold text-xl flex-1">{title}</h2>
      {headerDropdownProps.chartData ? (
        // eslint-disable-next-line @typescript-eslint/ban-ts-comment
        // @ts-ignore
        <HeaderDownloadComponent {...headerDropdownProps} />
      ) : null}
    </header>
  );
}
