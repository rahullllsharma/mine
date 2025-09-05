type MappingValue = {
  defaultLabel: string;
  label: string;
};

type FormInputs = {
  label: string;
  labelPlural: string;
  mappingValues: MappingValue[];
};

export type { FormInputs, MappingValue };
