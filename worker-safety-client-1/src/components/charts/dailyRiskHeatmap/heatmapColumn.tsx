/* eslint-disable @typescript-eslint/no-explicit-any */
import type { EntityRiskLevelByDate } from "./types";
import cx from "classnames";
import { Icon } from "@urbint/silica";
import { getFormattedDate, getDayRangeBetween } from "@/utils/date/helper";
import { RiskLevel } from "@/components/riskBadge/RiskLevel";
import Tooltip from "@/components/shared/tooltip/Tooltip";
import {
  getBackgroundColorByRiskLevel,
  getBackgroundHoverColorByRiskLevel,
  sentenceCap,
} from "@/utils/risk";

export function withDateToRiskLevel(
  data: readonly EntityRiskLevelByDate[]
): EntityRiskLevelByDate[] {
  return data.map(risk => {
    const dateToRiskLevel = risk.riskLevelByDate.reduce(
      (acc: { [date: string]: RiskLevel }, next) => {
        acc[next.date] = next.riskLevel;
        return acc;
      },
      {}
    );
    risk.dateToRiskLevel = dateToRiskLevel;
    return risk;
  });
}

function riskLevelBgClass(riskLevel: RiskLevel): string {
  if (riskLevel == RiskLevel.UNKNOWN || riskLevel == RiskLevel.RECALCULATING) {
    // the heatmap shows white for unknown
    return "";
  }
  return getBackgroundColorByRiskLevel(riskLevel);
}

type headerDatesRowOpts = {
  dates: string[];
  onPreviousDateClick?: () => void;
  onNextDateClick?: () => void;
};

function headerDatesRow({
  dates,
  onPreviousDateClick,
  onNextDateClick,
}: headerDatesRowOpts) {
  const topRowClasses =
    "h-8 flex-none flex flex-col items-center justify-center text-center border border-brand-gray-30 text-neutral-shade-75";

  const dayHeaders = dates.map(date => {
    const day = getFormattedDate(date, false, false, "numeric");

    return (
      <div key={date} className={`${topRowClasses} w-12 py-1`}>
        {day}
      </div>
    );
  });

  const leftArrow = onPreviousDateClick ? (
    <button
      className={cx(topRowClasses, "w-10 rounded-l-sm cursor-pointer")}
      disabled={!onPreviousDateClick}
      onClick={onPreviousDateClick}
    >
      <Icon name={"chevron_big_left"} className="text-lg font-bold" />
    </button>
  ) : null;
  const rightArrow = onNextDateClick ? (
    <button
      className={cx(topRowClasses, "w-10 rounded-r-sm cursor-pointer")}
      disabled={!onNextDateClick}
      onClick={onNextDateClick}
    >
      <Icon name={"chevron_big_right"} className="text-lg font-bold" />
    </button>
  ) : null;

  return (
    <div className="flex items-center">
      {leftArrow}
      {dayHeaders}
      {rightArrow}
    </div>
  );
}

type riskCellProps = {
  date: string;
  entityRisk: EntityRiskLevelByDate;
  firstRow: boolean;
  lastRow: boolean;
};

function riskCell({ date, entityRisk, firstRow, lastRow }: riskCellProps) {
  const sharedCellClasses = cx(
    "w-12 h-8 border-brand-gray-20 border-r border-l",
    {
      "border-b": !lastRow,
      "border-b-2": lastRow,
      "border-t": !firstRow,
    }
  );

  const riskLevel = entityRisk?.dateToRiskLevel?.[date];

  if (!riskLevel)
    return (
      <div key={date} aria-label={`${date}`} className={sharedCellClasses} />
    );

  return (
    <Tooltip
      key={date}
      title={sentenceCap(`${riskLevel} risk`)}
      position="top"
      contentClasses="bg-white font-semibold"
      isDisabled={
        riskLevel === RiskLevel.UNKNOWN || riskLevel === RiskLevel.RECALCULATING
      }
    >
      <div
        aria-label={`${sentenceCap(riskLevel)} risk on ${getFormattedDate(
          date,
          "long"
        )}`}
        className={cx(
          riskLevelBgClass(riskLevel),
          getBackgroundHoverColorByRiskLevel(riskLevel),
          sharedCellClasses
        )}
      />
    </Tooltip>
  );
}

type heatmapColumnOpts = {
  startDate: string;
  endDate: string;
  rowCount: number;
  onPreviousDateClick?: () => void;
  onNextDateClick?: () => void;
};

export function heatmapColumn({
  startDate,
  endDate,
  rowCount,
  onPreviousDateClick,
  onNextDateClick,
}: heatmapColumnOpts): any {
  const monthYear = getFormattedDate(startDate, "long", "numeric", false);
  const dates = getDayRangeBetween(startDate, endDate);

  // 48 is approximate width of each risk cell (w-12)
  const cellWidth = 48;
  const arrowColWidth = 40;
  const spaceForPrevArrowCol = arrowColWidth * (onPreviousDateClick ? 1 : 0);
  const spaceForNextArrowCol = arrowColWidth * (onNextDateClick ? 1 : 0);
  const fullWidth =
    cellWidth * dates.length + spaceForPrevArrowCol + spaceForNextArrowCol;

  return {
    id: "heatmap",
    Header: function header() {
      return (
        <div>
          {monthYear}
          {headerDatesRow({ dates, onPreviousDateClick, onNextDateClick })}
        </div>
      );
    },
    width: fullWidth,
    // eslint-disable-next-line react/display-name
    accessor: (entityRisk: EntityRiskLevelByDate, index: number) => {
      const firstRow = index === 0;
      const lastRow = index === rowCount - 1;
      const spacerClasses = "w-10 h-8 flex-none shrink-0 border-brand-gray-20";

      return (
        <div className="flex">
          {onPreviousDateClick && (
            <div
              className={cx(spacerClasses, "border-r", {
                "border-t": !firstRow,
                "border-b": !lastRow,
                "border-b-2": lastRow,
              })}
            />
          )}
          {dates.map(date => riskCell({ date, firstRow, lastRow, entityRisk }))}
          {onNextDateClick && <div className={cx(spacerClasses, "border-l")} />}
        </div>
      );
    },
  };
}
