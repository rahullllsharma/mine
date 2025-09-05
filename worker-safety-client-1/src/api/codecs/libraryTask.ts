import type { CheckKeys } from "./utils";
import type { LibraryTask as LibraryTaskDto } from "../generated/types";
import * as Eq from "fp-ts/lib/Eq";
import * as Ord from "fp-ts/lib/Ord";
import { Eq as EqString, Ord as OrdString } from "fp-ts/lib/string";
import * as t from "io-ts";
import * as tt from "io-ts-types";
import { stringEnum } from "@/utils/validation";
import { RiskLevel } from "../generated/types";
import { hazardCodec } from "./hazard";

interface LibraryTaskIdBrand {
  readonly TaskId: unique symbol;
}

export const libraryTaskIdCodec = t.brand(
  tt.NonEmptyString,
  (s): s is t.Branded<tt.NonEmptyString, LibraryTaskIdBrand> => true,
  "TaskId"
);
export type LibraryTaskId = t.TypeOf<typeof libraryTaskIdCodec>;

export const ordLibraryTaskId = Ord.contramap((id: LibraryTaskId) => id)(
  OrdString
);
export const eqLibraryTaskId = Eq.contramap((id: LibraryTaskId) => id)(
  EqString
);

interface ActivitiesGroupIdBrand {
  readonly ActivitiesGroupId: unique symbol;
}

export const activitiesGroupIdCodec = t.brand(
  tt.NonEmptyString,
  (s): s is t.Branded<tt.NonEmptyString, ActivitiesGroupIdBrand> => true,
  "ActivitiesGroupId"
);
export type ActivitiesGroupId = t.TypeOf<typeof activitiesGroupIdCodec>;

export const ordActivitiesGroupId = Ord.contramap(
  (id: ActivitiesGroupId) => id
)(OrdString);
export const eqActivitiesGroupId = Eq.contramap((id: ActivitiesGroupId) => id)(
  EqString
);

export const activitiesGroupCodec = t.type({
  id: activitiesGroupIdCodec,
  name: tt.NonEmptyString,
  tasks: t.array(t.type({ id: libraryTaskIdCodec })),
});

export type ActivitiesGroup = t.TypeOf<typeof activitiesGroupCodec>;

interface WorkTypeIdBrand {
  readonly WorkTypeIdBrand: unique symbol;
}

export const workTypeIdCodec = t.brand(
  tt.NonEmptyString,
  (s): s is t.Branded<tt.NonEmptyString, WorkTypeIdBrand> => true,
  "WorkTypeIdBrand"
);
export type WorkTypeId = t.TypeOf<typeof workTypeIdCodec>;

export const eqWorkTypeId = Eq.contramap((id: WorkTypeId) => id)(EqString);

export const eqWorkTypeName = Eq.contramap((name: tt.NonEmptyString) => name)(
  EqString
);

export const eqWorkTypeByName = Eq.contramap(
  (workType: WorkType) => workType.name
)(eqWorkTypeName);

export const eqWorkTypeById = Eq.contramap((workType: WorkType) => workType.id)(
  eqWorkTypeId
);

export const workTypeCodec = t.type({
  id: workTypeIdCodec,
  name: tt.NonEmptyString,
});

export type WorkType = t.TypeOf<typeof workTypeCodec>;

export const libraryTaskCodec = t.type({
  id: libraryTaskIdCodec,
  name: t.string,
  riskLevel: t.string.pipe(
    stringEnum<typeof RiskLevel>(RiskLevel, "RiskLevel")
  ),
  workTypes: tt.optionFromNullable(t.array(workTypeCodec)),
  hazards: t.array(hazardCodec),
  activitiesGroups: tt.optionFromNullable(t.array(activitiesGroupCodec)),
});
export type LibraryTask = t.TypeOf<typeof libraryTaskCodec>;

type _C = CheckKeys<keyof LibraryTask, keyof LibraryTaskDto>;
