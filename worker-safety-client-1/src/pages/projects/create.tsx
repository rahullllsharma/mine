import type { SubmitHandler } from "react-hook-form";
import type { ProjectInputs } from "@/types/form/Project";
import type { GetServerSideProps } from "next";
import type { LibraryDivision } from "@/types/project/LibraryDivision";
import type { LibraryRegion } from "@/types/project/LibraryRegion";
import type { LibraryProjectType } from "@/types/project/LibraryProjectType";
import type { User } from "@/types/User";
import type { Contractor } from "@/types/project/Contractor";
import type { LibraryAssetType } from "@/types/project/LibraryAssetType";
import type { Project } from "@/types/project/Project";
import type { TenantWorkTypes } from "../../types/project/TenantWorkTypes";
import { useForm, FormProvider } from "react-hook-form";
import { useRouter } from "next/router";
import { gql, useMutation } from "@apollo/client";
import { useContext } from "react";
import PageHeader from "@/components/layout/pageHeader/PageHeader";
import PageFooter from "@/components/layout/pageFooter/PageFooter";
import PageLayout from "@/components/layout/pageLayout/PageLayout";
import {
  authenticatedQuery,
  authGetServerSidePropsProxy,
} from "@/graphql/client";
import useLeavePageConfirm from "@/hooks/useLeavePageConfirm";
import { orderByName } from "@/graphql/utils";
import { ProjectStatus } from "@/types/project/ProjectStatus";
import ToastContext from "@/components/shared/toast/context/ToastContext";
import query from "@/container/project/form/details/ProjectLibraries.query.gql";
import { useTenantStore } from "@/store/tenant/useTenantStore.store";
import { PageProvider } from "@/context/PageProvider";
import ProjectDetails from "@/container/project/form/details/ProjectDetails";
import ProjectLocations from "@/container/project/form/locations/ProjectLocations";
import { sessionExpiryHandlerForApolloClient } from "@/utils/auth";

const createProjectMutation = gql`
  mutation CreateProject($project: CreateProjectInput!) {
    createProject(project: $project) {
      id
    }
  }
`;

export type ProjectFormProps = {
  project?: Project;
  divisionsLibrary: LibraryDivision[];
  regionsLibrary: LibraryRegion[];
  projectTypesLibrary: LibraryProjectType[];
  assetTypesLibrary: LibraryAssetType[];
  managers: User[];
  supervisors: User[];
  contractors: Contractor[];
  tenantWorkTypes: TenantWorkTypes[];
};

export default function ProjectCreatePage(
  props: ProjectFormProps
): JSX.Element {
  const { workPackage } = useTenantStore(state => state.getAllEntities());
  const methods = useForm<ProjectInputs>({
    defaultValues: {
      status: ProjectStatus.PENDING,
      locations: [{ name: "" }],
    },
  });
  const router = useRouter();
  const toastCtx = useContext(ToastContext);

  const {
    handleSubmit,
    reset,
    formState: { isDirty },
  } = methods;

  useLeavePageConfirm("Discard unsaved changes?", isDirty);

  const [createProjects, { loading: isLoading }] = useMutation(
    createProjectMutation,
    {
      onCompleted: () => {
        toastCtx?.pushToast("success", `${workPackage.label} added`);
      },
      onError: _err => {
        toastCtx?.pushToast(
          "error",
          `Error creating a ${workPackage.label.toLowerCase()}`
        );
        sessionExpiryHandlerForApolloClient(_err);
      },
    }
  );

  const onSubmit: SubmitHandler<ProjectInputs> = async (
    data: ProjectInputs
  ) => {
    const { tenantWorkTypesId, ...restData } = data;

    await createProjects({
      variables: {
        project: {
          ...restData,
          workTypeIds: tenantWorkTypesId,
          name: data.name.trim(),
          locations: data.locations.map(
            ({
              id,
              name,
              latitude,
              longitude,
              supervisorId,
              additionalSupervisors,
              externalKey,
            }) => ({
              id,
              name: name.trim(),
              latitude,
              longitude,
              supervisorId,
              additionalSupervisors,
              externalKey,
            })
          ),
        },
      },
    });

    reset(data, {
      keepDirty: false,
    });

    router.push("/projects");
  };

  return (
    <PageProvider props={props}>
      <PageLayout
        header={
          <PageHeader
            pageTitle={`Add ${workPackage.label.toLowerCase()}`}
            linkText={`${workPackage.label} selection`}
            linkRoute="/projects"
          />
        }
        footer={
          <PageFooter
            onPrimaryClick={handleSubmit(onSubmit)}
            primaryActionLabel="Save"
            isPrimaryActionLoading={isLoading}
          />
        }
      >
        <FormProvider {...methods}>
          <section className="responsive-padding-x">
            <div className="p-8 bg-white flex flex-col gap-4">
              <ProjectDetails />
              <ProjectLocations />
            </div>
          </section>
        </FormProvider>
      </PageLayout>
    </PageProvider>
  );
}

export const getServerSideProps: GetServerSideProps = async context =>
  authGetServerSidePropsProxy(context, async () => {
    const { data } = await authenticatedQuery(
      {
        query,
        variables: {
          orderBy: [orderByName],
        },
      },
      context
    );

    return {
      props: {
        ...data,
      },
    };
  });
