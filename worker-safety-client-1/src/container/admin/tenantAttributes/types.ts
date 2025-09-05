type SelectedField = {
  /**
   * Keys used to be able to update the BE
   */
  entityKey?: string;
  attributeKey?: string;
  /**
   * Used for the title in the modal
   */
  label: string;
};

type ValidKeys = "visible" | "required" | "filterable";
type FormInputsOptions = {
  key: ValidKeys;
  value: boolean;
  isDisabled: boolean;
};
type FormInputs = {
  label: string;
  labelPlural: string;
  mappings?: Record<string, string[]>;
  mandatory: boolean;
  options: FormInputsOptions[];
};

export type { SelectedField, FormInputs, FormInputsOptions, ValidKeys };
