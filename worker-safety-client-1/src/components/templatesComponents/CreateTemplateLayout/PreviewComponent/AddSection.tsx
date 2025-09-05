import { useEffect, useState } from "react";
import { Controller, FormProvider, useForm } from "react-hook-form";

import { BodyText } from "@urbint/silica";
import ButtonPrimary from "@/components/shared/button/primary/ButtonPrimary";
import ButtonTertiary from "@/components/shared/button/tertiary/ButtonTertiary";
import { FieldRules } from "@/components/shared/field/FieldRules";
import FieldInput from "@/components/shared/field/fieldInput/FieldInput";
import Modal from "@/components/shared/modal/Modal";
import { Toggle } from "@/components/forms/Basic/Toggle";
import style from "../createTemplateStyle.module.scss";

type AddSectionType = {
  initialName?: string;
  initialRepeatable?: boolean;
  setSectionName: (item: string, item1: boolean) => void;
  onCancel: () => void;
  toggleDisabled?: boolean;
};

const AddSectionComponent = ({
  initialName = "",
  initialRepeatable = false,
  setSectionName,
  onCancel,
  toggleDisabled = false,
}: AddSectionType) => {
  const [isOpen, setIsOpen] = useState(true);
  const [isMounted, setIsMounted] = useState(true);

  const rules = {
    ...FieldRules.REQUIRED,
    pattern: {
      value: /^[a-zA-Z0-9_&-]+(?:\s[a-zA-Z0-9_&-]*)*$/,
      message: "Invalid input",
    },
  };

  const methods = useForm<{ name: string }>({
    mode: "onChange",
    defaultValues: { name: initialName },
  });
  const { handleSubmit, reset } = methods;
  const { errors } = methods.formState;

  const onSubmit = (data: { name: string; is_repeatable: boolean }) => {
    setSectionName(data.name || "", data.is_repeatable || false);
    setIsOpen(false);
  };

  const onReset = () => {
    setIsOpen(false);
    onCancel();
  };

  useEffect(() => {
    return () => {
      setIsMounted(false); // Component is unmounting
    };
  }, []);

  useEffect(() => {
    if (!isOpen && !isMounted) {
      reset(); // Reset the form after closing and unmounting
    }
  }, [isOpen, isMounted, reset]);

  if (!isOpen) {
    return null; // Render null when the modal is closed
  }

  return (
    <div className={style.previewComponentParent__ctaSection}>
      <Modal title={"Section name"} isOpen={isOpen} closeModal={onReset}>
        <FormProvider {...methods}>
          <form onSubmit={handleSubmit(onSubmit)}>
            <div className="flex flex-col gap-6">
              <Controller
                name="name"
                rules={rules}
                render={({ field }) => (
                  <FieldInput
                    {...field}
                    htmlFor="name"
                    id="name"
                    label="Name"
                    error={errors.name?.message}
                    containerClassName="w-full sm:flex-1"
                    className={`focus:outline-none focus:border-blue-500 focus:ring-blue-500`}
                    placeholder=""
                    required
                  />
                )}
              />
              <Controller
                name="is_repeatable"
                defaultValue={initialRepeatable}
                render={({ field }) => (
                  <div className="flex items-center gap-2 justify-between">
                    <BodyText className="block text-tiny md:text-sm font-semibold leading-normal">
                      Is Repeatable
                    </BodyText>
                    <Toggle
                      checked={field.value}
                      onClick={() => {
                        if (!toggleDisabled) {
                          field.onChange(!field.value);
                        }
                      }}
                      disabled={toggleDisabled}
                    />
                  </div>
                )}
              />
              <footer className="flex justify-end gap-4 border-t border-gray-300 pt-4 pb-0 px-6 w-[calc(100%+48px)] -left-6 relative">
                <ButtonTertiary label="Cancel" onClick={onReset} />
                <ButtonPrimary label={"Add"} type="submit" />
              </footer>
            </div>
          </form>
        </FormProvider>
      </Modal>
    </div>
  );
};

export default AddSectionComponent;
