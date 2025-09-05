import type { Hazard } from "@/types/project/Hazard";
import type { Control } from "@/types/project/Control";
import type { SelectCardOption } from "../select/SelectCard";
import type { TaskFormHazard } from "@/types/task/TaskFormHazard";
import type { ErrorOption, FieldValues } from "react-hook-form";
import type { TaskFormControl } from "@/types/task/TaskFormControl";
import type { HazardInput } from "@/types/form/HazardInput";
import { Controller, useFormContext } from "react-hook-form";
import { useEffect, useRef } from "react";
import { get as findByKey } from "lodash-es";
import { excludeRecommendedControls } from "@/utils/task";
import { useCardStateManagement } from "@/hooks/useCardStateManagement";
import { useTenantStore } from "@/store/tenant/useTenantStore.store";
import SelectCard from "../select/SelectCard";
import HazardCard from "../hazard/HazardCard";
import { addSelectedOption, removeSelectedOption } from "./utils";
import HazardCardContent from "./hazardCardContent/HazardCardContent";
import HazardHeaderContent from "./hazardHeaderContent/HazardHeaderContent";

const getDefaultOption = (hazard: Hazard) => {
  if (hazard.libraryHazard?.id) {
    return { id: hazard.libraryHazard?.id as string, name: hazard.name };
  }
  return undefined;
};

type SelectCardFormControllerProps = {
  hazard: TaskFormHazard;
  hazardOptions: SelectCardOption[];
  userInitials: string;
  onRemoveHazard: (id: string) => void;
  onSelectHazard: (id: string, option: SelectCardOption) => void;
  isDisabled?: boolean;
  controlFormPrefix?: `${string}.${number}`;
};

const SelectCardFormController = ({
  hazard,
  hazardOptions,
  userInitials,
  onSelectHazard,
  onRemoveHazard,
  controlFormPrefix,
  isDisabled = false,
}: SelectCardFormControllerProps) => {
  const controlFormId = [controlFormPrefix, "hazards", hazard.key].join(".");

  const { hazard: hazardEntity } = useTenantStore(state =>
    state.getAllEntities()
  );
  const {
    formState: { errors },
  } = useFormContext<FieldValues>();

  const removeHazardHandler = (key: string, id: string): void => {
    removeSelectedOption(hazardOptions, id);
    onRemoveHazard(key);
  };

  const updateHazardHandler = (
    key: string,
    id: string,
    option: SelectCardOption
  ): void => {
    //Creating separate methods, because "removeSelected" will be used alone on the "removeControlHandler"
    addSelectedOption(hazardOptions, option.id.toString());
    removeSelectedOption(hazardOptions, id);

    onSelectHazard(key, option);
  };

  const hazardErrors = findByKey(errors, controlFormId) as ErrorOption;
  const { trigger } = useFormContext();

  return (
    <Controller
      name={controlFormId}
      rules={{
        required: "This field is required",
        onBlur() {
          trigger(controlFormId);
        },
        validate: {
          selectedHazard(option: HazardInput) {
            const hasLibraryHazardIdSelected =
              typeof option?.libraryHazardId === "string" &&
              option.libraryHazardId.length > 0;

            if (hasLibraryHazardIdSelected) {
              return true;
            }

            return "Please select a hazard";
          },
        },
      }}
      render={({ field: { onChange, ref, onBlur } }) => (
        <SelectCard
          userInitials={userInitials}
          type="hazard"
          defaultOption={getDefaultOption(hazard)}
          buttonRef={ref}
          isInvalid={!!hazardErrors}
          error={hazardErrors?.message}
          placeholder={`Select a ${hazardEntity.label.toLowerCase()}`}
          isDisabled={isDisabled}
          onBlur={onBlur}
          options={hazardOptions.filter(
            option => !option.isSelected || option.name === hazard.name
          )}
          onSelect={option => {
            onChange({
              libraryHazardId: option.id,
              isApplicable: true,
            });
            updateHazardHandler(hazard.key, hazard.id, option);
          }}
          onRemove={() => removeHazardHandler(hazard.key, hazard.id)}
        />
      )}
    />
  );
};

type TaskContentEditProps = {
  controlsLibrary?: Control[];
  hazardsLibrary?: Hazard[];
  hazards: TaskFormHazard[];
  onRemoveHazard: (id: string) => void;
  onSelectHazard: (id: string, option: SelectCardOption) => void;
  isDisabled?: boolean;
  controlFormPrefix?: `${string}.${number}`;
};

const getHazardsOptions = (hazardsLibrary: Hazard[], hazards: Hazard[]) => {
  return hazardsLibrary.map(libHazard => ({
    id: libHazard.id,
    name: libHazard.name,
    isSelected: !!hazards.find(
      hazard => hazard.createdBy && hazard.libraryHazard?.id === libHazard.id
    ),
  }));
};

export default function TaskContentEdit({
  hazards,
  controlsLibrary = [],
  hazardsLibrary = [],
  onRemoveHazard,
  onSelectHazard,
  isDisabled,
  controlFormPrefix,
}: TaskContentEditProps): JSX.Element {
  const controlPrefix = [controlFormPrefix, "hazards"].join(".");

  const { getValues } = useFormContext<FieldValues>();

  const [isHazardApplicable, setIsHazardApplicable] = useCardStateManagement();
  const userInitials = "UB";
  const hazardOptionsRef = useRef<SelectCardOption[]>(
    getHazardsOptions(hazardsLibrary, hazards)
  );

  const { current: hazardOptions } = hazardOptionsRef;

  useEffect(() => {
    hazardOptionsRef.current = getHazardsOptions(hazardsLibrary, hazards);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [hazardsLibrary]);

  const isHazardActive = (hazard: TaskFormHazard) =>
    isHazardApplicable[hazard.id] ?? hazard.isApplicable;

  const handleHazardHeaderToggle = (hazard: TaskFormHazard) =>
    setIsHazardApplicable(hazard.id, !isHazardActive(hazard));

  return (
    <>
      {hazards.map(hazard => {
        const controlFormId = `${controlPrefix}.${hazard.id}`;
        const HazardHeader = (
          <Controller
            name={controlFormId}
            defaultValue={getValues(controlFormId)}
            render={({ field: { onChange } }) => (
              <HazardHeaderContent
                label={hazard.name}
                isActive={isHazardActive(hazard)}
                isDisabled={isDisabled}
                onToggle={(state: boolean) => {
                  const libraryHazardId = hazard.libraryHazard?.id;

                  let hazardPayload: HazardInput = {
                    libraryHazardId: libraryHazardId ?? hazard.id,
                    isApplicable: state,
                  };

                  if (libraryHazardId) {
                    hazardPayload = { ...hazardPayload, id: hazard.id };
                  }

                  onChange({
                    ...hazardPayload,
                    controls: getValues(controlFormId)?.controls,
                  });
                  handleHazardHeaderToggle(hazard);
                }}
              />
            )}
          />
        );

        return (
          <div
            className="bg-brand-gray-10 px-4 rounded first:mt-0 mt-2"
            key={hazard.key}
          >
            {hazard.createdBy ? (
              <>
                <SelectCardFormController
                  hazard={hazard}
                  hazardOptions={hazardOptions}
                  userInitials={hazard.createdBy.name}
                  onSelectHazard={onSelectHazard}
                  onRemoveHazard={onRemoveHazard}
                  isDisabled={isDisabled}
                  controlFormPrefix={controlFormPrefix}
                />
                <div className="pb-4">
                  <HazardCardContent
                    hazardId={hazard.key}
                    hazardControls={hazard.controls as TaskFormControl[]}
                    controlsLibrary={excludeRecommendedControls(
                      controlsLibrary,
                      hazard.controls
                    )}
                    userInitials={userInitials}
                    isDisabled={isDisabled}
                    controlFormPrefix={controlFormPrefix}
                  />
                </div>
              </>
            ) : (
              <HazardCard header={HazardHeader}>
                <div
                  className={isHazardActive(hazard) ? "block pb-4" : "hidden"}
                >
                  <HazardCardContent
                    hazardId={hazard.key}
                    hazardControls={hazard.controls as TaskFormControl[]}
                    controlsLibrary={excludeRecommendedControls(
                      controlsLibrary,
                      hazard.controls
                    )}
                    userInitials={userInitials}
                    isDisabled={isDisabled}
                    controlFormPrefix={controlFormPrefix}
                  />
                </div>
              </HazardCard>
            )}
          </div>
        );
      })}
    </>
  );
}
