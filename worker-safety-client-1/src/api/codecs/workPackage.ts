import * as t from "io-ts";
import * as tt from "io-ts-types";
import { Eq as EqString, Ord as OrdString } from "fp-ts/lib/string";
import * as Ord from "fp-ts/lib/Ord";
import * as Eq from "fp-ts/lib/Eq";

interface WorkPackageIdBrand {
  readonly WorkPackageId: unique symbol;
}

export const workPackageIdCodec = t.brand(
  tt.NonEmptyString,
  (s): s is t.Branded<tt.NonEmptyString, WorkPackageIdBrand> => true,
  "WorkPackageId"
);

export type WorkPackageId = t.TypeOf<typeof workPackageIdCodec>;

export const ordWorkPackageId = Ord.contramap((id: WorkPackageId) => id)(
  OrdString
);
export const eqWorkPackageId = Eq.contramap((id: WorkPackageId) => id)(
  EqString
);
