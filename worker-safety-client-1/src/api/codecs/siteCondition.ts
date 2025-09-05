import type { SiteConditionsQuery } from "../generated/types";
import type { CheckKeys } from "./utils";
import * as Eq from "fp-ts/lib/Eq";
import * as Ord from "fp-ts/lib/Ord";
import { Eq as EqString, Ord as OrdString } from "fp-ts/lib/string";
import * as t from "io-ts";
import * as tt from "io-ts-types";
import { librarySiteConditionIdCodec } from "./librarySiteCondition";

interface SiteConditionIdBrand {
  readonly SiteConditionId: unique symbol;
}

export const siteConditionIdCodec = t.brand(
  tt.NonEmptyString,
  (s): s is t.Branded<tt.NonEmptyString, SiteConditionIdBrand> => true,
  "SiteConditionId"
);
export type SiteConditionId = t.TypeOf<typeof siteConditionIdCodec>;

export const ordSiteConditionId = Ord.contramap((id: SiteConditionId) => id)(
  OrdString
);
export const eqSiteConditionId = Eq.contramap((id: SiteConditionId) => id)(
  EqString
);

export const siteConditionCodec = t.type({
  id: siteConditionIdCodec,
  name: tt.NonEmptyString,
  librarySiteCondition: t.type({
    id: librarySiteConditionIdCodec,
  }),
});

export type SiteCondition = t.TypeOf<typeof siteConditionCodec>;

type _C = CheckKeys<
  keyof SiteCondition,
  keyof SiteConditionsQuery["siteConditions"][0]
>;
