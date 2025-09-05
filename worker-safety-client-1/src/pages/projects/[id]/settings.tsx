import type { PageHeaderAction } from "@/components/layout/pageHeader/components/headerActions/HeaderActions";
import type { ProjectInputs } from "@/types/form/Project";
import type { GetServerSideProps } from "next";
import type { NavigationOption } from "@/components/navigation/Navigation";
import type { ProjectFormProps } from "../create";
import { gql, useMutation } from "@apollo/client";
import { useRouter } from "next/router";
import { useContext, useState } from "react";
import { FormProvider, useForm } from "react-hook-form";
import cx from "classnames";
import { isMobile, isTablet } from "react-device-detect";
import PageFooter from "@/components/layout/pageFooter/PageFooter";
import PageHeader from "@/components/layout/pageHeader/PageHeader";
import PageLayout from "@/components/layout/pageLayout/PageLayout";
import RiskBadge from "@/components/riskBadge/RiskBadge";
import ToastContext from "@/components/shared/toast/context/ToastContext";
import {
  authenticatedQuery,
  authGetServerSidePropsProxy,
} from "@/graphql/client";
import query from "@/graphql/queries/getProjectByIdEdit.gql";
import useLeavePageConfirm from "@/hooks/useLeavePageConfirm";
import ProjectSettings from "@/container/project/ProjectSettings";
import {
  ProjectNavigationTab,
  projectNavigationTabOptions,
} from "@/types/project/ProjectNavigationTabs";
import { useAuthStore } from "@/store/auth/useAuthStore.store";
import {
  getProjectDefaults,
  isAuditNavigationTab,
} from "@/container/project/utils";
import Navigation from "@/components/navigation/Navigation";
import Modal from "@/components/shared/modal/Modal";
import ButtonRegular from "@/components/shared/button/regular/ButtonRegular";
import ButtonDanger from "@/components/shared/button/danger/ButtonDanger";
import DeleteProject from "@/graphql/queries/deleteProject.gql";
import Paragraph from "@/components/shared/paragraph/Paragraph";
import ProjectLibraries from "@/container/project/form/details/ProjectLibraries.query.gql";
import { orderByName } from "@/graphql/utils";
import { getUpdatedRouterQuery } from "@/utils/router";
import { useTenantStore } from "@/store/tenant/useTenantStore.store";
import { PageProvider } from "@/context/PageProvider";
import { sessionExpiryHandlerForApolloClient } from "@/utils/auth";
import Tooltip from "../../../components/shared/tooltip/Tooltip";

const editProjectMutation = gql`
  mutation EditProject($project: EditProjectInput!) {
    editProject(project: $project) {
      id
    }
  }
`;

export type ProjectEditProps = Required<ProjectFormProps>;

const getProjectNavigationTabLabel = (tab: ProjectNavigationTab) =>
  projectNavigationTabOptions.find(option => option.id === tab)?.name as string;

const getTabOptions = (
  canViewAuditTab: boolean,
  locationsLabel: string
): NavigationOption[] => {
  const tabsOptions: NavigationOption[] = [
    {
      id: 0,
      name: getProjectNavigationTabLabel(ProjectNavigationTab.DETAILS),
      icon: "settings_filled",
    },
    {
      id: 1,
      name: locationsLabel,
      icon: "location",
    },
  ];

  if (canViewAuditTab) {
    tabsOptions.push({
      id: 2,
      name: getProjectNavigationTabLabel(ProjectNavigationTab.AUDIT),
      icon: "history",
    });
  }

  return tabsOptions;
};

const deleteModalText = (workPackageLabel: string, taskLabel: string) =>
  `By deleting this ${workPackageLabel}, the associated ${taskLabel}, daily inspection reports, and insights will no longer appear within the application.`;

export default function ProjectSettingsPage(
  props: ProjectEditProps
): JSX.Element {
  const { workPackage, location, task } = useTenantStore(state =>
    state.getAllEntities()
  );

  const { project } = props;

  const methods = useForm<ProjectInputs>({
    defaultValues: getProjectDefaults(project),
  });
  const {
    handleSubmit,
    formState: { isDirty },
    reset,
  } = methods;
  const router = useRouter();
  const { id } = router.query;
  const { isAdmin, isManager, isSupervisor, hasPermission } = useAuthStore();
  const toastCtx = useContext(ToastContext);
  useLeavePageConfirm("Discard unsaved changes?", isDirty);

  const [editProject, { loading: isLoading }] = useMutation(
    editProjectMutation,
    {
      onCompleted: () =>
        toastCtx?.pushToast("success", `${workPackage.label} saved`),
      onError: error => {
        toastCtx?.pushToast(
          "error",
          `Error saving ${workPackage.label.toLowerCase()}`
        );
        sessionExpiryHandlerForApolloClient(error);
      },
    }
  );

  const removeProjectHandler = () => setIsModalOpen(true);
  const closeModalHandler = () => setIsModalOpen(false);
  const confirmProjectDeleteHandler = () => {
    closeModalHandler();
    deleteProject({
      variables: {
        deleteProjectId: project.id,
      },
    });
  };

  const [deleteProject] = useMutation(DeleteProject, {
    onCompleted: () => {
      toastCtx?.pushToast("success", `${workPackage.label} deleted`);
      router.push("/projects");
    },
    onError: error => {
      toastCtx?.pushToast(
        "error",
        `Error deleting ${workPackage.label.toLowerCase()}`
      );
      sessionExpiryHandlerForApolloClient(error);
    },
  });

  const canViewAuditTab = isAdmin() || isManager() || isSupervisor();
  const tabsOptions = getTabOptions(canViewAuditTab, location.labelPlural);

  const [selectedTab, setSelectedTab] = useState(0);
  const [projectName, setProjectName] = useState(project.name);
  const [isModalOpen, setIsModalOpen] = useState(false);

  const onSubmit = async (data: ProjectInputs) => {
    const { tenantWorkTypesId, ...restData } = data;

    await editProject({
      variables: {
        project: {
          id,
          ...restData,
          workTypeIds: tenantWorkTypesId,
        },
      },
    });

    setProjectName(data.name);

    reset(data, {
      keepDirty: false,
    });
  };

  const isAudit = isAuditNavigationTab(selectedTab);
  const isProjectDeletionAllowed = hasPermission("DELETE_PROJECTS");
  const readOnly = !hasPermission("EDIT_PROJECTS");

  const footer = isAudit ? undefined : (
    <PageFooter
      onPrimaryClick={readOnly ? undefined : handleSubmit(onSubmit)}
      primaryActionLabel="Save"
      isPrimaryActionDisabled={!isDirty}
      isPrimaryActionLoading={isLoading}
      className={cx({ ["mb-16"]: isMobile || isTablet })}
    />
  );

  const headerAction: PageHeaderAction = {
    icon: "trash_empty",
    title: `Remove ${workPackage.label.toLowerCase()}`,
    onClick: removeProjectHandler,
  };

  return (
    <PageProvider props={props}>
      <PageLayout
        className="responsive-padding-top"
        header={
          <PageHeader
            linkText={`${workPackage.label} Daily Summary`}
            linkRoute={{
              pathname: "/projects/[id]",
              query: getUpdatedRouterQuery(
                { id },
                { key: "source", value: router.query.source }
              ),
            }}
            actions={isProjectDeletionAllowed ? headerAction : undefined}
          >
            <h4 className="text-neutral-shade-100 mr-3">{projectName}</h4>
            <Tooltip
              title={
                "The High / Medium / Low classification represents the relative likelihood of presence of high energy hazards while the task is being performed"
              }
              position="bottom"
              className="max-w-xl"
            >
              <RiskBadge
                risk={project.riskLevel}
                label={`${project.riskLevel}`}
              />
            </Tooltip>
          </PageHeader>
        }
        footer={footer}
      >
        <section className="responsive-padding-x grid gap-x-6 grid-rows-2-auto-expand md:grid-cols-2-auto-expand md:grid-rows-none h-full overflow-hidden">
          <Navigation
            options={tabsOptions}
            onChange={setSelectedTab}
            selectedIndex={selectedTab}
            sidebarClassNames="bg-white p-3 min-w-[200px]"
            selectClassNames="ml-3 w-60 mb-4"
          />
          <div className="p-8 bg-white overflow-y-auto">
            <FormProvider {...methods}>
              <ProjectSettings selectedTab={selectedTab} readOnly={readOnly} />
            </FormProvider>
          </div>
        </section>
        <Modal
          title={`Delete this ${workPackage.label.toLowerCase()}?`}
          isOpen={isModalOpen}
          closeModal={closeModalHandler}
        >
          <div className="mb-10">
            <Paragraph
              text={deleteModalText(
                workPackage.label.toLowerCase(),
                task.labelPlural.toLowerCase()
              )}
            />
          </div>
          <div className="flex justify-end">
            <ButtonRegular
              className="mr-3"
              label="Cancel"
              onClick={closeModalHandler}
            />

            <ButtonDanger
              label={`Delete ${workPackage.label.toLowerCase()}`}
              onClick={confirmProjectDeleteHandler}
            />
          </div>
        </Modal>
      </PageLayout>
    </PageProvider>
  );
}

export const getServerSideProps: GetServerSideProps = async context =>
  authGetServerSidePropsProxy(context, async () => {
    const { id } = context.query;

    const projectQuery = authenticatedQuery(
      {
        query,
        variables: { projectId: id },
      },
      context
    );

    const projectLibrariesQuery = authenticatedQuery(
      {
        query: ProjectLibraries,
        variables: {
          orderBy: [orderByName],
        },
      },
      context
    );

    const [projectQueryResult, projectLibrariesResult] = await Promise.all([
      projectQuery,
      projectLibrariesQuery,
    ]);

    return {
      props: {
        ...projectQueryResult.data,
        ...projectLibrariesResult.data,
      },
    };
  });
