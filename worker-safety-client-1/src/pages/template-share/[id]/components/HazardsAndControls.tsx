import type {
  HazardControl,
  Hazards,
  Task,
  Controls,
  FormElement,
} from "@/components/templatesComponents/customisedForm.types";
import {
  ActionLabel,
  BodyText,
  CaptionText,
  SectionHeading,
} from "@urbint/silica";
import Image from "next/image";
import { useMemo } from "react";
import {
  ApplicabilityLevel,
  EnergyLevel,
  ENERGY_TYPE_COLORS,
} from "@/components/templatesComponents/customisedForm.types";
import ControlValue from "./ControlValue";

const HazardsAndControls = ({
  subTitle,
  hazardsAndControls,
  isEnergyWheelEnabled,
  item,
}: {
  subTitle: string;
  hazardsAndControls: HazardControl | undefined;
  isEnergyWheelEnabled: boolean;
  item: FormElement;
}): JSX.Element => {
  const getControlOptions = (controls: Controls[] | undefined) => {
    if (!controls || !Array.isArray(controls)) return [];

    return controls.map(control => ({
      value: control.id,
      id: control.id,
      name: control.name,
      selected: control.selected,
      isUserAdded: control.isUserAdded,
    }));
  };

  const taskHazards = useMemo(
    () => hazardsAndControls?.tasks || [],
    [hazardsAndControls?.tasks]
  );

  const hazardsFromTasks = useMemo(() => {
    return (
      taskHazards
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
            selected: hazard.selected ?? true,
            controls: processedControls,
          };
        }) || []
    );
  }, [taskHazards]);

  const siteConditionHazards = useMemo(
    () => hazardsAndControls?.site_conditions || [],
    [hazardsAndControls?.site_conditions]
  );

  const hazardsFromSiteConditions = useMemo(() => {
    return (
      siteConditionHazards
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
            selected: hazard.selected ?? true,
            controls: processedControls,
          };
        }) || []
    );
  }, [siteConditionHazards]);

  const savedManuallyAddedHazards = useMemo(
    () => hazardsAndControls?.manually_added_hazards || [],
    [hazardsAndControls?.manually_added_hazards]
  );

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
      ];

  const uniqueHazards = Array.from(
    new Map(mergedHazards.map(hazard => [hazard.id, hazard])).values()
  );

  const groupedHazards = useMemo(() => {
    return uniqueHazards.reduce(
      (acc, hazard) => {
        if (hazard.energyLevel === "HIGH_ENERGY") {
          acc.HIGH_ENERGY.push(hazard);
        } else {
          acc.LOW_ENERGY.push(hazard);
        }
        return acc;
      },
      { HIGH_ENERGY: [] as Hazards[], LOW_ENERGY: [] as Hazards[] }
    );
  }, [uniqueHazards]);

  const renderHazardSection = (
    energyType: string,
    sectionHazards: Hazards[]
  ) => {
    const hazardLabel =
      energyType === "HIGH_ENERGY"
        ? subTitle || "High Energy Hazards"
        : "Other Hazards";

    if (!sectionHazards.length) {
      return <BodyText>No {hazardLabel} Added</BodyText>;
    }

    const getHazardCustomColor = (hazardEnergyType?: string): `#${string}` => {
      return (
        isEnergyWheelEnabled && hazardEnergyType
          ? ENERGY_TYPE_COLORS[hazardEnergyType]
          : "#CCCCCC"
      ) as `#${string}`;
    };

    const energyTypeGroups = isEnergyWheelEnabled
      ? sectionHazards.reduce((acc, hazard) => {
          const type = hazard.energyType || "UNSPECIFIED";
          if (!acc[type]) {
            acc[type] = [];
          }
          acc[type].push(hazard);
          return acc;
        }, {} as Record<string, Hazards[]>)
      : { "": sectionHazards }; // If energy wheel is disabled, put all hazards in a single group

    return (
      <>
        <ActionLabel className="text-neutral-shade-75 text-lg">
          {hazardLabel}
        </ActionLabel>

        {Object.entries(energyTypeGroups).map(([type, typeHazards]) => {
          const backgroundColor = getHazardCustomColor(type);
          return (
            <div key={type} className="rounded-lg">
              {isEnergyWheelEnabled &&
              type &&
              type.toUpperCase() !== "UNSPECIFIED" &&
              type !== "NOT_DEFINED" ? (
                <div
                  className="p-2 flex items-center justify-between rounded-t-lg"
                  style={{ backgroundColor }}
                >
                  <div className="flex items-center gap-x-1">
                    <Image
                      src={require(`public/assets/CWF/EnergyWheel/${type.toLocaleLowerCase()}.svg`)}
                      alt={type}
                      className="mr-3"
                      width={32}
                      height={32}
                    />
                    <BodyText className="text-lg font-semibold">
                      {type}
                    </BodyText>
                  </div>
                </div>
              ) : null}

              <div
                className={`bg-white border border-gray-200 ${
                  type && (type === "UNSPECIFIED" || type === "NOT_DEFINED")
                    ? "rounded-lg"
                    : "rounded-b-lg"
                }`}
              >
                {typeHazards.map(hazard => (
                  <div
                    key={hazard.id}
                    className="border-t border-gray-200 first:border-t-0 p-4"
                  >
                    <div className="flex items-center justify-between mb-4">
                      <div className="flex items-center gap-x-3">
                        {hazard.imageUrl &&
                          hazard.energyLevel === EnergyLevel.HighEnergy && (
                            <Image
                              src={hazard.imageUrl}
                              alt={hazard.name}
                              width={64}
                              height={64}
                            />
                          )}
                        <CaptionText className="text-lg font-semibold">
                          {hazard.name}
                        </CaptionText>
                      </div>
                    </div>
                    <ControlValue
                      options={getControlOptions(hazard.controls).filter(
                        option => option.selected === true
                      )}
                      customColor={getHazardCustomColor(hazard.energyType)}
                      noControlsImplemented={
                        hazard.noControlsImplemented ?? false
                      }
                    />
                  </div>
                ))}
              </div>
            </div>
          );
        })}
      </>
    );
  };

  return (
    <div className="bg-brand-gray-10 p-4 flex flex-col gap-4 rounded-lg">
      <SectionHeading className="text-[20px] text-neutral-shade-100 font-semibold">
        {item.properties.title ?? "Hazards and Controls"}
      </SectionHeading>
      {groupedHazards.HIGH_ENERGY.length === 0 &&
      groupedHazards.LOW_ENERGY.length === 0 ? (
        <BodyText className="flex text-base font-semibold text-neutrals-tertiary">
          No information provided
        </BodyText>
      ) : (
        <>
          {renderHazardSection("HIGH_ENERGY", groupedHazards.HIGH_ENERGY)}
          {renderHazardSection("LOW_ENERGY", groupedHazards.LOW_ENERGY)}
        </>
      )}
    </div>
  );
};

export default HazardsAndControls;
