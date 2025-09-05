import { faker } from "@faker-js/faker";
import {
  getFormattedLocaleDateTime,
  convertDateToString,
} from "../../src/utils/date/helper";

type AllowedTravel = "past" | "future";
type AllowedCloseTravel = "recent" | "soon";

/**
 * Function that randomly generates new date and time with YYYY-MM-DDTHH:MM format
 * @param  {number} days - The number of days that should be used to calculate past and future dates
 * @param  {string} travel - "past" uses faker.date.recent ; "future" uses faker.date.soon
 * @see https://fakerjs.dev/api/date.html#recent
 * @see https://fakerjs.dev/api/date.html#soon
 */
export const getFormattedDateTime = (
  days: number,
  travel: AllowedTravel
): string => {
  if (travel === "past")
    return getFormattedLocaleDateTime(faker.date.recent(days).toISOString());
  else if (travel === "future")
    return getFormattedLocaleDateTime(faker.date.soon(days).toISOString());

  return getFormattedLocaleDateTime(new Date().toISOString());
};

/**
 * Function that randomly generates new dates with YYYY-MM-DD format
 * @param  {number} years - The number of years that should be used to calculate past and future dates
 * @param  {string} travel - "past" uses faker.date.past ; "future" uses faker.date.future
 * @see https://fakerjs.dev/api/date.html#past
 * @see https://fakerjs.dev/api/date.html#future
 */
export const getFormattedDate = (
  years: number,
  travel: AllowedTravel
): string => {
  if (travel === "past") return convertDateToString(faker.date.past(years));
  else if (travel === "future")
    return convertDateToString(faker.date.future(years));
  return getFormattedLocaleDateTime(new Date().toISOString());
};

/**
 * Function that randomly generates new dates with YYYY-MM-DD format
 * @param  {number} days - The number of days that should be used to calculate past and future dates
 * @param  {string} travel - "recent" uses faker.date.recent ; "soon" uses faker.date.soon
 * @see https://fakerjs.dev/api/date.html#recent
 * @see https://fakerjs.dev/api/date.html#soon
 */
export const getCloseFormattedDate = (
  days: number,
  travel: AllowedCloseTravel
): string => {
  if (travel === "recent") return convertDateToString(faker.date.recent(days));
  else if (travel === "soon") return convertDateToString(faker.date.soon(days));
  return getFormattedLocaleDateTime(new Date().toISOString());
};

/**
 * Function that randomly generates new date and time between from and to dates with YYYY-MM-DDTHH:MM format
 * @param  {string} from - The date that starts the date range
 * @param  {string} to - The date that ends the date range
 * @see https://fakerjs.dev/api/date.html#between
 */
export const getBetweenFormattedDateTime = (
  from: string,
  to: string
): string => {
  return getFormattedLocaleDateTime(faker.date.between(from, to).toISOString());
};
