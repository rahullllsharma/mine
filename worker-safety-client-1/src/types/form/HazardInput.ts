import type { ControlKeyInput } from "./ControlInput";

type KeyInput<T> = { [key: string]: T };
export type HazardKeyInput = KeyInput<HazardInput>;

export type HazardInput = {
  id?: string;
  libraryHazardId: string;
  isApplicable: boolean;
  controls?: ControlKeyInput;
};
