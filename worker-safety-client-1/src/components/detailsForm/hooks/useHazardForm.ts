import type { SelectCardOption } from "@/components/layout/taskCard/select/SelectCard";
import type { Control } from "@/types/project/Control";
import type { Hazard } from "@/types/project/Hazard";
import type { TaskFormControl } from "@/types/task/TaskFormControl";
import type { TaskFormHazard } from "@/types/task/TaskFormHazard";
import { nanoid } from "nanoid";
import { useState, useEffect } from "react";
import { useFormContext } from "react-hook-form";
import { getFormHazards } from "@/utils/task";
import { useAuthStore } from "@/store/auth/useAuthStore.store";

const getFormControl = (control: Control): TaskFormControl => ({
  ...control,
  key: control.createdBy ? nanoid() : control.id,
});

const getFormHazard = (hazard: Hazard): TaskFormHazard => ({
  ...hazard,
  key: hazard.createdBy ? nanoid() : hazard.id,
  controls: hazard.controls.map(getFormControl),
});

type HazardHandler = {
  hazards: TaskFormHazard[];
  isAddButtonDisabled: () => boolean;
  addHazardHandler: () => void;
  removeHazardHandler: (key: string) => void;
  selectHazardHandler: (key: string, option: SelectCardOption) => void;
};

type UseHazardFormOptions =
  | {
      taskIndex: number;
      prefix: string;
    }
  | undefined;

function useHazardForm(
  taskHazards: Hazard[],
  hazardsLibrary: Hazard[],
  options?: UseHazardFormOptions
): HazardHandler {
  const { me } = useAuthStore();
  const { setValue, getValues } = useFormContext();

  const [hazards, setHazards] = useState<TaskFormHazard[]>(
    taskHazards.map(getFormHazard)
  );

  useEffect(() => {
    // concat a prefix with `{prefix.index.}hazards`
    const formValuePrefixes = options
      ? [options.prefix, options.taskIndex]
      : [];

    const formValue = formValuePrefixes.concat("hazards").join(".");

    setValue(formValue, getFormHazards(hazards));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [hazards]);

  function isAddButtonDisabled(): boolean {
    return (
      hazards.filter(hazard => hazard.createdBy).length ===
      hazardsLibrary.length
    );
  }

  function addHazardHandler(): void {
    const hazard: TaskFormHazard = {
      id: "",
      name: "",
      isApplicable: true,
      createdBy: {
        id: me.id,
        name: me.initials,
      },
      key: nanoid(),
      controls: [],
    };
    setHazards((prevState: TaskFormHazard[]) => [hazard, ...prevState]);
  }

  function removeHazardHandler(key: string): void {
    const formHazards = { ...getValues("hazards") };
    delete formHazards[key];

    setValue("hazards", formHazards, { shouldDirty: true });
    setHazards(prevState => prevState.filter(hazard => hazard.key !== key));
  }

  const getControls = (id: string) =>
    hazardsLibrary.find(hazard => hazard.id === id)?.controls as Control[];

  function selectHazardHandler(key: string, option: SelectCardOption): void {
    setHazards(prevState =>
      prevState.map(hazard => {
        if (hazard.key === key) {
          const id = option.id.toString();
          return {
            ...hazard,
            id,
            name: option.name,
            controls: getControls(id).map(getFormControl),
          };
        }

        return hazard;
      })
    );
  }

  return {
    hazards,
    isAddButtonDisabled,
    addHazardHandler,
    removeHazardHandler,
    selectHazardHandler,
  };
}

export { useHazardForm };
