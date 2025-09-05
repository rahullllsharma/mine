import type { Task as TaskDto } from "../generated/types";
import type { CheckKeys } from "./utils";
import * as Eq from "fp-ts/lib/Eq";
import * as Ord from "fp-ts/lib/Ord";
import { Eq as EqString, Ord as OrdString } from "fp-ts/lib/string";
import * as t from "io-ts";
import * as tt from "io-ts-types";
import { stringEnum } from "@/utils/validation";
import { RiskLevel } from "../generated/types";
import { libraryTaskIdCodec } from "./libraryTask";

interface TaskIdBrand {
  readonly TaskId: unique symbol;
}

export const taskIdCodec = t.brand(
  tt.NonEmptyString,
  (s): s is t.Branded<tt.NonEmptyString, TaskIdBrand> => true,
  "TaskId"
);

export type TaskId = t.TypeOf<typeof taskIdCodec>;

export const ordTaskId = Ord.contramap((id: TaskId) => id)(OrdString);
export const eqTaskId = Eq.contramap((id: TaskId) => id)(EqString);

export const taskCodec = t.type({
  id: taskIdCodec,
  name: tt.NonEmptyString,
  riskLevel: t.string.pipe(
    stringEnum<typeof RiskLevel>(RiskLevel, "RiskLevel")
  ),
  libraryTask: t.type({
    id: libraryTaskIdCodec,
  }),
});

export type Task = t.TypeOf<typeof taskCodec>;

type _C = CheckKeys<keyof Task, keyof TaskDto>;
