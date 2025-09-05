import type {
  PageHeaderAction,
  PageHeaderActionTooltip,
} from "@/components/layout/pageHeader/components/headerActions/HeaderActions";
import type { Control } from "@/types/project/Control";
import type { Hazard } from "@/types/project/Hazard";
import type { HazardAggregator } from "@/types/project/HazardAggregator";
import type { SiteConditionInputs } from "@/types/siteCondition/SiteConditionInputs";
import type { GetServerSideProps } from "next";
import { useMutation } from "@apollo/client";
import router from "next/router";
import { useContext, useState } from "react";
import { FormProvider, useForm } from "react-hook-form";
import cx from "classnames";
import { isMobile, isTablet } from "react-device-detect";
import SiteConditionDetailsForm from "@/components/detailsForm/siteConditionDetailsForm/SiteConditionDetailsForm";
import PageFooter from "@/components/layout/pageFooter/PageFooter";
import PageHeader from "@/components/layout/pageHeader/PageHeader";
import PageLayout from "@/components/layout/pageLayout/PageLayout";
import ButtonDanger from "@/components/shared/button/danger/ButtonDanger";
import ButtonRegular from "@/components/shared/button/regular/ButtonRegular";
import Modal from "@/components/shared/modal/Modal";
import ToastContext from "@/components/shared/toast/context/ToastContext";
import {
  authenticatedQuery,
  authGetServerSidePropsProxy,
} from "@/graphql/client";
import TenantLinkedControlsLibrary from "@/graphql/queries/tenantLinkedControlsLibrary.gql";
import DeleteSiteCondition from "@/graphql/queries/deleteSiteCondition.gql";
import EditSiteCondition from "@/graphql/queries/editSiteCondition.gql";
import TenantLinkedHazardsLibrary from "@/graphql/queries/tenantLinkedHazardsLibrary.gql";
import SiteConditions from "@/graphql/queries/siteConditions.gql";
import { orderByName } from "@/graphql/utils";
import { LibraryFilterType } from "@/types/LibraryFilterType";
import { buildSiteConditionData } from "@/utils/task";
import { useGetProjectUrl } from "@/container/projectSummaryView/utils";
import { useTenantStore } from "@/store/tenant/useTenantStore.store";
import { messages } from "@/locales/messages";

type SiteConditionDetailsProps = {
  siteConditions: HazardAggregator;
  hazardsLibrary: Hazard[];
  controlsLibrary: Control[];
  projectId: string;
};

export default function SiteConditionDetailsViewPage({
  siteConditions,
  hazardsLibrary,
  controlsLibrary,
  projectId,
}: SiteConditionDetailsProps): JSX.Element {
  const { workPackage, siteCondition } = useTenantStore(state =>
    state.getAllEntities()
  );

  // TODO: handle loading/error states for each mutation
  const [deleteSiteCondition, { loading: isDeleting }] =
    useMutation(DeleteSiteCondition);
  const [editSiteCondition, { loading: isEditing }] =
    useMutation(EditSiteCondition);

  const [isModalOpen, setIsModalOpen] = useState(false);
  const form = useForm<SiteConditionInputs>({
    defaultValues: {},
  });
  const {
    handleSubmit,
    formState: { isDirty, isValid },
    reset,
  } = form;
  const toastCtx = useContext(ToastContext);
  const projectUrl = useGetProjectUrl(projectId);

  const removeSiteConditionHandler = () => setIsModalOpen(true);
  const closeModalHandler = () => setIsModalOpen(false);
  const navigateToProject = () => router.push(projectUrl);
  const deleteSiteConditionHandler = async () => {
    await deleteSiteCondition({
      variables: {
        deleteSiteConditionId: siteConditions.id,
      },
    });
    navigateToProject();
    toastCtx?.pushToast("success", `${siteCondition.label} deleted`);
  };
  const editSiteConditionHandler = async (data: SiteConditionInputs) => {
    await editSiteCondition({
      variables: {
        data: { ...buildSiteConditionData(data), id: siteConditions.id },
      },
    });

    toastCtx?.pushToast("success", `${siteCondition.label} saved`);

    reset(data, {
      keepDirty: false,
    });
  };

  const isDisabled = !siteConditions.isManuallyAdded;

  const headerAction: PageHeaderAction | PageHeaderActionTooltip = isDisabled
    ? {
        type: "tooltip",
        icon: "info_circle_outline",
        title: messages.autoPopulatedSiteConditionMessage,
      }
    : {
        icon: "trash_empty",
        title: `Remove ${siteCondition.label.toLowerCase()}`,
        onClick: removeSiteConditionHandler,
      };

  return (
    <PageLayout
      header={
        <PageHeader
          linkText={`${workPackage.label} summary view`}
          linkRoute={projectUrl}
          actions={headerAction}
        >
          <h4 className="text-shade-primary mr-3">{siteConditions.name}</h4>
        </PageHeader>
      }
      footer={
        <PageFooter
          primaryActionLabel="Save"
          isPrimaryActionDisabled={!isDirty || !isValid}
          isPrimaryActionLoading={isEditing}
          onPrimaryClick={handleSubmit(editSiteConditionHandler)}
          className={cx({ ["mb-16"]: isMobile || isTablet })}
        />
      }
    >
      <section className="flex-1 responsive-padding-x">
        <FormProvider {...form}>
          <SiteConditionDetailsForm
            siteCondition={siteConditions}
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
            {`Deleting this ${siteCondition.label.toLowerCase()} will remove it from summary view and
            future reports.`}
          </p>
        </div>
        <div className="flex justify-end">
          <ButtonRegular
            className="mr-3"
            label="Cancel"
            onClick={closeModalHandler}
          />

          <ButtonDanger
            label={`Delete ${siteCondition.label.toLowerCase()}`}
            onClick={deleteSiteConditionHandler}
            loading={isDeleting}
          />
        </div>
      </Modal>
    </PageLayout>
  );
}

export const getServerSideProps: GetServerSideProps = async context =>
  authGetServerSidePropsProxy(context, async () => {
    const { id, siteConditionId } = context.query;

    const {
      data: { siteConditions },
    } = await authenticatedQuery(
      {
        query: SiteConditions,
        variables: {
          siteConditionsId: siteConditionId,
          filterTenantSettings: true,
        },
      },
      context
    );

    const { data: hazardsData = {} } = await authenticatedQuery(
      {
        query: TenantLinkedHazardsLibrary,
        variables: {
          type: LibraryFilterType.SITE_CONDITION,
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
          type: LibraryFilterType.SITE_CONDITION,
          orderBy: [orderByName],
        },
      },
      context
    );
    // TODO: Handle errors(400, 404, 500 and error states from queries)

    return {
      props: {
        projectId: id,
        siteConditions: siteConditions[0],
        hazardsLibrary: hazardsData.tenantLinkedHazardsLibrary,
        controlsLibrary: tenantLinkedControlsLibrary,
      },
    };
  });
