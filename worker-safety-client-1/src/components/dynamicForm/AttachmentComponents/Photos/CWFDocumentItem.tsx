import type { CWFDocumentItemProps } from "@/components/templatesComponents/customisedForm.types";
import type { MenuItemProps } from "@/components/shared/dropdown/Dropdown";
import React from "react";
import { CaptionText, ComponentLabel, Icon } from "@urbint/silica";
import Dropdown from "@/components/shared/dropdown/Dropdown";

const CWFDocumentItem = ({
  document: { size, displayName, category, date, time },
  readOnly = false,
  onEdit,
  onDownload,
  onDelete,
}: CWFDocumentItemProps): JSX.Element => {
  const convertSizeToMB = (sizeInKB: string): string => {
    if (!sizeInKB) return "";

    const sizeInMB = parseFloat(sizeInKB) / 1024;
    return `${sizeInMB.toFixed(2)} MB`;
  };

  const getDocumentOptions = (): MenuItemProps[][] => {
    const documentOptions: MenuItemProps[][] = [];

    const groupOptions: MenuItemProps[] = [
      {
        label: "Download",
        icon: "download",
        onClick: onDownload,
      },
    ];

    const deleteOptions: MenuItemProps[] = [];

    if (!readOnly) {
      groupOptions.unshift({ label: "Edit", icon: "edit", onClick: onEdit });

      deleteOptions.push({
        label: "Delete",
        icon: "trash_empty",
        onClick: onDelete,
      });
    }

    documentOptions.push(groupOptions);
    if (deleteOptions.length > 0) {
      documentOptions.push(deleteOptions);
    }

    return documentOptions;
  };

  const convertedSize = convertSizeToMB(size);
  const documentDetails = [convertedSize, category, date, time]
    .filter(Boolean)
    .join(" • ");

  return (
    <div
      className="h-14 w-full border border-neutral-shade-38 rounded flex items-center px-2"
      data-testid="document-item"
    >
      <Icon name="file_blank_outline" className="text-2xl" />
      <div className="ml-2 truncate">
        <ComponentLabel>{displayName}</ComponentLabel>
        <CaptionText className="text-xs">{documentDetails}</CaptionText>
      </div>
      <div className="ml-auto">
        <Dropdown className="z-100" menuItems={getDocumentOptions()}>
          <button className="text-xl">
            <Icon name="more_horizontal" />
          </button>
        </Dropdown>
      </div>
    </div>
  );
};

export default CWFDocumentItem;
