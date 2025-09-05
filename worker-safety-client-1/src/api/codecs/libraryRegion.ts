import type { LibraryRegion as LibraryRegionDTO } from "../generated/types";
import type { CheckKeys } from "./utils";
import * as t from "io-ts";
import * as tt from "io-ts-types";

interface LibraryRegionIdBrand {
  readonly LibraryRegionId: unique symbol;
}

const libraryRegionIdCodec = t.brand(
  tt.NonEmptyString,
  (s): s is t.Branded<tt.NonEmptyString, LibraryRegionIdBrand> => true,
  "LibraryRegionId"
);

export type LibraryRegionId = t.TypeOf<typeof libraryRegionIdCodec>;

export const libraryRegionCodec = t.type({
  id: libraryRegionIdCodec,
  name: tt.NonEmptyString,
});

export type LibraryRegion = t.TypeOf<typeof libraryRegionCodec>;

type _C = CheckKeys<keyof LibraryRegion, keyof LibraryRegionDTO>;
