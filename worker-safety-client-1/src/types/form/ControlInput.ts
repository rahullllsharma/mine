type KeyInput<T> = { [key: string]: T };
export type ControlKeyInput = KeyInput<ControlInput>;

export type ControlInput = {
  id?: string;
  libraryControlId: string;
  isApplicable: boolean;
};
