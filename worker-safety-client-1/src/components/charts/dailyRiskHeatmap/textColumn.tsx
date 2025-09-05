import type {
  EntityRiskLevelByDate,
  ColumnDef,
} from "@/components/charts/dailyRiskHeatmap/types";
import cx from "classnames";
import Tooltip from "@/components/shared/tooltip/Tooltip";

type BuildTextColumnProps = {
  id: string;
  Header: string;
  width: number;
  accessor: (entityRisk: EntityRiskLevelByDate, index: number) => JSX.Element;
};

export function buildTextColumn(
  rowCount: number,
  columnDef: ColumnDef
): BuildTextColumnProps {
  // `value` should be used to opt-in to the default accessor classes
  const { value, ...rest } = columnDef;

  // `accessor` can be set to overwrite it (if necessary)
  // `width` can be used to create wider columns
  return {
    width: 140,
    accessor: function accessor(
      entityRisk: EntityRiskLevelByDate,
      index: number
    ) {
      const firstRow = index === 0;
      const lastRow = index === rowCount - 1;
      return (
        <div
          className={cx("h-8 py-2 pr-4 border-brand-gray-20", {
            "border-t": !firstRow,
            "border-b": !lastRow,
            "border-b-2": lastRow,
          })}
        >
          {value && (
            <Tooltip
              title={value(entityRisk)}
              position="top"
              contentClasses="bg-white font-semibold"
              containerClasses="block"
            >
              <span className="truncate">{value(entityRisk)}</span>
            </Tooltip>
          )}
        </div>
      );
    },
    ...rest,
  };
}
