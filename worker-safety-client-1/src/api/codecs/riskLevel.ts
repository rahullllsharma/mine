import * as t from "io-ts";

export const riskLevelCodec = t.union([
  t.literal("HIGH"),
  t.literal("MEDIUM"),
  t.literal("LOW"),
  t.literal("RECALCULATING"),
  t.literal("UNKNOWN"),
]);

export type RiskLevel = t.TypeOf<typeof riskLevelCodec>;
