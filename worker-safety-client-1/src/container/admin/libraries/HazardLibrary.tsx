import type { LibraryTask } from "@/types/task/LibraryTask";
import { useQuery } from "@apollo/client";
import { useContext } from "react";
import EmptyContent from "@/components/emptyContent/EmptyContent";
import Table from "@/components/table/Table";
import { orderByName } from "@/graphql/utils";
import ToastContext from "@/components/shared/toast/context/ToastContext";
import query from "@/graphql/queries/adminTasksHazardsLibrary.gql";
import { sessionExpiryHandlerForApolloClient } from "@/utils/auth";

const columns = [
  {
    Header: "Task name",
    width: 100,
    accessor: (task: LibraryTask) => task.name,
  },
  {
    Header: "Hazard ",
    accessor: (task: LibraryTask) => {
      return task.hazards.map(hazard => (
        <p key={hazard.id}>
          {hazard.name} - {hazard.id}
        </p>
      ));
    },
  },
];

const HazardsLibrary = () => {
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
      toastCtx?.pushToast("error", "Error while getting tasks and hazards");
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

export { HazardsLibrary };
