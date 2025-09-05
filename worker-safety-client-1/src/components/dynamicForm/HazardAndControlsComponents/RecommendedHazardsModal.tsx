import type { Hazards } from "@/components/templatesComponents/customisedForm.types";
import Image from "next/image";
import { CaptionText, Icon } from "@urbint/silica";
import { useState } from "react";
import cx from "classnames";
import Button from "@/components/shared/button/Button";
import Modal from "@/components/shared/modal/Modal";
import { useFormRendererContext } from "@/components/templatesComponents/FormPreview/Components/FormRendererContext";
import { ENERGY_TYPE_COLORS } from "@/components/templatesComponents/customisedForm.types";
import BottomSectionHazardsModal from "./BottomSectionHazardsModal";

const RecommendedHazardsModal = ({
  isOpen,
  setOpen,
  save,
  manuallyAddHazardsHandler,
  subTitle,
}: {
  isOpen: boolean;
  setOpen: React.Dispatch<React.SetStateAction<boolean>>;
  save: () => void;
  manuallyAddHazardsHandler: (hazards: Hazards[]) => void;
  subTitle: string;
}) => {
  const { getTaskHazardsMapping, selectedHazards } = useFormRendererContext();
  const [selectedRecommendedHazards, setSelectedRecommendedHazards] = useState<
    Hazards[]
  >([]);

  //Adds/removes recommended hazards from the selection list
  const handleRecommendedHazardClick = (hazard: Hazards) => () => {
    if (isHazardSelected(hazard)) {
      setSelectedRecommendedHazards(
        selectedRecommendedHazards.filter(current => current.id !== hazard.id)
      );
    } else {
      setSelectedRecommendedHazards([...selectedRecommendedHazards, hazard]);
    }
  };

  //closes modal and resets selected hazard list
  const handleClose = () => {
    setOpen(false);
    setSelectedRecommendedHazards([]);
  };

  //handles clicking the footer button.
  const handlePrimaryClick = () => {
    if (selectedRecommendedHazards.length === 0) {
      save();
    } else {
      manuallyAddHazardsHandler([
        ...selectedHazards,
        ...selectedRecommendedHazards,
      ]);
    }
    handleClose();
  };

  //determines whether a hazard is currently selected
  const isHazardSelected = (hazard: Hazards) =>
    selectedRecommendedHazards.some(current => hazard.id === current.id);

  return (
    <Modal
      title={`Recommended ${subTitle || "High Energy Hazards"}`}
      subtitle=""
      isOpen={isOpen}
      closeModal={handleClose}
      dismissable={true}
      size="lg"
    >
      <CaptionText className="text-base mb-4">
        Review additional {subTitle || "High Energy Hazards"} that may be
        present for this job. Select and confirm all that apply:
      </CaptionText>
      <div className="flex flex-col  max-h-[75vh] overflow-auto sm:max-h-[65vh] custom-mobile-max-height">
        {Object.entries(getTaskHazardsMapping()).map(([taskName, hazards]) => (
          <div
            key={taskName}
            className="bg-white shadow-md rounded-lg mb-6 p-4"
            style={{
              borderLeft: `10px solid ${
                hazards[0]?.energyType
                  ? ENERGY_TYPE_COLORS[hazards[0].energyType]
                  : "#CCCCCC"
              }`,
            }}
          >
            <h2 className="text-xl font-bold text-gray-800 h-16">{taskName}</h2>
            <div className="flex flex-wrap gap-3 flex-col items-start">
              {hazards.map(hazard => (
                <Button
                  key={hazard.id}
                  onClick={handleRecommendedHazardClick(hazard)}
                  className={cx(
                    "bg-brand-gray-10 w-full items-start flex gap-5  py-2 px-4 text-neutrals-secondary font-semibold rounded-lg",
                    isHazardSelected(hazard) &&
                      "bg-brand-urbint-10 ring-brand-urbint-30 ring"
                  )}
                  controlStateClass="h-10 justify-between w-full"
                >
                  <div className="flex items-center gap-2.5">
                    <Image
                      src={hazard.imageUrl || ""}
                      alt={hazard.name}
                      height={40}
                      width={40}
                    />
                    <span className="overflow-auto">{hazard.name}</span>
                  </div>
                  {isHazardSelected(hazard) ? (
                    <Icon
                      name={"check_bold"}
                      className="ml-0 pointer-events-none w-6 h-6 text-xl leading-none text-brand-urbint-40"
                    />
                  ) : (
                    ""
                  )}
                </Button>
              ))}
            </div>
          </div>
        ))}
      </div>
      <BottomSectionHazardsModal
        handleClose={handleClose}
        handlePrimaryClick={handlePrimaryClick}
        selectedRecommendedHazards={selectedRecommendedHazards}
      />
    </Modal>
  );
};
export default RecommendedHazardsModal;
