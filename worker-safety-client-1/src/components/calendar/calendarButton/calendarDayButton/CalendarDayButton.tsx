import type { CalendarButtonProps } from "../CalendarButton";
import cx from "classnames";
import { Icon } from "@urbint/silica";
import { getDayAndWeekdayFromDate, checkIsToday } from "@/utils/date/helper";
import { useTenantStore } from "@/store/tenant/useTenantStore.store";
import { RiskLevel } from "../../../riskBadge/RiskLevel";
import CalendarButton from "../CalendarButton";
import Tooltip from "../../../shared/tooltip/Tooltip";
import { getTextColorByRiskLevel } from "../../../../utils/risk";

export type CalendarDayButtonProps = CalendarButtonProps & {
  date: string;
  isCritical?: boolean;
  riskLevel?: RiskLevel;
};

export default function CalendarDayButton({
  date,
  isCritical = false,
  riskLevel = RiskLevel.UNKNOWN,
  ...tailProps
}: CalendarDayButtonProps): JSX.Element {
  const [day, weekday] = getDayAndWeekdayFromDate(date);
  const { activity: activityEntity } = useTenantStore(state =>
    state.getAllEntities()
  );

  const isToday = checkIsToday(date);
  const dayStyles = isToday ? "text-brand-urbint-40" : "text-brand-urbint-60";

  return (
    <CalendarButton {...tailProps} isToday={isToday}>
      <span className={cx("text-base font-semibold", dayStyles)}>{day}</span>
      <div className="flex">
        <span className="mt-1 text-tiny font-medium text-neutral-shade-100">
          {weekday}
        </span>
        {isCritical && (
          <Tooltip
            title={`${activityEntity.attributes.criticalActivity.label} scheduled`}
            position="bottom"
            className="max-w-xm"
          >
            <Icon
              name={"warning"}
              className={cx(
                "pointer-events-none text-lg bg-transparent ml-1 mt-[0.1rem] leading-none",
                getTextColorByRiskLevel(riskLevel)
              )}
            />
          </Tooltip>
        )}
      </div>
    </CalendarButton>
  );
}
