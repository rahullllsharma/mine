import type { NearestMedicalFacilitiesQuery } from "../generated/types";
import type { CheckKeys } from "./utils";
import * as t from "io-ts";
import * as tt from "io-ts-types";

export const medicalFacilityCodec = t.type({
  description: t.string,
  address: tt.optionFromNullable(tt.NonEmptyString),
  city: tt.optionFromNullable(tt.NonEmptyString),
  distanceFromJob: tt.optionFromNullable(t.number),
  phoneNumber: tt.optionFromNullable(tt.NonEmptyString),
  state: tt.optionFromNullable(tt.NonEmptyString),
  zip: tt.optionFromNullable(t.Int),
});
export type MedicalFacility = t.TypeOf<typeof medicalFacilityCodec>;

type MedicalFacilityDto =
  NearestMedicalFacilitiesQuery["nearestMedicalFacilities"][number];
type _CheckMedicalFacility = CheckKeys<
  keyof MedicalFacility,
  keyof MedicalFacilityDto
>;
