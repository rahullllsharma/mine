import type { ProjectLocation as ProjectLocationDto } from "../generated/types";
import type { CheckKeys } from "./utils";
import * as Eq from "fp-ts/lib/Eq";
import * as Ord from "fp-ts/lib/Ord";
import { Eq as EqString, Ord as OrdString } from "fp-ts/lib/string";
import * as t from "io-ts";
import * as tt from "io-ts-types";
import { stringEnum } from "@/utils/validation";
import { RiskLevel } from "../generated/types";
import { jsbIdCodec } from "./jsb";
import { siteConditionCodec } from "./siteCondition";
import { taskCodec } from "./task";
import { activityCodec } from "./activity";

interface ProjectLocationIdBrand {
  readonly ProjectLocationId: unique symbol;
}

export const projectLocationIdCodec = t.brand(
  tt.NonEmptyString,
  (s): s is t.Branded<tt.NonEmptyString, ProjectLocationIdBrand> => true,
  "ProjectLocationId"
);
export type ProjectLocationId = t.TypeOf<typeof projectLocationIdCodec>;

export const ordProjectLocationId = Ord.contramap(
  (id: ProjectLocationId) => id
)(OrdString);
export const eqProjectLocationId = Eq.contramap((id: ProjectLocationId) => id)(
  EqString
);

export const jsbStatusCodec = t.union([
  t.literal("COMPLETE"),
  t.literal("IN_PROGRESS"),
]);

export const jsbDataCodec = t.type({
  id: jsbIdCodec,
  name: tt.NonEmptyString,
  status: jsbStatusCodec,
  // workPackageName: tt.NonEmptyString,
});
export type JsbData = t.TypeOf<typeof jsbDataCodec>;

export const projectLocationCodec = t.type({
  id: projectLocationIdCodec,
  name: tt.NonEmptyString,
  project: t.type(
    {
      id: tt.NonEmptyString,
      name: tt.NonEmptyString,
      description: tt.optionFromNullable(t.string),
    },
    "Project"
  ),
  address: tt.optionFromNullable(t.string),
  latitude: tt.NumberFromString,
  longitude: tt.NumberFromString,
  riskLevel: t.string.pipe(
    stringEnum<typeof RiskLevel>(RiskLevel, "RiskLevel")
  ),
  jobSafetyBriefings: t.array(jsbDataCodec),
  activities: t.array(activityCodec),
  tasks: t.array(taskCodec),
  siteConditions: t.array(siteConditionCodec),
});
export type ProjectLocation = t.TypeOf<typeof projectLocationCodec>;

type _C = CheckKeys<keyof ProjectLocation, keyof ProjectLocationDto>;
