import type { LibraryActivityGroup } from "@/types/task/LibraryActivityGroup";
import { useQuery } from "@apollo/client";
import { useContext } from "react";
import Table from "@/components/table/Table";
import { orderByName } from "@/graphql/utils";
import ToastContext from "@/components/shared/toast/context/ToastContext";
import EmptyContent from "@/components/emptyContent/EmptyContent";
import query from "@/graphql/queries/activityGroupsLibrary.gql";
import { sessionExpiryHandlerForApolloClient } from "@/utils/auth";

const columns = [
  {
    Header: "Activity Group Name",
    width: 100,
    accessor: (activityGroup: LibraryActivityGroup) => activityGroup.name,
  },
  {
    Header: "Task Name",
    accessor: (activityGroup: LibraryActivityGroup) => {
      return (activityGroup.tasks ?? []).map(task => (
        <p key={task.id}> {task.name}</p>
      ));
    },
  },
];

const ActivityGroups = () => {
  const toastCtx = useContext(ToastContext);

  const {
    data = { activityGroupsLibrary: [] },
    loading,
    error,
  } = useQuery(query, {
    variables: {
      orderBy: [orderByName],
    },
    onError: _err => {
      sessionExpiryHandlerForApolloClient(_err);
      toastCtx?.pushToast("error", "Error while getting activity groups");
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
    <Table
      columns={columns}
      data={data.activityGroupsLibrary}
      isLoading={loading}
    />
  );
};

export { ActivityGroups };
