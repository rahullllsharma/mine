import type { CheckKeys } from "./utils";
import type { LibrarySiteCondition as LibrarySiteConditionDto } from "../generated/types";
import * as Eq from "fp-ts/lib/Eq";
import * as Ord from "fp-ts/lib/Ord";
import { Eq as EqString, Ord as OrdString } from "fp-ts/lib/string";
import * as t from "io-ts";
import * as tt from "io-ts-types";
import { hazardCodec } from "./hazard";

interface LibrarySiteConditionIdBrand {
  readonly SiteConditionId: unique symbol;
}

export const librarySiteConditionIdCodec = t.brand(
  tt.NonEmptyString,
  (s): s is t.Branded<tt.NonEmptyString, LibrarySiteConditionIdBrand> => true,
  "SiteConditionId"
);
export type LibrarySiteConditionId = t.TypeOf<
  typeof librarySiteConditionIdCodec
>;

export const ordLibrarySiteConditionId = Ord.contramap(
  (id: LibrarySiteConditionId) => id
)(OrdString);
export const eqLibrarySiteConditionId = Eq.contramap(
  (id: LibrarySiteConditionId) => id
)(EqString);

export const librarySiteConditionCodec = t.type({
  id: librarySiteConditionIdCodec,
  name: tt.NonEmptyString,
  hazards: t.array(hazardCodec),
  archivedAt: tt.optionFromNullable(tt.NonEmptyString),
});
export type LibrarySiteCondition = t.TypeOf<typeof librarySiteConditionCodec>;

type _C = CheckKeys<keyof LibrarySiteCondition, keyof LibrarySiteConditionDto>;
