import type { Insight } from "@/types/insights/Insight";
import type { OnDragEndResponder } from "react-beautiful-dnd";
import type { Column } from "react-table";
import { useMemo } from "react";
import Table from "@/components/table/Table";
import PopoverIcon from "@/components/shared/popover/popoverIcon/PopoverIcon";
import EditInsightMenu from "./EditInsightMenu";

type InsightsTableProps = {
  data: Insight[];
  onEdit: (id: string) => void;
  onDelete: (id: string) => void;
  onReOrder: OnDragEndResponder;
  isLoading?: boolean;
};

const InsightsTable = ({
  data,
  onEdit,
  onDelete,
  onReOrder,
  isLoading = false,
}: InsightsTableProps): JSX.Element => {
  const columns: Column<Insight>[] = useMemo(
    () => [
      {
        Header: "Report Name",
        width: 150,
        accessor: (insight: Insight) => (
          <span className="break-words">{insight.name}</span>
        ),
      },
      {
        Header: "Url",
        width: 300,
        accessor: (insight: Insight) => insight.url,
      },
      {
        Header: "Created On",
        width: 200,
        accessor: (insight: Insight) =>
          new Date(insight.created_at).toLocaleDateString(),
      },
      {
        Header: "Visibility",
        accessor: (insight: Insight) =>
          insight.visibility ? "Visible" : "Not visible",
      },
      {
        id: "actions",
        width: 50,
        accessor: ({ id }: Insight) => (
          <div className="w-full flex justify-end">
            <PopoverIcon iconName="more_horizontal" className="right-0">
              <EditInsightMenu id={id} onEdit={onEdit} onDelete={onDelete} />
            </PopoverIcon>
          </div>
        ),
      },
    ],
    [onEdit, onDelete]
  );

  return (
    <Table
      columns={columns}
      data={data}
      isLoading={isLoading}
      emptyStateMessage="Add an Insights Report"
      reOrderable={true}
      onDragEnd={onReOrder}
    />
  );
};

export default InsightsTable;
