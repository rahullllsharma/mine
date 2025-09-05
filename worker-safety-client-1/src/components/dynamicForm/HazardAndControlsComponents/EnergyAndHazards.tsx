import type {
  Controls,
  EnergyAndHazardsProps,
  EnergyType,
  Hazards,
  Task,
} from "../../templatesComponents/customisedForm.types";
import { useCallback, useContext, useEffect, useMemo, useState } from "react";
import { FormProvider, useForm } from "react-hook-form";
import { useFormRendererContext } from "@/components/templatesComponents/FormPreview/Components/FormRendererContext";
import CustomisedFromStateContext from "@/context/CustomisedDataContext/CustomisedFormStateContext";
import {
  FORM_EVENTS,
  formEventEmitter,
} from "@/context/CustomisedDataContext/CustomisedFormStateProvider";
import useCWFFormState from "@/hooks/useCWFFormState";
import { CF_REDUCER_CONSTANTS } from "@/utils/customisedFormUtils/customisedForm.constants";
import ButtonSecondary from "../../shared/button/secondary/ButtonSecondary";
import {
  ApplicabilityLevel,
  EnergyLevel,
} from "../../templatesComponents/customisedForm.types";

import EnergyWheel from "../EnergyWheel";
import HazardsCard from "./HazardsCard";
import HazardsModal from "./HazardsModal";

const energyWheelInitialStatus = {
  CHEMICAL: false,
  TEMPERATURE: false,
  GRAVITY: false,
  MOTION: false,
  MECHANICAL: false,
  ELECTRICAL: false,
  PRESSURE: false,
  SOUND: false,
  RADIATION: false,
  BIOLOGICAL: false,
};

const EnergyAndHazards = ({
  readOnly,
  preSelectedHazards,
  isSummaryView = false,
  subTitle,
}: EnergyAndHazardsProps) => {
  const [addHazardsModalOpen, setAddHazardsModalOpen] = useState(false);
  const [selectedEnergyType, setSeelectedEnergyType] = useState<
    EnergyType | undefined
  >(undefined);

  const [isInitialized, setIsInitialized] = useState(false);
  const { setCWFFormStateDirty } = useCWFFormState();
  const [userAddedControls, setUserAddedControls] = useState<Controls[]>([]);
  const [activeTab, setActiveTab] = useState("highEnergy");

  const { state, dispatch } = useContext(CustomisedFromStateContext)!;
  const isEnergyWheelEnabled =
    state.form.metadata?.is_energy_wheel_enabled ?? true;
  const isEnergyWheelDisabled =
    state.form.metadata?.is_energy_wheel_enabled ?? false;
  const {
    hazardsData,
    selectedHazards,
    setSelectedHazards,
    setIsHazardsAndControlsPage,
    manuallyAddedHazardIds,
    setManuallyAddedHazardIds,
  } = useFormRendererContext();

  useEffect(() => {
    setIsHazardsAndControlsPage(true);
    return () => {
      setIsHazardsAndControlsPage(false);
    };
  }, [setIsHazardsAndControlsPage]);

  const methods = useForm({
    defaultValues: { hazards_controls: [] },
  });

  const addHazardHandler = (selectedTab?: string) => {
    setSeelectedEnergyType(undefined);
    setAddHazardsModalOpen(true);
    setActiveTab(selectedTab || "highEnergy");
  };

  const cwfTaskHazards = useMemo(
    () => state.form.component_data?.hazards_controls?.tasks || [],
    [state.form.component_data?.hazards_controls?.tasks]
  );

  const cwfSiteConditionHazards = useMemo(
    () => state.form.component_data?.hazards_controls?.site_conditions || [],
    [state.form.component_data?.hazards_controls?.site_conditions]
  );

  // Get hazards from tasks with HIGH_ENERGY level and applicabilityLevel ALWAYS
  const hazardsFromTasks = useMemo(() => {
    return (
      cwfTaskHazards
        ?.flatMap((task: Task) => task.hazards || [])
        ?.filter(
          (hazard: Hazards | undefined): hazard is Hazards =>
            !!hazard &&
            hazard.taskApplicabilityLevels?.some(
              level => level.applicabilityLevel === ApplicabilityLevel.Always
            ) === true &&
            hazard.energyLevel === EnergyLevel.HighEnergy &&
            // Only include hazards where selected is true or if there is no selected key
            (hazard.selected === true || hazard.selected === undefined)
        )
        ?.map((hazard: Hazards) => {
          // Process controls to check which ones have selected set to true
          const processedControls =
            hazard.controls?.map(control => {
              return {
                ...control,
                selected: control.selected === true,
              };
            }) || [];

          return {
            ...hazard,
            selected: true,
            controls: processedControls,
          };
        }) || []
    );
  }, [cwfTaskHazards]);

  const hazardsFromSiteConditions = useMemo(() => {
    return (
      cwfSiteConditionHazards
        ?.filter(
          (hazard: Hazards | undefined): hazard is Hazards =>
            !!hazard &&
            hazard.taskApplicabilityLevels?.some(
              level => level.applicabilityLevel === ApplicabilityLevel.Always
            ) === true &&
            hazard.energyLevel === EnergyLevel.HighEnergy &&
            // Only include hazards where selected is true or if there is no selected key
            (hazard.selected === true || hazard.selected === undefined)
        )
        ?.map((hazard: Hazards) => {
          const processedControls =
            hazard.controls?.map(control => ({
              ...control,
              selected: control.selected === true,
            })) || [];
          return {
            ...hazard,
            selected: true,
            controls: processedControls,
          };
        }) || []
    );
  }, [cwfSiteConditionHazards]);

  const hazardFromTaskIds = hazardsFromTasks.map(h => h.id);
  const hazardFromSiteConditionIds = hazardsFromSiteConditions.map(h => h.id);
  const savedManuallyAddedHazards = useMemo(
    () =>
      state.form.component_data?.hazards_controls?.manually_added_hazards ?? [],
    [state.form.component_data?.hazards_controls?.manually_added_hazards]
  );

  useEffect(() => {
    if (savedManuallyAddedHazards.length > 0) {
      // Extract all user-added controls from saved hazards
      const savedUserControls: Controls[] = [];

      savedManuallyAddedHazards.forEach(hazard => {
        const userControls = (hazard.controls || []).filter(
          control => control.isUserAdded === true
        );
        userControls.forEach(control => {
          // Only add if not already in the array
          if (!savedUserControls.some(c => c.id === control.id)) {
            savedUserControls.push(control);
          }
        });
      });

      setUserAddedControls(savedUserControls);
    }
  }, [savedManuallyAddedHazards]);

  const noHazardsAvailable = [
    hazardsFromTasks,
    hazardsFromSiteConditions,
    savedManuallyAddedHazards,
  ].every(hazards => hazards.length === 0);

  const mergedHazards = noHazardsAvailable
    ? []
    : [
        ...hazardsFromTasks,
        ...hazardsFromSiteConditions,
        ...savedManuallyAddedHazards,
      ].filter(hazard => {
        // For task hazards, only include if selected is true
        if (hazardFromTaskIds.includes(hazard.id)) {
          return hazard.selected === true;
        }
        // For site condition hazards, only include if selected is true
        if (hazardFromSiteConditionIds.includes(hazard.id)) {
          return hazard.selected === true;
        }
        // For manually added hazards, always include them (don't filter based on selected)
        if (savedManuallyAddedHazards.some(saved => saved.id === hazard.id)) {
          return true;
        }
        // For other hazards, include them (they don't have selected property)
        return true;
      });

  const uniqueHazards = Array.from(
    new Map(mergedHazards.map(hazard => [hazard.id, hazard])).values()
  );

  // Filter selectedHazards to only show hazards with selected: true
  const filteredSelectedHazards = useMemo(() => {
    return selectedHazards.filter(hazard => {
      // For task hazards, only include if selected is true
      if (hazardFromTaskIds.includes(hazard.id)) {
        return hazard.selected === true;
      }
      // For site condition hazards, only include if selected is true
      if (hazardFromSiteConditionIds.includes(hazard.id)) {
        return hazard.selected === true;
      }
      // For manually added hazards, always include them (don't filter based on selected)
      if (manuallyAddedHazardIds.includes(hazard.id)) {
        return true;
      }
      // For other hazards, include them (they don't have selected property)
      return true;
    });
  }, [
    selectedHazards,
    hazardFromTaskIds,
    hazardFromSiteConditionIds,
    manuallyAddedHazardIds,
  ]);

  useEffect(() => {
    if (uniqueHazards.length > 0 && hazardsData.length > 0 && !isInitialized) {
      const initialHazards: Hazards[] = uniqueHazards.map(preSelected => {
        const fullHazard = hazardsData.find(
          (formHazard: Hazards) => formHazard.id === preSelected.id
        ) || {
          id: preSelected.id,
          name: preSelected.name,
          energyLevel: preSelected.energyLevel,
          energyType: preSelected.energyType,
          isApplicable: preSelected.isApplicable,
          imageUrl: preSelected.imageUrl,
          noControlsImplemented: preSelected.noControlsImplemented || false,
          isUserAdded: preSelected?.isUserAdded || false,
          controls: [],
        };
        const selectedControlIds = (preSelected.controls || [])
          .filter(control => control.selected === true)
          .map(control => control.id);

        const updatedControls =
          fullHazard.controls?.map(control => {
            const isSelected = selectedControlIds.includes(control.id);
            return {
              ...control,
              selected: isSelected,
            };
          }) || [];
        const userAddedNewControls = (preSelected.controls || []).filter(
          control => control.isUserAdded === true
        );

        userAddedNewControls.forEach(userControl => {
          if (!updatedControls.some(c => c.id === userControl.id)) {
            updatedControls.push({
              ...userControl,
              selected: selectedControlIds.includes(userControl.id),
            });
          }
        });

        return {
          ...fullHazard,
          selected: preSelected.selected ?? true,
          selectedControlIds,
          noControlsImplemented: preSelected.noControlsImplemented || false,
          controls: updatedControls,
        };
      });
      setManuallyAddedHazardIds(
        savedManuallyAddedHazards
          .filter(
            hazard =>
              // Only include hazards that are NOT from tasks or site conditions
              !hazardFromTaskIds.includes(hazard.id) &&
              !hazardFromSiteConditionIds.includes(hazard.id)
          )
          .map(hazard => hazard.id)
      );

      setSelectedHazards(initialHazards);
      setIsInitialized(true);
    } else if (preSelectedHazards?.tasks?.length === 0 && !isInitialized) {
      setSelectedHazards([]);
      setIsInitialized(true);
    }
  }, [
    hazardsData,
    preSelectedHazards,
    savedManuallyAddedHazards,
    isInitialized,
    setSelectedHazards,
  ]);

  const manuallyAddHazardsHandler = (hazards: Hazards[]) => {
    const allSelectedIds = hazards.map(h => h.id);
    // Filter out both task and site condition hazards - only truly manually added hazards should be included
    const newManuallyAddedIds = allSelectedIds.filter(
      id =>
        !hazardFromTaskIds.includes(id) &&
        !hazardFromSiteConditionIds.includes(id)
    );
    setManuallyAddedHazardIds(newManuallyAddedIds);
    const combinedHazards = [];
    combinedHazards.push(...hazards);
    const hazardsWithUserControls = combinedHazards.map(hazard => {
      const existingHazard = selectedHazards.find(h => h.id === hazard.id);
      if (existingHazard) {
        const existingUserControls = (existingHazard.controls || []).filter(
          control => control.isUserAdded === true
        );
        const mergedControls = [...(hazard.controls || [])];

        existingUserControls.forEach(userControl => {
          if (!mergedControls.some(c => c.id === userControl.id)) {
            mergedControls.push(userControl);
          }
        });
        const combinedSelectedControlIds = hazard.selectedControlIds || [];

        if (existingHazard.selectedControlIds) {
          existingHazard.selectedControlIds.forEach(id => {
            const isUserControlId = existingUserControls.some(c => c.id === id);
            if (isUserControlId && !combinedSelectedControlIds.includes(id)) {
              combinedSelectedControlIds.push(id);
            }
          });
        }

        return {
          ...hazard,
          controls: mergedControls,
          selectedControlIds: combinedSelectedControlIds,
          noControlsImplemented: hazard.noControlsImplemented || false,
        };
      }

      return hazard;
    });
    setSelectedHazards(hazardsWithUserControls);
    setCWFFormStateDirty(true);
  };

  // Function to return hazards with only selected controls
  const getHazardsWithSelectedControls = useCallback(() => {
    return selectedHazards.map(hazard => {
      const selectedControls = (hazard.controls || [])
        .filter((control: Controls) =>
          hazard.selectedControlIds?.includes(control.id)
        )
        .map(control => ({
          ...control,
          selected: true,
        }));
      let allControls = selectedControls;
      if (
        hazardFromTaskIds.includes(hazard.id) ||
        hazardFromSiteConditionIds.includes(hazard.id)
      ) {
        const unselectedControls = (hazard.controls || [])
          .filter(
            (control: Controls) =>
              !hazard.selectedControlIds?.includes(control.id)
          )
          .map(control => ({
            ...control,
            selected: false,
          }));

        allControls = [...selectedControls, ...unselectedControls];
      }
      return {
        id: hazard.id,
        name: hazard.name,
        energyLevel: hazard.energyLevel,
        energyType: hazard.energyType,
        isApplicable: hazard.isApplicable,
        imageUrl: hazard.imageUrl,
        noControlsImplemented: hazard.noControlsImplemented || false,
        ...(hazard.isUserAdded !== undefined && {
          isUserAdded: hazard.isUserAdded,
        }),
        // Only include selected property for task and site condition hazards
        ...(hazardFromTaskIds.includes(hazard.id) ||
        hazardFromSiteConditionIds.includes(hazard.id)
          ? {
              selected: hazard.selected ?? true,
            }
          : {}),
        controls:
          hazardFromTaskIds.includes(hazard.id) ||
          hazardFromSiteConditionIds.includes(hazard.id)
            ? allControls
            : selectedControls,
      };
    });
  }, [selectedHazards, hazardFromTaskIds, hazardFromSiteConditionIds]);

  const getManuallyAddedHazardsWithControls = useCallback(() => {
    // Only return hazards that are truly manually added (not from tasks or site conditions)
    const manuallyAdded = selectedHazards.filter(
      hazard =>
        manuallyAddedHazardIds.includes(hazard.id) &&
        !hazardFromTaskIds.includes(hazard.id) &&
        !hazardFromSiteConditionIds.includes(hazard.id)
    );
    return manuallyAdded;
  }, [
    selectedHazards,
    manuallyAddedHazardIds,
    hazardFromTaskIds,
    hazardFromSiteConditionIds,
  ]);

  const updateTaskHazardsWithSelectedControls = useCallback(() => {
    const taskHazards = getHazardsWithSelectedControls().filter(hazard =>
      hazardFromTaskIds.includes(hazard.id)
    );
    return cwfTaskHazards.map((task: Task) => {
      const updatedHazards = (task.hazards || []).map((hazard: Hazards) => {
        const matchingHazard = taskHazards.find(h => h.id === hazard.id);

        if (!matchingHazard) return hazard;
        const selectedControlIds =
          selectedHazards.find(h => h.id === hazard.id)?.selectedControlIds ||
          [];
        const selectedHazardData = selectedHazards.find(
          h => h.id === hazard.id
        );
        const controlsImplementedValue =
          selectedHazardData?.noControlsImplemented ??
          hazard.noControlsImplemented ??
          false;

        const updatedControls = [...(hazard.controls || [])];
        updatedControls.forEach((control, index) => {
          const isSelected = selectedControlIds.includes(control.id);
          updatedControls[index] = {
            ...control,
            selected: isSelected,
          };
        });

        matchingHazard.controls?.forEach(control => {
          if (!updatedControls.some(c => c.id === control.id)) {
            updatedControls.push({
              ...control,
              selected: selectedControlIds.includes(control.id),
            });
          }
        });

        return {
          ...hazard,
          selected: selectedHazardData?.selected ?? true,
          noControlsImplemented: controlsImplementedValue,
          controls: updatedControls,
        };
      });

      return {
        ...task,
        hazards: updatedHazards,
      };
    });
  }, [
    getHazardsWithSelectedControls,
    cwfTaskHazards,
    hazardFromTaskIds,
    selectedHazards,
  ]);

  const updateSiteConditionHazardsWithSelectedControls = useCallback(() => {
    const siteConditionHazards = getHazardsWithSelectedControls().filter(
      hazard => hazardFromSiteConditionIds.includes(hazard.id)
    );
    return cwfSiteConditionHazards.map((hazard: Hazards) => {
      const matchingHazard = siteConditionHazards.find(h => h.id === hazard.id);
      if (!matchingHazard) return hazard;
      const selectedControlIds =
        selectedHazards.find(h => h.id === hazard.id)?.selectedControlIds || [];
      const selectedHazardData = selectedHazards.find(h => h.id === hazard.id);
      const controlsImplementedValue =
        selectedHazardData?.noControlsImplemented ??
        hazard.noControlsImplemented ??
        false;
      const updatedControls = [...(hazard.controls || [])];
      updatedControls.forEach((control, index) => {
        const isSelected = selectedControlIds.includes(control.id);
        updatedControls[index] = {
          ...control,
          selected: isSelected,
        };
      });
      matchingHazard.controls?.forEach(control => {
        if (!updatedControls.some(c => c.id === control.id)) {
          updatedControls.push({
            ...control,
            selected: selectedControlIds.includes(control.id),
          });
        }
      });
      return {
        ...hazard,
        selected: selectedHazardData?.selected ?? true,
        noControlsImplemented: controlsImplementedValue,
        controls: updatedControls,
      };
    });
  }, [
    getHazardsWithSelectedControls,
    cwfSiteConditionHazards,
    hazardFromSiteConditionIds,
    selectedHazards,
  ]);

  const updateSelectedControls = (
    hazardId: string,
    selectedControlIds: string[]
  ) => {
    setSelectedHazards((prevHazards: Hazards[]) =>
      prevHazards.map(hazard => {
        if (hazard.id !== hazardId) return hazard;
        const existingControlIds =
          hazard.controls?.map(control => control.id) || [];
        const newControlIds = selectedControlIds.filter(
          id => !existingControlIds.includes(id)
        );
        let updatedControls = [...(hazard.controls || [])];

        if (newControlIds.length > 0) {
          const fullHazard = hazardsData.find(h => h.id === hazardId);

          if (fullHazard) {
            newControlIds.forEach(newId => {
              const userAddedControl = userAddedControls.find(
                c => c.id === newId
              );

              if (userAddedControl) {
                updatedControls.push({
                  ...userAddedControl,
                  selected: true,
                });
              } else {
                const newControl = fullHazard.controls?.find(
                  c => c.id === newId
                );
                if (newControl) {
                  updatedControls.push({
                    ...newControl,
                    selected: true,
                  });
                }
              }
            });
          } else {
            newControlIds.forEach(newId => {
              const userAddedControl = userAddedControls.find(
                c => c.id === newId
              );
              if (userAddedControl) {
                updatedControls.push({
                  ...userAddedControl,
                  selected: true,
                });
              }
            });
          }
        }

        updatedControls = updatedControls.map(control => {
          const isSelected = selectedControlIds.includes(control.id);

          return {
            ...control,
            selected: isSelected,
          };
        });

        return {
          ...hazard,
          selectedControlIds,
          controls: updatedControls,
        };
      })
    );

    setCWFFormStateDirty(true);
  };

  const handleAddUserControl = (hazardId: string, newControl: Controls) => {
    setUserAddedControls(prev => {
      if (prev.some(c => c.id === newControl.id)) return prev;
      return [...prev, newControl];
    });

    setSelectedHazards(prevHazards =>
      prevHazards.map(hazard => {
        if (hazard.id !== hazardId) return hazard;

        const updatedControls = [...(hazard.controls || [])];
        if (!updatedControls.some(c => c.id === newControl.id)) {
          updatedControls.push(newControl);
        }
        const updatedSelectedControlIds = [
          ...(hazard.selectedControlIds || []),
        ];
        if (!updatedSelectedControlIds.includes(newControl.id)) {
          updatedSelectedControlIds.push(newControl.id);
        }

        return {
          ...hazard,
          noControlsImplemented: hazard.noControlsImplemented || false,
          controls: updatedControls,
          selectedControlIds: updatedSelectedControlIds,
        };
      })
    );
    setCWFFormStateDirty(true);
  };

  useEffect(() => {
    const token = formEventEmitter.addListener(
      FORM_EVENTS.SAVE_AND_CONTINUE,
      () => {
        const manuallyAddedHazards = getManuallyAddedHazardsWithControls();
        //Resetting HazardControls , if No controls Implemented Checked
        const resettedHazardsAndControls =
          validateNoControlImplemented(manuallyAddedHazards);

        const updatedTasks = updateTaskHazardsWithSelectedControls();
        const updatedSiteConditionHazards =
          updateSiteConditionHazardsWithSelectedControls();
        dispatch({
          type: CF_REDUCER_CONSTANTS.ENERGY_HAZARDS_VALUE_CHANGE,
          payload: resettedHazardsAndControls,
        });
        dispatch({
          type: CF_REDUCER_CONSTANTS.SET_TASKS_HAZARD_DATA,
          payload: updatedTasks,
        });
        dispatch({
          type: CF_REDUCER_CONSTANTS.SET_SITE_CONDITIONS_HAZARD_DATA,
          payload: updatedSiteConditionHazards,
        });
      }
    );

    return () => {
      token.remove();
    };
  }, [
    selectedHazards,
    isInitialized,
    dispatch,
    getHazardsWithSelectedControls,
    getManuallyAddedHazardsWithControls,
    updateTaskHazardsWithSelectedControls,
    manuallyAddedHazardIds,
    cwfTaskHazards,
    hazardsFromTasks,
    userAddedControls,
  ]);

  const removeHazard = (hazardId: string) => {
    if (hazardFromTaskIds.includes(hazardId) && readOnly) {
      console.log(
        "Cannot remove hazard from task in read-only mode:",
        hazardId
      );
      return;
    }

    // For manually added hazards, remove them completely (original behavior)
    if (
      !hazardFromTaskIds.includes(hazardId) &&
      !hazardFromSiteConditionIds.includes(hazardId)
    ) {
      setSelectedHazards(prevHazards =>
        prevHazards.filter(hazard => hazard.id !== hazardId)
      );
      setManuallyAddedHazardIds(prevIds =>
        prevIds.filter(id => id !== hazardId)
      );
      return;
    }

    // For task and site condition hazards, set selected to false instead of removing
    setSelectedHazards(prevHazards =>
      prevHazards.map(hazard => {
        if (hazard.id !== hazardId) return hazard;

        // For task hazards, set selected to false instead of removing
        if (hazardFromTaskIds.includes(hazardId)) {
          return {
            ...hazard,
            selected: false,
          };
        }

        // For site condition hazards, set selected to false instead of removing
        if (hazardFromSiteConditionIds.includes(hazardId)) {
          return {
            ...hazard,
            selected: false,
          };
        }

        return hazard;
      })
    );
  };

  const setHazardNoControlsImplemented = (hazardId: string) => {
    setSelectedHazards(prevHazards =>
      prevHazards.map(hazard => {
        if (hazard.id !== hazardId) return hazard;

        return {
          ...hazard,
          noControlsImplemented: !hazard.noControlsImplemented,
        };
      })
    );
  };

  const validateNoControlImplemented = (
    inputHazardsData: Hazards[]
  ): Hazards[] => {
    const filteredHazardsData: Hazards[] = inputHazardsData.map(hazard =>
      hazard?.noControlsImplemented == true
        ? resetHazardControls(hazard)
        : hazard
    );
    return filteredHazardsData;
  };

  const resetHazardControls = (hazard: Hazards): Hazards => {
    if (!hazard) return hazard;

    const updatedControls = (hazard.controls ?? [])
      .filter(control => !control.isUserAdded)
      .map(control => ({
        ...control,
        selected: false,
      }));

    return {
      ...hazard,
      controls: updatedControls,
      selectedControlIds: [], // Clear selected control IDs
    };
  };

  const computedEnergyWheelStatus = filteredSelectedHazards.reduce(
    (currentStatus, hazard) => {
      return { ...currentStatus, [String(hazard.energyType)]: true };
    },
    energyWheelInitialStatus
  );

  useEffect(() => {
    setIsInitialized(false);
  }, [cwfSiteConditionHazards]);
  return (
    <FormProvider {...methods}>
      {readOnly
        ? ""
        : !isSummaryView &&
          isEnergyWheelDisabled && (
            <ButtonSecondary
              label="Add Hazards"
              iconStart="plus_circle_outline"
              size="sm"
              className="block mb-2 ml-auto -mt-8"
              onClick={() => addHazardHandler()}
              disabled={readOnly}
            />
          )}
      <HazardsModal
        addHazardsModalOpen={addHazardsModalOpen}
        setAddHazardsModalOpen={setAddHazardsModalOpen}
        energyType={selectedEnergyType}
        manuallyAddedHazards={manuallyAddHazardsHandler}
        hazardsData={hazardsData}
        subTitle={subTitle}
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        preSelectedHazards={filteredSelectedHazards}
      />
      {!isSummaryView && isEnergyWheelEnabled && (
        <div className="border p-3 rounded-lg border-gr mt-3">
          Select an energy type to add hazards
          <EnergyWheel
            status={computedEnergyWheelStatus}
            callback={energyType => {
              setSeelectedEnergyType(energyType);
              setAddHazardsModalOpen(true);
            }}
            readOnly={readOnly}
          />
        </div>
      )}
      <HazardsCard
        hazards={filteredSelectedHazards}
        getHazardsWithSelectedControls={getHazardsWithSelectedControls}
        updateSelectedControls={updateSelectedControls}
        removeHazard={removeHazard}
        setHazardNoControlsImplemented={setHazardNoControlsImplemented}
        readOnly={readOnly}
        isSummaryView={isSummaryView}
        userAddedControls={userAddedControls}
        onAddUserControl={handleAddUserControl}
        subTitle={subTitle}
        addHazardHandler={addHazardHandler}
      />
    </FormProvider>
  );
};

export default EnergyAndHazards;
