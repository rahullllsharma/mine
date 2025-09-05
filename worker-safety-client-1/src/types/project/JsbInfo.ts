import * as t from "io-ts";
import * as tt from "io-ts-types";
import { FormStatus } from "@/api/generated/types";
import { stringEnum, validDateTimeCodecS } from "@/utils/validation";
import { medicalFacilityCodec } from "@/api/codecs";

export const jsbInfoCodec = t.type(
  {
    id: tt.NonEmptyString,
    name: tt.optionFromNullable(tt.NonEmptyString),
    status: t.string.pipe(
      stringEnum<typeof FormStatus>(FormStatus, "JsbStatus")
    ),
    createdAt: tt.optionFromNullable(t.string.pipe(validDateTimeCodecS)),
    createdBy: tt.optionFromNullable(t.type({ name: tt.NonEmptyString })),
    completedAt: tt.optionFromNullable(t.string.pipe(validDateTimeCodecS)),
    completedBy: tt.optionFromNullable(t.type({ name: tt.NonEmptyString })),

    contents: t.type({
      emergencyContacts: tt.optionFromNullable(
        t.array(
          t.type({
            name: tt.NonEmptyString,
            phoneNumber: tt.NonEmptyString,
            primary: t.boolean,
          })
        )
      ),
      nearestMedicalFacility: tt.optionFromNullable(medicalFacilityCodec),
      customNearestMedicalFacility: tt.optionFromNullable(
        t.type({ address: t.string })
      ),
      aedInformation: tt.optionFromNullable(
        t.type({
          location: tt.NonEmptyString,
        })
      ),
      workLocation: tt.optionFromNullable(
        t.type({
          address: tt.NonEmptyString,
          description: tt.NonEmptyString,
        })
      ),
      gpsCoordinates: tt.optionFromNullable(
        t.array(
          t.type({
            latitude: tt.NumberFromString,
            longitude: tt.NumberFromString,
          })
        )
      ),
      jsbMetadata: tt.optionFromNullable(
        t.type({
          briefingDateTime: t.string.pipe(validDateTimeCodecS),
        })
      ),
      energySourceControl: tt.optionFromNullable(
        t.type({
          ewp: t.array(
            t.type({
              id: tt.NonEmptyString,
              equipmentInformation: t.array(
                t.type({
                  circuitBreaker: tt.NonEmptyString,
                })
              ),
            })
          ),
        })
      ),
    }),
  },
  "JsbInfo"
);

export type JsbInfo = t.TypeOf<typeof jsbInfoCodec>;
