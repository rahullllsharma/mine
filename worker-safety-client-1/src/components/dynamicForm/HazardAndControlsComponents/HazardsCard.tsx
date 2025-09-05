import type {
  Controls,
  Hazards,
} from "../../templatesComponents/customisedForm.types";
import { BodyText, CaptionText, Icon } from "@urbint/silica";
import Image from "next/image";
import { useEffect, useState, useContext } from "react";
import { Checkbox } from "@/components/forms/Basic/Checkbox";
import CardLazyLoader from "@/components/shared/cardLazyLoader/CardLazyLoader";
import { useFormRendererContext } from "@/components/templatesComponents/FormPreview/Components/FormRendererContext";
import CustomisedFromStateContext from "@/context/CustomisedDataContext/CustomisedFormStateContext";
import Button from "../../shared/button/Button";
import ButtonSecondary from "../../shared/button/secondary/ButtonSecondary";
import {
  ENERGY_TYPE_COLORS,
  EnergyLevel,
} from "../../templatesComponents/customisedForm.types";
import ControlModal from "./ControlModal";
import ControlValueSelectComponent from "./ControlValueSelectComponent";
import { DeleteHazardModal, HazardsCardBlankField } from "./utils";

interface HazardsCardProps {
  hazards: Hazards[];
  getHazardsWithSelectedControls: () => Hazards[];
  updateSelectedControls: (
    hazardId: string,
    selectedControlIds: string[]
  ) => void;
  removeHazard: (hazardId: string) => void;
  setHazardNoControlsImplemented: (hazardId: string) => void;
  readOnly?: boolean;
  isSummaryView?: boolean;
  // Added props for user controls handling
  userAddedControls?: Controls[];
  onAddUserControl?: (hazardId: string, newControl: Controls) => void;
  subTitle: string;
  addHazardHandler: (tab?: string) => void;
}

const getHazardCustomColor = (
  isEnergyWheelEnabled: boolean,
  hazardEnergyType?: string
): `#${string}` => {
  return (
    isEnergyWheelEnabled && hazardEnergyType
      ? ENERGY_TYPE_COLORS[hazardEnergyType]
      : "#CCCCCC"
  ) as `#${string}`;
};

const HazardsCard = ({
  hazards = [],
  getHazardsWithSelectedControls,
  updateSelectedControls,
  removeHazard,
  setHazardNoControlsImplemented,
  readOnly = false,
  userAddedControls = [],
  isSummaryView,
  onAddUserControl,
  subTitle,
  addHazardHandler,
}: HazardsCardProps) => {
  const { state } = useContext(CustomisedFromStateContext)!;
  const isEnergyWheelEnabled =
    state.form.metadata?.is_energy_wheel_enabled ?? true;
  const [hazardToDelete, setHazardToDelete] = useState<string | null>(null);
  const [isDeleteModalOpen, setIsDeleteModalOpen] = useState(false);
  const [controlModalOpen, setControlModalOpen] = useState(false);
  const [selectedHazardId, setSelectedHazardId] = useState("");
  const [selectedHazardControls, setSelectedHazardControls] = useState<
    Controls[]
  >([]);
  const [availableControls, setAvailableControls] = useState<Controls[]>([]);
  const { isLoading, showMissingControlsError } = useFormRendererContext();

  const getControlOptions = (controls: Controls[] | undefined) => {
    if (!controls || !Array.isArray(controls)) return [];

    return controls.map(control => ({
      value: control.id,
      id: control.id,
      name: control.name,
      isUserAdded: control.isUserAdded,
    }));
  };

  const openControlModal = (hazardId: string) => {
    setSelectedHazardId(hazardId);
    const currentHazard = hazards.find(h => h.id === hazardId);

    if (!currentHazard) return;
    const selectedControlIds = currentHazard.selectedControlIds || [];
    const preSelectedControls = (currentHazard.controls || []).filter(control =>
      selectedControlIds.includes(control.id)
    );

    setSelectedHazardControls(preSelectedControls);
    const allAvailableControls = [...(currentHazard.controls || [])];
    if (userAddedControls && userAddedControls.length > 0) {
      const existingControlIds = new Set(allAvailableControls.map(c => c.id));
      userAddedControls.forEach(userControl => {
        if (!existingControlIds.has(userControl.id)) {
          allAvailableControls.push(userControl);
        }
      });
    }
    const filteredControls = allAvailableControls.filter(
      control => control.name !== "Other"
    );
    setAvailableControls(filteredControls);
    setControlModalOpen(true);
  };

  const handleAddControl = (updatedControls: Controls[], hazardId: string) => {
    const currentHazard = hazards.find(h => h.id === hazardId);
    if (!currentHazard) return;
    const controlIds = updatedControls.map(control => control.id);
    updateSelectedControls(hazardId, controlIds);
    const existingControlIds = new Set(
      (currentHazard.controls || []).map(c => c.id)
    );
    const newUserControls = updatedControls.filter(
      control => control.isUserAdded && !existingControlIds.has(control.id)
    );
    if (newUserControls.length > 0 && onAddUserControl) {
      newUserControls.forEach(newControl => {
        onAddUserControl(hazardId, newControl);
      });
    }
    setControlModalOpen(false);
  };

  const handleRemoveControl = (hazardId: string, controlId: string) => {
    const currentHazard = hazards.find(h => h.id === hazardId);
    if (!currentHazard) return;
    const updatedControlIds = (currentHazard.selectedControlIds || []).filter(
      id => id !== controlId
    );
    updateSelectedControls(hazardId, updatedControlIds);
  };

  useEffect(() => {
    getHazardsWithSelectedControls();
  }, [hazards]);

  const [groupedHazards, setGroupedHazards] = useState({
    HIGH_ENERGY: [] as Hazards[],
    LOW_ENERGY: [] as Hazards[],
  });

  const [expandedSections, setExpandedSections] = useState<
    Record<string, boolean>
  >({});

  useEffect(() => {
    const grouped = hazards.reduce(
      (acc, hazard) => {
        if (hazard.energyLevel === EnergyLevel.HighEnergy) {
          acc.HIGH_ENERGY.push(hazard);
        } else {
          acc.LOW_ENERGY.push(hazard);
        }
        return acc;
      },
      { HIGH_ENERGY: [] as Hazards[], LOW_ENERGY: [] as Hazards[] }
    );

    setGroupedHazards(grouped);

    hazards.forEach(hazard => {
      if (!hazard.selectedControlIds) {
        updateSelectedControls(hazard.id, []);
      }
    });
  }, [hazards, updateSelectedControls]);

  const toggleSection = (sectionId: string) => {
    setExpandedSections(prev => ({
      ...prev,
      [sectionId]: !prev[sectionId],
    }));
  };

  const confirmDeleteHazard = () => {
    if (hazardToDelete) {
      removeHazard(hazardToDelete);
      setIsDeleteModalOpen(false);
      setHazardToDelete(null);
    }
  };

  const handleDeleteClick = (hazardId: string) => {
    setHazardToDelete(hazardId);
    setIsDeleteModalOpen(true);
  };

  const renderHazardSection = (
    energyType: string,
    sectionHazards: Hazards[]
  ) => {
    if (!sectionHazards.length) {
      return (
        <HazardsCardBlankField
          addHazardHandler={addHazardHandler}
          subTitle={subTitle}
          energyType={energyType}
          readOnly={readOnly}
          inSummary={isSummaryView}
        />
      );
    }

    const noControlsImplementedHazardsTemplate = () => {
      return (
        <div className="text-[#FF0000] text-sm pt-2 pb-2">
          Select at least one control or check &apos;No controls
          implemented&apos;
        </div>
      );
    };

    const isHazardSubmittable = (hazardItem: Hazards) => {
      if (hazardItem.noControlsImplemented === true) {
        return true;
      }
      const hasSelectedControls =
        hazardItem.controls &&
        hazardItem.controls.some(control => control.selected === true);
      return hasSelectedControls;
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

    const tab =
      energyType === EnergyLevel.HighEnergy ? "highEnergy" : "otherHazards";

    return (
      <div
        className={`mb-4 mt-5 ${
          isSummaryView ? "" : "bg-gray-100 rounded p-3"
        }`}
      >
        <div className="flex items-center">
          <BodyText
            className={`${
              isSummaryView ? "text-lg" : "text-xl"
            } font-semibold mb-2`}
          >
            {energyType === EnergyLevel.HighEnergy
              ? subTitle || "High Energy Hazards"
              : "Other Hazards"}
          </BodyText>
          {!isSummaryView && (
            <ButtonSecondary
              label="Add Hazards"
              iconStart="plus_circle_outline"
              size="sm"
              className="mb-2 ml-auto"
              onClick={() => addHazardHandler(tab)}
              disabled={readOnly}
            />
          )}
        </div>

        {Object.entries(energyTypeGroups).map(([type, typeHazards]) => {
          const sectionId = `${energyType}-${type}`;
          const isExpanded = expandedSections[sectionId] !== false;
          const backgroundColor = getHazardCustomColor(
            isEnergyWheelEnabled,
            type
          );

          return (
            <div key={type} className="mb-4 rounded-lg">
              {isEnergyWheelEnabled &&
              type &&
              type !== "UNSPECIFIED" &&
              type !== "NOT_DEFINED" ? (
                <div
                  className="p-2 flex items-center justify-between cursor-pointer rounded-t-lg"
                  style={{ backgroundColor }}
                  onClick={() => toggleSection(sectionId)}
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
                  <Icon
                    className={`text-neutral-shade-75 text-xl transition-transform ${
                      isExpanded ? "rotate-180" : ""
                    }`}
                    name="chevron_big_down"
                  />
                </div>
              ) : null}

              {(!isEnergyWheelEnabled || isExpanded) && (
                <div
                  className={`bg-white border border-gray-200 ${
                    isSummaryView &&
                    (!type || type === "UNSPECIFIED" || type === "NOT_DEFINED")
                      ? "rounded-lg"
                      : "rounded-b-lg"
                  }`}
                >
                  {typeHazards.map(hazard => (
                    <div
                      key={hazard.id}
                      id={hazard.id}
                      className="border-t border-gray-200 first:border-t-0 p-4"
                    >
                      <div className="flex items-center justify-between mb-4">
                        <div className="flex items-center gap-x-3">
                          {hazard.imageUrl &&
                            energyType === EnergyLevel.HighEnergy && (
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
                        {!isSummaryView && (
                          <Button
                            disabled={readOnly}
                            onClick={() => handleDeleteClick(hazard.id)}
                          >
                            <Icon
                              className="text-neutral-shade-58 text-xl cursor-pointer"
                              name="trash_empty"
                            />
                          </Button>
                        )}
                      </div>
                      {isSummaryView ? (
                        hazard.noControlsImplemented ? (
                          <BodyText className="text-neutrals-tertiary text-sm font-semibold">
                            No controls implemented
                          </BodyText>
                        ) : (
                          <></>
                        )
                      ) : (
                        <div className="flex mb-3 mt-3">
                          {hazard.noControlsImplemented}
                          <Checkbox
                            className="w-auto"
                            checked={hazard.noControlsImplemented || false}
                            disabled={isSummaryView || readOnly}
                            onClick={() =>
                              setHazardNoControlsImplemented(hazard.id)
                            }
                          >
                            <span className="text-gray-800  text-sm font-semibold">
                              No controls implemented
                            </span>
                          </Checkbox>
                        </div>
                      )}
                      {isSummaryView ? (
                        hazard.noControlsImplemented ? (
                          <></>
                        ) : (
                          <div className="relative">
                            <div className="mb-1 text-sm font-semibold">
                              Controls
                            </div>
                            <ControlValueSelectComponent
                              options={getControlOptions(
                                hazard.controls
                              ).filter(option =>
                                hazard.selectedControlIds?.includes(option.id)
                              )}
                              customColor={getHazardCustomColor(
                                isEnergyWheelEnabled,
                                hazard.energyType
                              )}
                              onRemoveOption={controlId => {
                                if (!isSummaryView) {
                                  handleRemoveControl(hazard.id, controlId);
                                }
                              }}
                              openModal={() => {
                                if (!isSummaryView) {
                                  openControlModal(hazard.id);
                                }
                              }}
                              isSummaryView={isSummaryView}
                            />
                            {showMissingControlsError &&
                              !isHazardSubmittable(hazard) &&
                              noControlsImplementedHazardsTemplate()}
                          </div>
                        )
                      ) : (
                        <>
                          {hazard.noControlsImplemented ? (
                            <></>
                          ) : (
                            <>
                              <div className="relative">
                                <div className="mb-1 text-sm font-semibold">
                                  Controls
                                </div>
                                <ControlValueSelectComponent
                                  options={getControlOptions(
                                    hazard.controls
                                  ).filter(option =>
                                    hazard.selectedControlIds?.includes(
                                      option.id
                                    )
                                  )}
                                  customColor={getHazardCustomColor(
                                    isEnergyWheelEnabled,
                                    hazard.energyType
                                  )}
                                  onRemoveOption={controlId =>
                                    handleRemoveControl(hazard.id, controlId)
                                  }
                                  openModal={() => openControlModal(hazard.id)}
                                  readOnly={readOnly}
                                />
                                {showMissingControlsError &&
                                  !isHazardSubmittable(hazard) &&
                                  noControlsImplementedHazardsTemplate()}
                              </div>
                            </>
                          )}
                        </>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </div>
          );
        })}
      </div>
    );
  };

  return (
    <>
      {isLoading ? (
        <CardLazyLoader />
      ) : (
        <div className="mt-4">
          {(!isSummaryView || groupedHazards.HIGH_ENERGY.length > 0) &&
            renderHazardSection("HIGH_ENERGY", groupedHazards.HIGH_ENERGY)}
          {(!isSummaryView || groupedHazards.LOW_ENERGY.length > 0) &&
            renderHazardSection("LOW_ENERGY", groupedHazards.LOW_ENERGY)}
        </div>
      )}

      <DeleteHazardModal
        isDeleteModalOpen={isDeleteModalOpen}
        setIsDeleteModalOpen={setIsDeleteModalOpen}
        setHazardToDelete={setHazardToDelete}
        confirmDeleteHazard={confirmDeleteHazard}
      />

      <ControlModal
        controlModalOpen={controlModalOpen}
        onClose={() => setControlModalOpen(false)}
        preSelectedControls={selectedHazardControls}
        hazardsControlList={availableControls}
        selectedHazardId={selectedHazardId}
        onAddControl={handleAddControl}
      />
    </>
  );
};

export default HazardsCard;
