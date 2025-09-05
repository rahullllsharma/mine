import ButtonPrimary from "@/components/shared/button/primary/ButtonPrimary";
import ButtonRegular from "@/components/shared/button/regular/ButtonRegular";
import MultiSelect from "@/components/shared/inputSelect/multiSelect/MultiSelect";
import { useEffect, useState } from "react";

import Modal from "@/components/shared/modal/Modal";

type WorkType = {
  id: string;
  name: string;
  prepopulate?: boolean;
};

type SelectWorkTypeModalProps = {
  showModal: boolean;
  selectedTemplate?: {
    id: string;
    templateName: string;
    workTypes: WorkType[];
  } | null;
  closeModal: () => void;
  cancel: () => void;
  continueToForm: (
    selectedWorkTypes: { id: string; name: string; prepopulate?: boolean }[]
  ) => void;
};

export default function SelectWorkTypeModal({
  showModal,
  selectedTemplate,
  closeModal,
  cancel,
  continueToForm,
}: SelectWorkTypeModalProps) {
  const [selectedWorkType, setSelectedWorkType] = useState<
    { id: string; name: string }[]
  >([]);

  useEffect(() => {
    if (selectedTemplate?.workTypes) {
      const preselectedWorkTypes = selectedTemplate.workTypes.filter(
        workType => workType.prepopulate === true
      );

      setSelectedWorkType(preselectedWorkTypes);
    }
  }, [selectedTemplate]);

  const onSelectOfMultiSelect = (
    items: readonly { id: string; name: string }[]
  ) => {
    setSelectedWorkType(items.map(item => ({ ...item, prepopulate: false })));
  };

  return (
    <>
      <Modal
        title="Select work type"
        size="lg"
        isOpen={showModal}
        closeModal={closeModal}
      >
        <div className="mb-3 border-b pb-4">
          <div className="mb-2 text-[15px]">
            <span className="font-semibold">
              {selectedTemplate?.templateName}
            </span>{" "}
            <span className=" text-gray-700">
              form supports multiple work types. Select the one(s) needed to
              filter the tasks, site conditions, and hazards available.
            </span>
          </div>
          <div className="text-gray-800 text-[15px] mt-4 mb-1">Work Types</div>
          <MultiSelect
            options={selectedTemplate?.workTypes || []}
            isClearable={true}
            closeMenuOnSelect={false}
            onSelect={option => onSelectOfMultiSelect(option)}
            value={selectedWorkType}
          />
        </div>

        <div className="flex justify-end gap-3">
          <ButtonRegular label="Cancel" className="border" onClick={cancel} />
          <ButtonPrimary
            label={`Continue`}
            onClick={() => continueToForm(selectedWorkType)}
            disabled={selectedWorkType.length === 0}
          />
        </div>
      </Modal>
    </>
  );
}
