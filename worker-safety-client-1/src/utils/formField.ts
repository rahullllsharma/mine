import type { Either } from "fp-ts/Either";
import type * as t from "io-ts";
import { right } from "fp-ts/Either";

export type FormField<E, R, V> = {
  readonly val: Either<E, V>;
  readonly raw: R;
  readonly dirty: boolean;
};

export const initFormField =
  <E, R, V>(decoderFn: (s: R) => Either<E, V>) =>
  (raw: R): FormField<E, R, V> => ({ raw, val: decoderFn(raw), dirty: false });

export const updateFormField =
  <E, R, V>(decoderFn: (s: R) => Either<E, V>) =>
  (raw: R): FormField<E, R, V> => ({ raw, val: decoderFn(raw), dirty: true });

export const setFormField =
  <E, R, V>(encodeFn: (v: V) => R) =>
  (value: V): FormField<E, R, V> => ({
    raw: encodeFn(value),
    val: right(value),
    dirty: false,
  });

export const setDirty = <E, R, V>(
  field: FormField<E, R, V>
): FormField<E, R, V> => ({
  ...field,
  dirty: true,
});

export type FieldDefinition<V> = {
  init: (raw: string) => FormField<t.Errors, string, V>;
  update: (raw: string) => FormField<t.Errors, string, V>;
};

export function fieldDef<V>(
  decoder: (r: string) => t.Validation<V>
): FieldDefinition<V> {
  return {
    init: initFormField<t.Errors, string, V>(decoder),
    update: updateFormField<t.Errors, string, V>(decoder),
  };
}
