// TODO upon backend changes, generated/types will result with probably an Employee
import type { CrewLeader as CrewMemberDTO } from "../generated/types";
import type { CheckKeys } from "./utils";
import * as t from "io-ts";
import * as tt from "io-ts-types";

interface CrewMemberIdBrand {
  readonly CrewMemberId: unique symbol;
}

const crewMemberIdCodec = t.brand(
  tt.NonEmptyString,
  (s): s is t.Branded<tt.NonEmptyString, CrewMemberIdBrand> => true,
  "CrewMemberId"
);

export type CrewMemberId = t.TypeOf<typeof crewMemberIdCodec>;

export const crewMemberCodec = t.type({
  id: crewMemberIdCodec,
  name: tt.NonEmptyString,
});

export type CrewMember = t.TypeOf<typeof crewMemberCodec>;

type _C = CheckKeys<keyof CrewMember, keyof CrewMemberDTO>;
