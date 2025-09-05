import type { TaskHazardAggregator } from "@/types/project/HazardAggregator";
import NextLink from "next/link";
import { useRouter } from "next/router";
import { getUpdatedRouterQuery } from "@/utils/router";
import { taskStatusOptions } from "@/types/task/TaskStatus";
import { ProjectViewTab } from "@/types/project/ProjectViewTabs";
import { useTenantStore } from "@/store/tenant/useTenantStore.store";
import Link from "../shared/link/Link";
import CardRow from "../cardItem/cardRow/CardRow";

type TaskCardProps = {
  projectId: string;
  locationId: string;
  task: TaskHazardAggregator;
};

const regex = new RegExp(/\-/g);

//This component is temporary. We should define a Card Layout and reuse it across all application
export default function TaskCard({
  projectId,
  locationId,
  task,
}: TaskCardProps): JSX.Element {
  const { task: taskEntity } = useTenantStore(state => state.getAllEntities());
  const router = useRouter();
  const { id, name, activity, libraryTask } = task;
  const { status } = activity || {};

  const startDate = activity?.startDate.replace(regex, "/");
  const endDate = activity?.endDate.replace(regex, "/");

  const query = getUpdatedRouterQuery(
    { id: projectId, locationId, taskId: id, activeTab: ProjectViewTab.TASKS },
    { key: "source", value: router.query.source }
  );

  return (
    <div className="flex flex-col rounded bg-white shadow-5 p-3">
      <header className="mb-2">
        <NextLink
          href={{
            pathname: "/projects/[id]/locations/[locationId]/tasks/[taskId]",
            query,
          }}
          passHref
        >
          {/* Link component was modified to allow text wrapping (default was truncate)
            If this feature is not needed in the new Card Layout, it should be reverted */}
          <Link label={name} allowWrapping />
        </NextLink>
      </header>
      <CardRow label={`${taskEntity.label} category`}>
        <span className="truncate">{libraryTask?.category}</span>
      </CardRow>
      <CardRow label="Status">
        {taskStatusOptions.find(option => option.id === status)?.name}
      </CardRow>
      <CardRow label="Start - End dates">{`${startDate} - ${endDate}`}</CardRow>
    </div>
  );
}
