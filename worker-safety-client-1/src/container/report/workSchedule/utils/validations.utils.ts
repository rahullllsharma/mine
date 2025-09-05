import {
  getDateAsUnixTimestamp,
  convertToDate,
  isSameDate,
} from "@/utils/date/helper";

type GreaterThanDateArgs = {
  start: string;
  end: string;
};

type GreaterThanDateTimeArgs = {
  startDate: string;
  startTime: string;
  endDate: string;
  endTime: string;
};

const unpackTimeToNumbers = (time: string) =>
  time
    .split(":")
    .map(p => parseInt(p, 10))
    .concat([0, 0]) as [number, number, number, number];

/**
 * Compares if a date is greater than another date.
 * Needs to unpack those dates before comparing.
 *
 * @param {GreaterThanDateArgs} params
 * @returns {bool}
 */
const greaterThanDate = (params: GreaterThanDateArgs): boolean => {
  const paramsAsArray = Object.values(params);

  // Skip validation when field has an unrecognized type
  if (paramsAsArray.some(param => typeof param !== "string")) {
    return true;
  }

  try {
    return (
      getDateAsUnixTimestamp(params.end) >= getDateAsUnixTimestamp(params.start)
    );
  } catch (e) {
    return false;
  }
};

/**
 * Compares if a date is greater than another.
 * It needs `date` and `times` for both arguments in test.
 *
 * @param {GreaterThanDateTimeArgs} params
 * @returns {bool}
 *
 * @deprecated
 */
const greaterThanTimeSameDay = (params: GreaterThanDateTimeArgs): boolean => {
  const paramsAsArray = Object.values(params);

  // Skip validation when field has an unrecognized type
  if (paramsAsArray.some(param => typeof param !== "string")) {
    return true;
  }

  // there is the potential "risk" that any parameter is NOT a valid date - it's user input, after all ...
  // `new Date(NOT_A_DATE).valueOf` returns NaN which is not equal to anything.
  const { startDate, endDate } = params;

  try {
    const startDateAsDate = convertToDate(startDate);
    const endDateAsDate = convertToDate(endDate);

    if (!isSameDate(startDateAsDate, endDateAsDate)) {
      return true;
    }

    const { startTime, endTime } = params;
    const startDateTimeInMilliseconds = startDateAsDate.setHours(
      ...unpackTimeToNumbers(startTime)
    );
    const endDateTimeInMilliseconds = endDateAsDate.setHours(
      ...unpackTimeToNumbers(endTime)
    );

    return (
      !isNaN(startDateTimeInMilliseconds) &&
      !isNaN(endDateTimeInMilliseconds) &&
      startDateTimeInMilliseconds <= endDateTimeInMilliseconds
    );
  } catch (e) {
    return false;
  }
};

export { greaterThanTimeSameDay, greaterThanDate };
