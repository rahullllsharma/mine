import type {
  ActivePageObjType,
  FormRendererContextType,
  FormRendererProviderProps,
  Hazards,
  PageType,
  Task,
} from "../../customisedForm.types";
import orderBy from "lodash/orderBy";
import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
} from "react";
import {
  ApplicabilityLevel,
  CWFItemType,
  EnergyLevel,
} from "../../customisedForm.types";

const FormContext = createContext<FormRendererContextType | undefined>(
  undefined
);

const getFormContents = (
  data: PageType[],
  activePageDetails: ActivePageObjType
) => {
  const doWork = () => {
    if (activePageDetails?.type) {
      if (activePageDetails.type === CWFItemType.SubPage) {
        return (
          data
            .filter(
              (element: PageType) => element.id === activePageDetails.parentId
            )?.[0]
            ?.contents.filter(
              (item: PageType) => item.id === activePageDetails.id
            )?.[0]?.contents || []
        );
      } else {
        return (
          data?.filter(
            (element: PageType) => element.id === activePageDetails.id
          )?.[0]?.contents || []
        );
      }
    }
  };
  return orderBy(doWork() || [], o => o.order, "asc");
};

export const FormRendererProvider = ({
  children,
  formObject,
  activePageDetails,
  setActivePageDetails,
  mode,
  hazardsData,
  tasksHazardData,
  isLoading,
  librarySiteConditionsData,
  librarySiteConditionsLoading,
}: FormRendererProviderProps) => {
  // State for selected hazards
  const [selectedHazards, setSelectedHazards] = useState<Hazards[]>([]);
  const [isHazardsAndControlsPage, setIsHazardsAndControlsPage] =
    useState<boolean>(false);
  const [manuallyAddedHazardIds, setManuallyAddedHazardIds] = useState<
    string[]
  >([]);
  const [showMissingControlsError, setShowMissingControlsError] =
    useState<boolean>(false);

  // Common function to determine if a hazard is recommended
  const isRecommendedHazard = useCallback(
    (hazard: Hazards): boolean => {
      // Check if taskApplicabilityLevels exists and is MOSTLY applicable
      const isMostlyApplicable = !!hazard.taskApplicabilityLevels?.some(
        level => level.applicabilityLevel === ApplicabilityLevel.Mostly
      );

      // Check for HIGH energy
      const isHighEnergy = hazard.energyLevel === EnergyLevel.HighEnergy;

      // Check if NOT already selected
      const isNotSelected = !selectedHazards.some(
        selectedHazard => selectedHazard.id === hazard.id
      );

      // All conditions must be true
      return isMostlyApplicable && isHighEnergy && isNotSelected;
    },
    [selectedHazards]
  );

  // This function creates a list of recommended hazards for selection
  const getTaskHazardsMapping = useCallback((): Record<string, Hazards[]> => {
    // Initialize result object
    const taskHazardsMapping: Record<string, Hazards[]> = {};

    // Return empty object if no task library data
    if (!tasksHazardData) {
      return taskHazardsMapping;
    }

    // Process each task in the library
    tasksHazardData.forEach((task: Task) => {
      // Filter hazards using the common function
      const filteredHazards =
        task.hazards?.filter(isRecommendedHazard)?.map((hazard: Hazards) => ({
          ...hazard,
          // we need to add the imageUrl to display in the modal
          imageUrl: hazardsData.find(({ id }) => id === hazard.id)?.imageUrl,
        })) || [];

      // Only add to mapping if there are filtered hazards
      if (filteredHazards.length > 0) {
        taskHazardsMapping[task.name] = filteredHazards;
      }
    });

    return taskHazardsMapping;
  }, [tasksHazardData, hazardsData, isRecommendedHazard]);

  // Variable stores whether or not there are recommended hazards
  const hasRecommendedHazards = useMemo(() => {
    const allRecommendedHazards =
      tasksHazardData
        ?.flatMap((task: Task) => task.hazards || [])
        ?.filter(
          (hazard: Hazards | undefined): hazard is Hazards =>
            !!hazard && isRecommendedHazard(hazard)
        ) || [];

    return !!allRecommendedHazards.length;
  }, [tasksHazardData, isRecommendedHazard]);

  const cwfTaskHazards = useMemo(
    () => formObject.component_data?.hazards_controls?.tasks || [],
    [formObject.component_data?.hazards_controls?.tasks]
  );

  const cwfSiteConditionHazards = useMemo(
    () => formObject.component_data?.hazards_controls?.site_conditions || [],
    [formObject.component_data?.hazards_controls?.site_conditions]
  );

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
            controls: processedControls,
          };
        }) || []
    );
  }, [cwfTaskHazards]);
  const savedManuallyAddedHazards = useMemo(
    () =>
      formObject.component_data?.hazards_controls?.manually_added_hazards ?? [],
    [formObject.component_data?.hazards_controls?.manually_added_hazards]
  );

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
            controls: processedControls,
          };
        }) || []
    );
  }, [cwfSiteConditionHazards]);

  // Initialize selectedHazards from formObject when component mounts or when formObject changes
  useEffect(() => {
    const noHazardsAvailable =
      hazardsFromTasks.length === 0 &&
      savedManuallyAddedHazards.length === 0 &&
      hazardsFromSiteConditions.length === 0;

    const mergedHazards = noHazardsAvailable
      ? []
      : [
          ...hazardsFromTasks,
          ...savedManuallyAddedHazards,
          ...hazardsFromSiteConditions,
        ];
    const uniqueHazards = Array.from(
      new Map(mergedHazards.map(hazard => [hazard.id, hazard])).values()
    );
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
        controls: preSelected.controls || [],
        isUserAdded: preSelected?.isUserAdded || false,
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
      savedManuallyAddedHazards.map(hazard => hazard.id)
    );
    setSelectedHazards(initialHazards);
  }, [
    hazardsFromTasks,
    savedManuallyAddedHazards,
    hazardsData,
    hazardsFromSiteConditions,
  ]);

  // Add a context value for manuallyAddHazardsHandler
  const manuallyAddHazardsHandler = (hazards: Hazards[]) => {
    const allSelectedIds = hazards.map(h => h.id);
    // Only hazards not from tasks are considered manually added
    const hazardFromTaskIds = hazardsFromTasks.map(h => h.id);
    const newManuallyAddedIds = allSelectedIds.filter(
      id => !hazardFromTaskIds.includes(id)
    );
    setManuallyAddedHazardIds(newManuallyAddedIds);
    setSelectedHazards(hazards);
  };

  const value = {
    formObject,
    activePageDetails,
    setActivePageDetails,
    mode,
    hazardsData,
    tasksHazardData,
    getFormContents,
    hasRecommendedHazards,
    getTaskHazardsMapping,
    selectedHazards,
    setSelectedHazards,
    isHazardsAndControlsPage,
    setIsHazardsAndControlsPage,
    manuallyAddedHazardIds,
    setManuallyAddedHazardIds,
    isLoading,
    showMissingControlsError,
    setShowMissingControlsError,
    manuallyAddHazardsHandler,
    librarySiteConditionsData,
    librarySiteConditionsLoading,
  };
  return <FormContext.Provider value={value}>{children}</FormContext.Provider>;
};

export const useFormRendererContext = () => {
  const context = useContext(FormContext);
  if (context === undefined) {
    throw new Error("useFormContext must be used within a FormProvider");
  }
  return context;
};
