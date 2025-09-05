import { CaptionText, Icon } from "@urbint/silica";
import cx from "classnames";
import Image from "next/image";
import { useEffect, useState } from "react";
import ButtonPrimary from "../../shared/button/primary/ButtonPrimary";
import ButtonRegular from "../../shared/button/regular/ButtonRegular";
import Modal from "../../shared/modal/Modal";
import {
  ENERGY_TYPE_COLOR,
  type Hazards,
  type HazardsModalProps,
} from "../../templatesComponents/customisedForm.types";
import AddOtherComponent from "./AddOtherComponent";
import HazardsTabs from "./HazardsTabs";

export enum EnergyLevel {
  highEnergy = "HIGH_ENERGY",
  lowEnergy = "LOW_ENERGY",
}

const HazardsModal = ({
  addHazardsModalOpen,
  hazardsData,
  preSelectedHazards = [],
  energyType,
  setAddHazardsModalOpen,
  manuallyAddedHazards,
  subTitle,
  activeTab,
  setActiveTab,
}: HazardsModalProps) => {
  const [selectedHighEnergyHazards, setSelectedHighEnergyHazards] = useState<
    Hazards[]
  >([]);
  const [selectedOtherHazards, setSelectedOtherHazards] = useState<Hazards[]>(
    []
  );
  const [searchTerm, setSearchTerm] = useState("");
  const [showUserInput, setShowUserInput] = useState(false);
  const [userAddedHazards, setUserAddedHazards] = useState<Hazards[]>([]);

  // Initialize selected hazards from preSelectedHazards when modal opens
  useEffect(() => {
    if (addHazardsModalOpen) {

      // Load ALL selected hazards from preSelectedHazards - we'll filter display later
      const highEnergySelected = preSelectedHazards.filter(
        cwfHazard => cwfHazard.energyLevel === EnergyLevel.highEnergy
      );
      
      const otherSelected = preSelectedHazards.filter(
        cwfHazard => cwfHazard.energyLevel !== EnergyLevel.highEnergy
      );

      // Filter user-added hazards from preSelectedHazards (all energy types)
      const userAdded = preSelectedHazards.filter(hazard => hazard.isUserAdded).sort((a, b) => a.name.localeCompare(b.name));
      
      setSelectedHighEnergyHazards(highEnergySelected);
      setSelectedOtherHazards(otherSelected);
      setUserAddedHazards(userAdded);
    }
  }, [addHazardsModalOpen, preSelectedHazards]);

  // Filter hazards by energy type for display only
  const highEnergyHazards = hazardsData.filter(
    (hazard: Hazards) =>
      hazard.energyLevel === "HIGH_ENERGY" &&
      (energyType ? hazard.energyType === energyType : true)
  ) 

  const otherHazards = hazardsData.filter(
    (hazard: Hazards) =>
      hazard.energyLevel !== "HIGH_ENERGY" &&
      (energyType ? hazard.energyType === energyType : true)
  ) 

  

  const handleHighEnergyHazardSelect = (hazard: Hazards) => {
    const isSelected = selectedHighEnergyHazards.some(
      userSelectedHighHazard => userSelectedHighHazard.id === hazard.id
    );

    if (isSelected) {
      setSelectedHighEnergyHazards(
        selectedHighEnergyHazards.filter(
          userSelectedHighHazard => userSelectedHighHazard.id !== hazard.id
        )
      );
    } else {
      setSelectedHighEnergyHazards([...selectedHighEnergyHazards, hazard]);
    }
  };

  const handleOtherHazardSelect = (hazard: Hazards) => {
    const isSelected = selectedOtherHazards.some(
      userSelectedLowHazard => userSelectedLowHazard.id === hazard.id
    );

    if (isSelected) {
      setSelectedOtherHazards(
        selectedOtherHazards.filter(
          userSelectedLowHazard => userSelectedLowHazard.id !== hazard.id
        )
      );
    } else {
      setSelectedOtherHazards([...selectedOtherHazards, hazard]);
    }
  };

  const handleUserAddedHazardSelect = (hazard: Hazards) => {
    const isSelected = selectedOtherHazards.some(
      userSelectedLowHazard => userSelectedLowHazard.id === hazard.id
    );
  
    if (isSelected) {
      // Only remove from selectedOtherHazards, but keep it in userAddedHazards
      setSelectedOtherHazards(
        selectedOtherHazards.filter(
          userSelectedLowHazard => userSelectedLowHazard.id !== hazard.id
        )
      );
      // Don't remove from userAddedHazards here
    } else {
      setSelectedOtherHazards([...selectedOtherHazards, hazard]);
    }
  };

  const isHighEnergyHazardSelected = (hazardId: string) => {
    return selectedHighEnergyHazards.some(
      userSelectedHighHazard => userSelectedHighHazard.id === hazardId
    );
  };

  const isOtherHazardSelected = (hazardId: string) => {
    return selectedOtherHazards.some(
      userSelectedLowHazard => userSelectedLowHazard.id === hazardId
    );
  };

  // Filter other hazards by search term AND current energy type
  const filteredOtherHazards = otherHazards
    .filter((hazard: Hazards) => 
      hazard.name.toLowerCase().includes(searchTerm.toLowerCase()) &&
      (!energyType || hazard.energyType === energyType)
    );

  const handleAddUserHazard = (selectedHazardValue:{
    id: string;
    name: string;
    isUserAdded: boolean;
    isApplicable: boolean;
  }) => {
      const userAddedHazard :Hazards= {
       ...selectedHazardValue,
        imageUrl: 'https://storage.googleapis.com/worker-safety-public-icons/DefaultHazardIcon.svg',
        energyLevel: 'LOW_ENERGY',
        energyType: energyType || 'UNSPECIFIED',
        noControlsImplemented: false,
        isUserAdded: true,
      };
      
      setUserAddedHazards([...userAddedHazards, userAddedHazard].sort((a, b) => a.name.localeCompare(b.name)));
      setSelectedOtherHazards([...selectedOtherHazards, userAddedHazard]);
      setShowUserInput(false);
    
  };

  const handleSave = () => {
    // Get hazards that were already selected for other energyTypes (that we want to preserve)
    const otherEnergyTypeHazards = preSelectedHazards.filter(
      hazard => energyType && hazard.energyType !== energyType
    );

    // Combine both selected arrays for current energy type
    const currentEnergyTypeHazards = [
      ...selectedHighEnergyHazards.filter(hazard => 
        !energyType || hazard.energyType === energyType
      ),
      ...selectedOtherHazards.filter(hazard => 
        !energyType || hazard.energyType === energyType
      ),
    ];

    // Combine current energy type selections with preserved selections from other energy types
    const allSelectedHazards = [...currentEnergyTypeHazards, ...otherEnergyTypeHazards];

    // Process each hazard
    const result = allSelectedHazards.map(hazard => {
      // Check if this hazard already exists in preSelectedHazards
      const existingHazard = preSelectedHazards.find(h => h.id === hazard.id);
      
      if (existingHazard && existingHazard.selectedControlIds) {
        // Keep existing control selections for hazards that were already selected
        return {
          ...hazard,
          selectedControlIds: existingHazard.selectedControlIds,
          // Preserve the controls array that contains ALL available controls
          controls: hazard.controls || existingHazard.controls || [],
        };
      }
      
      // For newly added hazards, always initialize with empty selectedControlIds array
      // but preserve the controls array that contains ALL available controls
      return {
        ...hazard,
        selectedControlIds: [], // ALWAYS empty for new hazards
        controls: hazard.controls || [], // Preserve all available controls
      };
    });

    if (manuallyAddedHazards) {
      manuallyAddedHazards(result);
    }
    handleModalClose();
  };

  const handleModalClose = () => {
    setAddHazardsModalOpen(false);
    setSearchTerm("");
    setShowUserInput(false);
  };

  return (
    <Modal
      title={energyType ? "" : "Add Hazards"}
      isOpen={addHazardsModalOpen}
      closeModal={handleModalClose}
      size="lg"
      className="max-h-[80vh] overflow-auto"
    >
      <div className="flex flex-col pr-1">
        {energyType ? (
          <div className="flex gap-4 mb-6 -mt-9 w-1/2">
            <div
              className="w-14 h-14 rounded-xl flex items-center justify-around"
              style={{
                backgroundColor: ENERGY_TYPE_COLOR[energyType],
              }}
            >
              <Image
                src={require(`public/assets/CWF/EnergyWheel/${energyType.toLocaleLowerCase()}.svg`)}
                alt={energyType}
                width={44}
                height={44}
              />
            </div>
            <div className="flex flex-col justify-between py-1 h-14">
              <span className="capitalize font-bold">
                {energyType.toLocaleLowerCase()}
              </span>
              <span>Select hazards that apply</span>
            </div>
          </div>
        ) : (
          <HazardsTabs
            activeTab={activeTab}
            setActiveTab={setActiveTab}
            selectedHighEnergyHazards={selectedHighEnergyHazards}
            selectedOtherHazards={selectedOtherHazards}
            subTitle={subTitle}
          />
        )}

        {activeTab === "highEnergy" && (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {highEnergyHazards.map((hazard: Hazards) => (
              <div
                key={hazard.id}
                className={cx(
                  "border rounded-lg p-4 cursor-pointer flex items-center border-none bg-brand-gray-10",
                  isHighEnergyHazardSelected(hazard.id) &&
                    "bg-brand-urbint-10 border-brand-urbint-30 box-border ring-1 ring-brand-urbint-40"
                )}
                onClick={() => handleHighEnergyHazardSelect(hazard)}
              >
                <div className="flex-shrink-0 mr-3">
                  {hazard.imageUrl ? (
                    <Image
                      src={hazard.imageUrl}
                      alt={hazard.name}
                      className="w-8 h-8"
                      width={32}
                      height={32}
                    />
                  ) : (
                    <div className="w-8 h-8 bg-gray-200 rounded-full"></div>
                  )}
                </div>
                <div className="flex-grow">
                  <CaptionText
                    className={cx(
                      "text-sm font-semibold",
                      isHighEnergyHazardSelected(hazard.id) &&
                        "text-brand-urbint-40"
                    )}
                  >
                    {hazard.name}
                  </CaptionText>
                </div>
                {isHighEnergyHazardSelected(hazard.id) && (
                  <Icon
                    name={"check_bold"}
                    className="ml-0 pointer-events-none w-6 h-6 text-xl leading-none text-brand-urbint-40"
                  />
                )}
              </div>
            ))}
          </div>
        )}
        <div className="mt-6">
          <h4 className="font-medium mb-3 text-lg">
            Other
            {energyType ? (
              <span className="capitalize">{` ${energyType.toLowerCase()}`}</span>
            ) : (
              ""
            )}{" "}
            Hazards
          </h4>
          <div className="relative mb-4">
            <Icon
              name={"search"}
              className="absolute m-2.5 pointer-events-none w-6 h-6 text-xl leading-none text-neutral-shade-58"
            />
            <input
              type="search"
              className="block w-full p-2.5 pl-10 text-sm border border-gray-300 rounded-lg"
              placeholder="Search for hazards"
              value={searchTerm}
              onChange={e => setSearchTerm(e.target.value)}
            />
          </div>

          <div className="max-h-[16.5vh] overflow-auto border rounded-lg">
            {filteredOtherHazards.map((hazard: Hazards, index: number) => (
              <div
                key={hazard.id}
                className={cx(
                  "px-1.5 py-2 cursor-pointer flex items-center gap-2",
                  index !== filteredOtherHazards.length - 1 && "border-b",
                  isOtherHazardSelected(hazard.id) && "bg-brand-urbint-10"
                )}
                onClick={() => handleOtherHazardSelect(hazard)}
              >
                <Icon
                  name={"check_bold"}
                  className={cx(
                    "ml-0 pointer-events-none w-6 h-6 text-xl leading-none",
                    isOtherHazardSelected(hazard.id)
                      ? "visible text-brand-urbint-40"
                      : "invisible"
                  )}
                />
                <div className="flex-grow">
                  <CaptionText
                    className={cx(
                      "text-tiny font-semibold",
                      isOtherHazardSelected(hazard.id) && "text-brand-urbint-40"
                    )}
                  >
                    {hazard.name}
                  </CaptionText>
                </div>
              </div>
            ))}
              <div className="px-1.5 py-2  flex items-center gap-2 border text-tiny font-semibold">User Added </div>
            {/* User added hazards */}
            {userAddedHazards
              .filter(hazard => !energyType || hazard.energyType === energyType)
              .map((hazard: Hazards) => (
                <div
                  key={hazard.id}
                  className={cx(
                    "px-1.5 py-2 cursor-pointer flex items-center gap-2",
                    "border-b",
                    isOtherHazardSelected(hazard.id) && "bg-brand-urbint-10"
                  )}
                  onClick={() => handleUserAddedHazardSelect(hazard)}
                >
                  <Icon
                    name={"check_bold"}
                    className={cx(
                      "ml-0 pointer-events-none w-6 h-6 text-xl leading-none",
                      isOtherHazardSelected(hazard.id)
                        ? "visible text-brand-urbint-40"
                        : "invisible"
                    )}
                  />
                  <div className="flex-grow">
                    <CaptionText
                      className={cx(
                        "text-tiny font-semibold",
                        isOtherHazardSelected(hazard.id) && "text-brand-urbint-40"
                      )}
                    >
                      {hazard.name}
                    </CaptionText>
                  </div>
                </div>
              ))}
            
           
          </div>
           {/* "Other" option to add custom hazard */}
            <AddOtherComponent 
            onAdd={handleAddUserHazard} 
            showOther={showUserInput} 
            setShowOther={setShowUserInput} 
            placeholder="Please enter new hazard name"/>

            
        </div>
      </div>

      <div className="flex justify-end gap-2 pt-4 border-t mt-6">
        <ButtonRegular label="Cancel" onClick={handleModalClose} />
        <ButtonPrimary
          label="Add Hazards"
          onClick={handleSave}
          disabled={
            selectedHighEnergyHazards.length === 0 &&
            selectedOtherHazards.length === 0
          }
        />
      </div>
    </Modal>
  );
};

export default HazardsModal;