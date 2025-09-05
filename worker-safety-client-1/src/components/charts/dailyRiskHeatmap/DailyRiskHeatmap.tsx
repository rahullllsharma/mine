import type { WorkbookData } from "@/components/fileDownloadDropdown/providers/spreadsheet";
import type { EntityRiskLevelByDate, ColumnDef } from "./types";
import { useEffect } from "react";
import partial from "lodash/partial";
import includes from "lodash/includes";

import ChartHeader from "@/container/insights/charts/chartHeader/ChartHeader";
import { stripTypename } from "@/utils/shared";
import EmptyChart from "@/components/emptyChart/EmptyChart";
import { RiskLevel } from "@/components/riskBadge/RiskLevel";
import HeatmapTable from "./HeatmapTable";
import { heatmapColumn, withDateToRiskLevel } from "./heatmapColumn";
import { riskLegend } from "./riskLegend";
import { buildTextColumn } from "./textColumn";

function hasAtLeastOneRiskLevel(datum: EntityRiskLevelByDate): boolean {
  return datum.riskLevelByDate.some(({ riskLevel }) =>
    includes([RiskLevel.LOW, RiskLevel.MEDIUM, RiskLevel.HIGH], riskLevel)
  );
}
export type DailyRiskHeatmapProps = {
  data: readonly EntityRiskLevelByDate[];
  columns: readonly ColumnDef[];
  startDate?: string;
  endDate?: string;
  onPreviousDateClick?: () => void;
  onNextDateClick?: () => void;
  showLegend?: boolean;
  emptyStateText?: string;
  title?: string;
  setHasData?: (hasData: boolean) => void;
  workbookData?: WorkbookData;
  workbookDownloadable?: boolean;
  workbookActionTitle?: string;
  workbookFilename: string;
};

export default function DailyRiskHeatmap({
  data,
  columns,
  startDate,
  endDate,
  onPreviousDateClick,
  onNextDateClick,
  showLegend = false,
  title,
  setHasData,
  workbookData,
  workbookDownloadable,
  workbookActionTitle,
  workbookFilename,
}: DailyRiskHeatmapProps): JSX.Element | null {
  const filteredData = data.filter(hasAtLeastOneRiskLevel);
  const rowCount = filteredData.length;

  const hasData = rowCount > 0;
  useEffect(() => {
    if (setHasData) setHasData(hasData);
  }, [setHasData, hasData]);

  const hasDates = startDate && endDate;
  if (!hasDates) return null;

  const columnsWithRisk = columns
    .map(partial(buildTextColumn, rowCount))
    .concat([
      heatmapColumn({
        startDate: startDate as string,
        endDate: endDate as string,
        rowCount,
        onPreviousDateClick,
        onNextDateClick,
      }),
    ]);

  const columnWidths = columnsWithRisk.reduce(
    (sum, { width }) => sum + width,
    0
  );
  const offset = 12; // correct table padding to align the cells with the header
  const width = columnWidths + offset;

  const extensibleData = filteredData.map(stripTypename);

  if (!hasData) {
    return (
      <EmptyChart
        title={title || "Risk Heatmap"}
        description="There is currently no data available for this chart"
      />
    );
  }

  return (
    <>
      <ChartHeader
        title={title || "Risk Heatmap"}
        chartData={workbookData}
        chartFilename={workbookFilename}
        downloadable={workbookDownloadable}
        actionTitle={workbookActionTitle}
      />
      <div className="px-4 pt-6 pb-10 w-full h-full bg-white rounded-xl flex flex-col items-center overflow-auto">
        <div className="flex flex-row">
          <HeatmapTable
            columns={columnsWithRisk}
            data={withDateToRiskLevel(extensibleData)}
            width={width}
          />
          {showLegend && riskLegend()}
        </div>
      </div>
    </>
  );
}
