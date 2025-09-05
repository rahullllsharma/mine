import type { LibraryControl as HazardControlDto } from "../generated/types";
import type { CheckKeys } from "./utils";
import type { ControlSelection } from "./jsb";
import * as t from "io-ts";
import * as tt from "io-ts-types";
import * as Ord from "fp-ts/lib/Ord";
import * as Eq from "fp-ts/lib/Eq";
import { Eq as EqString, Ord as OrdString } from "fp-ts/lib/string";
import { stringEnum } from "@/utils/validation";

interface HazardControlIdBrand {
  readonly HazardControlId: unique symbol;
}

export const ordHazardControlName = Ord.contramap(
  (hazardControl: HazardControl) => hazardControl.name
)(OrdString);

export const ordHazardControlId = Ord.contramap((id: HazardControlId) => id)(
  OrdString
);

export const eqHazardControlId = Eq.contramap((id: HazardControlId) => id)(
  EqString
);

export const ordControlSelectionById = Ord.contramap(
  (controlSelection: ControlSelection) => controlSelection.id
)(OrdString);

export const eqControlSelectionById = Eq.contramap(
  (controlSelection: ControlSelection) => controlSelection.id
)(EqString);

export enum ControlType {
  DIRECT = "DIRECT",
  INDIRECT = "INDIRECT",
}

export const controlTypeCodec = stringEnum<typeof ControlType>(
  ControlType,
  "ControlType"
);

export const hazardControlIdCodec = t.brand(
  tt.NonEmptyString,
  (s): s is t.Branded<tt.NonEmptyString, HazardControlIdBrand> => true,
  "HazardControlId"
);

export type HazardControlId = t.TypeOf<typeof hazardControlIdCodec>;

export const hazardControlCodec = t.type({
  id: hazardControlIdCodec,
  name: t.string,
  isApplicable: t.boolean,
  controlType: tt.optionFromNullable(t.string.pipe(controlTypeCodec)),
  ppe: tt.optionFromNullable(t.boolean),
});
export type HazardControl = t.TypeOf<typeof hazardControlCodec>;

type _C = CheckKeys<keyof HazardControl, keyof HazardControlDto>;
