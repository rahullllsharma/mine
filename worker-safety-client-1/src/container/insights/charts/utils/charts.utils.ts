import type { WatchQueryFetchPolicy } from "@apollo/client";
import type { TaskRiskLevelByDate } from "@/components/charts/dailyRiskHeatmap/types";
import type { BarDatum } from "@nivo/bar";
import type { FiltersDescriptionsReturn as FiltersDescriptions } from "../hooks/useFiltersDescriptions";
import type { WorkbookData } from "@/components/fileDownloadDropdown/providers/spreadsheet";
import type { ApplicableHazardsChartProps } from "../applicableHazardsChart/ApplicableHazardsChart";
import type { ControlsNotImplementedChartProps } from "../controlsNotImplementedChart/ControlsNotImplementedChart";
import type { FiltersPayload } from "../types";
import type { PortfolioFiltersPayload } from "../../portfolioFilters/PortfolioFilters";
import type { ProjectFiltersPayload } from "../../projectFilters/ProjectFilters";
import { useTenantStore } from "@/store/tenant/useTenantStore.store";

export const lazyQueryOpts: {
  fetchPolicy: WatchQueryFetchPolicy;
  nextFetchPolicy: WatchQueryFetchPolicy;
} = {
  fetchPolicy: "network-only", // TODO: use default fetchPolicy once this is fixed https://github.com/apollographql/apollo-client/issues/6636#issuecomment-692220069
  nextFetchPolicy: "standby", // prevent refetching on every re-render
};

export const getTaskNameColumn = (header: string) => ({
  id: "task_name",
  Header: `${header} name`,
  width: 180,
  value: (taskRisk: TaskRiskLevelByDate): string => {
    return taskRisk.taskName;
  },
});

export const getLocationNameColumn = (header: string) => ({
  id: "location_name",
  Header: header,
  width: 180,
  value: (taskRisk: TaskRiskLevelByDate): string => {
    return taskRisk.locationName;
  },
});

export const getProjectNameColumn = (header: string) => ({
  id: "project_name",
  Header: header,
  width: 180,
  value: (taskRisk: TaskRiskLevelByDate): string => {
    return taskRisk.projectName;
  },
});

type FormatChartDataWithFiltersArgs = {
  chartData: BarDatum[];
  chartTitle: string;
  filtersData?: FiltersDescriptions;
};

/** Prepares the chart data and filters to be consumed and downloadable */
export function formatChartDataWithFilters({
  chartData,
  chartTitle,
  filtersData,
}: FormatChartDataWithFiltersArgs): WorkbookData {
  return [
    ...(Array.isArray(filtersData) && filtersData.length > 0
      ? [["Filters applied", filtersData]]
      : []),
    [chartTitle, chartData],
  ] as WorkbookData;
}

type FormatDrillDownChartsDataWithFiltersParams = {
  selected: string;
  filters?: FiltersDescriptions;
} & (
  | {
      type: "control";
      primaryData: ControlsNotImplementedChartProps["controlsData"];
      drilldownData: ControlsNotImplementedChartProps["charts"];
    }
  | {
      type: "hazard";
      primaryData: ApplicableHazardsChartProps["hazardsData"];
      drilldownData: ApplicableHazardsChartProps["charts"];
    }
);

/** Prepares the drill down charts and filters to be consumed and downloadable */
export const formatDrillDownChartsDataWithFilters = ({
  type,
  selected,
  primaryData,
  drilldownData,
  filters,
}: FormatDrillDownChartsDataWithFiltersParams): WorkbookData => {
  let report: string;
  let reportTransformFn: any;
  let drillDownTransformFn: any;

  const { control, hazard } = useTenantStore.getState().getAllEntities();

  // `${report} - Project ${title}`, this will break because we're already trimming by 31 chars ...
  const trimDataTitle = (p: string) => p.replace(/by/gi, "").trim();

  switch (type) {
    case "control": {
      const controlLabelLower = control.label.toLocaleLowerCase();
      const controlLabelPluralLower = control.labelPlural.toLocaleLowerCase();

      report = `${control.labelPlural} Not Implemented`;

      reportTransformFn = ({
        percent,
        libraryControl: { name },
      }: ControlsNotImplementedChartProps["controlsData"][number]) => ({
        [`${control.label} Not Implemented`]: name,
        [`% of ${controlLabelPluralLower} not implemented`]: percent * 100,
      });

      drillDownTransformFn = ({ title = "", data = [] }) => [
        `${control.labelPlural} ${title}`,
        data.map(({ name, percent }) => ({
          [`Selected ${controlLabelLower} not implemented`]: selected,
          [`${trimDataTitle(title)}`]: name,
          [`% of ${controlLabelPluralLower} not implemented ${title}`]:
            percent * 100,
        })),
      ];
      break;
    }

    case "hazard":
    default: {
      const hazardLabel = hazard.label.toLocaleLowerCase();

      report = `Applicable ${hazard.labelPlural}`;

      reportTransformFn = ({
        count,
        libraryHazard: { name },
      }: ApplicableHazardsChartProps["hazardsData"][number]) => ({
        [`Applicable ${hazardLabel}`]: name,
        [`# of times ${hazardLabel} was applicable`]: count,
      });

      drillDownTransformFn = ({ title = "", data = [] }) => [
        `AH ${title}`,
        data.map(({ name, count }) => ({
          [`Selected applicable ${hazardLabel}`]: selected,
          [`${trimDataTitle(title)}`]: name,
          [`# of times ${hazardLabel} was applicable ${title}`]: count,
        })),
      ];
      break;
    }
  }

  return formatChartDataWithFilters({
    chartTitle: report,
    chartData: primaryData.map(reportTransformFn),
    filtersData: filters,
  }).concat(drilldownData.map(drillDownTransformFn));
};

type FormatRiskHeatmapChartsWithFilters = {
  title: string;
  data: (Partial<
    Pick<TaskRiskLevelByDate, "locationName" | "projectName" | "taskName">
  > &
    Pick<TaskRiskLevelByDate, "riskLevelByDate">)[];
  filters?: FiltersDescriptions;
};

/** Prepares the heatmap data for the risk charts and filters to be consumed and downloadable */
export const formatRiskHeatmapChartsWithFilters = ({
  title,
  data,
  filters,
}: FormatRiskHeatmapChartsWithFilters): WorkbookData => {
  const {
    workPackage: {
      attributes: { name: workPackageNameAttr },
    },
    location: {
      attributes: { name: locationAttrName },
    },
    task,
  } = useTenantStore.getState().getAllEntities();

  return formatChartDataWithFilters({
    filtersData: filters,
    chartTitle: title,
    chartData: data.reduce((acc, { riskLevelByDate, ...attributes }) => {
      const { taskName, locationName, projectName } = attributes;
      return acc.concat(
        ...riskLevelByDate.map(({ date, riskLevel }) => ({
          date,
          ...(taskName && {
            [`${task.label} name`]: taskName,
          }),
          ...(locationName && {
            [locationAttrName.label]: locationName,
          }),
          ...(projectName && {
            [workPackageNameAttr.label]: projectName,
          }),
          "Risk level (high, medium, low)": riskLevel,
        }))
      );
    }, [] as { [key: string]: string }[]),
  });
};

/** Parse the project filters descriptions into a project with number and name */
export const getProjectDescriptionFromFilters = ({
  filters,
  filtersDescriptions,
}: {
  filters?: FiltersPayload;
  filtersDescriptions?: FiltersDescriptions;
}): { name: string; number?: string } => {
  const {
    workPackage: {
      label: workPackageLabel,
      labelPlural: workPackageLabelPlural,
      attributes: { externalKey: workPackageNumber, name: workPackageName },
    },
  } = useTenantStore.getState().getAllEntities();

  const projects =
    (filters as PortfolioFiltersPayload)?.projectIds ?? [
      (filters as ProjectFiltersPayload)?.projectId,
    ] ??
    [];

  const projectCount = projects.length;

  if (projectCount === 1) {
    const [filtersApplied] = filtersDescriptions || [];

    // This implementation sucks because the information is tied to a dynamic key, set by the tenant information
    // FIXME: When refactoring the insights, create a metadata filters instead.
    return {
      name:
        filtersApplied?.[workPackageName.label]?.toString() || workPackageLabel,
      number: filtersApplied?.[workPackageNumber.label]?.toString(),
    };
  }

  return {
    name: `${
      projectCount === 0 ? "All" : "Multiple"
    } ${workPackageLabelPlural}`,
  };
};
