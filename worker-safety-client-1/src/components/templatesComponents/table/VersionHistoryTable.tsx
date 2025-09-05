import { DateTime } from "luxon";
import Table from "@/components/table/Table";
import PopoverIcon from "../../shared/popover/popoverIcon/PopoverIcon";
import VersionHistoryListAction from "../listActions/versionHistoryListActions";
import { TemplatesList } from "../customisedForm.types";

type PublishedTemplatesTableProps = {
  onView: (id: string) => void;
};

const getColumns = ({ onView }: PublishedTemplatesTableProps) => [
  {
    id: "version",
    Header: "Version",
    width: 50,
    accessor: (listData: TemplatesList) => listData?.version,
  },
  {
    id: "publishedBy",
    Header: "PublishedBy",
    width: 80,
    accessor: (listData: TemplatesList) => listData?.published_by?.user_name,
  },
  {
    id: "publishedOn",
    Header: "PublishedOn",
    width: 80,
    accessor: (listData: TemplatesList) =>
      listData?.published_at
        ? DateTime.fromISO(listData?.published_at).toFormat("MM-dd-yyyy")
        : "",
  },
  {
    id: "actions",
    width: 50,
    Header: "Action",
    accessor: ({ id }: any) => (
      <div className="w-full flex relative">
        <PopoverIcon
          iconName="more_horizontal"
          className="right-0 relative bottom-8 mt-0"
        >
          <VersionHistoryListAction id={id} onView={onView} />
        </PopoverIcon>
      </div>
    ),
  },
];

const VersionHistoryTable = ({
  listData,
  onView,
  isLoading = false,
}: {
  listData: TemplatesList[];
  isLoading?: boolean;
  onView: (id: string) => void;
}): JSX.Element => {
  const columns = getColumns({ onView });

  return <Table columns={columns} data={listData} isLoading={isLoading} />;
};

export default VersionHistoryTable;
