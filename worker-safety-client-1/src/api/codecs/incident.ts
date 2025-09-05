import * as t from "io-ts";
import * as tt from "io-ts-types";
import * as Ord from "fp-ts/lib/Ord";
import { Ord as OrdString } from "fp-ts/lib/string";
import { libraryTaskIdCodec } from "@/api/codecs/libraryTask";

interface IncidentTaskIdBrand {
  readonly IncidentId: unique symbol;
}

export const incidentTaskIdCodec = t.brand(
  tt.NonEmptyString,
  (s): s is t.Branded<tt.NonEmptyString, IncidentTaskIdBrand> => true,
  "IncidentId"
);
export type IncidentId = t.TypeOf<typeof incidentTaskIdCodec>;

export const ordIncidentTaskId = Ord.contramap((id: IncidentId) => id)(
  OrdString
);

export const severityCodeCodec = t.union([
  t.literal("OTHER_NON_OCCUPATIONAL"),
  t.literal("FIRST_AID_ONLY"),
  t.literal("REPORT_PURPOSES_ONLY"),
  t.literal("RESTRICTION_OR_JOB_TRANSFER"),
  t.literal("LOST_TIME"),
  t.literal("NEAR_DEATHS"),
  t.literal("DEATHS"),
  t.literal("NOT_APPLICABLE"),
]);
export const incidentCodec = t.type({
  id: incidentTaskIdCodec,
  severity: t.string,
  incidentDate: t.string,
  taskTypeId: tt.optionFromNullable(libraryTaskIdCodec),
  taskType: tt.optionFromNullable(t.string),
  severityCode: severityCodeCodec,
  incidentType: t.string,
  incidentId: tt.optionFromNullable(incidentTaskIdCodec),
  description: tt.NonEmptyString,
});

export type Incident = t.TypeOf<typeof incidentCodec>;

export const incidentDataCodec = t.type({
  historicalIncidents: t.array(incidentCodec),
});
