import type { Activity } from "@/types/activity/Activity";
import type { TaskHazardAggregator } from "@/types/project/HazardAggregator";
import type { WithEmptyStateProps } from "../withEmptyState";
import { useState } from "react";
import * as O from "fp-ts/lib/Option";
import { Icon } from "@urbint/silica";
import cx from "classnames";
import Dropdown from "@/components/shared/dropdown/Dropdown";
import ButtonIcon from "@/components/shared/button/icon/ButtonIcon";
import { useTenantStore } from "@/store/tenant/useTenantStore.store";
import { EditActivityModal } from "@/container/activity/editActivityModal/EditActivityModal";
import { DeleteActivityModal } from "@/container/activity/deleteActivityModal/DeleteActivityModal";
import { HistoricIncidentsModal } from "@/container/activity/historicIncidentsModal/HistoricIncidentsModal";
import Tooltip from "@/components/shared/tooltip/Tooltip";
import { ActivityTaskSection } from "./ActivityTaskSection";

type ModalType = null | "edit" | "delete" | "historic";

type ActivitiesProps = WithEmptyStateProps<Activity, TaskHazardAggregator> & {
  projectStartDate: string;
  projectEndDate: string;
  isCardOpen: (element: TaskHazardAggregator) => boolean;
  onCardToggle: (element: TaskHazardAggregator) => void;
};

type ActivityId = Activity["id"];

function Activities({
  elements,
  projectStartDate,
  projectEndDate,
  isCardOpen,
  onCardToggle,
  onElementClick,
}: ActivitiesProps): JSX.Element {
  const { activity: activityEntity } = useTenantStore(state =>
    state.getAllEntities()
  );

  const [selectedActivityId, setSelectedActivityId] = useState<
    ActivityId | undefined
  >(undefined);
  const [selectedTask, setSelectedTask] = useState<
    TaskHazardAggregator | undefined
  >(undefined);

  const [modalOpened, setModalOpened] = useState<ModalType>(null);

  const onModalClose = () => setModalOpened(null);

  const openModal = (activityId: ActivityId, modalType: ModalType) => {
    setSelectedActivityId(activityId);
    setModalOpened(modalType);
  };

  const openIncidentModal = (
    activityId: ActivityId,
    task: TaskHazardAggregator
  ) => {
    setSelectedTask(task);
    openModal(activityId, "historic");
  };

  const getMenuOptions = (activityId: ActivityId) => {
    return [
      [
        {
          label: `Edit ${activityEntity.label}`,
          onClick: () => openModal(activityId, "edit"),
        },
      ],
      [
        {
          label: `Delete ${activityEntity.label}`,
          onClick: () => openModal(activityId, "delete"),
        },
      ],
    ];
  };

  return (
    <>
      {elements.map(({ id, name, tasks = [], isCritical }) => (
        <div key={id} className="mb-6">
          <div className="flex items-center justify-between mb-2">
            <div className="text-sm font-semibold text-neutral-shade-75 flex items-center">
              {name}{" "}
              {isCritical && (
                <Tooltip
                  title={activityEntity.attributes.criticalActivity.label}
                >
                  <Icon
                    name={"warning"}
                    className={cx(
                      "pointer-events-none text-lg bg-transparent ml-1 leading-none"
                    )}
                  />
                </Tooltip>
              )}
            </div>

            <Dropdown className="z-30" menuItems={getMenuOptions(id)}>
              <ButtonIcon iconName="more_horizontal" />
            </Dropdown>
          </div>
          {tasks.map(aggregator => (
            <ActivityTaskSection
              key={aggregator.id}
              task={aggregator}
              isOpen={isCardOpen(aggregator)}
              onToggle={onCardToggle}
              onTaskClicked={onElementClick}
              onHistoricOptionClick={() => openIncidentModal(id, aggregator)}
            />
          ))}
        </div>
      ))}
      {modalOpened === "edit" && (
        <EditActivityModal
          activity={elements.find(e => e.id === selectedActivityId) as Activity}
          onModalClose={onModalClose}
          projectStartDate={projectStartDate}
          projectEndDate={projectEndDate}
        />
      )}
      {modalOpened === "delete" && (
        <DeleteActivityModal
          activityId={selectedActivityId as ActivityId}
          onModalClose={onModalClose}
          onConfirm={O.none}
        />
      )}
      {modalOpened === "historic" && !!selectedTask && (
        <HistoricIncidentsModal
          task={selectedTask}
          onModalClose={onModalClose}
        />
      )}
    </>
  );
}

export { Activities };
export type { ActivitiesProps };
