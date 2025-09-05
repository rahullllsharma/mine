import type { Option } from "fp-ts/lib/Option";
import * as E from "fp-ts/lib/Either";
import * as O from "fp-ts/lib/Option";
import { identity, pipe } from "fp-ts/lib/function";
import * as t from "io-ts";
import * as tt from "io-ts-types";
import { DateTime, Duration } from "luxon";
import { failure } from "io-ts/PathReporter";

export const showValidationError = (e: t.Errors): string =>
  pipe(failure(e), errors => errors.join("\n"));

export const withMessage =
  <C extends t.Any>(msg: (i: t.InputOf<C>, c: t.Context) => string) =>
  (codec: C) =>
    tt.withMessage(codec, msg);

interface ValidDateBrand {
  readonly ValidDate: unique symbol;
}

function isDate(d: unknown): d is DateTime {
  return d instanceof DateTime;
}

export const dateTimeCodec = new t.Type<DateTime, DateTime, unknown>(
  "Date",
  isDate,
  (u, c) => (isDate(u) ? t.success(u) : t.failure(u, c, "Invalid date")),
  t.identity
);

export const validDateTimeCodec = t.brand(
  dateTimeCodec,
  (d): d is t.Branded<DateTime, ValidDateBrand> => d.isValid,
  "ValidDate"
);

export type ValidDateTime = t.TypeOf<typeof validDateTimeCodec>;

export const dateLaterOrEqual = (target: ValidDateTime) => {
  return new t.Type<ValidDateTime, ValidDateTime, ValidDateTime>(
    "DateLaterOrEqual",
    validDateTimeCodec.is,
    (u, c) =>
      u.year >= target.year && u.month >= target.month && u.day >= target.day
        ? t.success(u)
        : t.failure(
            u,
            c,
            "Date must be after or equal to " +
              target.setZone("local").toFormat("dd/MM/yyyy")
          ),
    identity
  );
};

export const dateEarlierOrEqual = (target: ValidDateTime) => {
  return new t.Type<ValidDateTime, ValidDateTime, ValidDateTime>(
    "DateEarlierOrEqual",
    validDateTimeCodec.is,
    (u, c) => {
      return u.year <= target.year &&
        u.month <= target.month &&
        u.day >= target.day - 1 &&
        u.day <= target.day + 14
        ? t.success(u)
        : t.failure(
            u,
            c,
            "Invalid date. Please enter a date between yesterday and two weeks in the future."
          );
    },
    identity
  );
};

export const validDateTimeCodecS = new t.Type<ValidDateTime, string, string>(
  "ValidDateS",
  validDateTimeCodec.is,
  (u, c) => {
    const d = DateTime.fromISO(u);
    return validDateTimeCodec.is(d)
      ? t.success(d)
      : t.failure(u, c, "Invalid date");
  },
  a => a.toISO() || ""
);

interface ValidDurationBrand {
  readonly ValidDuration: unique symbol;
}

function isDuration(d: unknown): d is Duration {
  return d instanceof Duration;
}

export const durationCodec = new t.Type<Duration, Duration, unknown>(
  "Duration",
  isDuration,
  (u, c) => (isDuration(u) ? t.success(u) : t.failure(u, c, "Invalid time")),
  t.identity
);

export const validDurationCodec = t.brand(
  durationCodec,
  (d): d is t.Branded<Duration, ValidDurationBrand> => d.isValid,
  "ValidDuration"
);

export type ValidDuration = t.TypeOf<typeof validDurationCodec>;

export const validDurationCodecS = new t.Type<ValidDuration, string, string>(
  "ValidDurationS",
  validDurationCodec.is,
  (u, c) => {
    const d = Duration.fromISOTime(u);
    return validDurationCodec.is(d)
      ? t.success(d)
      : t.failure(u, c, "Invalid time");
  },
  a => a.toISOTime() || ""
);

export const nonEmptyStringCodec = (
  allowWhitespace = false
): t.Type<tt.NonEmptyString, string, string> =>
  pipe(
    new t.Type<tt.NonEmptyString, string, string>(
      "NonEmptyString",
      tt.NonEmptyString.is,
      (u, c) => tt.NonEmptyString.validate(allowWhitespace ? u : u?.trim(), c),
      tt.NonEmptyString.encode
    ),
    withMessage(() => "This field is required")
  );

// eslint-disable-next-line @typescript-eslint/no-explicit-any
export function optionFromString<C extends t.Type<any, string, unknown>>(
  codec: C,
  name = `OptionFromString<${codec.name}>`
) {
  return new t.Type<Option<t.TypeOf<C>>, string, unknown>(
    name,
    (u): u is Option<t.TypeOf<C>> => tt.option(codec).is(u),
    (u, c) => {
      if (u === "") {
        return t.success(O.none);
      } else {
        return pipe(
          codec.validate(u, c),
          E.fold(E.left, val => t.success(O.some(val)))
        );
      }
    },
    x => (O.isSome(x) ? codec.encode(x.value) : "")
  );
}

export const intCodec = new t.Type<t.Int, number, number>(
  "Int",
  t.Int.is,
  t.Int.validate,
  t.Int.encode
);

export const intCodecS: t.Type<t.Int, string, string> = new t.Type<
  t.Int,
  string,
  string
>(
  "IntFromString",
  t.Int.is,
  tt.IntFromString.validate,
  tt.IntFromString.encode
);

interface ValidPhoneNumberBrand {
  readonly ValidPhoneNumber: unique symbol;
}

export const validPhoneNumberCodec = pipe(
  t.brand(
    nonEmptyStringCodec(),
    (s): s is t.Branded<tt.NonEmptyString, ValidPhoneNumberBrand> =>
      /^\d{10}$/.test(s),
    "ValidPhoneNumber"
  ),
  withMessage(() => "Invalid phone number")
);

export type ValidPhoneNumber = t.TypeOf<typeof validPhoneNumberCodec>;

const isNumericEnumValue = <T extends { [key: string]: string | number }>(
  e: T,
  u: unknown
): u is number & T[keyof T] =>
  typeof u === "number" && Object.values(e).includes(u);

const isStringEnumValue = <T extends { [key: string]: string }>(
  e: T,
  u: unknown
): u is T[keyof T] => typeof u === "string" && Object.values(e).includes(u);

export function numericEnum<T extends { [key: string]: string | number }>(
  e: T,
  name: string
) {
  return new t.Type<T[keyof T], number, number>(
    name,
    (u): u is T[keyof T] => isNumericEnumValue(e, u),
    (u, c) => (isNumericEnumValue(e, u) ? t.success(u) : t.failure(u, c)),
    (x: unknown) => x as number
  );
}

export function stringEnum<T extends { [key: string]: string }>(
  e: T,
  name: string
) {
  return new t.Type<T[keyof T], string, string>(
    name,
    (u): u is T[keyof T] => isStringEnumValue(e, u),
    (u, c) => (isStringEnumValue(e, u) ? t.success(u) : t.failure(u, c)),
    (x: unknown) => x as string
  );
}

type LiteralNES<S extends string> = S extends "" ? never : S;

/**
 * SHOULD ONLY BE USED WITH STRING LITERALS
 * - use for testing or hardcoded data only
 *
 * eg.
 * literalNES("") will fail the type check
 * literalNES("something") will produce NonEmptyString
 *
 * DON'T DO THIS
 * literalNES(s)
 * if s === "", this will throw an exception at runtime
 */
export function literalNES<S extends string>(
  s: LiteralNES<S>
): tt.NonEmptyString {
  if (s === "") {
    throw new Error("SHOULD ONLY BE USED WITH STRING LITERALS");
  }

  return s as string as tt.NonEmptyString;
}
