import type { Insight, InsightFormInputs } from "@/types/insights/Insight";
import type { GetServerSideProps, NextApiRequest } from "next";
import type {
  LibraryRegion,
  LibraryDivision,
  Contractor,
} from "@/api/generated/types";
import type { FilterProject } from "@/container/insights/utils";
import { ConfidentialClientApplication } from "@azure/msal-node";
import axios from "axios";
import { useMemo, useState } from "react";
import { getServerSession } from "next-auth";
import axiosRest from "@/api/restApi";
import PageLayout from "@/components/layout/pageLayout/PageLayout";
import InsightsList from "@/container/reportInsights/InsightsList/InsightsList";
import {
  authGetServerSidePropsProxy,
  authenticatedQuery,
} from "@/graphql/client";
import TenantName from "@/graphql/queries/tenantName.gql";
import { config } from "@/config";
import { useTenantFeatures } from "@/hooks/useTenantFeatures";
import OtherReportList from "@/container/otherTypeReports/OtherReportList";
import InsightReportType from "@/container/reportInsights/insightReportType/insightReportType";
import PlanningAndLearningReportType from "@/container/reportInsights/planningAndLearningReportType/PlanningAndLearningReportType";
import { getNextConfig } from "@/utils/auth";

type EmbedReportData = {
  embedUrl: string;
  reportId: string;
  id: string;
};
type OtherReportType = {
  name: string;
  path: string;
  id: string;
  isEnable: boolean;
};
type PlanningAndLearning = {
  projects?: FilterProject[];
  regions?: LibraryRegion[];
  divisions?: LibraryDivision[];
  contractors?: Contractor[];
  isPlanningEnable: boolean;
  isLearningEnable: boolean;
};

type InsightsProps = {
  embedReportsData: EmbedReportData[];
  embedToken?: string;
  insights?: Insight[];
  planningAndLearning: PlanningAndLearning;
  displayProjectTaskRiskHeatmap?: boolean;
};

const Insights = ({
  embedReportsData = [],
  embedToken = "",
  insights = [],
  planningAndLearning,
  displayProjectTaskRiskHeatmap,
}: InsightsProps) => {
  let otherTypeReportList: OtherReportType[] = [
    {
      name: "Learnings Dashboard",
      id: "learnings",
      path: "/learnings",
      isEnable: planningAndLearning.isLearningEnable,
    },
    {
      name: "Plannings Dashboard",
      id: "plannings",
      path: "/plannings",
      isEnable: planningAndLearning.isPlanningEnable,
    },
  ];

  otherTypeReportList = otherTypeReportList.filter(item => item.isEnable);

  const visibleInsights = useMemo(
    () => insights.filter(insight => insight.visibility),
    [insights]
  );

  // Making first record selected in case there is any record present in Insight Type Record
  // otherwise selecting first record of otherTypeReportList
  const [activeInsightId, setActiveInsightId] = useState(
    visibleInsights.length === 0
      ? otherTypeReportList[0]?.id
      : visibleInsights[0]?.id
  );

  //There are two report types 1: Other Type (Includes Planning and Learning) and 2:Insight Type report type
  // By Default we are showing first Insight Report if any Insight Reports are present
  // otherwise showing first other type report ( Learning Dashboard Report )
  const [isPlanningAndLearningReportType, setPlanningAndLearningReportType] =
    useState(otherTypeReportList.length < 0);

  const activeInsight = useMemo(
    () => visibleInsights.find(i => i.id === activeInsightId),
    [activeInsightId, visibleInsights]
  );

  const changeActiveInsight = (id: string) => {
    if (id == "plannings" || id == "learnings") {
      setActiveInsightId(id);
      setPlanningAndLearningReportType(true);
    } else {
      setPlanningAndLearningReportType(false);
      setActiveInsightId(id);
    }
  };

  const embedData = useMemo(
    () => embedReportsData.find(dt => dt.id === activeInsight?.id),
    [embedReportsData, activeInsight?.id]
  );

  const renderReportType = () => {
    if (isPlanningAndLearningReportType) {
      return (
        <PlanningAndLearningReportType
          planningAndLearning={planningAndLearning}
          activeInsightId={activeInsightId}
          displayProjectTaskRiskHeatmap={displayProjectTaskRiskHeatmap}
        />
      );
    }

    if (visibleInsights.length !== 0) {
      return (
        <InsightReportType
          insight={activeInsight}
          embedData={embedData}
          embedToken={embedToken}
          visibleInsights={visibleInsights}
        />
      );
    }

    return (
      <PlanningAndLearningReportType
        planningAndLearning={planningAndLearning}
        activeInsightId={activeInsightId}
        displayProjectTaskRiskHeatmap={displayProjectTaskRiskHeatmap}
      />
    );
  };

  return (
    <PageLayout className="responsive-padding-x w-full flex-1">
      <h4 className="text-neutral-shade-100 mb-8">Insights</h4>
      <section className="grid grid-cols-[20rem,auto] gap-8 flex-1">
        <div className="bg-white rounded-xl py-8 px-6 flex flex-col gap-3">
          <InsightsList
            insights={visibleInsights}
            changeActiveInsight={changeActiveInsight}
            activeInsightId={activeInsightId}
          />
          <OtherReportList
            reports={otherTypeReportList}
            changeActiveReport={changeActiveInsight}
            activeReportId={activeInsightId}
          />
        </div>
        <div className="bg-white overflow-y-auto p-4">{renderReportType()}</div>
      </section>
    </PageLayout>
  );
};

export const getServerSideProps: GetServerSideProps = async context =>
  authGetServerSidePropsProxy(context, async () => {
    //TODO Needs to be revised when we switch to feature flags
    //https://urbint.atlassian.net/browse/WSAPP-1207

    const {
      data: { me },
    } = await authenticatedQuery(
      {
        query: TenantName,
      },
      context
    );

    const {
      displayPlannings,
      displayLearnings,
      displayInsights,
      displayProjectTaskRiskHeatmap,
    } = useTenantFeatures(me.tenant.name);

    const planningAndLearning: PlanningAndLearning = {
      // Removing it as we dont need PlanningAndLearning Data
      // since we are removing Planning and Learning Dashboard
      // projects: data.projects ?? [],
      // regions: data.regionsLibrary ?? [],
      // divisions: data.divisionsLibrary ?? [],
      // contractors: data.contractors ?? [],
      isPlanningEnable: displayPlannings ? true : false,
      isLearningEnable: displayLearnings ? true : false,
    };

    if (!displayInsights) {
      return {
        redirect: {
          permanent: false,
          destination: "/404",
        },
      };
    }
    const nextConfig = await getNextConfig(context?.req as NextApiRequest);
    const token = await getServerSession(
      context?.req,
      context?.res,
      nextConfig
    );

    if (!token) {
      return {
        props: {},
      };
    }
    let insights: Insight[] = [];

    try {
      insights = (
        await axiosRest.get("/insights", {
          params: {
            "page[limit]": 100,
          },
          headers: {
            Authorization: `Bearer ${token.accessToken}`,
          },
        })
      ).data.data.map((dt: { attributes: InsightFormInputs; id: string }) => ({
        ...dt.attributes,
        id: dt.id,
      }));

      const embedInsights = insights.filter(insight => insight.visibility);

      const accessTokenRes = await getAccessToken();

      if (accessTokenRes) {
        const { accessToken } = accessTokenRes;

        const reportsDataResult = await Promise.allSettled(
          embedInsights.map(async insight => {
            const reportId = new URL(insight.url).searchParams.get("reportId");
            const reportData = await axios.get(
              `https://api.powerbi.com/v1.0/myorg/groups/${config.powerBi.workspaceId}/reports/${reportId}`,
              {
                headers: {
                  Authorization: `Bearer ${accessToken}`,
                },
              }
            );

            return { ...reportData.data, insightId: insight.id };
          })
        );

        const reportsData = reportsDataResult
          .map(res => (res.status === "fulfilled" ? res.value : null))
          .filter(Boolean);

        const reportsEmbedToken = await axios.post(
          "https://api.powerbi.com/v1.0/myorg/GenerateToken",
          {
            datasets: [
              ...new Set(reportsData.map(report => report.datasetId)),
            ].map(id => ({ id })),
            reports: [...new Set(reportsData.map(report => report.id))].map(
              id => ({ id })
            ),
          },
          {
            headers: {
              Authorization: `Bearer ${accessToken}`,
            },
          }
        );

        return {
          props: {
            embedReportsData: reportsData.map(r => ({
              embedUrl: r.embedUrl,
              reportId: r.id,
              id: r.insightId,
            })),
            embedToken: reportsEmbedToken.data.token,
            insights,
            planningAndLearning,
          },
        };
      }

      return {
        props: {
          insights,
          planningAndLearning,
          displayProjectTaskRiskHeatmap,
        },
      };
    } catch (error) {
      console.log(error);
      return {
        props: {
          insights,
          planningAndLearning,
          displayProjectTaskRiskHeatmap,
        },
      };
    }
  });

export default Insights;

const getAccessToken = async () => {
  const msalConfig = {
    auth: {
      clientId: config.powerBi.clientId,
      authority: `${config.powerBi.authorityUrl}${config.powerBi.tenantId}`,
      clientSecret: config.powerBi.clientSecret,
    },
  };

  if (config.powerBi.authenticationMode.toLowerCase() !== "serviceprincipal") {
    return;
  }

  // Service Principal auth is the recommended by Microsoft to achieve App Owned Data Power BI embedding
  const clientApplication = new ConfidentialClientApplication(msalConfig);

  const clientCredentialRequest = {
    scopes: [config.powerBi.scopeBase],
  };

  return clientApplication.acquireTokenByClientCredential(
    clientCredentialRequest
  );
};
