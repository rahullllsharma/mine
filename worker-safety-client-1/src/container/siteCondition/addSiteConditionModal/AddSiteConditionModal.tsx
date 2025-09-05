import type { ModalSize } from "@/components/shared/modal/Modal";
import type { SiteConditionInputs } from "@/types/siteCondition/SiteConditionInputs";
import type { InputSelectOption } from "@/components/shared/inputSelect/InputSelect";
import type { HazardAggregator } from "@/types/project/HazardAggregator";
import type { LibrarySiteCondition } from "@/types/siteCondition/LibrarySiteCondition";
import type { WorkType } from "@/types/task/WorkType";
import cx from "classnames";
import { gql, useLazyQuery, useMutation, useQuery } from "@apollo/client";
import { useContext, useMemo, useState } from "react";
import {
  Controller,
  FormProvider,
  useForm,
  useFormContext,
} from "react-hook-form";
import differenceWith from "lodash-es/differenceWith";
import Loader from "@/components/shared/loader/Loader";
import Modal from "@/components/shared/modal/Modal";
import ButtonRegular from "@/components/shared/button/regular/ButtonRegular";
import ButtonPrimary from "@/components/shared/button/primary/ButtonPrimary";
import SiteConditionDetailsForm from "@/components/detailsForm/siteConditionDetailsForm/SiteConditionDetailsForm";
import HazardsControlsLibrary from "@/graphql/queries/hazardsControlsLibrary.gql";
import { LibraryFilterType } from "@/types/LibraryFilterType";
import ToastContext from "@/components/shared/toast/context/ToastContext";
import FieldSearchSelect from "@/components/shared/field/fieldSearchSelect/FieldSearchSelect";
import { orderByName } from "@/graphql/utils";
import { useTenantStore } from "@/store/tenant/useTenantStore.store";
import WorkTypeSiteConditionsLibrary from "@/graphql/queries/workTypeSiteConditionsLibrary.gql";

const showDetailsTimeout = 350;

function SiteConditionTypeSelection({
  siteConditionLibrary,
}: {
  siteConditionLibrary: InputSelectOption[];
}): JSX.Element {
  const { location, siteCondition } = useTenantStore(state =>
    state.getAllEntities()
  );

  useFormContext();

  return (
    <Controller
      name="librarySiteConditionId"
      rules={{ required: true }}
      render={({ field: { onChange } }) => (
        <FieldSearchSelect
          label={siteCondition.label}
          caption={`Any ${siteCondition.labelPlural.toLowerCase()} added will apply indefinitely to your
            ${location.label.toLowerCase()} until removed.`}
          options={siteConditionLibrary}
          onSelect={option => onChange(option.id)}
        />
      )}
    />
  );
}

const addSiteConditionMutation = gql`
  mutation Mutation($siteConditionData: CreateSiteConditionInput!) {
    createSiteCondition(data: $siteConditionData) {
      id
    }
  }
`;

enum AddSiteConditionStep {
  INITIAL,
  LOADING,
  SHOW_DETAILS,
}

/**
 * Return an array of site conditions available to add by excluding the site conditions already in use
 *
 * @param library
 * @param siteConditionsInUse
 */
const excludeSiteConditions = (
  library: LibrarySiteCondition[] = [],
  siteConditionsInUse: HazardAggregator[] = []
) => {
  return differenceWith(
    library,
    siteConditionsInUse,
    (siteConditionLibrary, inUse) =>
      siteConditionLibrary.id ===
      (inUse.librarySiteCondition as LibrarySiteCondition).id
  );
};

export type AddSiteConditionModalProps = {
  isOpen: boolean;
  closeModal: () => void;
  locationId: string;
  addSiteConditionSuccessHandler: () => void;
  siteConditions: HazardAggregator[];
  projectWorkTypes?: WorkType[];
};

export default function AddSiteConditionModal({
  isOpen,
  closeModal,
  locationId,
  addSiteConditionSuccessHandler,
  siteConditions,
  projectWorkTypes,
}: AddSiteConditionModalProps): JSX.Element {
  const workTypeIds = useMemo(
    () => projectWorkTypes?.map((workType: WorkType) => workType.id) || [],
    [projectWorkTypes]
  );

  const { siteCondition } = useTenantStore(state => state.getAllEntities());
  const { data = [], error } = useQuery(WorkTypeSiteConditionsLibrary, {
    variables: {
      orderBy: [orderByName],
      workTypeIds: workTypeIds,
    },
  });
  const [step, setStep] = useState(AddSiteConditionStep.INITIAL);
  const toastCtx = useContext(ToastContext);

  const [
    getSiteConditionAndLibraries,
    { data: { tenantAndWorkTypeLinkedLibrarySiteConditions = [] } = {} },
  ] = useLazyQuery(WorkTypeSiteConditionsLibrary, {
    onCompleted: () =>
      setTimeout(
        () => setStep(AddSiteConditionStep.SHOW_DETAILS),
        showDetailsTimeout
      ),
  });

  const [
    getHazardsControlsLibrary,
    { data: { hazardsLibrary = [], controlsLibrary = [] } = {} },
  ] = useLazyQuery(HazardsControlsLibrary, {
    variables: {
      type: LibraryFilterType.SITE_CONDITION,
      orderBy: [orderByName],
    },
  });

  const [addSiteCondition, { loading: isLoading }] = useMutation(
    addSiteConditionMutation
  );

  if (error) {
    // TODO: work with design to have an error state in the modal
    closeModal();
  }

  const methods = useForm({
    mode: "onChange",
  });
  const {
    handleSubmit,
    formState: { isValid },
  } = methods;

  const getLibraries = (librarySiteConditionId: string) => {
    setStep(AddSiteConditionStep.LOADING);
    getSiteConditionAndLibraries({
      variables: {
        siteConditionsLibraryId: librarySiteConditionId,
        orderBy: [orderByName],
        hazardsOrderBy: [orderByName],
        controlsOrderBy: [orderByName],
        workTypeIds: workTypeIds,
      },
    });
    getHazardsControlsLibrary();
  };

  // TODO: Review this, buildTaskData can be reused?!
  const submitAddSiteCondition = async (
    siteConditionInputData: SiteConditionInputs
  ) => {
    const hazards = Object.values(siteConditionInputData.hazards ?? []).map(
      hazard => ({
        ...hazard,
        controls: Object.values(hazard.controls ?? []),
      })
    );

    return addSiteCondition({
      variables: {
        siteConditionData: {
          ...siteConditionInputData,
          hazards,
          locationId,
        },
      },
    });
  };

  const primaryClickHandler = () => {
    if (step === AddSiteConditionStep.INITIAL) {
      handleSubmit((siteConditionInputData: SiteConditionInputs) =>
        getLibraries(siteConditionInputData.librarySiteConditionId)
      )();
    } else if (step === AddSiteConditionStep.SHOW_DETAILS) {
      handleSubmit(async (siteConditionInputData: SiteConditionInputs) => {
        await submitAddSiteCondition(siteConditionInputData);
        toastCtx?.pushToast("success", `${siteCondition.label} added`);
        addSiteConditionSuccessHandler();
        closeModal();
      })();
    }
  };

  const modalSize: ModalSize =
    step === AddSiteConditionStep.SHOW_DETAILS ? "lg" : "md";

  return (
    <Modal
      title={`Add ${siteCondition.label.toLowerCase()}`}
      isOpen={isOpen}
      closeModal={closeModal}
      size={modalSize}
      className={cx("min-h-[237px]", { "my-4": modalSize === "lg" })}
    >
      <FormProvider {...methods}>
        {step === AddSiteConditionStep.INITIAL && (
          <SiteConditionTypeSelection
            siteConditionLibrary={excludeSiteConditions(
              data.tenantAndWorkTypeLinkedLibrarySiteConditions,
              siteConditions
            )}
          />
        )}

        {step === AddSiteConditionStep.LOADING && (
          <div className="self-center">
            <Loader />
          </div>
        )}

        {step === AddSiteConditionStep.SHOW_DETAILS && (
          <section>
            <p className="text-base font-bold text-shade-neutral-75">
              {tenantAndWorkTypeLinkedLibrarySiteConditions[0].name}
            </p>
            <SiteConditionDetailsForm
              siteCondition={tenantAndWorkTypeLinkedLibrarySiteConditions[0]}
              hazardsLibrary={hazardsLibrary}
              controlsLibrary={controlsLibrary}
            />
          </section>
        )}
      </FormProvider>

      {step !== AddSiteConditionStep.LOADING && (
        <div className="flex justify-end mt-5">
          <ButtonRegular className="mr-3" label="Cancel" onClick={closeModal} />

          <ButtonPrimary
            label={
              step === AddSiteConditionStep.INITIAL
                ? "Continue"
                : `Add ${siteCondition.label}`
            }
            onClick={primaryClickHandler}
            disabled={!isValid}
            loading={isLoading}
          />
        </div>
      )}
    </Modal>
  );
}
