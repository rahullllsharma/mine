import type { CheckKeys } from "./utils";
import type { EnergyBasedObservationLayout as EboDto } from "@/api/generated/types";
import * as Ord from "fp-ts/lib/Ord";
import * as t from "io-ts";
import * as tt from "io-ts-types";
import { Ord as OrdString } from "fp-ts/lib/string";
import { RiskLevel, FormStatus } from "@/api/generated/types";
import {
  stringEnum,
  validDateTimeCodecS,
  validDurationCodecS,
} from "@/utils/validation";
import { incidentTaskIdCodec } from "@/api/codecs/incident";
import {
  activitiesGroupIdCodec,
  libraryTaskIdCodec,
  workTypeIdCodec,
} from "./libraryTask";
import { hazardIdCodec } from "./hazard";
import { gpsCoordinatesCodec, sourceInfoCodec } from "./jsb";
import { hazardControlIdCodec } from "./hazardControl";

interface EboIdBrand {
  readonly EboId: unique symbol;
}

interface PersonnelIdBrand {
  readonly PersonnelId: unique symbol;
}

interface TaskHazardConnectorIdBrand {
  readonly TaskHazardConnectorId: unique symbol;
}

interface HazardControlConnectorIdBrand {
  readonly HazardControlConnectorId: unique symbol;
}

export const eboIdCodec = t.brand(
  tt.NonEmptyString,
  (s): s is t.Branded<tt.NonEmptyString, EboIdBrand> => true,
  "EboId"
);
export type EboId = t.TypeOf<typeof eboIdCodec>;
export const ordEboId = Ord.contramap((id: EboId) => id)(OrdString);

export const personnelIdCodec = t.brand(
  tt.NonEmptyString,
  (s): s is t.Branded<tt.NonEmptyString, PersonnelIdBrand> => true,
  "PersonnelId"
);

export type PersonnelId = t.TypeOf<typeof personnelIdCodec>;

export const taskHazardConnectorIdCodec = t.brand(
  tt.NonEmptyString,
  (s): s is t.Branded<tt.NonEmptyString, TaskHazardConnectorIdBrand> => true,
  "TaskHazardConnectorId"
);

export type TaskHazardConnectorId = t.TypeOf<typeof taskHazardConnectorIdCodec>;

export const hazardControlConnectorIdCodec = t.brand(
  tt.NonEmptyString,
  (s): s is t.Branded<tt.NonEmptyString, HazardControlConnectorIdBrand> => true,
  "HazardControlConnectorId"
);

export type HazardControlConnectorId = t.TypeOf<
  typeof hazardControlConnectorIdCodec
>;

export const eboHazardControlCodec = t.type({
  id: hazardControlIdCodec,
  name: t.string,
  hazardControlConnectorId: tt.optionFromNullable(
    hazardControlConnectorIdCodec
  ),
});

export const hazardObservationCodec = t.type({
  id: hazardIdCodec,
  name: tt.NonEmptyString,
  taskHazardConnectorId: tt.optionFromNullable(taskHazardConnectorIdCodec),
  hazardControlConnectorId: tt.optionFromNullable(
    hazardControlConnectorIdCodec
  ),
  description: tt.optionFromNullable(t.string),
  energyLevel: tt.optionFromNullable(t.string),
  directControls: tt.optionFromNullable(t.array(eboHazardControlCodec)),
  directControlsImplemented: tt.optionFromNullable(t.boolean),
  directControlDescription: tt.optionFromNullable(t.string),
  indirectControls: tt.optionFromNullable(t.array(eboHazardControlCodec)),
  limitedControls: tt.optionFromNullable(t.array(eboHazardControlCodec)),
  limitedControlDescription: tt.optionFromNullable(t.string),
  observed: t.boolean,
  reason: tt.optionFromNullable(t.string),
});

export type HazardObservation = t.TypeOf<typeof hazardObservationCodec>;

export const selectedTaskCodec = t.type({
  id: libraryTaskIdCodec,
  name: t.string,
  fromWorkOrder: t.boolean,
  riskLevel: t.string.pipe(
    stringEnum<typeof RiskLevel>(RiskLevel, "RiskLevel")
  ),
  instanceId: t.number,
  taskHazardConnectorId: tt.optionFromNullable(taskHazardConnectorIdCodec),
  hazards: t.array(hazardObservationCodec),
});

export type SelectedTaskCodec = t.TypeOf<typeof selectedTaskCodec>;

export const eboActivityCodec = t.type({
  id: activitiesGroupIdCodec,
  name: tt.NonEmptyString,
  tasks: t.array(selectedTaskCodec),
});

export type EboActivity = t.TypeOf<typeof eboActivityCodec>;

export const additionalInformationCodec = tt.optionFromNullable(t.string);

export type AdditionalInformation = t.TypeOf<typeof additionalInformationCodec>;

const workTypeCodec = t.type({
  id: workTypeIdCodec,
  name: tt.NonEmptyString,
});

export const CommonCodec = t.type({
  id: tt.optionFromNullable(t.string),
  name: tt.NonEmptyString,
});

export const detailsCodec = t.type({
  departmentObserved: CommonCodec,
  opcoObserved: CommonCodec,
  subopcoObserved: tt.optionFromNullable(CommonCodec),
  observationDate: t.string.pipe(validDateTimeCodecS),
  observationTime: t.string.pipe(validDurationCodecS),
  workLocation: tt.optionFromNullable(t.string),
  workOrderNumber: tt.optionFromNullable(t.string),
  workType: t.array(workTypeCodec),
});

export const highEnergyTaskCodec = t.type({
  activityId: activitiesGroupIdCodec,
  activityName: t.string,
  id: libraryTaskIdCodec,
  instanceId: t.number,
  taskHazardConnectorId: tt.optionFromNullable(taskHazardConnectorIdCodec),
  hazards: t.array(hazardObservationCodec),
});

export type HighEnergyTasksObservations = t.TypeOf<typeof highEnergyTaskCodec>;

export const photoCodec = t.type({
  id: tt.NonEmptyString,
  displayName: tt.NonEmptyString,
  exists: t.boolean,
  name: tt.NonEmptyString,
  signedUrl: tt.NonEmptyString,
  size: tt.NonEmptyString,
  url: tt.NonEmptyString,
});

export type EboPhoto = t.TypeOf<typeof photoCodec>;

export const personnelCodec = t.type({
  id: tt.optionFromNullable(personnelIdCodec),
  name: t.string,
  role: t.string,
});

export const eboCreatedByCodec = t.type({
  firstName: tt.NonEmptyString,
  lastName: tt.NonEmptyString,
  id: tt.NonEmptyString,
  name: tt.NonEmptyString,
});

export const eboContentsCodec = t.type({
  activities: tt.optionFromNullable(t.array(eboActivityCodec)),
  additionalInformation: additionalInformationCodec,
  details: tt.optionFromNullable(detailsCodec),
  gpsCoordinates: tt.optionFromNullable(t.array(gpsCoordinatesCodec)),
  highEnergyTasks: tt.optionFromNullable(t.array(highEnergyTaskCodec)),
  historicIncidents: tt.optionFromNullable(t.array(incidentTaskIdCodec)),
  personnel: tt.optionFromNullable(t.array(personnelCodec)),
  summary: tt.optionFromNullable(t.type({ viewed: t.boolean })),
  photos: tt.optionFromNullable(t.array(photoCodec)),
  sourceInfo: tt.optionFromNullable(sourceInfoCodec),
});

export type EboContents = t.TypeOf<typeof eboContentsCodec>;

type _C = CheckKeys<keyof EboContents, keyof EboDto>;

export const eboCodec = t.type({
  id: eboIdCodec,
  contents: eboContentsCodec,
  createdBy: eboCreatedByCodec,
  status: t.string.pipe(
    stringEnum<typeof FormStatus>(FormStatus, "FormStatus")
  ),
  completedBy: tt.optionFromNullable(
    t.type({
      id: tt.NonEmptyString,
    })
  ),
});

export type Ebo = t.TypeOf<typeof eboCodec>;

export const savedEboInfoCodec = t.type({
  id: eboIdCodec,
  createdBy: eboCreatedByCodec,
  status: t.string.pipe(
    stringEnum<typeof FormStatus>(FormStatus, "FormStatus")
  ),
  contents: eboContentsCodec,
  completedBy: tt.optionFromNullable(
    t.type({
      id: tt.NonEmptyString,
    })
  ),
});

export type SavedEboInfo = t.TypeOf<typeof savedEboInfoCodec>;

export const eboDetailsForFormHistoryCodec = t.type({
  completedBy: tt.optionFromNullable(
    t.type({
      id: tt.NonEmptyString,
    })
  ),
  contents: eboContentsCodec,
  createdBy: eboCreatedByCodec,
  id: eboIdCodec,
  status: t.string.pipe(
    stringEnum<typeof FormStatus>(FormStatus, "FormStatus")
  ),
  updatedAt: t.string,
  completedAt: t.string,
  createdAt: t.string,
});

export type EboDetailsForFormHistory = t.TypeOf<
  typeof eboDetailsForFormHistoryCodec
>;
