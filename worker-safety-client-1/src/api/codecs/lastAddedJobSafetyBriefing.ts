import type { CheckKeys } from "./utils";
import type { LastAddedJobSafetyBriefingQuery } from "../generated/types";
import * as t from "io-ts";
import * as tt from "io-ts-types";
import { medicalFacilityCodec } from "./medicalFacility";
import { aedInformationCodec, emergencyContactCodec } from "./jsb";

const workLocationCodec = t.type({
  address: t.string,
  description: t.string,

});
const workLocationAdhocCodec=t.type({
  address:t.string,
  operatingHq: t.string,
})

export const contentsCodec = t.type({
  workLocation: tt.optionFromNullable(workLocationCodec),
  nearestMedicalFacility: tt.optionFromNullable(medicalFacilityCodec),
  aedInformation: tt.optionFromNullable(aedInformationCodec),
  emergencyContacts: tt.optionFromNullable(t.array(emergencyContactCodec)),
});

export const contentsAdhocCodec=t.type({
  workLocation: tt.optionFromNullable(workLocationAdhocCodec),
  nearestMedicalFacility: tt.optionFromNullable(medicalFacilityCodec),
  aedInformation: tt.optionFromNullable(aedInformationCodec),
  emergencyContacts: tt.optionFromNullable(t.array(emergencyContactCodec)),
});

export type LastJsbContents = t.TypeOf<typeof contentsCodec>;

export const lastAddedJobSafetyBriefingCodec = t.type({
  lastAddedJobSafetyBriefing: tt.optionFromNullable(
    t.type({
      contents: contentsCodec,
    })
  ),
});

export type LastAdhocJsbContents = t.TypeOf<typeof contentsAdhocCodec>;

export const lastAddedAdhocJobSafetyBriefingCodec=t.type({
  lastAddedAdhocJobSafetyBriefing:tt.optionFromNullable(
    t.type({
      contents:contentsAdhocCodec,
    })
  ),
});

type LastAddedJobSafetyBriefingInfo = t.TypeOf<
  typeof lastAddedJobSafetyBriefingCodec
>;

type _CheckCriticalRiskAreaSelection = CheckKeys<
  keyof LastAddedJobSafetyBriefingInfo,
  keyof LastAddedJobSafetyBriefingQuery
>;
type _CheckCriticalRiskAreaSelectionContents = CheckKeys<
  keyof LastJsbContents,
  keyof NonNullable<
    LastAddedJobSafetyBriefingQuery["lastAddedJobSafetyBriefing"]
  >["contents"]
>;
