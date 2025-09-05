import type {
  ControlModalProps,
  Controls,
} from "../../templatesComponents/customisedForm.types";
import { CaptionText, Icon } from "@urbint/silica";
import { useEffect, useState } from "react";

import cx from "classnames";
import Modal from "@/components/shared/modal/Modal";
import ButtonPrimary from "../../shared/button/primary/ButtonPrimary";
import ButtonRegular from "../../shared/button/regular/ButtonRegular";
import AddOtherComponent from "./AddOtherComponent";

function ControlModal({
  controlModalOpen,
  preSelectedControls,
  hazardsControlList,
  selectedHazardId,
  onAddControl,
  onClose,
}: ControlModalProps) {
  const [searchTerm, setSearchTerm] = useState("");
  const [showUserInput, setShowUserInput] = useState(false);
  const [userAddedControls, setUserAddedControls] = useState<Controls[]>([]);
  const [preSelectedControlsValues, setPreSelectedControlsValues] =
    useState<Controls[]>(preSelectedControls);

  // Reset and initialize state when modal opens
  useEffect(() => {
    if (controlModalOpen) {
      setPreSelectedControlsValues(preSelectedControls);
      const userAdded = preSelectedControls
        .filter(control => control.isUserAdded === true)
        .sort((a, b) => a.name.localeCompare(b.name));
      setUserAddedControls(userAdded);
    }
  }, [controlModalOpen, preSelectedControls]);

  const handleModalClose = () => {
    onClose();
    setSearchTerm("");
    setShowUserInput(false);
  };

  const handleControlSelect = (selectedControl: Controls) => {
    const isSelected = preSelectedControlsValues.some(
      value => value.id === selectedControl.id
    );

    if (isSelected) {
      setPreSelectedControlsValues(
        preSelectedControlsValues.filter(
          value => value.id !== selectedControl.id
        )
      );
    } else {
      setPreSelectedControlsValues([
        ...preSelectedControlsValues,
        selectedControl,
      ]);
    }
  };

  // Filter controls based on search term
  const filteredControls = hazardsControlList.filter(
    (control: Controls) =>
      !control.isUserAdded &&
      control.name.toLowerCase().includes(searchTerm.toLowerCase())
  );

  // Filter user-added controls based on search term
  const filteredUserControls = userAddedControls.filter((control: Controls) =>
    control.name.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const isControlSelected = (controlId: string) => {
    return preSelectedControlsValues.some(value => value.id === controlId);
  };

  const onAddOfUserControl = (newControl: {
    id: string;
    name: string;
    isUserAdded: boolean;
    isApplicable: boolean;
  }) => {
    // Create new control with required properties
    const newUserAddedControl: Controls = {
      ...newControl,
      isApplicable: false,
      selected: true,
    };

    // Add to user controls list
    setUserAddedControls(
      [...userAddedControls, newUserAddedControl].sort((a, b) =>
        a.name.localeCompare(b.name)
      )
    );
    setPreSelectedControlsValues([
      ...preSelectedControlsValues,
      newUserAddedControl,
    ]);
    setShowUserInput(false);
  };

  const handleSave = () => {
    onAddControl(preSelectedControlsValues, selectedHazardId);
    handleModalClose();
  };

  return (
    <>
      <Modal
        title={"Select Controls"}
        isOpen={controlModalOpen}
        closeModal={handleModalClose}
        size="lg"
        className="max-h-[100vh] overflow-auto"
      >
        <div className="">
          <div className="relative mb-4">
            <Icon
              name={"search"}
              className="absolute m-2.5 pointer-events-none w-6 h-6 text-xl leading-none text-neutral-shade-58"
            />
            <input
              type="search"
              className="block w-full p-2.5 pl-10 text-sm border border-gray-300 rounded-lg"
              placeholder="Search for controls"
              value={searchTerm}
              onChange={e => setSearchTerm(e.target.value)}
            />
          </div>

          <div className="max-h-[40vh] overflow-auto border rounded-lg">
            {filteredControls.length > 0 &&
              filteredControls.map((control: Controls, index: number) => (
                <div
                  key={control.id}
                  className={cx(
                    "px-1.5 py-2 cursor-pointer flex items-center gap-2",
                    index !== filteredControls.length - 1 && "border-b",
                    isControlSelected(control.id) && "bg-brand-urbint-10"
                  )}
                  onClick={() => handleControlSelect(control)}
                >
                  <Icon
                    name={"check_bold"}
                    className={cx(
                      "ml-0 pointer-events-none w-6 h-6 text-xl leading-none",
                      isControlSelected(control.id)
                        ? "visible text-brand-urbint-40"
                        : "invisible"
                    )}
                  />
                  <div className="flex-grow">
                    <CaptionText
                      className={cx(
                        "text-tiny font-semibold",
                        isControlSelected(control.id) && "text-brand-urbint-40"
                      )}
                    >
                      {control.name}
                    </CaptionText>
                  </div>
                </div>
              ))}

            {filteredUserControls.length > 0 && (
              <div className="px-1.5 py-2 flex items-center gap-2 border text-tiny font-semibold">
                User Added
              </div>
            )}
            {filteredUserControls.length > 0 &&
              filteredUserControls.map((control: Controls, index: number) => (
                <div
                  key={control.id}
                  className={cx(
                    "px-1.5 py-2 cursor-pointer flex items-center gap-2",
                    index !== filteredUserControls.length - 1 && "border-b",
                    isControlSelected(control.id) && "bg-brand-urbint-10"
                  )}
                  onClick={() => handleControlSelect(control)}
                >
                  <Icon
                    name={"check_bold"}
                    className={cx(
                      "ml-0 pointer-events-none w-6 h-6 text-xl leading-none",
                      isControlSelected(control.id)
                        ? "visible text-brand-urbint-40"
                        : "invisible"
                    )}
                  />
                  <div className="flex-grow">
                    <CaptionText
                      className={cx(
                        "text-tiny font-semibold",
                        isControlSelected(control.id) && "text-brand-urbint-40"
                      )}
                    >
                      {control.name}
                    </CaptionText>
                  </div>
                </div>
              ))}
          </div>

          <AddOtherComponent
            onAdd={onAddOfUserControl}
            showOther={showUserInput}
            placeholder="Please enter new control name"
            setShowOther={setShowUserInput}
          />
        </div>

        <div className="flex justify-end gap-2 pt-4 border-t mt-6">
          <ButtonRegular label="Cancel" onClick={handleModalClose} />
          <ButtonPrimary label="Add Control" onClick={handleSave} />
        </div>
      </Modal>
    </>
  );
}

export default ControlModal;
