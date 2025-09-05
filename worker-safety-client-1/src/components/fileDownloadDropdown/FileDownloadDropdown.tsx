import type { PropsWithClassName } from "@/types/Generic";
import type { MouseEvent } from "react";
import type { MenuItemProps } from "@/components/shared/dropdown/Dropdown";
import type { SpreadsheetData } from "./hooks/useGenerateSpreadsheet";
import { useState } from "react";
import cx from "classnames";
import Dropdown from "@/components/shared/dropdown/Dropdown";
import { IconSpinner } from "@/components/iconSpinner";
import ButtonIcon from "../shared/button/icon/ButtonIcon";
import useGenerateSpreadsheet from "./hooks/useGenerateSpreadsheet";

type FileTypes = "csv" | "xlsx";

type FileDownloadOptions = {
  isGeneratingFile: boolean;
  hasFileDownloading?: FileTypes;
  handleMenuItemClick: (fileType: FileTypes) => (e: MouseEvent) => void;
};

export type FilesDownloadDropdownProps = Omit<
  PropsWithClassName<{
    data: SpreadsheetData;
    fileName: string;
    label?: string;
    action?: {
      title: string;
      disabled: boolean;
    };
  }>,
  "children"
>;

const getOptionsStatus = ({
  isGeneratingFile,
  hasFileDownloading,
  handleMenuItemClick,
}: FileDownloadOptions): MenuItemProps[][] => {
  const isDownloadingCsvFile = isGeneratingFile && hasFileDownloading === "csv";
  const isDownloadingXlsxFile =
    isGeneratingFile && hasFileDownloading === "xlsx";

  return [
    [
      {
        label: "Export CSV",
        disabled: isGeneratingFile,
        onClick: handleMenuItemClick("csv"),
        rightSlot: (
          <IconSpinner
            className={cx({
              ["invisible"]: !isDownloadingCsvFile,
              ["visible"]: isDownloadingCsvFile,
            })}
          />
        ),
      },
      {
        label: "Export XLSX",
        disabled: isGeneratingFile,
        onClick: handleMenuItemClick("xlsx"),
        rightSlot: (
          <IconSpinner
            className={cx({
              ["invisible"]: !isDownloadingXlsxFile,
              ["visible"]: isDownloadingXlsxFile,
            })}
          />
        ),
      },
    ],
  ];
};

export default function FilesDownloadDropdown({
  fileName = "files",
  label = "Download CSV/XLSX files",
  data,
  className,
  action: { disabled, title } = {
    disabled: false,
    title: "",
  },
}: FilesDownloadDropdownProps): JSX.Element {
  const [isDownloadingFile, setIsDownloadingFile] =
    useState<FileDownloadOptions["hasFileDownloading"]>(undefined);

  const { generateDocument, isLoading } = useGenerateSpreadsheet();

  const handleMenuItemClick: FileDownloadOptions["handleMenuItemClick"] =
    fileType => e => {
      /// Prevent from closing the dropdown when clicking another menu item.
      e.stopPropagation();
      setIsDownloadingFile(fileType);
      generateDocument(data, { fileName, fileType });
    };

  return (
    <Dropdown
      className={cx("inline-block z-30", className)}
      menuItems={getOptionsStatus({
        isGeneratingFile: isLoading,
        hasFileDownloading: isDownloadingFile,
        handleMenuItemClick,
      })}
    >
      <ButtonIcon
        iconName="more_horizontal"
        aria-label={label}
        disabled={disabled}
        title={title}
        className={`w-7 h-7 flex justify-center items-center gap-1 rounded
        hover:bg-neutral-light-16 focus:bg-neutral-shade-7 active:bg-neutral-shade-7`}
      />
    </Dropdown>
  );
}
