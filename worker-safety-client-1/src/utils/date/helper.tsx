import { DateTime } from "luxon";

type DateFormat = string | Date;
export type MonthFormatOptions = "long" | "short" | "2-digit" | "numeric";
export type YearFormatOptions = "2-digit" | "numeric";
export type DayFormatOptions = "2-digit" | "numeric";
export type WeekDayFormatOptions = "long" | "short";

// DateTimeFormatType maps date component types ("day", "month", "year") to their respective format strings ("dd", "MM", "yyyy").
const DateTimeFormatType: Record<string, string> = {
  day: "dd",
  month: "MM",
  year: "yyyy",
};
const timeRegExp = /^([0-9]|0[0-9]|1[0-9]|2[0-3]):[0-5][0-9]/;

/** Uses the Intl.DateTimeFormat object with the user's locale (navigator.language) to format the date.
 * Filter out the parts that correspond to "day", "month", and "year",
 * then maps these parts to their respective format strings as defined in DateTimeFormatType
 * @returns Converted date format according to user's locale language(en-US/en-GB/en-ZA etc..)
 */
export const getLocaleDateFormat = (): string => {
  const date = new Date(2000, 11, 31);
  const formatParts = new Intl.DateTimeFormat(navigator.language, {
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
  }).formatToParts(date);

  return formatParts
    .filter(part => part.type in DateTimeFormatType)
    .map(part => DateTimeFormatType[part.type])
    .join("/");
};
export const getFormattedDate = (
  date: DateFormat,
  monthFormat: MonthFormatOptions | false,
  yearFormat: YearFormatOptions | false = "numeric",
  dayFormat: DayFormatOptions | false = "numeric",
  weekDayFormat?: WeekDayFormatOptions
): string => {
  const format: {
    day?: DayFormatOptions;
    month?: MonthFormatOptions;
    year?: YearFormatOptions;
    weekday?: WeekDayFormatOptions;
  } = {};
  if (dayFormat) {
    format.day = dayFormat;
  }
  if (monthFormat) {
    format.month = monthFormat;
  }
  if (yearFormat) {
    format.year = yearFormat;
  }
  if (weekDayFormat) {
    format.weekday = weekDayFormat;
  }
  return Intl.DateTimeFormat("en-US", format).format(convertToDate(date));
};

export const convertToDateStringFormat = (date: Date): string => {
  // Convert the JavaScript Date object to Luxon DateTime object
  const luxonDateTime = DateTime.fromJSDate(date);

  // Format the Luxon DateTime object as a string in the desired format
  const formattedDate = luxonDateTime.toFormat("yyyy-MM-dd'T'HH:mm:ss");

  return formattedDate;
};
export const isDateValid = (date: string): boolean => {
  return !isNaN(Date.parse(date));
};

export const checkIsToday = (date: string): boolean => {
  if (!isDateValid(date)) {
    return false;
  }

  const today = new Date();
  return isSameDate(convertToDate(date), today);
};

export const isSameDate = (date1: Date, date2: Date): boolean => {
  const firstValue = date1.setHours(0, 0, 0, 0);
  const secondValue = date2.setHours(0, 0, 0, 0);

  return firstValue.valueOf() === secondValue.valueOf();
};

export const getDayAndWeekdayFromDate = (date: string): string[] => {
  if (!isDateValid(date)) {
    return ["", ""];
  }

  const formattedDate = convertToDate(date).toLocaleDateString("en-US", {
    weekday: "short",
    day: "numeric",
  });
  return formattedDate.split(" ");
};

export const getDate = (
  date: DateFormat,
  increment: number,
  { includeToday } = { includeToday: false }
): string => {
  //setting non-zero hours to avoid DST issues: https://docs.microsoft.com/en-us/troubleshoot/developer/browsers/core-features/error-dst-time-zones
  const formattedDate = new Date(convertToDate(date).setHours(6, 0, 0, 0));
  let newIncrement = increment;

  if (includeToday && increment > 0) {
    newIncrement -= 1;
  } else if (includeToday && increment < 0) {
    newIncrement += 1;
  }
  return convertDateToString(
    new Date(formattedDate.getTime() + newIncrement * 24 * 60 * 60 * 1000)
  );
};

export const getDayRange = (
  referenceDay: DateFormat,
  numberOfDaysBefore: number,
  numberOfDaysAfter: number
): string[] => {
  const list = [];

  for (let i = -numberOfDaysBefore; i <= numberOfDaysAfter; i++) {
    list.push(convertDateToString(getDate(referenceDay, i)));
  }

  return list;
};

export const getDayRangeBetween = (
  startDay: DateFormat,
  endDay: DateFormat
): string[] => {
  const timeBetween =
    convertToDate(endDay).valueOf() - convertToDate(startDay).valueOf();
  const daysBetween = timeBetween / (1000 * 3600 * 24);

  return getDayRange(startDay, 0, daysBetween);
};

export const isPreviousDate = (
  date: DateFormat,
  dateToCompare: DateFormat
): boolean => {
  return (
    convertToDate(date).valueOf() <= convertToDate(dateToCompare).valueOf()
  );
};

export const isFollowingDate = (
  date: DateFormat,
  dateToCompare: DateFormat
): boolean => {
  return (
    convertToDate(date).valueOf() >= convertToDate(dateToCompare).valueOf()
  );
};

export const isDateWithinRange = (
  startDate: DateFormat,
  endDate: DateFormat,
  referenceDate: DateFormat
): boolean => {
  const date = convertToDate(referenceDate);

  return (
    isFollowingDate(date, convertToDate(startDate)) &&
    isPreviousDate(date, convertToDate(endDate))
  );
};

/**
 * Return a date in the format yyyy-mm-dd
 *
 * @param date
 * @returns
 */
export const convertDateToString = (date: DateFormat = new Date()): string => {
  return Intl.DateTimeFormat("en-US", {
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
  })
    .format(convertToDate(date))
    .replace(/(\d{2})\/(\d{2})\/(\d{4})/, "$3-$1-$2");
};

export const getCurrentDate = () => {
  const today = new Date();
  const dd = String(today.getDate()).padStart(2, "0");
  const mm = String(today.getMonth() + 1).padStart(2, "0"); // January is 0!
  const yyyy = today.getFullYear();

  return `${yyyy}-${mm}-${dd}`;
};

export const formatCamelCaseString = (input: string) => {
  // Use regular expression to insert spaces before capital letters
  return input.replace(/([a-z])([A-Z])/g, "$1 $2");
};

export const capitalizeFirstLetter = (input: string) => {
  return input.charAt(0).toUpperCase() + input.slice(1).toLowerCase();
};

// format a string with Camel case and replace underscores with hyphens
export const formatStatusString = (status: string | undefined) => {
  if (!status) return;
  if (status === "PENDING_POST_JOB_BRIEF") return "PENDING POST JOB BRIEF";
  if (status === "PENDING_SIGN_OFF") return "PENDING SIGN OFF";
  const formattedText = `${status[0].toUpperCase()}${status
    .slice(1)
    .replace(/_/g, "-")}`;
  return formattedText;
};

export const formatTimeHoursAndMinutes = (time: string): string | undefined => {
  if (typeof time !== "string") {
    return undefined;
  }

  const matches = time.match(timeRegExp);
  return matches?.[0];
};

export const isDateFormatValid = (date: DateFormat): boolean =>
  date instanceof Date || !isNaN(Date.parse(date));

export const convertToDate = (date: DateFormat = new Date()): Date => {
  if (!isDateFormatValid(date)) {
    throw new Error(`Invalid Date = ${date}`);
  }

  if (typeof date === "string") {
    const normalizeDate = /^[0-9]{4,4}\-[0-9]{1,2}\-[0-9]{1,2}$/.test(date)
      ? date.replace(/-/g, "/")
      : date;

    return new Date(normalizeDate);
  }

  return date;
};

export const getEarliestDate = (...dates: DateFormat[]): Date => {
  const uniques = [];

  for (const date of new Set(dates).values()) {
    uniques.push(new Date(date).valueOf());
  }

  return new Date(Math.max(...uniques));
};

export const getDefaultDate = (
  startDate: string,
  endDate: string,
  today: string
): string => {
  if (isDateWithinRange(startDate, endDate, today)) return today;

  let defaultDate = today;

  if (isPreviousDate(today, startDate)) {
    defaultDate = convertDateToString(startDate);
  } else if (isFollowingDate(today, endDate)) {
    defaultDate = convertDateToString(endDate);
  }

  return defaultDate;
};

export const getFormattedDateTimeTimezone = (date: string): string =>
  new Intl.DateTimeFormat("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
    hour: "numeric",
    minute: "numeric",
    timeZoneName: "short",
  }).format(new Date(date));

/**
 * Converts a date as string to the date and time using the longer format including timezone
 * for the given locale (default, the user own locale)
 * @deprecated in favor of luxon lib
 */
export const getFormattedFullDateTime = (
  date: string,
  locale?: string
): string =>
  new Intl.DateTimeFormat(locale, {
    dateStyle: "full",
    timeStyle: "long",
  }).format(new Date(date));

/** Converts a date as string to the date and time, using the short notation for the given locale (default, the user own locale). */
export const getFormattedShortDateTime = (
  date: string,
  locale?: string
): string =>
  new Intl.DateTimeFormat(locale, {
    dateStyle: "short",
    timeStyle: "short",
  }).format(new Date(date));

/** Converts a date as string to yyyy-mm-ddThh:mm format.*/
export const getFormattedLocaleDateTime = (
  dateAsString: string,
  { time = "" }: { time?: string } = {}
): string => {
  if (!isDateValid(dateAsString)) {
    // FIXME: report an issue when converting dates
    console.error("invalid date", dateAsString);
    return "";
  }

  // Construct a new date based on the user local settings
  let date = new Date(dateAsString);

  if (timeRegExp.test(time)) {
    const [hours, minutes] = time.split(":");

    date = new Date(date.setHours(+hours));
    date = new Date(date.setMinutes(+minutes));
  }

  return "[year]-[month]-[day]T[hour]:[minutes]"
    .replace("[year]", date.getFullYear().toString())
    .replace("[month]", (date.getMonth() + 1).toString().padStart(2, "0"))
    .replace("[day]", date.getDate().toString().padStart(2, "0"))
    .replace("[hour]", date.getHours().toString().padStart(2, "0"))
    .replace("[minutes]", date.getMinutes().toString().padStart(2, "0"));
};

export const getGenerationDate = (): string =>
  new Intl.DateTimeFormat("en-US", {
    dateStyle: "short",
    timeStyle: "long",
  }).format(new Date());

export const getDateAsUTC = (date: DateFormat): string =>
  convertToDate(date).toISOString();

export const getDateAsUnixTimestamp = (date: DateFormat): number =>
  convertToDate(date).valueOf();

export const getFullDateTime = (date: DateTime) =>
  date.toLocaleString({
    dateStyle: "full",
    timeStyle: "long",
  });

export const getFormattedShortTime = (date: string, locale = "en-US"): string =>
  new Intl.DateTimeFormat(locale, {
    timeStyle: "short",
  }).format(new Date(date));

export const getFormattedDateTimeForFormAudits = (date: string): string => {
  if (!date) return "";

  const dateObj = new Date(date);

  const dateFormatter = new Intl.DateTimeFormat("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
  });

  const timeFormatter = new Intl.DateTimeFormat("en-US", {
    hour: "numeric",
    minute: "numeric",
    hour12: true,
  });
  const formattedDate = dateFormatter.format(dateObj);
  const formattedTime = timeFormatter.format(dateObj);

  return `${formattedDate}, at ${formattedTime}`;
};

/**
 * Formats a date with abbreviated relative time for recent updates (< 24hrs) and absolute dates for older ones
 * @param dateString - ISO date string from API
 * @returns Formatted date string - abbreviated relative time (e.g., "17 min ago", "2 hr ago") for recent dates, YYYY-MM-DD for older dates
 */
export const formatRelativeOrAbsoluteDate = (dateString: string): string => {
  if (!dateString) return "";

  try {
    const date = DateTime.fromISO(dateString);
    const now = DateTime.now();

    if (!date.isValid) {
      console.error("Invalid date string:", dateString);
      return "";
    }

    // Calculate the difference in hours
    const diffInHours = now.diff(date, "hours").hours;

    // If less than 24 hours, show relative time with abbreviated units
    if (Math.abs(diffInHours) < 24) {
      const diffInMinutes = now.diff(date, "minutes").minutes;
      const diffInSeconds = now.diff(date, "seconds").seconds;

      const isPast = diffInSeconds > 0;
      const absMinutes = Math.abs(diffInMinutes);
      const absHours = Math.abs(diffInHours);

      // Less than 1 minute
      if (absMinutes < 1) {
        return "just now";
      }
      // Less than 1 hour
      else if (absHours < 1) {
        const minutes = Math.round(absMinutes);
        return isPast ? `${minutes} min ago` : `in ${minutes} min`;
      }
      // Less than 24 hours
      else {
        const hours = Math.round(absHours);
        return isPast ? `${hours} hr ago` : `in ${hours} hr`;
      }
    } else {
      // Show absolute date in YYYY-MM-DD format
      return date.toFormat("yyyy-MM-dd");
    }
  } catch (error) {
    console.error("Error formatting date:", error);
    return "";
  }
};
