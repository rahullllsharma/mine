import type { Insight, InsightFormInputs } from "@/types/insights/Insight";
import type { FormEvent } from "react";
import { isMatch } from "lodash-es";
import { useEffect, useState } from "react";
import { Controller, FormProvider, useForm } from "react-hook-form";
import ButtonPrimary from "@/components/shared/button/primary/ButtonPrimary";
import ButtonSecondary from "@/components/shared/button/secondary/ButtonSecondary";
import ButtonTertiary from "@/components/shared/button/tertiary/ButtonTertiary";
import Checkbox from "@/components/shared/checkbox/Checkbox";
import { FieldRules } from "@/components/shared/field/FieldRules";
import FieldInput from "@/components/shared/field/fieldInput/FieldInput";
import FieldTextArea from "@/components/shared/field/fieldTextArea/FieldTextArea";
import Modal from "@/components/shared/modal/Modal";
import { messages } from "@/locales/messages";

interface AddInsightModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (data: InsightFormInputs) => void;
  defaultValues?: Insight;
  onDelete: (id: string) => void;
  isSubmitting?: boolean;
}

const rules = {
  ...FieldRules.REQUIRED,
  ...FieldRules.NOT_ONLY_WHITESPACE,
  minLength: {
    value: 3,
    message: messages.minCharLength.replace("{value}", "3"),
  },
};

const rulesForUrl = {
  ...FieldRules.REQUIRED,
  ...FieldRules.URL,
};

const defaultFormValues = {
  name: "",
  url: "",
  description: "",
  visibility: true,
};

const AddInsightModal = ({
  isOpen,
  onClose,
  onSubmit,
  defaultValues,
  onDelete,
  isSubmitting = false,
}: AddInsightModalProps): JSX.Element => {
  const [isVisibilityChecked, setIsVisibilityChecked] = useState(true);

  const methods = useForm<InsightFormInputs>({
    mode: "onChange",
    defaultValues: {
      ...defaultFormValues,
    },
  });

  const { name, description, url, visibility } = methods.getValues();
  const { errors } = methods.formState;

  useEffect(() => {
    if (defaultValues && !isMatch(defaultValues, defaultFormValues)) {
      methods.setValue("name", defaultValues.name);
      methods.setValue("description", defaultValues.description);
      methods.setValue("url", defaultValues.url);
      setIsVisibilityChecked(defaultValues.visibility);
      methods.setValue("visibility", defaultValues.visibility);
    }

    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [defaultValues]);

  const closeModal = () => {
    onClose();
    /**
     * In case a form is closed with errors, RHF will keep the errors into the next modal.
     */
    methods.clearErrors();
    methods.reset();
  };

  return (
    <Modal
      isOpen={isOpen}
      closeModal={closeModal}
      title={`${defaultValues ? "Edit" : "Add"} Insight`}
    >
      <FormProvider {...methods}>
        <div className="flex flex-col gap-4">
          <Controller
            name="name"
            rules={rules}
            defaultValue={name}
            render={({ field }) => (
              <FieldInput
                {...field}
                htmlFor="name"
                id="name"
                label="Name"
                error={errors.name?.message}
                containerClassName="w-full sm:flex-1"
                placeholder="Type Report name"
                required
              />
            )}
          />
          <Controller
            name="url"
            rules={rulesForUrl}
            defaultValue={url}
            render={({ field }) => (
              <FieldInput
                {...field}
                htmlFor="url"
                id="url"
                label="Report URL"
                error={errors.url?.message}
                containerClassName="w-full sm:flex-1"
                placeholder="BI report URL"
                required
              />
            )}
          />
          <Controller
            name="description"
            defaultValue={description}
            render={({ field }) => (
              <FieldTextArea
                {...field}
                htmlFor="description"
                id="description"
                label="Description"
                error={errors.description?.message}
                className="w-full sm:flex-1"
                placeholder="Add brief description of report here"
              />
            )}
          />
          <p className="block text-tiny md:text-sm text-neutral-shade-75 font-semibold mb-2 leading-normal">
            Visibility
          </p>
          <Controller
            name="visibility"
            defaultValue={visibility}
            render={({ field }) => (
              <label className="flex items-center gap-3 hover:cursor-pointer">
                <Checkbox
                  {...field}
                  id="visibility"
                  checked={isVisibilityChecked}
                  onChange={(event: FormEvent<HTMLInputElement>) => {
                    /**
                     * Maintain RHF normal behavior
                     */
                    field.onChange(event);
                    methods.trigger("visibility");
                    setIsVisibilityChecked(prev => !prev);
                  }}
                />
                <span className="capitalize text-neutral-shade-100">
                  Visible
                </span>
              </label>
            )}
          />
          <footer className="flex justify-end gap-4 border-t border-gray-300 pt-4 pb-0 px-6 w-[calc(100%+48px)] -left-6 relative">
            {defaultValues ? (
              <ButtonSecondary
                label="Delete"
                className="mr-auto !text-system-error-40"
                onClick={() => {
                  onDelete(defaultValues.id);
                  closeModal();
                }}
              />
            ) : null}
            <ButtonTertiary label="Cancel" onClick={closeModal} />
            <ButtonPrimary
              label={defaultValues ? "Save Report" : "Add Report"}
              type="submit"
              onClick={methods.handleSubmit(data => {
                onSubmit(data);
                closeModal();
              })}
              loading={isSubmitting}
            />
          </footer>
        </div>
      </FormProvider>
    </Modal>
  );
};

export default AddInsightModal;
