import type { DailyReportInputs } from "@/types/report/DailyReportInputs";
import type { ChangeEvent } from "react";
import { Controller, useFormContext } from "react-hook-form";
import { messages } from "@/locales/messages";
import FieldInput from "@/components/shared/field/fieldInput/FieldInput";

type CrewMembersFields =
  | "crew.nWelders"
  | "crew.nSafetyProf"
  | "crew.nFlaggers"
  | "crew.nLaborers"
  | "crew.nOperators"
  | "crew.nOtherCrew";

type CrewControlInputProps = {
  fieldType:
    | "nWelders"
    | "nSafetyProf"
    | "nFlaggers"
    | "nLaborers"
    | "nOperators"
    | "nOtherCrew";
  label: string;
  isCompleted?: boolean;
};

type CrewMembersProps = {
  isCompleted?: boolean;
};

const CrewControlInput = ({
  fieldType,
  label,
  isCompleted,
}: CrewControlInputProps): JSX.Element => {
  const {
    getValues,
    formState: { errors },
  } = useFormContext<Pick<DailyReportInputs, "crew">>();

  const fieldName: CrewMembersFields = `crew.${fieldType}`;
  const fieldError = errors?.crew?.[fieldType];

  return (
    <Controller
      name={fieldName}
      rules={{ required: messages.required }}
      defaultValue={getValues(fieldName)}
      render={({ field }) => (
        <FieldInput
          id={label}
          htmlFor={label}
          label={label}
          type="number"
          required
          error={fieldError?.message}
          min={0}
          readOnly={isCompleted}
          {...field}
          onChange={(e: ChangeEvent<HTMLInputElement>) => {
            const { value } = e.target;
            field.onChange(value === "" ? null : +value);
          }}
        />
      )}
    />
  );
};

const getTotalCrewMembers = (res: Array<number | string | undefined>) =>
  res.reduce((acc = 0, current = 0) => +current + +acc, 0) || 0;

export default function CrewMembers({
  isCompleted,
}: CrewMembersProps): JSX.Element {
  const { watch } = useFormContext<DailyReportInputs>();
  const result = watch([
    "crew.nWelders",
    "crew.nSafetyProf",
    "crew.nFlaggers",
    "crew.nLaborers",
    "crew.nOperators",
    "crew.nOtherCrew",
  ]) as Array<undefined | string>;

  return (
    <>
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <CrewControlInput
          fieldType="nWelders"
          label="# of welders"
          isCompleted={isCompleted}
        />
        <CrewControlInput
          fieldType="nSafetyProf"
          label="# of safety prof."
          isCompleted={isCompleted}
        />
        <CrewControlInput
          fieldType="nFlaggers"
          label="# of flaggers"
          isCompleted={isCompleted}
        />
        <CrewControlInput
          fieldType="nLaborers"
          label="# of laborers"
          isCompleted={isCompleted}
        />
        <CrewControlInput
          fieldType="nOperators"
          label="# of operators"
          isCompleted={isCompleted}
        />
        <CrewControlInput
          fieldType="nOtherCrew"
          label="# of other crew members"
          isCompleted={isCompleted}
        />
      </div>
      <div className="mt-4">
        <FieldInput
          label="Total # of crew members"
          value={getTotalCrewMembers(result)}
          disabled={!isCompleted}
          readOnly={isCompleted}
        />
      </div>
    </>
  );
}
