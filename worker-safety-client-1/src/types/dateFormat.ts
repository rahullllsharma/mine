// Date formatting types and interfaces

export type DateFormatType = "date" | "time" | "datetime-local";

export interface LocaleFormatConfig {
  dateFormat: string;
  timeFormat: string;
  fallbackDateFormat: string;
  fallbackTimeFormat: string;
}
