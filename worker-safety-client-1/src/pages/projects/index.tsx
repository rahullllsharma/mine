import type { ChangeEvent } from "react";
import type { Project } from "@/types/project/Project";
import type { GetServerSideProps } from "next";
import { useContext, useState } from "react";
import { debounce } from "lodash-es";
import { useRouter } from "next/router";
import { useQuery } from "@apollo/client";
import { useAuthStore } from "@/store/auth/useAuthStore.store";
import EmptyContent from "@/components/emptyContent/EmptyContent";
import PageLayout from "@/components/layout/pageLayout/PageLayout";
import ToastContext from "@/components/shared/toast/context/ToastContext";
import TabsLight from "@/components/shared/tabs/light/TabsLight";
import {
  ProjectStatus,
  projectStatusOptions,
} from "@/types/project/ProjectStatus";
import { NonMobileView } from "@/components/layout/nonMobileView/NonMobileView";
import Input from "@/components/shared/input/Input";
import { orderByName, orderByRiskLevel } from "@/graphql/utils";
import { useTenantStore } from "@/store/tenant/useTenantStore.store";
import GetProjects from "@/graphql/queries/getProjects.gql";
import ButtonPrimary from "@/components/shared/button/primary/ButtonPrimary";
import {
  getProjectStatusById,
  getProjectStatusLabel,
} from "@/container/projectList/list/utils";
import { List as ProjectsList } from "@/container/projectList/list/List";
import TenantName from "@/graphql/queries/tenantName.gql";
import {
  authenticatedQuery,
  authGetServerSidePropsProxy,
} from "@/graphql/client";
import { useTenantFeatures } from "@/hooks/useTenantFeatures";
import { sessionExpiryHandlerForApolloClient } from "@/utils/auth";
import { convertDateToString } from "../../utils/date/helper";

/** Only used for the initial request */
const GET_PROJECTS_OFFSET = 0;

/** Total projects per request */
const GET_PROJECTS_LIMIT = 50;

const getListProjectState = ({
  current = [],
  previous = [],
  loading,
}: {
  current?: Project[];
  previous?: Project[];
  loading?: boolean;
}) => {
  if (loading) {
    return "loading";
  }

  if (current.length <= previous.length) {
    return "complete";
  }

  return undefined;
};

export default function Home() {
  const { workPackage } = useTenantStore(state => state.getAllEntities());
  const [selectedTab, setSelectedTab] = useState(ProjectStatus.ACTIVE);
  const [search, setSearch] = useState("");
  const router = useRouter();
  const { hasPermission } = useAuthStore();
  const toastCtx = useContext(ToastContext);
  const currentDate = convertDateToString(new Date());

  const {
    data: { projects = [] } = {},
    previousData,
    refetch: getProjects,
    fetchMore,
    loading,
    variables,
  } = useQuery<{ projects: Project[] }>(GetProjects, {
    notifyOnNetworkStatusChange: true,
    fetchPolicy: "network-only",
    nextFetchPolicy: "cache-first",
    variables: {
      status: ProjectStatus.ACTIVE,
      orderBy: [orderByRiskLevel, orderByName],
      limit: GET_PROJECTS_LIMIT,
      offset: GET_PROJECTS_OFFSET,
      date: currentDate,
    },
    onError: _err => {
      sessionExpiryHandlerForApolloClient(_err);
      toastCtx?.pushToast("error", "Error searching this");
    },
  });

  const onSelectedTab = (_index: number, label: string) => {
    const status = projectStatusOptions().find(option => option.name === label)
      ?.id as ProjectStatus;

    getProjects({
      ...variables,
      status,
      search,
    });

    setSelectedTab(status);
  };

  const addProjectClick = () => router.push("/projects/create");

  const selectStatus = getProjectStatusById(selectedTab);

  const onChange = debounce((text: ChangeEvent<HTMLInputElement>) => {
    const searchTerm = text.target.value;

    setSearch(searchTerm);
    getProjects({
      ...variables,
      status: selectStatus?.id,
      search: searchTerm,
    });
  }, 500);

  const onLoadMoreProjects = () => {
    fetchMore({
      variables: {
        offset: projects.length,
      },
    });
  };

  const tabOptions = [
    getProjectStatusLabel(ProjectStatus.ACTIVE),
    getProjectStatusLabel(ProjectStatus.PENDING),
    getProjectStatusLabel(ProjectStatus.COMPLETED),
  ];

  const uiState = getListProjectState({
    current: projects,
    previous: previousData?.projects,
    loading,
  });

  return (
    <PageLayout className="responsive-padding-x h-full">
      <section className="flex mb-6">
        <div className="flex flex-1">
          <h4
            className="text-neutral-shade-100"
            data-testid="work-package-header"
          >
            {workPackage.labelPlural}
          </h4>
          <Input
            containerClassName="hidden lg:flex lg:w-60 ml-6"
            placeholder={`Search ${workPackage.labelPlural.toLowerCase()}`}
            onChange={onChange}
            icon="search"
            data-testid="work-package-search"
          />
        </div>
        <NonMobileView condition={hasPermission("ADD_PROJECTS")}>
          <ButtonPrimary
            className="my-0.5"
            onClick={addProjectClick}
            label={`Add ${workPackage.label}`}
            data-testid="add-work-package-button"
          />
        </NonMobileView>
      </section>

      <Input
        containerClassName="lg:hidden mb-8"
        placeholder={`Search ${workPackage.labelPlural.toLowerCase()}`}
        onChange={onChange}
        icon="search"
        data-testid="work-package-search"
      />

      <TabsLight options={tabOptions} onSelect={onSelectedTab} />

      <div className="responsive-padding-y flex-1">
        {loading || projects.length > 0 ? (
          <ProjectsList
            projects={projects}
            state={uiState}
            onLoadMore={() => onLoadMoreProjects()}
          />
        ) : search ? (
          // Showing this template when user do search & api has a empty response
          <div className="w-full h-full lg:h-2/3 flex items-center justify-center">
            <EmptyContent
              title={`There are no ${workPackage.labelPlural.toLowerCase()} found`}
              description="based on the filters you've set. Try changing your filters."
            />
          </div>
        ) : (
          <div className="w-full h-full lg:h-2/3 flex items-center justify-center">
            <EmptyContent
              title={`You currently have no ${
                selectStatus.name
              } ${workPackage.labelPlural.toLowerCase()}`}
              description="If you believe this is an error, please contact your customer success manager to help troubleshoot the issues"
            />
          </div>
        )}
      </div>
    </PageLayout>
  );
}

export const getServerSideProps: GetServerSideProps = async context =>
  authGetServerSidePropsProxy(context, async () => {
    const {
      data: { me },
    } = await authenticatedQuery(
      {
        query: TenantName,
      },
      context
    );

    const { displayWorkPackage } = useTenantFeatures(me.tenant.name);

    if (!displayWorkPackage) {
      return {
        redirect: {
          permanent: false,
          destination: "/404",
        },
      };
    }
    return { props: {} };
  });
