import * as Eq from "fp-ts/lib/Eq";
import * as Ord from "fp-ts/lib/Ord";
import { Eq as EqString, Ord as OrdString } from "fp-ts/lib/string";
import * as t from "io-ts";

export const criticalRiskCodec = t.union([
  t.literal("ArcFlash"),
  t.literal("CollisionLossOfControl"),
  t.literal("ConfinedSpace"),
  t.literal("ExposureToEnergy"),
  t.literal("FallOrFallArrest"),
  t.literal("FireOrExplosion"),
  t.literal("HoistedLoads"),
  t.literal("LineOfFire"),
  t.literal("MobileEquipment"),
  t.literal("TrenchingOrExcavation"),
]);

export type CriticalRisk = t.TypeOf<typeof criticalRiskCodec>;

export const ordCriticalRisk = Ord.contramap((risk: CriticalRisk) => risk)(
  OrdString
);
export const eqCriticalRisk = Eq.contramap((risk: CriticalRisk) => risk)(
  EqString
);
