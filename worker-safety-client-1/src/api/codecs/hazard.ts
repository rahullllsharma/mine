import type { LibraryHazard as HazardDto } from "../generated/types";
import type { CheckKeys } from "./utils";
import * as t from "io-ts";
import * as tt from "io-ts-types";
import * as Ord from "fp-ts/lib/Ord";
import * as Eq from "fp-ts/lib/Eq";
import { Eq as EqString, Ord as OrdString } from "fp-ts/lib/string";
import { stringEnum } from "@/utils/validation";
import { EnergyType } from "../generated/types";
import { hazardControlCodec } from "./hazardControl";

interface HazardIdBrand {
  readonly HazardId: unique symbol;
}

// duplicate declaratiog to avoid circular-dependency
interface LibraryTaskIdBrand {
  readonly TaskId: unique symbol;
}
const libraryTaskIdCodec = t.brand(
  tt.NonEmptyString,
  (s): s is t.Branded<tt.NonEmptyString, LibraryTaskIdBrand> => true,
  "TaskId"
);

export enum EnergyLevel {
  HighEnergy = "HIGH_ENERGY",
  LowEnergy = "LOW_ENERGY",
  NotDefined = "NOT_DEFINED",
}

export enum ApplicabilityLevel {
  ALWAYS = "ALWAYS",
  MOSTLY = "MOSTLY",
  RARELY = "RARELY",
  NEVER = "NEVER",
}

export const energyLevelCodec = stringEnum<typeof EnergyLevel>(
  EnergyLevel,
  "EnergyLevel"
);

export const applicabilityLevelCodec = stringEnum<typeof ApplicabilityLevel>(
  ApplicabilityLevel,
  "ApplicabilityLevel"
);

export const energyTypeCodec = stringEnum<typeof EnergyType>(
  EnergyType,
  "EnergyType"
);

export const hazardIdCodec = t.brand(
  tt.NonEmptyString,
  (s): s is t.Branded<tt.NonEmptyString, HazardIdBrand> => true,
  "HazardId"
);
export type HazardId = t.TypeOf<typeof hazardIdCodec>;

export const ordHazardId = Ord.contramap((id: HazardId) => id)(OrdString);
export const eqHazardId = Eq.contramap((id: HazardId) => id)(EqString);
export const hazardApplicabilityLevelsCodec = t.type({
  applicabilityLevel: t.string.pipe(applicabilityLevelCodec),
  taskId: libraryTaskIdCodec,
});
export const hazardCodec = t.type({
  id: hazardIdCodec,
  name: t.string,
  isApplicable: t.boolean,
  controls: t.array(hazardControlCodec),
  energyType: tt.optionFromNullable(t.string.pipe(energyTypeCodec)),
  energyLevel: tt.optionFromNullable(t.string.pipe(energyLevelCodec)),
  taskApplicabilityLevels: t.array(hazardApplicabilityLevelsCodec),
  imageUrl: tt.optionFromNullable(t.string),
  archivedAt: tt.optionFromNullable(t.string),
});

export const hazardResultCodec = t.type({
  hazardsLibrary: t.array(hazardCodec),
});
export type Hazard = t.TypeOf<typeof hazardCodec>;

type _C = CheckKeys<keyof Hazard, keyof HazardDto>;
