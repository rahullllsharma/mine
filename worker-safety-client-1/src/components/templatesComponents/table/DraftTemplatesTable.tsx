import type { TemplatesList } from "../customisedForm.types";
import type { Dispatch, SetStateAction } from "react";
import NextLink from "next/link";
import { useEffect, useState } from "react";
import { DateTime } from "luxon";
import Link from "@/components/shared/link/Link";
import Table from "@/components/table/Table";
import { useLocalStorage } from "@/hooks/storage/useStorage";
import PopoverIcon from "../../shared/popover/popoverIcon/PopoverIcon";
import DraftListAction from "../listActions/draftListActions";

type DraftTemplatesTableProps = {
  onPublishTemplate: (id: string) => void;
  onEdit: (id: string) => void;
  setLastVisitedTemplateId: Dispatch<SetStateAction<string>>;
};

const getColumns = ({
  onEdit,
  onPublishTemplate,
  setLastVisitedTemplateId,
}: DraftTemplatesTableProps) => [
  {
    id: "templateName",
    Header: "Template Name",
    width: 120,
    // eslint-disable-next-line react/display-name
    accessor: (listData: TemplatesList) => {
      return (
        <NextLink href={`/templates/create?templateId=` + listData.id} passHref>
          <Link
            label={
              listData?.title ? listData?.title : ""
            }
            target="_blank"
            onClick={() => setLastVisitedTemplateId(listData.id)}
            allowWrapping
          />
        </NextLink>
      );
    },
  },
  {
    id: "lastUpdatedBy",
    Header: "Last Updated By",
    width: 100,
    accessor: (listData: TemplatesList) => listData?.updated_by?.user_name,
  },
  {
    id: "lastUpdatedOn",
    Header: "Last Updated On",
    width: 100,
    accessor: (listData: TemplatesList) =>
      listData?.updated_at
        ? DateTime.fromISO(listData?.updated_at).toFormat("LLL dd, yyyy")
        : "",
  },
  {
    id: "actions",
    width: 50,
    Header: "Action",
    accessor: (listData: TemplatesList) => (
      <div className="w-full flex items-center">
        <PopoverIcon
          iconName="more_horizontal"
          className="right-0 absolute top-8 min-w-[13rem]"
        >
          <DraftListAction
            id={listData?.id || ""}
            onEdit={onEdit}
            onPublishTemplate={onPublishTemplate}
          />
        </PopoverIcon>
      </div>
    ),
  },
];

export default function DraftTemplatesTable({
  listData,
  isLoading = false,
  onPublishTemplate,
  onEdit,
}: {
  listData: TemplatesList[];
  isLoading?: boolean;
  onPublishTemplate: (id: string) => void;
  onEdit: (id: string) => void;
}): JSX.Element {
  const {
    store: storeToLocalStorage,
    read: readFromLocalStorage,
    clear: clearFromLocalStorage,
  } = useLocalStorage();

  const [lastVisitedTemplateId, setLastVisitedTemplateId] = useState(
    readFromLocalStorage("lastVisitedTemplateId")
  );

  useEffect(() => {
    return () => clearFromLocalStorage("lastVisitedTemplateId");
  }, [clearFromLocalStorage]);

  useEffect(() => {
    storeToLocalStorage("lastVisitedTemplateId", lastVisitedTemplateId);
  }, [storeToLocalStorage, lastVisitedTemplateId]);

  const columns = getColumns({
    onEdit,
    onPublishTemplate,
    setLastVisitedTemplateId: setLastVisitedTemplateId,
  });

  return (
    <Table
      columns={columns}
      data={listData}
      isLoading={isLoading}
      lastVisitedRowItemId={lastVisitedTemplateId}
    />
  );
}
