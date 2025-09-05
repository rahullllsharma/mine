import type {
  SettingsCheckBoxType,
  WorkTypes,
  WorkTypesProps,
} from "../../../../customisedForm.types";
import type { CheckboxOption } from "../../../../../checkboxGroup/CheckboxGroup";
import { Controller, useFormContext } from "react-hook-form";
import { ActionLabel, CaptionText, Subheading } from "@urbint/silica";
import { useEffect, useMemo, useState, useContext } from "react";
import { useQuery } from "@apollo/client";
import TenantWorkTypes from "@/graphql/queries/tenantWorkTypes.gql";
import { CF_REDUCER_CONSTANTS } from "@/utils/customisedFormUtils/customisedForm.constants";
import CustomisedFromStateContext from "@/context/CustomisedDataContext/CustomisedFormStateContext";
import CheckboxGroup from "../../../../../checkboxGroup/CheckboxGroup";

interface ExtendedWorkTypesProps extends WorkTypesProps {
  onWorkTypesModified?: () => void;
}

export default function WorkTypes({
  settings,
  onWorkTypesModified,
}: ExtendedWorkTypesProps): JSX.Element {
  const { setValue } = useFormContext();
  const { dispatch, state } = useContext(CustomisedFromStateContext)!;

  const [currentWorkTypes, setCurrentWorkTypes] = useState(
    settings.work_types === undefined ? null : settings.work_types
  );

  const { data } = useQuery(TenantWorkTypes, {
    fetchPolicy: "cache-and-network",
  });

  const workTypesOptions = useMemo(() => data?.tenantWorkTypes || [], [data]);

  // Build work types options based on conditions and current state
  const workTypesCheckboxOptions = useMemo(() => {
    if (!workTypesOptions.length) return [];

    // Clean up currentWorkTypes - remove any that no longer exist in API
    if (
      currentWorkTypes !== null &&
      currentWorkTypes !== undefined &&
      Array.isArray(currentWorkTypes)
    ) {
      const validCurrentWorkTypes = currentWorkTypes.filter(current =>
        workTypesOptions.some(
          (apiOption: WorkTypes) => apiOption.id === current.id
        )
      );

      // If some work types were removed, update the state
      if (validCurrentWorkTypes.length !== currentWorkTypes.length) {
        setCurrentWorkTypes(validCurrentWorkTypes);
        setValue("work_types", validCurrentWorkTypes, { shouldDirty: true });
        onWorkTypesModified?.();
      }

      return workTypesOptions.map((workType: WorkTypes) => {
        const isSelected = validCurrentWorkTypes.some(
          current => current.id === workType.id
        );
        return {
          id: workType.id,
          name: workType.name,
          isChecked: isSelected,
        };
      });
    }

    if (!settings.work_types || settings.work_types.length === 0) {
      const initialWorkTypes = workTypesOptions.map((workType: WorkTypes) => ({
        id: workType.id,
        name: workType.name,
      }));
      setCurrentWorkTypes(initialWorkTypes);
      setValue("work_types", initialWorkTypes, {
        shouldDirty: false,
        shouldValidate: true,
      });
      // Dispatch to update global state immediately
      dispatch({
        type: CF_REDUCER_CONSTANTS.CHANGE_INITIAL_STATE,
        payload: {
          ...state.form,
          settings: {
            ...state.form.settings,
            work_types: initialWorkTypes,
          },
        },
      });

      return workTypesOptions.map((workType: WorkTypes) => ({
        id: workType.id,
        name: workType.name,
        isChecked: true,
      }));
    }

    const validSettingsWorkTypes =
      settings.work_types?.filter(existing =>
        workTypesOptions.some(
          (apiOption: WorkTypes) => apiOption.id === existing.id
        )
      ) || [];

    if (
      settings.work_types &&
      validSettingsWorkTypes.length !== settings.work_types.length
    ) {
      setCurrentWorkTypes(validSettingsWorkTypes);
      setValue("work_types", validSettingsWorkTypes, { shouldDirty: true });
      onWorkTypesModified?.();
    }

    return workTypesOptions.map((workType: WorkTypes) => {
      const existingWorkType = validSettingsWorkTypes.find(
        existing => existing.id === workType.id
      );
      return {
        id: workType.id,
        name: workType.name,
        isChecked: !!existingWorkType,
      };
    });
  }, [
    workTypesOptions,
    currentWorkTypes,
    settings.work_types,
    setValue,
    dispatch,
    state.form,
    onWorkTypesModified,
  ]);

  useEffect(() => {
    const formWorkTypes = state.form.settings.work_types;
    if (!formWorkTypes || formWorkTypes.length === 0) {
      const initialWorkTypes = workTypesOptions.map((workType: WorkTypes) => ({
        id: workType.id,
        name: workType.name,
      }));
      setCurrentWorkTypes(initialWorkTypes);
      setValue("work_types", initialWorkTypes, {
        shouldDirty: false,
        shouldValidate: true,
      });
      // Dispatch to update global state immediately
      dispatch({
        type: CF_REDUCER_CONSTANTS.CHANGE_INITIAL_STATE,
        payload: {
          ...state.form,
          settings: {
            ...state.form.settings,
            work_types: initialWorkTypes,
          },
        },
      });
    }
  }, [settings, workTypesOptions, setValue, dispatch, state.form]);

  return (
    <div>
      <Subheading>Work Types</Subheading>
      <CaptionText className="text-neutral-shade-58 leading-[3rem]">
        Work types define the content available for Activities & Tasks, Site
        Conditions, and Hazards & Controls components added to this form.
      </CaptionText>
      <CaptionText className="text-neutral-shade-58 leading-[3rem]">
        This setting also controls how users start the form after selecting this
        template:
        <ul className="list-disc ml-6 leading-6">
          <li>
            If <b className="text-neutral-shade-75">one</b> work type is
            selected: Users start directly.{" "}
          </li>
          <li>
            If <b className="text-neutral-shade-75">multiple</b> work type are
            selected: Users choose a work type first.
          </li>
        </ul>
      </CaptionText>
      <CaptionText className="text-neutral-shade-58 leading-[3rem]">
        Visibility in Work Packages: If enabled for Work Packages (via Template
        Availability), this template will only appear in Work Packages with at
        least one matching work type.
      </CaptionText>

      <ActionLabel className="text-neutral-shade-75 leading-[3rem] mt-6">
        Select work types for this template*
      </ActionLabel>
      <Controller
        name="work_types"
        defaultValue={currentWorkTypes}
        rules={{
          validate: value =>
            (Array.isArray(value) && value.length > 0) ||
            "Select at least one option",
        }}
        render={({ field, fieldState: { error } }) => (
          <div className="max-h-[350px] overflow-y-auto">
            <CheckboxGroup
              options={workTypesCheckboxOptions}
              value={workTypesCheckboxOptions.filter(
                (option: SettingsCheckBoxType) => option.isChecked
              )}
              onChange={async (newValue: CheckboxOption[]) => {
                // Create array with only selected work types (no selected key)
                const selectedWorkTypes = newValue.map(selected => ({
                  id: selected.id,
                  name: selected.name,
                }));

                // Update local state first - this updates the UI immediately
                setCurrentWorkTypes(selectedWorkTypes);

                // Update form state without immediate validation
                setValue("work_types", selectedWorkTypes, {
                  shouldDirty: true,
                  shouldValidate: false,
                });

                // Notify parent that work types were modified
                onWorkTypesModified?.();

                // trigger validation after state update
                setTimeout(async () => {
                  await field.onChange(selectedWorkTypes);
                }, 0);
              }}
            />
            {error && (
              <span className="text-red-500 text-sm mt-1">{error.message}</span>
            )}
          </div>
        )}
      />
    </div>
  );
}
