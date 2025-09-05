import {
  convertDateToString,
  convertToDate,
  getEarliestDate,
} from "@/utils/date/helper";

type GetDatesBoundariesProps = {
  minStartDate: string | undefined;
  minEndDate: string | undefined;
};

const getDatesBoundaries = (
  startDate?: string,
  minProjectDate?: string,
  maxProjectDate?: string
): GetDatesBoundariesProps => {
  let minStartDate;
  try {
    minStartDate = minProjectDate
      ? convertDateToString(minProjectDate)
      : undefined;
  } catch (e) {}

  let minEndDate;
  try {
    let date;
    if (maxProjectDate && startDate) {
      date = getEarliestDate(maxProjectDate, startDate);
    } else if (maxProjectDate || startDate) {
      date = convertToDate(maxProjectDate ?? startDate);
    }

    minEndDate = date ? convertDateToString(date) : undefined;
  } catch (e) {}

  return {
    minStartDate,
    minEndDate,
  };
};

export { getDatesBoundaries };
