import type { ActivityInputs } from "../addActivityModal/AddActivityModal";
import type { Activity } from "@/types/activity/Activity";
import { useMutation, useQuery } from "@apollo/client";
import { useContext } from "react";
import { useForm, FormProvider } from "react-hook-form";
import ActivityConfiguration from "@/components/activity/activityConfiguration/ActivityConfiguration";
import ButtonPrimary from "@/components/shared/button/primary/ButtonPrimary";
import ButtonRegular from "@/components/shared/button/regular/ButtonRegular";
import Modal from "@/components/shared/modal/Modal";
import ToastContext from "@/components/shared/toast/context/ToastContext";
import { useTenantStore } from "@/store/tenant/useTenantStore.store";
import { taskStatusOptions } from "@/types/task/TaskStatus";
import EditActivityMutation from "@/graphql/mutations/activities/editActivity.gql";
import { useProjectSummaryEvents } from "@/container/projectSummaryView/context/ProjectSummaryContext";
import { orderByName } from "@/graphql/utils";
import ActivityTypesLibrary from "@/graphql/queries/activityTypesLibrary.gql";
import { sessionExpiryHandlerForApolloClient } from "@/utils/auth";

type EditActivityModalProps = {
  projectStartDate: string;
  projectEndDate: string;
  activity: Activity;
  onModalClose: () => void;
};

function EditActivityModal({
  activity,
  projectStartDate,
  projectEndDate,
  onModalClose,
}: EditActivityModalProps) {
  const toastCtx = useContext(ToastContext);
  const { activity: activityEntity } = useTenantStore(state =>
    state.getAllEntities()
  );

  const { data: activityTypesLib = [] } = useQuery(ActivityTypesLibrary, {
    variables: {
      orderBy: [orderByName],
    },
  });

  const activityTypes = activityTypesLib?.activityTypesLibrary || [];

  const {
    // eslint-disable-next-line @typescript-eslint/no-unused-vars
    tasks,
    id,
    status: currentStatus,
    libraryActivityType,
    ...defaultValues
  } = activity;

  const methods = useForm<ActivityInputs>({
    mode: "onChange",
    defaultValues: {
      ...defaultValues,
      status: taskStatusOptions.find(e => e.id === currentStatus),
      libraryActivityTypeId: libraryActivityType?.id,
    },
  });

  const {
    formState: { isValid },
  } = methods;

  const events = useProjectSummaryEvents();

  const [mutateActivity, { loading: isLoading }] = useMutation(
    EditActivityMutation,
    {
      onCompleted: () => {
        events.refetchActivitiesBasedOnLocation();
        toastCtx?.pushToast("success", `${activityEntity.label} saved`);
      },
      onError: _err => {
        sessionExpiryHandlerForApolloClient(_err);
        toastCtx?.pushToast(
          "error",
          `Error saving ${activityEntity.label.toLowerCase()}`
        );
      },
    }
  );

  const onSubmitHandler = () => {
    const {
      name,
      startDate,
      endDate,
      status: { id: status },
      libraryActivityTypeId,
      isCritical,
      criticalDescription,
    } = methods.getValues();

    mutateActivity({
      variables: {
        id,
        name,
        startDate,
        endDate,
        status,
        libraryActivityTypeId,
        isCritical,
        criticalDescription: isCritical === true ? criticalDescription : "",
      },
    });
  };

  return (
    <Modal
      isOpen
      title={`Edit ${activityEntity.label}`}
      closeModal={onModalClose}
    >
      <div className="mb-10">
        <FormProvider {...methods}>
          <ActivityConfiguration
            minStartDate={projectStartDate}
            maxEndDate={projectEndDate}
            activityTypeLibrary={activityTypes}
          />
        </FormProvider>
      </div>
      <footer className="flex flex-1 justify-end gap-2">
        <ButtonRegular label="Cancel" onClick={onModalClose} />
        <ButtonPrimary
          label={`Save ${activityEntity.label.toLowerCase()}`}
          onClick={onSubmitHandler}
          loading={isLoading}
          disabled={!isValid}
        />
      </footer>
    </Modal>
  );
}

export { EditActivityModal };
