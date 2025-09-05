import type { ProjectInputs } from "@/types/form/Project";
import type { Location } from "@/types/project/Location";
import type { ProjectFormProps } from "@/pages/projects/create";
import type { FormFieldError } from "@/types/form/FormFieldError";
import { useFieldArray, useFormContext, Controller } from "react-hook-form";
import { Icon } from "@urbint/silica";
import FieldInput from "@/components/shared/field/fieldInput/FieldInput";
import ButtonSecondary from "@/components/shared/button/secondary/ButtonSecondary";
import ButtonIcon from "@/components/shared/button/icon/ButtonIcon";
import Tooltip from "@/components/shared/tooltip/Tooltip";
import FieldSearchSelect from "@/components/shared/field/fieldSearchSelect/FieldSearchSelect";
import FieldMultiSelect from "@/components/shared/field/fieldMultiSelect/FieldMultiSelect";
import { useTenantStore } from "@/store/tenant/useTenantStore.store";
import { usePageContext } from "@/context/PageProvider";
import {
  getRequiredFieldRules,
  requiredFieldRules,
} from "@/container/project/form/utils";
import { formatCamelCaseString } from "@/utils/date/helper";

const canRemoveLocation = (locationsBlocked: Location[], id: string): boolean =>
  !locationsBlocked.some(location => location.id === id);

type ProjectLocationsProps = {
  locationsBlocked?: Location[];
  readOnly?: boolean;
};

const getFormRule = (value: number, message = "Data entered is invalid") => ({
  value,
  message,
});

const getFormPattern = (
  value: RegExp,
  message = "Data entered is invalid"
) => ({
  value,
  message,
});

export default function ProjectLocations({
  locationsBlocked = [],
  readOnly = false,
}: ProjectLocationsProps): JSX.Element {
  const { workPackage, location, task } = useTenantStore(state =>
    state.getAllEntities()
  );

  const { supervisors } = usePageContext<ProjectFormProps>();

  const {
    formState: { errors },
    watch,
    getValues,
  } = useFormContext<ProjectInputs>();

  const { fields, prepend, remove } = useFieldArray<ProjectInputs>({
    name: "locations",
    keyName: "key" as "id",
  });

  const addLocation = () => {
    prepend(
      {
        name: "",
        longitude: null,
        latitude: null,
        supervisorId: getValues("supervisorId"),
        additionalSupervisors: [],
        externalKey: "",
      },
      {}
    );
  };
  const supervisorsOptions = supervisors.map(({ id, name }) => ({ id, name }));

  const getSupervisorById = (id?: string) =>
    supervisorsOptions.find(supervisor => supervisor.id === id);

  const latitudeMinMaxValue = 90;
  const longitudeMinMaxValue = 180;

  const latitudeRules = {
    max: getFormRule(latitudeMinMaxValue),
    min: getFormRule(-latitudeMinMaxValue),
    pattern: getFormPattern(/^-?([0-8]?[0-9]|90)(\.[0-9]{1,10})?$/),
  };

  const longitudeRules = {
    max: getFormRule(longitudeMinMaxValue),
    min: getFormRule(-longitudeMinMaxValue),
    pattern: getFormPattern(/^-?([0-1]?[0-9]?[0-9]|180)(\.[0-9]{1,10})?$/),
  };

  const hasMultipleLocations = fields.length > 1;

  return (
    <div>
      <div className="flex items-center">
        <h6
          className="flex-1"
          data-testid="location-header"
        >{`${location.label}(s)`}</h6>
        {!readOnly && (
          <ButtonSecondary
            iconStart="plus"
            label={"Add a " + formatCamelCaseString(location.label)}
            onClick={addLocation}
            data-testid="add-location-button"
          />
        )}
      </div>

      {fields.map((entry, index: number) => {
        const {
          name,
          latitude,
          longitude,
          supervisorId,
          additionalSupervisors,
          externalKey,
        } = entry;
        // eslint-disable-next-line @typescript-eslint/ban-ts-comment
        // @ts-ignore
        const key = entry.id ?? entry.key; // ignore entry.key

        const canRemove = canRemoveLocation(locationsBlocked, key);
        const showRemoveAction = hasMultipleLocations && canRemove && !readOnly;
        const showMinLocationTooltip = fields.length === 1 && !!entry.id;
        const showLocationTooltip = hasMultipleLocations && !canRemove;
        const showTooltip = showMinLocationTooltip || showLocationTooltip;

        let tooltipMessage = `This ${location.label.toLowerCase()} can’t be deleted as ${workPackage.labelPlural.toLowerCase()} require a minimum of one (1) ${location.label.toLowerCase()}`;
        if (showLocationTooltip) {
          tooltipMessage = `This ${location.label.toLowerCase()} can´t be deleted because ${task.labelPlural.toLowerCase()} and/or daily inspection reports have already been added`;
        }

        const watchSupervisorId = watch(`locations.${index}.supervisorId`);
        const watchAdditionalSupervisors = watch(
          `locations.${index}.additionalSupervisors`
        );

        return (
          <div className="shadow-20 p-6 mt-5" key={`location_${key}`}>
            <div
              className="flex items-center text-base font-bold mb-4"
              data-testid="location-id"
            >
              <div className="flex-1">
                {entry.name?.length > 0
                  ? entry.name
                  : `${location.label} ${fields.length - index}`}
              </div>

              {showTooltip && (
                <Tooltip
                  title={tooltipMessage}
                  position="left"
                  className="w-72"
                >
                  <Icon name="info_circle_outline" className="text-lg" />
                </Tooltip>
              )}

              {showRemoveAction && (
                <ButtonIcon
                  iconName="trash_empty"
                  onClick={() => remove(index)}
                />
              )}
            </div>
            {entry.id && (
              <div className="hidden">
                <Controller
                  name={`locations.${index}.id`}
                  rules={requiredFieldRules}
                  defaultValue={entry.id}
                  render={({ field }) => (
                    <FieldInput
                      hidden
                      htmlFor={`locationId-${index}`}
                      id={`locationId-${index}`}
                      {...field}
                    />
                  )}
                />
              </div>
            )}
            <div className="flex flex-col pb-4" data-testid="location-name">
              <Controller
                name={`locations.${index}.name`}
                rules={requiredFieldRules}
                defaultValue={name}
                render={({ field }) => (
                  <FieldInput
                    htmlFor={`locationName-${index}`}
                    id={`locationName-${index}`}
                    label={location.attributes.name.label}
                    error={errors.locations?.[index]?.name?.message}
                    placeholder="Ex. 3rd street between Main and Broadway"
                    readOnly={readOnly}
                    required
                    {...field}
                  />
                )}
              />
            </div>

            <div className="flex flex-wrap">
              <div
                className="flex flex-1 flex-col pb-4 mr-4"
                data-testid="location-latitude"
              >
                <Controller
                  name={`locations.${index}.latitude`}
                  rules={{ ...requiredFieldRules, ...latitudeRules }}
                  defaultValue={latitude}
                  render={({ field }) => (
                    <FieldInput
                      htmlFor={`locationLat-${index}`}
                      id={`locationLat-${index}`}
                      type="text"
                      min={-latitudeMinMaxValue}
                      max={latitudeMinMaxValue}
                      label="Latitude"
                      error={errors.locations?.[index]?.latitude?.message}
                      placeholder="Ex. 34.054913"
                      readOnly={readOnly}
                      required
                      {...field}
                    />
                  )}
                />
              </div>
              <div
                className="flex flex-1 flex-col pb-4"
                data-testid="location-longitude"
              >
                <Controller
                  name={`locations.${index}.longitude`}
                  rules={{ ...requiredFieldRules, ...longitudeRules }}
                  defaultValue={longitude}
                  render={({ field }) => (
                    <FieldInput
                      htmlFor={`locationLong-${index}`}
                      id={`locationLong-${index}`}
                      type="text"
                      min={-longitudeMinMaxValue}
                      max={longitudeMinMaxValue}
                      label="Longitude"
                      error={errors.locations?.[index]?.longitude?.message}
                      placeholder="Ex. -62.136754"
                      readOnly={readOnly}
                      required
                      {...field}
                    />
                  )}
                />
              </div>
            </div>

            {location.attributes.primaryAssignedPerson.visible && (
              <div
                className="flex flex-col pb-4"
                data-testid="location-primary-assigned-person"
              >
                <Controller
                  name={`locations.${index}.supervisorId`}
                  rules={getRequiredFieldRules(
                    location.attributes.primaryAssignedPerson.required
                  )}
                  defaultValue={supervisorId}
                  render={({ field: { onChange, ref } }) => (
                    <FieldSearchSelect
                      htmlFor="supervisor"
                      label={location.attributes.primaryAssignedPerson.label}
                      placeholder={`Select a ${location.attributes.primaryAssignedPerson.label.toLowerCase()}`}
                      icon="user"
                      options={supervisorsOptions.filter(
                        option =>
                          !watchAdditionalSupervisors?.includes(option.id)
                      )}
                      defaultOption={getSupervisorById(supervisorId)}
                      error={errors.locations?.[index]?.supervisorId?.message}
                      isInvalid={!!errors.locations?.[index]?.supervisorId}
                      required={
                        location.attributes.primaryAssignedPerson.required
                      }
                      buttonRef={ref}
                      onSelect={option => onChange(option.id)}
                      readOnly={readOnly}
                    />
                  )}
                />
              </div>
            )}

            {location.attributes.additionalAssignedPerson.visible && (
              <div
                className="flex flex-col pb-4"
                data-testid="location-additional-assigned-person"
              >
                <Controller
                  name={`locations.${index}.additionalSupervisors`}
                  defaultValue={additionalSupervisors}
                  rules={getRequiredFieldRules(
                    location.attributes.additionalAssignedPerson.required
                  )}
                  render={({ field: { onChange, ref } }) => {
                    const multiSelectErrors = errors.locations?.[
                      index
                    ] as FormFieldError;

                    return (
                      <FieldMultiSelect
                        htmlFor="additionalSupervisors"
                        label={`${location.attributes.additionalAssignedPerson.label}(s)`}
                        placeholder={`Select ${location.attributes.additionalAssignedPerson.label.toLowerCase()}(s)`}
                        icon="user"
                        options={supervisorsOptions.filter(
                          options => options.id !== watchSupervisorId
                        )}
                        defaultOption={supervisorsOptions.filter(option =>
                          additionalSupervisors?.includes(option.id)
                        )}
                        buttonRef={ref}
                        onSelect={option => {
                          onChange(option.map(supervisor => supervisor.id));
                        }}
                        error={
                          multiSelectErrors?.additionalSupervisors?.message
                        }
                        required={
                          location.attributes.additionalAssignedPerson.required
                        }
                        isInvalid={!!multiSelectErrors?.additionalSupervisors}
                        readOnly={readOnly}
                      />
                    );
                  }}
                />
              </div>
            )}

            {location.attributes.externalKey.visible && (
              <div
                className="flex flex-col pb-4"
                data-testid="location-external-key"
              >
                <Controller
                  name={`locations.${index}.externalKey`}
                  defaultValue={externalKey}
                  rules={getRequiredFieldRules(
                    location.attributes.externalKey.required
                  )}
                  render={({ field }) => (
                    <FieldInput
                      htmlFor="externalKey"
                      id={`externalKey-${index}`}
                      label={location.attributes.externalKey.label}
                      placeholder="Ex. 1394|8044-A2B"
                      error={errors.externalKey?.message}
                      required={location.attributes.externalKey.required}
                      readOnly={readOnly}
                      {...field}
                    />
                  )}
                />
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
}
