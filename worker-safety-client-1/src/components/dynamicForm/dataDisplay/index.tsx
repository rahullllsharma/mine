import React, { useEffect, useState } from "react";
import { v4 as uuidv4 } from "uuid";
import Modal from "@/components/shared/modal/Modal";
import FieldTextEditor from "@/components/shared/field/fieldTextEditor/FieldTextEditor";
import ButtonPrimary from "@/components/shared/button/primary/ButtonPrimary";
import ButtonRegular from "@/components/shared/button/regular/ButtonRegular";

export type DataDisplayModalProps = {
  isOpen: boolean;
  onClose: () => void;
  onAdd: (value: any) => void;
  content?: any;
};

export function DataDisplayModal({
  isOpen,
  onClose,
  onAdd,
  content,
}: DataDisplayModalProps) {
  const [value, setValue] = useState<string>(content?.properties?.data);

  useEffect(() => {
    setValue(content?.properties?.data);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isOpen]);

  const handleOnChange = (latest: string) => {
    setValue(latest);
  };

  const handleAdd = () => {
    const payload = content
      ? { ...content, properties: { ...content.properties, data: value } }
      : {
          type: "rich_text_editor",
          properties: { data: value },
          id: uuidv4(),
        };
    onAdd(payload);
    handleClose();
  };

  const handleClose = () => {
    onClose();
    setValue("");
  };

  const hasContent = (htmlContent: string): boolean => {
    if (!htmlContent || htmlContent.trim() === "") return false;
    const textContent = htmlContent
      .replace(/<[^>]*>/g, "")
      .replace(/&nbsp;/g, " ")
      .replace(/&amp;/g, "&")
      .replace(/&lt;/g, "<")
      .replace(/&gt;/g, ">")
      .replace(/&quot;/g, '"')
      .trim();

    if (textContent.length > 0) return true;

    const hasMedia = /<img|<video|<audio|<iframe|<embed|<object/i.test(
      htmlContent
    );
    if (hasMedia) return true;

    const hasStructure = /<table|<ul|<ol|<li|<hr/i.test(htmlContent);
    if (hasStructure) return true;

    return false;
  };

  const isAddDisabled = !hasContent(value || "");

  return (
    <Modal
      title="Add data"
      isOpen={isOpen}
      closeModal={onClose}
      size="xl"
      dismissable
    >
      <FieldTextEditor value={value} onChange={handleOnChange} />
      <Foooter
        onAdd={handleAdd}
        onClose={handleClose}
        disabled={isAddDisabled}
      />
    </Modal>
  );
}

type FooterProps = {
  onAdd: () => void;
  onClose: () => void;
  disabled?: boolean;
};
export const Foooter = ({ onAdd, onClose, disabled }: FooterProps) => {
  const handleAdd = () => {
    onAdd();
  };
  return (
    <div className="flex self-end w-full pt-4 flex-row-reverse m-t-4 border-t-2 border-solid">
      <ButtonPrimary label={"Add"} onClick={handleAdd} disabled={disabled} />
      <ButtonRegular className="mr-2" label="Cancel" onClick={onClose} />
    </div>
  );
};
