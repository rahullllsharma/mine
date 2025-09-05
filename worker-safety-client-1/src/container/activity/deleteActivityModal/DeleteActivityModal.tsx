import type { Activity } from "@/types/activity/Activity";
import { useMutation } from "@apollo/client";
import { useContext } from "react";
import { pipe } from "fp-ts/function";
import * as O from "fp-ts/lib/Option";
import ButtonDanger from "@/components/shared/button/danger/ButtonDanger";
import ButtonRegular from "@/components/shared/button/regular/ButtonRegular";
import Modal from "@/components/shared/modal/Modal";
import { useTenantStore } from "@/store/tenant/useTenantStore.store";
import DeleteActivityMutation from "@/graphql/mutations/activities/deleteActivity.gql";
import ToastContext from "@/components/shared/toast/context/ToastContext";
import { useProjectSummaryEvents } from "@/container/projectSummaryView/context/ProjectSummaryContext";
import { sessionExpiryHandlerForApolloClient } from "@/utils/auth";

type DeleteActivityModalProps = {
  activityId: Activity["id"];
  onModalClose: () => void;
  onConfirm: O.Option<() => void>;
};

function DeleteActivityModal({
  activityId,
  onModalClose,
  onConfirm,
}: DeleteActivityModalProps) {
  const toastCtx = useContext(ToastContext);
  const {
    activity: activityEntity,
    workPackage,
    task,
  } = useTenantStore(state => state.getAllEntities());
  const events = useProjectSummaryEvents();
  const [deleteActivity, { loading: isLoading }] = useMutation(
    DeleteActivityMutation,
    {
      onCompleted: () => {
        events.refetchActivitiesBasedOnLocation();
        toastCtx?.pushToast("success", `${activityEntity.label} deleted`);
      },
      onError: _err => {
        sessionExpiryHandlerForApolloClient(_err);
        toastCtx?.pushToast(
          "error",
          `Error deleting ${activityEntity.label.toLowerCase()}`
        );
      },
    }
  );

  const modalConfirmHandler = () => {
    deleteActivity({
      variables: {
        id: activityId,
      },
    });
  };

  return (
    <Modal
      isOpen
      title="Are you sure you want to do this?"
      closeModal={onModalClose}
    >
      <div className="mb-10">
        <p className="mb-5 sentence">{`Deleting this ${activityEntity.label} will remove all the associated ${task.label} as well as remove it from any future reports.`}</p>
        <p className="sentence">{`This action will also affect the overall ${workPackage.label} risk.`}</p>
      </div>
      <div className="flex justify-end gap-3">
        <ButtonRegular label="Cancel" onClick={onModalClose} />
        <ButtonDanger
          label={`Delete ${activityEntity.label.toLowerCase()}`}
          onClick={pipe(
            onConfirm,
            O.fold(
              () => modalConfirmHandler,
              a => a
            )
          )}
          loading={isLoading}
        />
      </div>
    </Modal>
  );
}

export { DeleteActivityModal };
