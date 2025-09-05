import type { ProjectTasksProps } from "../projectSummaryView/tasks/ProjectTasks";
import type { TaskHazardAggregator } from "@/types/project/HazardAggregator";
import NextLink from "next/link";
import { useRouter } from "next/router";
import Link from "@/components/shared/link/Link";
import Table from "@/components/table/Table";
import { ProjectViewTab } from "@/types/project/ProjectViewTabs";
import { taskStatusOptions } from "@/types/task/TaskStatus";
import { getUpdatedRouterQuery } from "@/utils/router";
import { useTenantStore } from "@/store/tenant/useTenantStore.store";

type TaskTableProps = ProjectTasksProps;

const getColumns = (
  projectId: string,
  locationId: string,
  taskLabel: string,
  source?: string
) => {
  return [
    {
      id: "taskName",
      Header: `${taskLabel} Name`,
      width: 280,
      // eslint-disable-next-line react/display-name
      accessor: ({ id, name }: TaskHazardAggregator) => {
        const query = getUpdatedRouterQuery(
          {
            id: projectId,
            locationId,
            taskId: id,
            activeTab: ProjectViewTab.TASKS,
          },
          { key: "source", value: source }
        );
        return (
          <NextLink
            href={{
              pathname: "/projects/[id]/locations/[locationId]/tasks/[taskId]",
              query,
            }}
            passHref
          >
            <Link label={name} />
          </NextLink>
        );
      },
    },
    {
      id: "taskCategory",
      Header: `${taskLabel} category`,
      width: 180,
      accessor: (task: TaskHazardAggregator) => task.libraryTask?.category,
    },
    {
      id: "status",
      Header: "Status",
      width: 120,
      accessor: (task: TaskHazardAggregator) =>
        taskStatusOptions.find(option => option.id === task.activity?.status)
          ?.name,
    },
    {
      id: "startDate",
      Header: "Start Date",
      width: 100,
      accessor: (task: TaskHazardAggregator) => task.activity?.startDate,
    },
    {
      id: "endDate",
      Header: "End Date",
      width: 100,
      accessor: (task: TaskHazardAggregator) => task.activity?.endDate,
    },
  ];
};

export default function TaskTable({
  projectId,
  locationId,
  tasks,
}: TaskTableProps): JSX.Element {
  const { task } = useTenantStore(state => state.getAllEntities());
  const source = useRouter().query.source as string;
  return (
    <Table
      columns={getColumns(projectId, locationId, task.label, source)}
      data={tasks}
    />
  );
}
