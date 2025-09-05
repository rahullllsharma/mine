type PluralizeArgs = {
  subject: number | Array<unknown>;
  singular: string;
  plural: string;
  locale?: `${string}-${string}`;
};

const pluralize = ({ subject, singular, plural, locale }: PluralizeArgs) =>
  new Intl.PluralRules(locale).select(
    Array.isArray(subject) ? subject.length : subject
  ) === "one"
    ? singular
    : plural;

export { pluralize };
