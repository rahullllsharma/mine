import type { Activity as ActivityDto } from "../generated/types";
import type { CheckKeys } from "./utils";
import * as Eq from "fp-ts/lib/Eq";
import * as Ord from "fp-ts/lib/Ord";
import { Eq as EqString, Ord as OrdString } from "fp-ts/lib/string";
import * as t from "io-ts";
import * as tt from "io-ts-types";
import * as E from "fp-ts/lib/Either";
import { sequenceS } from "fp-ts/lib/Apply";
import { stringEnum, validDateTimeCodecS } from "@/utils/validation";
import { ActivityStatus } from "../generated/types";
import { taskCodec } from "./task";

interface ActivityIdBrand {
  readonly ActivityId: unique symbol;
}

export const activityIdCodec = t.brand(
  tt.NonEmptyString,
  (s): s is t.Branded<tt.NonEmptyString, ActivityIdBrand> => true,
  "ActivityId"
);
export type ActivityId = t.TypeOf<typeof activityIdCodec>;

export const ordActivityId = Ord.contramap((id: ActivityId) => id)(OrdString);
export const eqActivityId = Eq.contramap((id: ActivityId) => id)(EqString);

const activityStatusCodec = stringEnum<typeof ActivityStatus>(
  ActivityStatus,
  "ActivityStatus"
);

export const activityCodec = t.type({
  id: activityIdCodec,
  name: tt.NonEmptyString,
  status: t.string.pipe(activityStatusCodec),
  tasks: t.array(taskCodec),
  startDate: tt.optionFromNullable(t.string.pipe(validDateTimeCodecS)),
  endDate: tt.optionFromNullable(t.string.pipe(validDateTimeCodecS)),
});
export type Activity = t.TypeOf<typeof activityCodec>;

type _C = CheckKeys<keyof Activity, keyof ActivityDto>;

// TODO: This seems like a better way to write decoders than the standard io-ts t.type.
// At least from the type safety perspective. It forces the input key checks for free, and with some codec tweaking also the base type.
// It's a bit more verbose though.
function _decode(input: ActivityDto): t.Validation<Activity> {
  return sequenceS(E.Apply)({
    id: activityIdCodec.decode(input.id),
    name: tt.NonEmptyString.decode(input.name),
    status: E.right(input.status),
    tasks: t.array(taskCodec).decode(input.tasks),
    startDate: tt
      .optionFromNullable(t.string.pipe(validDateTimeCodecS))
      .decode(input.startDate),
    endDate: tt
      .optionFromNullable(t.string.pipe(validDateTimeCodecS))
      .decode(input.endDate),
  });
}
