import type { CrewProps } from "../Crew";
import type { DailyReportInputs } from "@/types/report/DailyReportInputs";
import { Controller, useFormContext } from "react-hook-form";
import FieldInput from "@/components/shared/field/fieldInput/FieldInput";
import FieldSearchSelect from "@/components/shared/field/fieldSearchSelect/FieldSearchSelect";
import { messages } from "@/locales/messages";
import { useTenantStore } from "@/store/tenant/useTenantStore.store";
import { getRequiredFieldRules } from "@/container/project/form/utils";
import CrewMembers from "../members/CrewMembers";

export default function CrewInformation({
  companies = [],
  isCompleted,
}: CrewProps): JSX.Element {
  const { workPackage } = useTenantStore(state => state.getAllEntities());
  const {
    getValues,
    setValue,
    formState: { errors },
  } = useFormContext<Pick<DailyReportInputs, "crew">>();

  if (!workPackage.attributes.primeContractor.visible) {
    setValue("crew.contractor", null);
  }

  return (
    <>
      <h5 className="font-semibold mb-6">Crew Information</h5>
      <section className="mb-6">
        {workPackage.attributes.primeContractor.visible && (
          <Controller
            name="crew.contractor"
            defaultValue={getValues("crew.contractor")}
            rules={getRequiredFieldRules(
              workPackage.attributes.primeContractor.required
            )}
            render={({ field: { ref, onChange } }) => (
              <FieldSearchSelect
                placeholder={`Select a ${workPackage.attributes.primeContractor.label.toLowerCase()}`}
                label={`Crew member ${workPackage.attributes.primeContractor.label.toLowerCase()} company`}
                className="mb-4"
                options={companies}
                defaultOption={companies.find(
                  option => option.name === getValues("crew.contractor")
                )}
                isInvalid={!!errors?.crew?.contractor}
                error={errors?.crew?.contractor?.message}
                buttonRef={ref}
                onSelect={option => onChange(option?.name ?? null)}
                readOnly={isCompleted}
                isClearable
                value={companies.find(
                  option => option.name === getValues("crew.contractor")
                )}
                required={workPackage.attributes.primeContractor.required}
              />
            )}
          />
        )}
        <Controller
          name="crew.foremanName"
          rules={{ required: messages.required }}
          defaultValue={getValues("crew.foremanName")}
          render={({ field }) => (
            <FieldInput
              {...field}
              label="Foreman Name"
              error={errors?.crew?.foremanName?.message}
              required
              readOnly={isCompleted}
            />
          )}
        />
      </section>
      <section className="mb-6">
        <CrewMembers isCompleted={isCompleted} />
      </section>
    </>
  );
}
