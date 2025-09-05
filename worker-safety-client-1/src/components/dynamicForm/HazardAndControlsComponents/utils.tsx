import { BodyText, CaptionText } from "@urbint/silica";
import BlankFieldTemplates from "../BlankFieldTemplates";
import Modal from "../../shared/modal/Modal";
import ButtonDanger from "../../shared/button/danger/ButtonDanger";
import ButtonRegular from "../../shared/button/regular/ButtonRegular";
import ButtonSecondary from "../../shared/button/secondary/ButtonSecondary";

interface HazardsCardBlankFieldProps {
  energyType?: string;
  subTitle?: string;
  addHazardHandler: (tab?: string) => void;
  readOnly?: boolean;
  inSummary?: boolean;
}
export type DeleteHazardModalProps = {
  isDeleteModalOpen: boolean;
  setIsDeleteModalOpen: (value: boolean) => void;
  setHazardToDelete: (value: string | null) => void;
  confirmDeleteHazard: () => void;
};

const HazardsBlankField = () => {
  return (
    <>
      <div className="text-xs text-neutral-600 mt-0.5 mb-4">
        <CaptionText>
          Select the tasks you were responsible for overseeing at this location.
        </CaptionText>
      </div>
      <BlankFieldTemplates />
    </>
  );
};

const HazardsCardBlankField = ({
  addHazardHandler,
  subTitle,
  energyType,
  readOnly,
  inSummary,
}: HazardsCardBlankFieldProps) => {
  const tab = energyType === "HIGH_ENERGY" ? "highEnergy" : "otherHazards";
  return (
    <div className="mb-4 mt-5 bg-gray-100 rounded p-3">
      <div className="flex items-center">
        <BodyText className="text-xl font-semibold mb-2">
          {energyType === "HIGH_ENERGY"
            ? subTitle || "High Energy Hazards"
            : "Other Hazards"}
        </BodyText>
        {!inSummary && (
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
      <div className="bg-white border rounded-lg p-4 px-8">
        {energyType === "HIGH_ENERGY" ? (
          <>
            <CaptionText className="font-semibold text-center text-md text-neutrals-secondary">
              Identify and Control {subTitle || "High Energy Hazards"}
            </CaptionText>
            <CaptionText className="text-center text-md text-neutrals-secondary">
              {subTitle} can cause serious injury or fatality. Add all
              applicable hazards and select the appropriate controls to
              eliminate, reduce, or mitigate the exposure.
            </CaptionText>
          </>
        ) : (
          <>
            <CaptionText className="font-semibold text-center text-md text-neutrals-secondary">
              Identify and Control Other Hazards
            </CaptionText>
            <CaptionText className="text-center text-md text-neutrals-secondary">
              Other hazards can result in incidents or injuries that require
              medical attention. Add all applicable hazards and select the
              appropriate controls to eliminate, reduce, or mitigate the
              exposure.
            </CaptionText>
          </>
        )}
      </div>
    </div>
  );
};

const DeleteHazardModal = ({
  isDeleteModalOpen,
  setIsDeleteModalOpen,
  setHazardToDelete,
  confirmDeleteHazard,
}: DeleteHazardModalProps) => {
  return (
    <Modal
      title="Delete Hazard"
      isOpen={isDeleteModalOpen}
      closeModal={() => {
        setIsDeleteModalOpen(false);
        setHazardToDelete(null);
      }}
      size="md"
    >
      <div className="mb-10">
        <BodyText className="text-neutral-shade-75">
          Are you sure you want to delete this hazard?
        </BodyText>
        <BodyText className="text-neutral-shade-75">
          This action cannot be undone.
        </BodyText>
      </div>
      <div className="flex justify-end gap-3">
        <ButtonRegular
          label="Cancel"
          onClick={() => {
            setIsDeleteModalOpen(false);
            setHazardToDelete(null);
          }}
        />
        <ButtonDanger label={`Confirm`} onClick={confirmDeleteHazard} />
      </div>
    </Modal>
  );
};

export { HazardsBlankField, HazardsCardBlankField, DeleteHazardModal };
