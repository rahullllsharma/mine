import type { taskIdCodec } from "@/api/codecs";
import * as t from "io-ts";
import * as tt from "io-ts-types";

interface OpCoIdBrand {
  readonly OpCoId: unique symbol;
}

export const OpCoIdCodec = t.brand(
  tt.NonEmptyString,
  (s): s is t.Branded<tt.NonEmptyString, OpCoIdBrand> => true,
  "OpCoId"
);
export type OpCoId = t.TypeOf<typeof taskIdCodec>;

export interface OpCo {
  attributes: Attributes;
  relationships: Relationships;
  type: string;
  id: OpCoId;
  links: OpCoLinks;
}

export interface Attributes {
  name: string;
  full_name: string;
  created_at: Date;
  parent_id: null;
}

export interface OpCoLinks {
  self: string;
}

export interface Relationships {
  tenant: Tenant;
}

export interface Tenant {
  data: Data;
  links: TenantLinks;
}

export interface Data {
  id: string;
  type: string;
}

export interface TenantLinks {
  related: string;
}
