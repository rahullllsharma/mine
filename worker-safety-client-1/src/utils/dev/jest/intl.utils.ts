/** Mock the default locale when using the Intl.DateTimeFormat class */
export function mockIntlDateTimeFormatLocale(locale: string): void {
  const { DateTimeFormat } = Intl;
  jest
    .spyOn(global.Intl, "DateTimeFormat")
    .mockImplementation((_, options) => new DateTimeFormat(locale, options));
}
