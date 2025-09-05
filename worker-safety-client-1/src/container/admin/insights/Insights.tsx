import type { Insight, InsightFormInputs } from "@/types/insights/Insight";
import type { OnDragEndResponder } from "react-beautiful-dnd";
import { useQueryClient } from "@tanstack/react-query";
import { useCallback, useContext, useEffect, useState } from "react";
import { differenceWith, fromPairs, isEqual, toPairs } from "lodash-es";
import { BodyText, SectionHeading } from "@urbint/silica";
import { QUERY_KEYS } from "@/api/restApi";
import EmptyContent from "@/components/emptyContent/EmptyContent";
import ButtonPrimary from "@/components/shared/button/primary/ButtonPrimary";
import ToastContext from "@/components/shared/toast/context/ToastContext";
import useRestMutation from "@/hooks/useRestMutation";
import useRestQuery from "@/hooks/useRestQuery";
import AddInsightModal from "./AddInsightModal";
import DeleteInsightConfirmationModal from "./DeleteInsightConfirmationModal";
import InsightsTable from "./InsightsTable";

const Insights = () => {
  const [isAddInsightModalOpen, setIsAddInsightModalOpen] = useState(false);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [toDeleteId, setToDeleteId] = useState<string | null>(null);
  const [isDeleteConfirmationModalOpen, setIsDeleteConfirmationModalOpen] =
    useState(false);

  const toastCtx = useContext(ToastContext);
  const queryClient = useQueryClient();

  const openAddInsightModal = () => {
    setIsAddInsightModalOpen(true);
  };

  const closeAddInsightModal = () => {
    setIsAddInsightModalOpen(false);
    setSelectedId(null);
  };

  const openDeleteConfirmationModal = () => {
    setIsDeleteConfirmationModalOpen(true);
  };

  const closeDeleteConfirmationModal = () => {
    setIsDeleteConfirmationModalOpen(false);
    setToDeleteId(null);
  };

  const {
    data: insights,
    isLoading,
    error,
  } = useRestQuery<
    { data: { attributes: Insight; id: string }[] },
    { data: Insight[] }
  >({
    key: [QUERY_KEYS.INSIGHTS],
    endpoint: "/insights",
    axiosConfig: {
      params: {
        "page[limit]": 100,
      },
    },
    queryOptions: {
      select(data) {
        return {
          data: data.data?.map(dt => ({ ...dt.attributes, id: dt.id })) || [],
        };
      },
    },
  });

  const {
    mutate: addInsight,
    isLoading: isAdding,
    error: addError,
  } = useRestMutation<InsightFormInputs>({
    endpoint: "/insights",
    method: "post",
    dtoFn: data => ({
      data: {
        attributes: { ...data },
      },
      type: "insight",
    }),
    mutationOptions: {
      onSuccess: () => {
        toastCtx?.pushToast("success", "Insight added successfully");
        queryClient.refetchQueries({ queryKey: [QUERY_KEYS.INSIGHTS] });
      },
    },
  });

  const {
    mutate: updateInsight,
    isLoading: isUpdating,
    error: updateError,
  } = useRestMutation<{ data: Partial<InsightFormInputs>; id: string }>({
    endpoint: data => `/insights/${data.id}`,
    method: "put",
    dtoFn: data => ({
      data: {
        attributes: { ...data.data },
      },
      type: "insight",
    }),
    mutationOptions: {
      onSuccess: () => {
        toastCtx?.pushToast("success", "Insight updated successfully");
        queryClient.refetchQueries({ queryKey: [QUERY_KEYS.INSIGHTS] });
      },
    },
  });

  const {
    mutate: deleteInsight,
    isLoading: isDeleting,
    error: deleteError,
  } = useRestMutation<{ id: string }>({
    endpoint: data => `/insights/${data.id}`,
    method: "delete",
    mutationOptions: {
      onSuccess: () => {
        closeDeleteConfirmationModal();
        toastCtx?.pushToast("success", "Insight deleted successfully");
        queryClient.refetchQueries({ queryKey: [QUERY_KEYS.INSIGHTS] });
      },
    },
  });

  const { mutate: reorderInsights, error: reorderError } = useRestMutation<{
    ids: string[];
  }>({
    endpoint: "/insights/reorder/",
    method: "put",
    dtoFn: data => data.ids,
    mutationOptions: {
      // Optimistic update
      onMutate: async ({ ids: newInsightIds }) => {
        // Cancel any outgoing refetches
        // (so they don't overwrite our optimistic update)
        await queryClient.cancelQueries({ queryKey: [QUERY_KEYS.INSIGHTS] });

        // Snapshot the previous value
        const previousInsightsData = queryClient.getQueryData([
          QUERY_KEYS.INSIGHTS,
        ]) as {
          data: { attributes: Insight; id: string }[];
        };

        // Optimistically update to the new value
        queryClient.setQueryData([QUERY_KEYS.INSIGHTS], () => ({
          data: newInsightIds.map(id =>
            previousInsightsData.data.find(insight => insight.id === id)
          ),
        }));

        // Return a context object with the snapshotted value
        return { previousInsightsData };
      },
      // If the mutation fails,
      // use the context returned from onMutate to roll back
      onError: (err, _, context) => {
        queryClient.setQueryData(
          [QUERY_KEYS.INSIGHTS],
          (
            context as {
              previousInsightsData: {
                data: { attributes: Insight; id: string }[];
              };
            }
          ).previousInsightsData
        );
      },
      onSettled: () => {
        queryClient.refetchQueries({ queryKey: [QUERY_KEYS.INSIGHTS] });
      },
    },
  });

  const handleAddInsightSubmit = (data: InsightFormInputs) => {
    if (selectedId) {
      const changes = fromPairs(
        differenceWith(
          toPairs(data),
          toPairs(
            insights?.data.find(insight => insight.id === selectedId) || {}
          ),
          isEqual
        )
      );
      updateInsight({ data: { ...changes }, id: selectedId });
      return;
    }

    addInsight(data);
  };

  const onEdit = useCallback((id: string) => {
    setSelectedId(id);
    setTimeout(() => {
      openAddInsightModal();
    }, 100);
  }, []);

  const onDeleteRequest = useCallback((id: string) => {
    setToDeleteId(id);
    closeAddInsightModal();
    openDeleteConfirmationModal();
  }, []);

  const onDelete = useCallback(
    (id: string) => {
      deleteInsight({ id });
    },
    [deleteInsight]
  );

  const onReOrder: OnDragEndResponder = useCallback(
    result => {
      const { source, destination, draggableId } = result;

      if (!destination) {
        return;
      }

      if (source.index === destination.index) {
        return;
      }

      if (!insights) {
        return;
      }

      const newInsights = insights.data.map(insight => insight.id) || [];
      newInsights.splice(source.index, 1);
      newInsights.splice(destination.index, 0, insights.data[+draggableId]?.id);
      reorderInsights({ ids: newInsights });
    },
    [insights, reorderInsights]
  );

  useEffect(() => {
    const errorMessage =
      error || addError || updateError || deleteError || reorderError;
    if (errorMessage) {
      toastCtx?.pushToast("error", errorMessage);
    }

    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [error, addError, updateError, deleteError, reorderError]);

  return (
    <div className="flex flex-col flex-1 overflow-hidden">
      <header className="text-neutral-shade-100 flex justify-between items-start mb-8">
        <div>
          <SectionHeading className="text-xl font-semibold">
            Insights
          </SectionHeading>
          <BodyText className="text-base">
            Create and modify Insights for your organization
          </BodyText>
        </div>
        <ButtonPrimary
          label="Add Insights"
          size="lg"
          onClick={openAddInsightModal}
        />
      </header>
      <div className="flex flex-1 overflow-hidden">
        {error ? (
          <EmptyContent
            title="Error getting data"
            description="Please contact the engineering team to help troubleshoot the issues"
          />
        ) : (
          <InsightsTable
            data={insights?.data || []}
            onEdit={onEdit}
            onDelete={onDeleteRequest}
            onReOrder={onReOrder}
            isLoading={isLoading}
          />
        )}
      </div>
      <AddInsightModal
        isOpen={isAddInsightModalOpen}
        onClose={closeAddInsightModal}
        onSubmit={handleAddInsightSubmit}
        defaultValues={
          selectedId
            ? insights?.data.find(insight => insight.id === selectedId)
            : undefined
        }
        onDelete={onDeleteRequest}
        isSubmitting={isAdding || isUpdating}
      />
      <DeleteInsightConfirmationModal
        isOpen={isDeleteConfirmationModalOpen}
        onClose={closeDeleteConfirmationModal}
        onSubmit={onDelete}
        id={toDeleteId}
        isDeleting={isDeleting}
      />
    </div>
  );
};

export default Insights;
