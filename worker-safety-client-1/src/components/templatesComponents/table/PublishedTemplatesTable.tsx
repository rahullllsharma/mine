import type { TemplatesList } from "../customisedForm.types";
import type { Dispatch, SetStateAction } from "react";
import NextLink from "next/link";
import { useEffect, useMemo, useState } from "react";
import { DateTime } from "luxon";
import Link from "@/components/shared/link/Link";
import Table from "@/components/table/Table";
import { useLocalStorage } from "@/hooks/storage/useStorage";
import PopoverIcon from "../../shared/popover/popoverIcon/PopoverIcon";
import PublishedListAction from "../listActions/publishedListActions";

type PublishedTemplatesTableProps = {
  onView: (id: string) => void;
  onVersionHistory: (templateUUID: string, templateTitle: string) => void;
  setLastVisitedTemplateId: Dispatch<SetStateAction<string>>;
};

const getColumns = ({
  onView,
  onVersionHistory,
  setLastVisitedTemplateId,
}: PublishedTemplatesTableProps) => [
  {
    id: "templateName",
    Header: "Template Name",
    width: 100,
    accessor: (listData: TemplatesList) => {
      return (
        <NextLink href={`/templates/view?templateId=` + listData.id} passHref>
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
    id: "version",
    Header: "Version",
    width: 50,
    accessor: (listData: TemplatesList) => listData?.version,
  },
  {
    id: "publishedBy",
    Header: "Published By",
    width: 80,
    accessor: (listData: TemplatesList) => listData?.published_by?.user_name,
  },
  {
    id: "publishedOn",
    Header: "Published On",
    width: 80,
    accessor: (listData: TemplatesList) =>
      listData?.published_at
        ? DateTime.fromISO(listData?.published_at).toFormat("LLL dd, yyyy")
        : "",
  },
  {
    id: "actions",
    width: 50,
    Header: "Action",
    accessor: (listData: TemplatesList) => (
      <div className="w-full flex 'items-center">
        <PopoverIcon
          iconName="more_horizontal"
          className="right-0 absolute top-0 min-w-[13rem]"
        >
          <PublishedListAction
            id={listData?.id || ""}
            onView={onView}
            onVersionHistory={onVersionHistory}
            uuid={listData?.template_unique_id}
            className={"left-0"}
            templateTitle={listData?.title || ""}
          />
        </PopoverIcon>
      </div>
    ),
  },
];

const PublishedTemplatesTable = ({
  listData,
  onView,
  onVersionHistory,
  isLoading = false,
}: {
  listData: TemplatesList[];
  isLoading?: boolean;
  onView: (id: string) => void;
  onVersionHistory: (templateUUID: string, templateTitle: string) => void;
}): JSX.Element => {
  const {
    store: storeToLocalStorage,
    read: readFromLocalStorage,
    clear: clearFromLocalStorage,
  } = useLocalStorage();

  const [lastVisitedTemplateId, setLastVisitedTemplateId] = useState(
    () => readFromLocalStorage("lastVisitedTemplateId") || ""
  );

  useEffect(() => {
    if (lastVisitedTemplateId) {
      storeToLocalStorage("lastVisitedTemplateId", lastVisitedTemplateId);
    }
  }, [lastVisitedTemplateId, storeToLocalStorage]);

  useEffect(() => {
    return () => clearFromLocalStorage("lastVisitedTemplateId");
  }, [clearFromLocalStorage]);

  const columns = useMemo(
    () =>
      getColumns({
        onView,
        onVersionHistory,
        setLastVisitedTemplateId,
      }),
    [onView, onVersionHistory] 
  );

  return (
    <Table
      columns={columns}
      data={listData}
      isLoading={isLoading}
      lastVisitedRowItemId={lastVisitedTemplateId}
    />
  );
};

export default PublishedTemplatesTable;
