import type { PropsWithClassName } from "@/types/Generic";
import type { MonthFormatOptions } from "@/utils/date/helper";
import cx from "classnames";
import { useState } from "react";
import ButtonIcon from "@/components/shared/button/icon/ButtonIcon";
import ButtonSmall from "@/components/shared/button/small/ButtonSmall";
import { getFormattedDate, isDateValid } from "@/utils/date/helper";
import useResizeWindow from "@/hooks/useResizeWindow";

export type DateSelectorProps = PropsWithClassName<{
  date: string;
  isTodayDisabled?: boolean;
  isPreviousDateDisabled?: boolean;
  isNextDateDisabled?: boolean;
  onTodayClicked: () => void;
  onPreviousDateClicked: () => void;
  onNextDateClicked: () => void;
}>;

const breakpointScreenMedium = 768;

export default function DateSelector({
  date,
  isTodayDisabled,
  isPreviousDateDisabled,
  isNextDateDisabled,
  onTodayClicked,
  onPreviousDateClicked,
  onNextDateClicked,
  className,
}: DateSelectorProps): JSX.Element {
  const [monthFormat, setMonthFormat] = useState<MonthFormatOptions>("long");
  const isValid = isDateValid(date);
  const formattedDate = getFormattedDate(date, monthFormat);

  const onResizeWindow = (isThresholdExceeded: boolean) => {
    setMonthFormat(isThresholdExceeded ? "long" : "short");
  };
  useResizeWindow(breakpointScreenMedium, onResizeWindow);

  return (
    <div className={cx("flex items-center", className)}>
      <ButtonSmall
        label="Today"
        disabled={isTodayDisabled}
        className="bg-brand-urbint-10 border border-brand-urbint-40 shadow-5 hover:shadow-10 text-neutral-shade-75"
        onClick={onTodayClicked}
      />
      {isValid && (
        <p className="text-lg md:text-xl ml-4 text-neutral-shade-100 truncate">
          {formattedDate}
        </p>
      )}

      <div className="flex ml-4 md:hidden text-neutral-shade-75">
        <ButtonIcon
          iconName="chevron_big_left"
          disabled={isPreviousDateDisabled}
          onClick={onPreviousDateClicked}
        />
        <ButtonIcon
          iconName="chevron_big_right"
          className="ml-4"
          disabled={isNextDateDisabled}
          onClick={onNextDateClicked}
        />
      </div>
    </div>
  );
}
