import type { ActivityTypeLibrary } from "@/types/activity/ActivityTypeLibrary";
import { Controller, useFormContext } from "react-hook-form";
import { Icon } from "@urbint/silica";
import cx from "classnames";
import { useMemo } from "react";
import FieldInput from "@/components/shared/field/fieldInput/FieldInput";
import FieldSelect from "@/components/shared/field/fieldSelect/FieldSelect";
import { taskStatusOptions } from "@/types/task/TaskStatus";
import FieldDatePicker from "@/components/shared/field/fieldDatePicker/FieldDatePicker";
import { convertDateToString } from "@/utils/date/helper";
import { messages } from "@/locales/messages";
import { useTenantStore } from "@/store/tenant/useTenantStore.store";
import { Toggle } from "../../forms/Basic/Toggle";
import { useTenantFeatures } from "../../../hooks/useTenantFeatures";

type ActivityConfigurationProps = {
  minStartDate: string;
  maxEndDate: string;
  activityTypeLibrary?: ActivityTypeLibrary[];
};

export default function ActivityConfiguration({
  minStartDate,
  maxEndDate,
  activityTypeLibrary = [],
}: ActivityConfigurationProps): JSX.Element {
  const { activity } = useTenantStore(state => state.getAllEntities());
  const {
    formState: { errors },
    getValues,
    trigger,
    watch,
    setValue,
  } = useFormContext();
  const { tenant } = useTenantStore();
  const { displayAddCriticalActivity } = useTenantFeatures(tenant.name);

  const status = getValues("status") || taskStatusOptions[0];
  const startDate = watch("startDate") || "";
  const endDate = watch("endDate") || "";
  const name = getValues("name") || "";
  const libraryActivityType = getValues("libraryActivityTypeId") || null;
  const isCritical = watch("isCritical") || false;
  const criticalDescription = watch("criticalDescription") || null;

  const { visible: isActivityTypeVisible, required: isActivityTypeRequired } =
    activity.attributes.libraryActivityType;

  const getStartDateMaxValue = () =>
    endDate ? convertDateToString(endDate) : "";
  const getEndDateMinValue = () =>
    startDate ? convertDateToString(startDate) : "";

  const minDate = minStartDate ? convertDateToString(minStartDate) : "";
  const maxDate = maxEndDate ? convertDateToString(maxEndDate) : "";
  const rules = { required: messages.required };

  const criticalActivityLabel = useMemo(
    () => activity.attributes?.criticalActivity?.label,
    [activity]
  );

  return (
    <div className="flex flex-col gap-4">
      <Controller
        name="name"
        rules={rules}
        defaultValue={name}
        render={({ field }) => (
          <FieldInput
            {...field}
            htmlFor="name"
            id="name"
            label={`${activity.label} name`}
            error={errors.name?.message}
            required
            onChange={e => {
              const inputValue = (e.target as HTMLInputElement).value;
              // Regex pattern to not allow spaces at beginning
              if (/^\s/.test(inputValue)) {
                field.onChange(inputValue.trimStart());
              } else {
                field.onChange(inputValue);
              }
            }}
          />
        )}
      />
      {displayAddCriticalActivity &&
        activity.attributes?.criticalActivity?.visible && (
          <>
            <div className="flex items-center gap-2">
              <Controller
                name="isCritical"
                render={({ field: { onChange } }) => (
                  <>
                    <Icon
                      name={"warning"}
                      className={cx(
                        "ml-0 pointer-events-none w-6 h-6 text-xl leading-none bg-white",
                        isCritical ? "text-[#f2a93c]" : "text-[#404e54]"
                      )}
                    />
                    <label className="block text-tiny md:text-sm text-neutral-shade-75 font-semibold leading-normal">
                      {criticalActivityLabel}
                    </label>
                    <Toggle
                      htmlFor="criticalActivityToggle"
                      containerStyle="flex"
                      checked={isCritical}
                      // onClick={() => onChange(!isCritical)}
                      onClick={() => {
                        onChange(!isCritical);
                        // If isCritical changes to false, set criticalDescription to an empty string
                        if (!isCritical) {
                          setValue("criticalDescription", "");
                        }
                      }}
                    />
                  </>
                )}
              />
            </div>

            {isCritical && (
              <div className="flex flex-col gap-4">
                <Controller
                  name="criticalDescription"
                  render={({ field }) => (
                    <FieldInput
                      {...field}
                      default={criticalDescription}
                      htmlFor="criticalDescription"
                      id="criticalDescription"
                      label={`${criticalActivityLabel} description`}
                      placeholder={`Include a description for your ${criticalActivityLabel.toLowerCase()}`}
                      onChange={e => {
                        const inputValue = (e.target as HTMLInputElement).value;
                        // Regex pattern to not allow spaces at beginning
                        if (/^\s/.test(inputValue)) {
                          field.onChange(inputValue.trimStart());
                        } else {
                          field.onChange(inputValue);
                        }
                      }}
                    />
                  )}
                />
              </div>
            )}
          </>
        )}

      {isActivityTypeVisible && activityTypeLibrary.length > 0 && (
        <Controller
          name="libraryActivityTypeId"
          rules={isActivityTypeRequired ? rules : {}}
          defaultValue={libraryActivityType}
          render={({ field: { onChange } }) => (
            <FieldSelect
              htmlFor="libraryActivityTypeId"
              label={activity.attributes.libraryActivityType.label}
              options={activityTypeLibrary}
              onSelect={option => onChange(option.id)}
              error={errors.libraryActivityTypeId?.message}
              defaultOption={activityTypeLibrary.find(
                option => option.id === libraryActivityType
              )}
              required={isActivityTypeRequired}
            />
          )}
        />
      )}

      <div className="flex flex-wrap gap-4">
        <Controller
          name="startDate"
          rules={{
            ...rules,
            max: {
              value: startDate === endDate ? "" : getStartDateMaxValue(),
              message: messages.date,
            },
          }}
          defaultValue={startDate}
          render={({ field }) => (
            <FieldDatePicker
              {...field}
              className="w-full sm:flex-1"
              label="Start date"
              error={errors.startDate?.message}
              onChange={event => {
                // When the clear button on the input is pressed, it gives an empty string
                // I am not sure how to best handle that case, so I am just returning here
                // which fixes the crash, but I am not sure how should this case be handled
                // from my reading of the code, it seems like startDate will use the current date
                // if it is empty, so I am not sure if this case is even possible where input is empty.
                if (event === "") return;
                field.onChange(event);
                trigger();
              }}
              min={minDate ?? undefined}
              max={maxDate ?? undefined}
              required
            />
          )}
        />
        <Controller
          name="endDate"
          rules={{
            ...rules,
            min: {
              value: getEndDateMinValue(),
              message: messages.date,
            },
            max: {
              value: maxDate,
              message: messages.date,
            },
          }}
          defaultValue={endDate}
          render={({ field }) => (
            <FieldDatePicker
              {...field}
              className="w-full sm:flex-1"
              label="End date"
              error={errors.endDate?.message}
              onChange={event => {
                field.onChange(event);
                trigger();
              }}
              min={minDate ?? undefined}
              max={maxDate ?? undefined}
              required
            />
          )}
        />
      </div>
      <div className="flex flex-wrap gap-4">
        {activity.attributes?.status?.visible && (
          <Controller
            name="status"
            defaultValue={status}
            rules={rules}
            render={({ field: { onChange } }) => (
              <FieldSelect
                className="w-full sm:flex-1"
                htmlFor="status"
                label={`${activity.label} status`}
                options={taskStatusOptions}
                onSelect={onChange}
                defaultOption={taskStatusOptions.find(
                  option => option.id === status.id
                )}
                required
              />
            )}
          />
        )}
      </div>
    </div>
  );
}
