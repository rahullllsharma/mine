import type { CriticalActivityType } from "../../container/report/dailyInspection/types";
import { useEffect, useState } from "react";
import {
  convertDateToString,
  getDate,
  getDayRange,
  getDefaultDate,
  isDateWithinRange,
  isFollowingDate,
  isPreviousDate,
} from "@/utils/date/helper";
import { RiskLevel } from "../riskBadge/RiskLevel";
import CalendarDayButton from "./calendarButton/calendarDayButton/CalendarDayButton";
import CalendarNavButton from "./calendarButton/calendarNavButton/CalendarNavButton";
import DateSelector from "./dateSelector/DateSelector";

export type CalendarProps = {
  startDate: string;
  endDate: string;
  onDateSelect: (date: string) => void;
  defaultDate?: string;
  isCritical?: boolean;
  dateRangeNavigator?: (initialDate: string, finalDate: string) => void;
  criticalActivityData?: CriticalActivityType[];
  riskLevel?: RiskLevel;
};

export default function Calendar({
  startDate,
  endDate,
  onDateSelect,
  defaultDate = "",
  dateRangeNavigator,
  criticalActivityData,
  riskLevel = RiskLevel.UNKNOWN,
}: CalendarProps): JSX.Element {
  const today = convertDateToString();
  const [selectedDate, setSelectedDate] = useState(
    getDefaultDate(startDate, endDate, defaultDate || today)
  );
  const [responsiveNavHelper, setResponsiveNavHelper] = useState(3); //middle item
  const [dateRange, setDateRange] = useState(
    getDayRange(getDefaultDate(startDate, endDate, today), 3, 3)
  );

  const isDayDisabled = (date: string) =>
    !isDateWithinRange(startDate, endDate, date);

  const isTodayDisabled = !isDateWithinRange(startDate, endDate, today);
  const isLastWeekDisabled = isPreviousDate(dateRange[0], startDate);
  const isPreviousDayDisabled = isPreviousDate(selectedDate, startDate);
  const isNextWeekDisabled = isFollowingDate(dateRange[6], endDate);
  const isNextDayDisabled = isFollowingDate(selectedDate, endDate);

  const setDate = (date: string): void => {
    setSelectedDate(date);
    onDateSelect(date);
  };

  const todayClickHandler = (): void => {
    if (!isDateWithinRange(dateRange[0], dateRange[6], today)) {
      setDateRange(getDayRange(today, 3, 3));
    }
    setDate(today);
    setResponsiveNavHelper(3);
  };

  const navigateToPreviousDay = (): void => {
    if (responsiveNavHelper === 0) {
      setDateRange(getDayRange(getDate(selectedDate, -1), 6, 0));
      setResponsiveNavHelper(6);
    } else {
      setResponsiveNavHelper(prevState => prevState - 1);
    }
    setDate(getDate(selectedDate, -1));
  };

  const navigateToNextDay = (): void => {
    if (responsiveNavHelper === 6) {
      setDateRange(getDayRange(getDate(selectedDate, 1), 0, 6));
      setResponsiveNavHelper(0);
    } else {
      setResponsiveNavHelper(prevState => prevState + 1);
    }
    setDate(getDate(selectedDate, 1));
  };

  const navigateToLastWeek = (): void => {
    const date = getDate(dateRange[0], -1);
    setDateRange(getDayRange(date, 6, 0));
    setDate(date);
    setResponsiveNavHelper(6);
  };

  const navigateToNextWeek = (): void => {
    const date = getDate(dateRange[6], 1);
    setDateRange(getDayRange(date, 0, 6));
    setSelectedDate(date);
    setDate(date);
    setResponsiveNavHelper(0);
  };

  useEffect(() => {
    dateRangeNavigator ? dateRangeNavigator(dateRange[0], dateRange[6]) : null;
  }, [dateRange]);

  return (
    <>
      <DateSelector
        className="mb-3"
        date={selectedDate}
        isTodayDisabled={isTodayDisabled}
        isPreviousDateDisabled={isPreviousDayDisabled}
        isNextDateDisabled={isNextDayDisabled}
        onTodayClicked={todayClickHandler}
        onPreviousDateClicked={navigateToPreviousDay}
        onNextDateClicked={navigateToNextDay}
      />
      <div className="md:flex justify-between hidden">
        <CalendarNavButton
          className="lg:mr-12 mr-4"
          icon="chevron_big_left"
          isDisabled={isLastWeekDisabled}
          onClick={navigateToLastWeek}
        />
        <div className="flex flex-1 lg:justify-center justify-between">
          {dateRange.map(date => (
            <CalendarDayButton
              className="lg:mr-8 last:mr-0"
              key={date}
              date={date}
              isDisabled={isDayDisabled(date)}
              isActive={selectedDate === date}
              onClick={() => setDate(date)}
              isCritical={
                (
                  criticalActivityData?.find(
                    (data: CriticalActivityType) => data.date === date
                  ) || {}
                ).isCritical || false
              }
              riskLevel={riskLevel}
            />
          ))}
        </div>
        <CalendarNavButton
          className="lg:ml-12 ml-4"
          icon="chevron_big_right"
          isDisabled={isNextWeekDisabled}
          onClick={navigateToNextWeek}
        />
      </div>
    </>
  );
}
