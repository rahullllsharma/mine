import type { DateFormatType, LocaleFormatConfig } from "../types/dateFormat";

const DEFAULT_LOCALE = "en-US";
const FALLBACK_FORMATS: Record<DateFormatType, string> = {
  date: "MM/DD/YYYY",
  time: "HH:mm",
  "datetime-local": "MM/DD/YYYY HH:mm",
} as const;

const SAMPLE_DATE = new Date(2023, 11, 25, 14, 30);

const FORMAT_REPLACEMENTS = {
  date: { 2023: "YYYY", 12: "MM", 25: "DD" },
  time: { 14: "HH", 30: "mm", 2: "h", PM: "A", AM: "A" },
} as const;

const formatCache = new Map<string, string>();
const localeCache = new Map<string, LocaleFormatConfig>();

const createCacheKey = (locale: string, type: string): string =>
  `${locale}-${type}`;

const normalizeFormat = (format: string): string => {
  return format.replace(/\./g, "/").replace(/-/g, "/");
};

const applyReplacements = (
  text: string,
  replacements: Record<string | number, string>
): string => {
  let result = text;
  Object.entries(replacements).forEach(([search, replace]) => {
    result = result.replace(new RegExp(search.toString(), "g"), replace);
  });
  return result;
};

const getUserLocale = (): string => {
  if (typeof navigator !== "undefined" && navigator.language) {
    return navigator.language;
  }
  return DEFAULT_LOCALE;
};

const getLocaleFormatConfig = (locale: string): LocaleFormatConfig => {
  const cacheKey = `config-${locale}`;

  if (localeCache.has(cacheKey)) {
    return localeCache.get(cacheKey)!;
  }

  const config: LocaleFormatConfig = {
    dateFormat: FALLBACK_FORMATS.date,
    timeFormat: FALLBACK_FORMATS.time,
    fallbackDateFormat: FALLBACK_FORMATS.date,
    fallbackTimeFormat: FALLBACK_FORMATS.time,
  };

  try {
    const dateFormatter = new Intl.DateTimeFormat(locale, {
      year: "numeric",
      month: "2-digit",
      day: "2-digit",
    });

    const formattedDate = dateFormatter.format(SAMPLE_DATE);
    config.dateFormat = normalizeFormat(
      applyReplacements(formattedDate, FORMAT_REPLACEMENTS.date)
    );

    const timeFormatter = new Intl.DateTimeFormat(locale, {
      hour: "2-digit",
      minute: "2-digit",
      hour12: true,
    });

    const formattedTime = timeFormatter.format(SAMPLE_DATE);
    config.timeFormat = applyReplacements(
      formattedTime,
      FORMAT_REPLACEMENTS.time
    );
  } catch (error) {
    console.warn(
      `Failed to generate locale formats for ${locale}, using fallbacks`,
      error
    );
  }

  localeCache.set(cacheKey, config);
  return config;
};

const createDateFormat = (type: DateFormatType, locale: string): string => {
  const cacheKey = createCacheKey(locale, type);

  if (formatCache.has(cacheKey)) {
    return formatCache.get(cacheKey)!;
  }

  const config = getLocaleFormatConfig(locale);
  let format: string;

  switch (type) {
    case "date":
      format = config.dateFormat;
      break;
    case "time":
      format = config.timeFormat;
      break;
    case "datetime-local":
      format = `${config.dateFormat} ${config.timeFormat}`;
      break;
    default:
      format = FALLBACK_FORMATS[type];
  }

  formatCache.set(cacheKey, format);
  return format;
};

const createPlaceholder = (type: DateFormatType, locale: string): string => {
  const format = createDateFormat(type, locale);

  switch (type) {
    case "date":
      return format;
    case "time":
      return "HH:mm";
    case "datetime-local":
      return format
        .replace(/0*h+/g, "HH")
        .replace(/\s*[ap]\.?m\.?\s*/gi, "")
        .replace(/A/g, "")
        .replace(/a/g, "")
        .replace(/\./g, "")
        .replace(/\s+/g, " ");
    default:
      return FALLBACK_FORMATS.date;
  }
};

const createDisplayFormat = (type: DateFormatType, locale: string): string => {
  const config = getLocaleFormatConfig(locale);

  switch (type) {
    case "date":
      return config.dateFormat;
    case "time":
      return "hh:mm A";
    case "datetime-local":
      return `${config.dateFormat} hh:mm A`;
    default:
      return config.fallbackDateFormat;
  }
};

export const getPlaceholder = (type: DateFormatType): string => {
  return createPlaceholder(type, getUserLocale());
};

export const getDisplayFormat = (type: DateFormatType): string => {
  return createDisplayFormat(type, getUserLocale());
};

export type { DateFormatType, LocaleFormatConfig };
