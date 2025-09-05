import type { SelectCardOption } from "../../select/SelectCard";
import type { TaskFormControl } from "@/types/task/TaskFormControl";
import type { FormFieldError } from "@/types/form/FormFieldError";
import type { ControlKeyInput, ControlInput } from "@/types/form/ControlInput";
import type { Control } from "@/types/project/Control";
import type { FieldValues } from "react-hook-form";
import { Controller, useFormContext } from "react-hook-form";
import { nanoid } from "nanoid";
import { useEffect, useRef, useState } from "react";
import { get as findByKey } from "lodash-es";
import ButtonSecondary from "@/components/shared/button/secondary/ButtonSecondary";
import { useCardStateManagement } from "@/hooks/useCardStateManagement";
import { useAuthStore } from "@/store/auth/useAuthStore.store";
import { useTenantStore } from "@/store/tenant/useTenantStore.store";
import { addSelectedOption, removeSelectedOption } from "../utils";
import ControlCardContent from "../controlCardContent/ControlCardContent";
import SelectCard from "../../select/SelectCard";

const getDefaultOption = (control: Control) => {
  if (control.libraryControl?.id) {
    return { id: control.libraryControl?.id as string, name: control.name };
  }
  return undefined;
};

type HazardCardContentProps = {
  hazardId: string;
  hazardControls: TaskFormControl[];
  controlsLibrary: SelectCardOption[];
  userInitials: string;
  isDisabled?: boolean;
  controlFormPrefix?: `${string}.${number}`;
};

type SelectCardFormControllerProps = {
  hazardId: string;
  control: TaskFormControl;
  userInitials: string;
  controlOptions: SelectCardOption[];
  onRemoveControl: () => void;
  onSelectControl: (option: SelectCardOption) => void;
  isDisabled?: boolean;
  controlFormPrefix?: `${string}.${number}`;
};

const SelectCardFormController = ({
  hazardId,
  control,
  userInitials,
  controlOptions,
  onRemoveControl,
  onSelectControl,
  isDisabled,
  controlFormPrefix,
}: SelectCardFormControllerProps) => {
  const controlFormId = [
    controlFormPrefix,
    "hazards",
    hazardId,
    "controls",
  ].join(".");

  const { control: controlEntity } = useTenantStore(state =>
    state.getAllEntities()
  );

  const {
    getValues,
    setValue,
    formState: { errors },
  } = useFormContext<FieldValues>();

  const removeControlHandler = (key: string, id: string): void => {
    const controls: ControlKeyInput = {
      ...getValues(controlFormId),
    };
    delete controls[key];

    setValue(controlFormId, controls, { shouldDirty: true });
    removeSelectedOption(controlOptions, id);
  };

  const updateControlHandler = (id: string, option: SelectCardOption): void => {
    //Creating separate methods, because "removeSelected" will be used alone on the "removeControlHandler"
    addSelectedOption(controlOptions, option.id.toString());
    removeSelectedOption(controlOptions, id);
  };

  const controlErrors = findByKey(errors, controlFormId) as FormFieldError;

  return (
    <Controller
      name={`${controlFormId}.${control.key}`}
      rules={{ required: "This field is required" }}
      render={({ field: { onChange, ref } }) => (
        <SelectCard
          userInitials={userInitials}
          type="control"
          defaultOption={getDefaultOption(control)}
          buttonRef={ref}
          isInvalid={!!controlErrors?.[control.key]}
          error={controlErrors?.[control.key]?.message}
          placeholder={`Select a ${controlEntity.label.toLowerCase()}`}
          isDisabled={isDisabled}
          options={controlOptions.filter(
            option => !option.isSelected || option.name === control.name
          )}
          onSelect={option => {
            onChange({
              libraryControlId: option.id,
              isApplicable: true,
            });
            updateControlHandler(control.id, option);
            onSelectControl(option);
          }}
          onRemove={() => {
            removeControlHandler(control.key, control.id);
            onRemoveControl();
          }}
        />
      )}
    />
  );
};

export default function HazardCardContent({
  hazardId,
  hazardControls,
  controlsLibrary,
  isDisabled,
  controlFormPrefix,
}: HazardCardContentProps): JSX.Element {
  const controlPrefix = [controlFormPrefix, "hazards"].join(".");
  const { control: controlEntity } = useTenantStore(state =>
    state.getAllEntities()
  );
  const { me } = useAuthStore();
  const { getValues } = useFormContext<FieldValues>();

  const [controls, setControls] = useState<TaskFormControl[]>(hazardControls);

  useEffect(() => {
    setControls(hazardControls);
  }, [hazardControls]);

  const [isControlApplicable, setIsControlApplicable] =
    useCardStateManagement();

  //Using useRef so that the object will persist for the full lifetime of the component.
  const controlOptionsRef = useRef<SelectCardOption[]>(
    controlsLibrary.map(libControl => ({
      id: libControl.id,
      name: libControl.name,
      isSelected: !!controls.find(
        control =>
          control.createdBy && control.libraryControl?.id === libControl.id
      ),
    }))
  );

  const { current: controlOptions } = controlOptionsRef;

  const isControlActive = (control: TaskFormControl) =>
    isControlApplicable[control.id] ?? control.isApplicable;

  const handleControlToggle = (control: TaskFormControl) =>
    setIsControlApplicable(control.id, !isControlActive(control));

  const addControlHandler = (): void => {
    const control: TaskFormControl = {
      id: "",
      name: "",
      isApplicable: true,
      createdBy: {
        id: me.id,
        name: me.initials,
      },
      key: nanoid(),
    };
    setControls((prevState: TaskFormControl[]) => [...prevState, control]);
  };

  const isAddButtonDisabled: boolean =
    controls.filter(control => control.createdBy).length ===
    controlOptions.length;

  const canAddControls = controlOptions.length > 0 && !isDisabled;

  const ControlCards = controls.map(control => {
    const controlFormId = `${controlPrefix}.${hazardId}.controls.${control.id}`;
    return (
      <div className="mt-2 first:mt-0 bg-brand-gray-20" key={control.key}>
        {control.createdBy ? (
          <SelectCardFormController
            hazardId={hazardId}
            control={control}
            userInitials={control.createdBy.name}
            controlOptions={controlOptions}
            isDisabled={isDisabled}
            controlFormPrefix={controlFormPrefix}
            onRemoveControl={() =>
              setControls(prevState =>
                prevState.filter(state => state.key !== control.key)
              )
            }
            onSelectControl={(option: SelectCardOption) =>
              setControls(prevState =>
                prevState.map(state =>
                  state.key === control.key
                    ? { ...state, id: option.id.toString(), name: option.name }
                    : state
                )
              )
            }
          />
        ) : (
          <Controller
            name={controlFormId}
            defaultValue={getValues(controlFormId)}
            render={({ field: { onChange } }) => (
              <ControlCardContent
                control={control}
                isActive={isControlActive(control)}
                isDisabled={isDisabled}
                onToggle={(state: boolean) => {
                  const libraryControlId = control.libraryControl?.id;

                  let controlPayload: ControlInput = {
                    libraryControlId: libraryControlId ?? control.id,
                    isApplicable: state,
                  };

                  if (libraryControlId) {
                    controlPayload = { ...controlPayload, id: control.id };
                  }

                  onChange(controlPayload);
                  handleControlToggle(control);
                }}
              />
            )}
          />
        )}
      </div>
    );
  });

  return (
    <>
      {ControlCards}
      {canAddControls && (
        <ButtonSecondary
          label={`Add a ${controlEntity.label.toLowerCase()}`}
          iconStart="plus"
          size="sm"
          className="mt-4"
          title={
            isAddButtonDisabled
              ? `No more ${controlEntity.labelPlural.toLowerCase()} available`
              : ""
          }
          disabled={isAddButtonDisabled}
          onClick={addControlHandler}
        />
      )}
    </>
  );
}
