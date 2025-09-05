import type { CheckKeys } from "./utils";
// import type { JobSafetyBriefingLayout as JsbDto } from "../generated/types";
import type { MedicalFacility } from "./medicalFacility";
import type { JsbContentsFragment, JsbDataFragment } from "../generated/types";
import * as Eq from "fp-ts/lib/Eq";
import * as Ord from "fp-ts/lib/Ord";
import { Eq as EqString, Ord as OrdString } from "fp-ts/lib/string";
import { Eq as EqNumber } from "fp-ts/lib/number";
import * as t from "io-ts";
import * as tt from "io-ts-types";
import { stringEnum, validDateTimeCodecS } from "@/utils/validation";
import { VoltageType } from "../generated/types";
import { criticalRiskCodec } from "./criticalRisk";
import { hazardIdCodec } from "./hazard";
import { hazardControlIdCodec } from "./hazardControl";
import { librarySiteConditionIdCodec } from "./librarySiteCondition";
import { libraryTaskIdCodec } from "./libraryTask";
import { workPackageIdCodec } from "./workPackage";
import { medicalFacilityCodec } from "./medicalFacility";

interface JsbIdBrand {
  readonly JsbId: unique symbol;
}

export const jsbIdCodec = t.brand(
  tt.NonEmptyString,
  (s): s is t.Branded<tt.NonEmptyString, JsbIdBrand> => true,
  "JsbId"
);
export type JsbId = t.TypeOf<typeof jsbIdCodec>;

export const ordJsbId = Ord.contramap((id: JsbId) => id)(OrdString);

// export const workProcedureIdCodec = t.brand(
//   tt.NonEmptyString,
//   (s): s is t.Branded<tt.NonEmptyString, WorkProcedureIdBrand> => true,
//   "WorkProcedureId"
// );
export const workProcedureIdCodec = t.union([
  t.literal("section_0"), // deprecated
  t.literal("distribution_bulletins"),
  t.literal("four_rules_of_cover_up"),
  t.literal("mad"),
  t.literal("sdop_switching_procedures"),
  t.literal("toc"),
  t.literal("excavation"), // deprecated
  t.literal("step_touch_potential"),
  t.literal("human_perf_toolkit"), // deprecated
]);
export type WorkProcedureId = t.TypeOf<typeof workProcedureIdCodec>;

export const ordWorkProcedureId = Ord.contramap((id: WorkProcedureId) => id)(
  OrdString
);
export const eqWorkProcedureId = Eq.contramap((id: WorkProcedureId) => id)(
  EqString
);

export const jsbMetadataCodec = t.type({
  briefingDateTime: t.string.pipe(validDateTimeCodecS),
});
export type JsbMetadata = t.TypeOf<typeof jsbMetadataCodec>;

export const stateCodec = t.union([t.literal("Georgia"), t.literal("")]);
export type State = t.TypeOf<typeof stateCodec>;

export const workLocationCodec = t.type({
  address: t.string,
  city: t.string,
  description: t.string,
  state: stateCodec,
  operatingHq: tt.optionFromNullable(t.string),
});
export type WorkLocation = t.TypeOf<typeof workLocationCodec>;

export const emergencyContactCodec = t.type({
  name: t.string,
  phoneNumber: t.string,
  primary: t.boolean,
});
export type EmergencyContact = t.TypeOf<typeof emergencyContactCodec>;

export const jsbActivityCodec = t.type({
  name: tt.NonEmptyString,
  tasks: t.array(t.type({ id: libraryTaskIdCodec })),
});

export const taskSelectionCodec = t.type({
  fromWorkOrder: t.boolean,
  id: libraryTaskIdCodec,
});
export type TaskSelection = t.TypeOf<typeof taskSelectionCodec>;

export const workProcedureCodec = t.type({
  id: workProcedureIdCodec,
  values: t.array(tt.NonEmptyString),
});
export type WorkProcedure = t.TypeOf<typeof workProcedureCodec>;

export const voltageTypeCodec = stringEnum<typeof VoltageType>(
  VoltageType,
  "VoltageType"
);

export const voltageCodec = t.type({
  type: t.string.pipe(voltageTypeCodec),
  valueStr: t.string,
  unit: t.string,
});

export const ewpMetadataCodec = t.type({
  completed: tt.optionFromNullable(t.string.pipe(validDateTimeCodecS)),
  issued: t.string.pipe(validDateTimeCodecS),
  issuedBy: tt.NonEmptyString,
  procedure: tt.NonEmptyString,
  receivedBy: tt.NonEmptyString,
  remote: t.boolean,
});
export type EwpMetadata = t.TypeOf<typeof ewpMetadataCodec>;

export const equipmentInformationCodec = t.type({
  circuitBreaker: t.string,
  switch: t.string,
  transformer: t.string,
});
export type EquipmentInformation = t.TypeOf<typeof equipmentInformationCodec>;

export const ewpCodec = t.type({
  id: tt.NonEmptyString,
  metadata: ewpMetadataCodec,
  equipmentInformation: t.array(equipmentInformationCodec),
  referencePoints: t.array(tt.NonEmptyString),
});
export type Ewp = t.TypeOf<typeof ewpCodec>;

export const energySourceControlCodec = t.type({
  arcFlashCategory: tt.optionFromNullable(t.Int),
  clearancePoints: tt.optionFromNullable(t.string),
  transferOfControl: t.boolean,
  ewp: t.array(ewpCodec),
  voltages: t.array(voltageCodec),
});
export type EnergySourceControl = t.TypeOf<typeof energySourceControlCodec>;

export const siteConditionSelectionCodec = t.type({
  id: librarySiteConditionIdCodec,
  recommended: t.boolean,
  selected: t.boolean,
});
export type SiteConditionSelection = t.TypeOf<
  typeof siteConditionSelectionCodec
>;

const booleanOrNullToTrue = new t.Type<boolean, boolean | null, unknown>(
  "booleanOrNullToTrue",
  t.boolean.is,
  (input, context) =>
    input === null ? t.success(true) : t.boolean.validate(input, context),
  t.identity
);

export const controlSelectionCodec = t.type({
  id: hazardControlIdCodec,
  selected: booleanOrNullToTrue,
  recommended: booleanOrNullToTrue,
});

export type ControlSelection = t.TypeOf<typeof controlSelectionCodec>;

export const controlAssessmentSelectionCodec = t.type({
  hazardId: hazardIdCodec,
  controlIds: t.array(hazardControlIdCodec),
  controlSelections: t.union([t.array(controlSelectionCodec), t.null]),
});

export type ControlAssessmentSelection = t.TypeOf<
  typeof controlAssessmentSelectionCodec
>;

export const gpsCoordinatesCodec = t.type({
  latitude: tt.NumberFromString,
  longitude: tt.NumberFromString,
});
export type GpsCoordinates = t.TypeOf<typeof gpsCoordinatesCodec>;

export const eqGpsCoordinates = Eq.struct<GpsCoordinates>({
  latitude: EqNumber,
  longitude: EqNumber,
});

interface JsbPhotoIdBrand {
  readonly JsbPhotoId: unique symbol;
}

export const jsbPhotoIdCodec = t.brand(
  tt.NonEmptyString,
  (s): s is t.Branded<tt.NonEmptyString, JsbPhotoIdBrand> => true,
  "JsbPhotoId"
);

export const jsbPhotoCodec = t.type({
  id: jsbPhotoIdCodec,
  displayName: tt.NonEmptyString,
  exists: t.boolean,
  name: tt.NonEmptyString,
  signedUrl: tt.NonEmptyString,
  size: tt.NonEmptyString,
  url: tt.NonEmptyString,
  date: tt.optionFromNullable(t.string),
  time: tt.optionFromNullable(t.string),
  category: tt.optionFromNullable(t.string),
});

export const jsbDocumentCodec = t.type({
  id: jsbPhotoIdCodec,
  displayName: tt.NonEmptyString,
  exists: t.boolean,
  name: tt.NonEmptyString,
  signedUrl: tt.NonEmptyString,
  size: tt.NonEmptyString,
  url: tt.NonEmptyString,
  date: tt.optionFromNullable(t.string),
  time: tt.optionFromNullable(t.string),
  category: tt.optionFromNullable(t.string),
});

export type JsbPhoto = t.TypeOf<typeof jsbPhotoCodec>;
export type JsbDocument = t.TypeOf<typeof jsbDocumentCodec>;

export const sourceInfoCodec = t.type({
  sourceInformation: t.string,
  appVersion: t.string,
});

export type SourceInfo = t.TypeOf<typeof sourceInfoCodec>;
export const crewSignatureCodec = t.partial({
  name: t.string,
  type: t.union([t.string, t.null]),
  externalId: t.union([t.string, t.null]),
  signature: tt.optionFromNullable(
    t.type({
      id: t.string,
      name: t.string,
      displayName: t.string,
      url: t.string,
      signedUrl: t.string,
      size: tt.optionFromNullable(t.string),
    })
  ),
  jobTitle: t.union([t.string, t.null]),
  employeeNumber: t.union([t.string, t.null]),
});

export const criticalRiskAreaSelectionCodec = t.type({
  name: criticalRiskCodec,
});
export type CriticalRiskAreaSelection = t.TypeOf<
  typeof criticalRiskAreaSelectionCodec
>;
type CriticalRiskAreaSelectionDto = NonNullable<
  JsbContentsFragment["criticalRiskAreaSelections"]
>[number];

type _CheckCriticalRiskAreaSelection = CheckKeys<
  keyof CriticalRiskAreaSelection,
  keyof CriticalRiskAreaSelectionDto
>;

export const aedInformationCodec = t.type({
  location: t.string,
});

export type AedInformation = t.TypeOf<typeof aedInformationCodec>;

type AedInformationDto = NonNullable<JsbContentsFragment["aedInformation"]>;
type _CheckAedInformation = CheckKeys<
  keyof AedInformation,
  keyof AedInformationDto
>;

export const jsbCodec = t.type({
  jsbId: jsbIdCodec,
  jsbMetadata: tt.optionFromNullable(jsbMetadataCodec),
  workLocation: tt.optionFromNullable(workLocationCodec),
  gpsCoordinates: tt.optionFromNullable(t.array(gpsCoordinatesCodec)),
  emergencyContacts: tt.optionFromNullable(t.array(emergencyContactCodec)),
  nearestMedicalFacility: tt.optionFromNullable(medicalFacilityCodec),
  customNearestMedicalFacility: tt.optionFromNullable(
    t.type({ address: t.string })
  ),
  aedInformation: tt.optionFromNullable(aedInformationCodec),
  activities: tt.optionFromNullable(t.array(jsbActivityCodec)),
  taskSelections: tt.optionFromNullable(t.array(taskSelectionCodec)),
  workProcedureSelections: tt.optionFromNullable(t.array(workProcedureCodec)),
  energySourceControl: tt.optionFromNullable(energySourceControlCodec),
  siteConditionSelections: tt.optionFromNullable(
    t.array(siteConditionSelectionCodec)
  ),
  controlAssessmentSelections: tt.optionFromNullable(
    t.array(controlAssessmentSelectionCodec)
  ),
  crewSignOff: tt.optionFromNullable(t.array(crewSignatureCodec)),
  criticalRiskAreaSelections: tt.optionFromNullable(
    t.array(t.type({ name: criticalRiskCodec }))
  ),
  hazardsAndControlsNotes: tt.optionFromNullable(t.string),
  photos: tt.optionFromNullable(t.array(jsbPhotoCodec)),
  documents: tt.optionFromNullable(t.array(jsbDocumentCodec)),
  groupDiscussion: tt.optionFromNullable(t.type({ viewed: t.boolean })),
  sourceInfo: tt.optionFromNullable(sourceInfoCodec),
  otherWorkProcedures: tt.optionFromNullable(t.string),
});
export type Jsb = t.TypeOf<typeof jsbCodec>;
type _CheckJsb = CheckKeys<keyof Jsb, keyof JsbContentsFragment>;
type JsbMedicalFacilityDto = NonNullable<
  JsbContentsFragment["nearestMedicalFacility"]
>;
type _CheckJsbMedicalFacilities = CheckKeys<
  keyof MedicalFacility,
  keyof JsbMedicalFacilityDto
>;

export const savedJsbDataCodec = t.type({
  id: jsbIdCodec,
  updatedAt: tt.optionFromNullable(t.string.pipe(validDateTimeCodecS)),
  workPackage: tt.optionFromNullable(
    t.type({
      id: workPackageIdCodec,
    })
  ),
  contents: jsbCodec,
  createdBy: t.type({
    id: tt.NonEmptyString,
  }),
  completedBy: tt.optionFromNullable(
    t.type({
      id: tt.NonEmptyString,
    })
  ),
  createdAt: tt.optionFromNullable(t.string.pipe(validDateTimeCodecS)),
});
export type SavedJsbData = t.TypeOf<typeof savedJsbDataCodec>;

type _CheckJsbData = CheckKeys<keyof SavedJsbData, keyof JsbDataFragment>;

export const jsbDetailsForFormHistoryCodec = t.type({
  id: jsbIdCodec,
  updatedAt: t.string,
  workPackage: tt.optionFromNullable(
    t.type({
      id: workPackageIdCodec,
    })
  ),
  contents: jsbCodec,
  createdBy: t.type({
    id: tt.NonEmptyString,
    name: t.string,
  }),
  completedBy: tt.optionFromNullable(
    t.type({
      id: tt.NonEmptyString,
    })
  ),
  createdAt: tt.optionFromNullable(t.string.pipe(validDateTimeCodecS)),
});

export type JsbDetailsForFormHistory = t.TypeOf<
  typeof jsbDetailsForFormHistoryCodec
>;
