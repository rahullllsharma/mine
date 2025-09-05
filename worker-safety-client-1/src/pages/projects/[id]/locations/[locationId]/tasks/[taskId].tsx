import type { Control } from "@/types/project/Control";
import type { Hazard } from "@/types/project/Hazard";
import type { TaskHazardAggregator } from "@/types/project/HazardAggregator";
import type { Project } from "@/types/project/Project";
import type { TaskInputs } from "@/types/task/TaskInputs";
import type { GetServerSideProps } from "next";
import type {
  PageHeaderAction,
  PageHeaderActionTooltip,
} from "@/components/layout/pageHeader/components/headerActions/HeaderActions";
import type { TenantEntityMap } from "@/store/tenant/types";
import { gql, useMutation } from "@apollo/client";
import router from "next/router";
import { useContext, useState } from "react";
import { FormProvider, useForm } from "react-hook-form";
import cx from "classnames";
import { isMobile, isTablet } from "react-device-detect";
import PageFooter from "@/components/layout/pageFooter/PageFooter";
import PageHeader from "@/components/layout/pageHeader/PageHeader";
import PageLayout from "@/components/layout/pageLayout/PageLayout";
import RiskBadge from "@/components/riskBadge/RiskBadge";
import ButtonDanger from "@/components/shared/button/danger/ButtonDanger";
import ButtonRegular from "@/components/shared/button/regular/ButtonRegular";
import Modal from "@/components/shared/modal/Modal";
import ToastContext from "@/components/shared/toast/context/ToastContext";
import {
  authenticatedQuery,
  authGetServerSidePropsProxy,
} from "@/graphql/client";
import TenantLinkedControlsLibrary from "@/graphql/queries/tenantLinkedControlsLibrary.gql";
import DeleteTask from "@/graphql/queries/deleteTask.gql";
import EditTask from "@/graphql/queries/editTask.gql";
import TenantLinkedHazardsLibrary from "@/graphql/queries/tenantLinkedHazardsLibrary.gql";
import Tasks from "@/graphql/queries/tasks.gql";
import { orderByName } from "@/graphql/utils";
import { LibraryFilterType } from "@/types/LibraryFilterType";
import { buildTaskData, isTaskComplete } from "@/utils/task";
import { useGetProjectUrl } from "@/container/projectSummaryView/utils";
import { useTenantStore } from "@/store/tenant/useTenantStore.store";
import { TaskDetails } from "@/components/layout/taskDetails/TaskDetails";
import { sessionExpiryHandlerForApolloClient } from "@/utils/auth";

// FIXME: Should this live here? Why not make this a fragment?
const queryProjectById = gql`
  query Project($projectId: UUID!) {
    project(projectId: $projectId) {
      id
      startDate
      endDate
    }
  }
`;

type TaskDetailsProps = {
  task: TaskHazardAggregator;
  hazardsLibrary: Hazard[];
  controlsLibrary: Control[];
  project: Pick<Project, "id" | "startDate" | "endDate">;
};

type GenerateHeaderActionParams = {
  isCompleted: boolean;
  task: TaskHazardAggregator;
  taskEntity: TenantEntityMap;
  removeTaskHandler: () => void;
};

/** Define the HeaderAction properties based on the Activity status. */
const generateHeaderAction = ({
  isCompleted,
  task,
  taskEntity,
  removeTaskHandler,
}: GenerateHeaderActionParams):
  | PageHeaderActionTooltip
  | PageHeaderAction
  | undefined => {
  if (isCompleted) {
    return {
      type: "tooltip",
      title:
        "This task can't be deleted because the Activity has a status of complete.",
    };
  }

  // Last task from an activity
  if (task.activity?.taskCount === 1) {
    return {
      type: "tooltip",
      title:
        "This task can't be deleted because the Activity must have at least one task. If you want to remove this task, use the option to delete the Activity",
    };
  }

  return {
    icon: "trash_empty",
    title: `Remove ${taskEntity.label.toLowerCase()}`,
    onClick: removeTaskHandler,
  };
};

export default function TaskDetailsViewPage({
  task,
  hazardsLibrary,
  controlsLibrary,
  project: { id },
}: TaskDetailsProps): JSX.Element {
  // By the graphql "contract", a task can have a nullable activity (still doesn't belong to one activity)
  // By the WS app types, the activity is optional. So, we catch any issue and report to DD.
  if (task?.activity === undefined || task.activity === null) {
    throw new Error(`Fail to load task ${task.id}, missing activities`);
  }

  const {
    status,
    startDate: taskStartDate = undefined,
    endDate: taskEndDate = undefined,
  } = task.activity;

  const { workPackage, task: taskEntity } = useTenantStore(state =>
    state.getAllEntities()
  );

  const [deleteTask, { loading: isLoading }] = useMutation(DeleteTask, {
    onCompleted: () => {
      toastCtx?.pushToast("success", `${taskEntity.label} deleted`);
      router.push(projectUrl);
    },
    onError: error => {
      toastCtx?.pushToast(
        "error",
        `Error deleting ${taskEntity.label.toLowerCase()}`
      );
      sessionExpiryHandlerForApolloClient(error);
    },
  });
  const [editTask, { loading: editTaskLoading }] = useMutation(EditTask, {
    onCompleted: () => {
      toastCtx?.pushToast("success", `${taskEntity.label} saved`);
    },
    onError: error => {
      toastCtx?.pushToast(
        "error",
        `Error saving ${taskEntity.label.toLowerCase()}`
      );
      sessionExpiryHandlerForApolloClient(error);
    },
  });
  const toastCtx = useContext(ToastContext);
  const projectUrl = useGetProjectUrl(id);

  const [isModalOpen, setIsModalOpen] = useState(false);
  const form = useForm<TaskInputs>({
    mode: "onChange",
    defaultValues: {
      startDate: taskStartDate,
      endDate: taskEndDate,
      status: {
        id: status,
        name: status,
      },
    },
  });
  const {
    handleSubmit,
    formState: { isDirty, isValid },
  } = form;

  const removeTaskHandler = () => setIsModalOpen(true);
  const closeModalHandler = () => setIsModalOpen(false);
  const deleteTaskHandler = () =>
    deleteTask({
      variables: {
        deleteTaskId: task.id,
      },
    });
  const editTaskHandler = (data: TaskInputs) =>
    editTask({
      variables: {
        taskData: { ...buildTaskData(data), id: task.id },
      },
    });

  const isCompleted = isTaskComplete(status);

  const headerAction = generateHeaderAction({
    isCompleted,
    task,
    taskEntity,
    removeTaskHandler,
  });

  return (
    <PageLayout
      header={
        <PageHeader
          linkText={`${workPackage.label} summary view`}
          linkRoute={projectUrl}
          actions={headerAction}
        >
          <h4 className="text-shade-primary mr-3 w-full sm:w-auto">
            {task.name}
          </h4>
          <RiskBadge risk={task.riskLevel} label={`${task.riskLevel} risk`} />
        </PageHeader>
      }
      footer={
        <PageFooter
          primaryActionLabel="Save"
          isPrimaryActionDisabled={!isDirty || !isValid}
          isPrimaryActionLoading={editTaskLoading}
          onPrimaryClick={handleSubmit(editTaskHandler)}
          className={cx({ ["mb-16"]: isMobile || isTablet })}
        />
      }
    >
      <section className="flex-1 responsive-padding-x">
        <FormProvider {...form}>
          <TaskDetails
            task={task}
            hazardsLibrary={hazardsLibrary}
            controlsLibrary={controlsLibrary}
          />
        </FormProvider>
      </section>

      <Modal
        title="Are you sure you want to do this?"
        isOpen={isModalOpen}
        closeModal={closeModalHandler}
      >
        <div className="mb-10">
          <p>
            {`Deleting this ${taskEntity.label.toLowerCase()} will remove it from all summary views and future reports.`}
          </p>
          <br />
          <p>{`This action will also effect the overall ${workPackage.label.toLowerCase()} risk.`}</p>
        </div>
        <div className="flex justify-end">
          <ButtonRegular
            className="mr-3"
            label="Cancel"
            onClick={closeModalHandler}
          />

          <ButtonDanger
            label={`Delete ${taskEntity.label.toLowerCase()}`}
            onClick={deleteTaskHandler}
            loading={isLoading}
          />
        </div>
      </Modal>
    </PageLayout>
  );
}

export const getServerSideProps: GetServerSideProps = async context =>
  authGetServerSidePropsProxy(context, async () => {
    const { id, taskId } = context.query;

    const {
      data: { project },
    } = await authenticatedQuery(
      {
        query: queryProjectById,
        variables: {
          projectId: id,
        },
      },
      context
    );

    const {
      data: { tasks = [] },
    } = await authenticatedQuery(
      {
        query: Tasks,
        variables: { tasksId: taskId, filterTenantSettings: true },
      },
      context
    );

    const { data: hazardsData = {} } = await authenticatedQuery(
      {
        query: TenantLinkedHazardsLibrary,
        variables: {
          type: LibraryFilterType.TASK,
          orderBy: [orderByName],
        },
      },
      context
    );
    const {
      data: { tenantLinkedControlsLibrary = [] },
    } = await authenticatedQuery(
      {
        query: TenantLinkedControlsLibrary,
        variables: {
          type: LibraryFilterType.TASK,
          orderBy: [orderByName],
        },
      },
      context
    );

    // TODO: Handle errors(400, 404, 500 and error states from queries)

    return {
      props: {
        project,
        task: tasks[0],
        hazardsLibrary: hazardsData.tenantLinkedHazardsLibrary,
        controlsLibrary: tenantLinkedControlsLibrary,
      },
    };
  });
