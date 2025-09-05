import type { Hazards } from "@/components/templatesComponents/customisedForm.types";
import ButtonRegular from "@/components/shared/button/regular/ButtonRegular";
import ButtonPrimary from "@/components/shared/button/primary/ButtonPrimary";

type BottomSectionProps = {
  handleClose: () => void;
  handlePrimaryClick: () => void;
  selectedRecommendedHazards: Hazards[];
};

const BottomSectionHazardsModal = ({
  handleClose,
  handlePrimaryClick,
  selectedRecommendedHazards,
}: BottomSectionProps) => {
  return (
    <div className="flex justify-end gap-2 pt-4 border-t mt-6">
      <ButtonRegular label="Cancel" onClick={handleClose} />
      <ButtonPrimary
        label={
          selectedRecommendedHazards.length
            ? "Confirm Updates"
            : "Skip Recommendation"
        }
        onClick={handlePrimaryClick}
      />
    </div>
  );
};

export default BottomSectionHazardsModal;
