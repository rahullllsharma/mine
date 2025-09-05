import type { LibraryTask } from "@/types/task/LibraryTask";
import type { WorkType } from "@/types/task/WorkType";
import { useQuery } from "@apollo/client";
import { useContext } from "react";
import Table from "@/components/table/Table";
import { orderByName } from "@/graphql/utils";
import ToastContext from "@/components/shared/toast/context/ToastContext";
import EmptyContent from "@/components/emptyContent/EmptyContent";
import query from "@/graphql/queries/adminTasksLibrary.gql";
import { sessionExpiryHandlerForApolloClient } from "@/utils/auth";

const columns = [
  {
    Header: "ID",
    width: 150,
    accessor: (task: LibraryTask) => task.id,
  },
  {
    Header: "Task type",
    width: 200,
    accessor: (task: LibraryTask) => task.name,
  },
  {
    Header: "Work types",
    accessor: (task: LibraryTask) => {
      return (task.workTypes as WorkType[]).reduce((acc, workType) => {
        return acc + workType.name + ", ";
      }, "");
    },
  },
  {
    Header: "Activity Groups",
    accessor: (task: LibraryTask) => {
      return task.activitiesGroups.map(activity => (
        <p key={activity.name}> {activity.name}</p>
      ));
    },
  },
];

const TaskLibrary = () => {
  const toastCtx = useContext(ToastContext);

  const {
    data = { tasksLibrary: [] },
    loading,
    error,
  } = useQuery(query, {
    variables: {
      orderBy: [orderByName],
    },
    onError: _err => {
      sessionExpiryHandlerForApolloClient(_err);
      toastCtx?.pushToast("error", "Error while getting tasks");
    },
  });

  if (error) {
    return (
      <EmptyContent
        title="Error getting data"
        description="Please contact the engineering team to help troubleshoot the issues"
      />
    );
  }

  return (
    <Table columns={columns} data={data.tasksLibrary} isLoading={loading} />
  );
};

export { TaskLibrary };
