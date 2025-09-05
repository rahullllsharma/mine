import type { RadioGroupOption } from "@/components/shared/radioGroup/RadioGroup";
import type { UserFormMode } from "../templatesComponents/customisedForm.types";
import React, { useMemo, useState, useContext } from "react";
import { useMutation } from "@apollo/client";
import { InputRaw } from "@/components/forms/Basic/Input";
import FieldRadioGroup from "@/components/shared/field/fieldRadioGroup/FieldRadioGroup";
import * as UploadButton from "@/components/forms/Basic/UploadButton/UploadButton";
import { Foooter, RepeatSectionContext } from "@/components/dynamicForm/index";
import FileUploadPolicies from "@/graphql/queries/fileUploadPolicies.gql";
import { buildUploadFormData, upload } from "@/components/upload/utils";
import { prePopulationOptions } from "@/utils/customisedFormUtils/customisedForm.constants";
import { WidgetCheckbox } from "@/components/dynamicForm/WidgetCheckbox";
import Button from "../shared/button/Button";
import { Checkbox } from "../forms/Basic/Checkbox";

type ChoiceType = "single_choice" | "multiple_choice";
type ResponseOption = "manual_entry" | "fetch" | "image";

export interface Option {
  value: string;
  label: string;
  image_url?: string;
}

export interface FormState {
  title: string;
  choice_type: ChoiceType;
  response_option: ResponseOption;
  options: Option[];
  include_other_option: boolean;
  include_NA_option: boolean;
  is_mandatory: boolean;
  comments_allowed: boolean;
  attachments_allowed: boolean;
  include_in_widget: boolean;
  defaultValue?: string[];
  user_value: string[] | null;
  pre_population_rule_name: null;
  user_comments: string | null;
  user_attachments: File[] | null;
}

const choices: RadioGroupOption[] = [
  { id: 1, value: "single_choice", description: "Single" },
  { id: 2, value: "multiple_choice", description: "Multiple" },
];

const responseOptions: RadioGroupOption[] = [
  { id: 1, value: "manual_entry", description: "Manually entry" },
  { id: 2, value: "fetch", description: "Fetch from source" },
  { id: 3, value: "image", description: "Add image as response" },
];

// OptionComponent.js or OptionComponent.jsx
interface OptionProps {
  option: Option;
  index: number;
  responseOption: ResponseOption;
  onRemove: (index: number) => void;
  onOptionChange: (option: Option) => void;
  onImageUpload: (option: Option, file: File) => void;
  disabled?: boolean;
}

const uploadButtonConfigs: UploadButton.UploadButtonConfigs = {
  icon: "image_alt",
  label: "Add photos",
  isLoading: false,
  allowMultiple: false,
  allowedExtensions: ".apng,.avif,.gif,.jpg,.jpeg,.png,.svg,.webp",
  maxFileSize: 10 * 1024 * 1024, // 10 MB
};

const allowedExtensionsArray = uploadButtonConfigs.allowedExtensions
  .split(",")
  .map(ext => ext.trim().toLowerCase());

const OptionComponent: React.FC<OptionProps> = ({
  option,
  index,
  responseOption,
  onRemove,
  onOptionChange,
  onImageUpload,
  disabled,
}) => {
  const [uploadError, setUploadError] = useState<string | null>(null);

  const handleUpload = (file: File) => {
    const maxFileSize = uploadButtonConfigs.maxFileSize ?? 10 * 1024 * 1024;

    // Check file extension
    const fileExtension = file.name.split(".").pop()?.toLowerCase();
    const isValidExtension =
      fileExtension && allowedExtensionsArray.includes(`.${fileExtension}`);

    if (!isValidExtension) {
      setUploadError(
        "Invalid file type. Please upload a valid image (APNG, AVIF, GIF, JPG/JPEG, PNG, SVG, WEBP)."
      );
      return;
    }

    // Check file size
    if (file.size > maxFileSize) {
      setUploadError("File size exceeds 10 MB. Please select a smaller file.");
      return;
    }

    // Clear error and proceed with upload
    setUploadError(null);
    onImageUpload(option, file);
  };

  switch (responseOption) {
    case "manual_entry":
      return (
        <div className="flex flex-col">
          {option.value !== "other" && option.value !== "na" ? (
            <div className="flex self-end" style={{ marginBottom: -20 }}>
              <Button
                label="Remove Option"
                iconStart="minus_circle_outline"
                className="text-sm md:text-sm text-neutral-shade-75 font-semibold mb-2 leading-normal"
                onClick={() => onRemove(index)}
                disabled={disabled}
              />
            </div>
          ) : null}
          <InputRaw
            label={`Option ${index + 1}*`}
            placeholder="Option label"
            value={option.label}
            onChange={value =>
              onOptionChange({ value: option.value, label: value })
            }
            disabled={disabled}
          />
        </div>
      );
    case "fetch":
      return null;
    case "image":
      return (
        <div className="flex flex-col">
          <div className="flex justify-between mb-4">
            <label className="md:text-sm text-neutral-shade-75 font-semibold mb-2 leading-normal">{`Option ${
              index + 1
            }*`}</label>
            <Button
              label="Remove Option"
              iconStart="minus_circle_outline"
              className="text-sm md:text-sm text-neutral-shade-75 font-semibold mb-2 leading-normal"
              onClick={() => onRemove(index)}
              disabled={disabled}
            />
          </div>

          {option.image_url ? (
            <div className="flex justify-between gap-4">
              <img
                src={option.image_url as string}
                alt="Selected"
                height={60}
                width={60}
              />
              <InputRaw
                label={`Caption *`}
                placeholder=""
                value={option.label}
                onChange={value =>
                  onOptionChange({
                    value: option.value,
                    label: value,
                    image_url: option.image_url,
                  })
                }
                disabled={disabled}
              />
            </div>
          ) : (
            <div className="flex justify-between align-middle">
              <div className="md:text-sm text-neutral-shade-75 leading-normal">
                APNG, AVIF, GIF, JPG/JPEG, PNG, SVG, or WEBP. Max file Size: 10
                MB
              </div>
              <UploadButton.View
                configs={uploadButtonConfigs}
                className="mt-2 md:mt-0"
                onUpload={e => handleUpload(e[0])}
              />
            </div>
          )}
          {uploadError && (
            <div className="text-red-500 text-sm">{uploadError}</div>
          )}
        </div>
      );
    default:
      return null;
  }
};

type Props = {
  initialState?: FormState;
  onAdd: (state: FormState) => void;
  onClose: () => void;
  disabled?: boolean;
  mode?: UserFormMode;
  onDataChange?: () => void;
};

const validateForm = (state: FormState) => {
  let valid = false;
  if (state.title && state.choice_type && state.response_option) {
    if (
      state.options.filter(
        o => o.label && (state.response_option === "image" ? o.image_url : true)
      ).length === state.options.length
    ) {
      valid = true;
    }
  }

  return valid;
};

const FormComponent = (props: Props): JSX.Element => {
  const [formState, setFormState] = useState<FormState>(
    props.initialState || {
      title: "",
      choice_type: "single_choice",
      response_option: "manual_entry",
      options: [{ value: "1", label: "" }],
      include_other_option: false,
      include_NA_option: false,
      is_mandatory: false,
      comments_allowed: false,
      attachments_allowed: false,
      include_in_widget: false,
      user_value: null,
      pre_population_rule_name: null,
      user_comments: null,
      user_attachments: null,
    }
  );
  const [generateFileUploadPolicies] = useMutation(FileUploadPolicies);
  const isRepeatableSection = useContext(RepeatSectionContext);

  const handleInputChange = (name: keyof FormState, value: any) => {
    setFormState(prevState => ({ ...prevState, [name]: value }));

    // Notify parent that data has been entered/changed
    if (props.onDataChange) {
      props.onDataChange();
    }

    if (name === "include_other_option") {
      if (value) {
        addOption({ value: "other", label: "Other" });
      } else {
        // find index of option where value is "other"
        // and remove it
        const index = formState.options.findIndex(o => o.value === "other");
        if (index !== -1) {
          removeOption(index);
        }
      }
    }
    if (name === "include_NA_option") {
      if (value) {
        addOption({ value: "na", label: "N/A" });
      } else {
        // find index of option where value is "na"
        // and remove it
        const index = formState.options.findIndex(o => o.value === "na");
        if (index !== -1) {
          removeOption(index);
        }
      }
    }
  };

  const addOption = (_options?: { value?: string; label?: string }) => {
    const newOption = {
      value: _options?.value || String(formState.options.length + 1),
      label: _options?.label || "",
    };
    handleInputChange("options", [...formState.options, newOption]);
  };

  const removeOption = (index: number) => {
    const updatedOptions = formState.options.filter((_, i) => i !== index);
    handleInputChange("options", updatedOptions);
  };

  const handleOptionChange = async (updatedOption: Option) => {
    try {
      const updatedOptions = formState.options.map(option =>
        option.value === updatedOption.value ? updatedOption : option
      );
      handleInputChange("options", updatedOptions);
    } catch (e) {
      console.error(e);
    }
  };

  const handleImageUpload = async (option: Option, file: File) => {
    try {
      const { data } = await generateFileUploadPolicies({
        variables: {
          count: 1,
        },
      });
      await upload(
        data.fileUploadPolicies[0].url,
        buildUploadFormData(data.fileUploadPolicies[0], file as File)
      );
      const updatedOptions = formState.options.map((o: Option) =>
        o.value === option.value
          ? { ...o, image_url: data.fileUploadPolicies[0].signedUrl }
          : o
      );
      handleInputChange("options", updatedOptions);
    } catch (e) {
      console.error(e);
    }
  };

  const isValidForm = useMemo(() => validateForm(formState), [formState]);

  const areOptionsValid = useMemo(() => {
    return formState.options && formState.options.length > 0
      ? formState.options.every(option => option.label.trim().length > 0)
      : false;
  }, [formState.options]);

  return (
    <>
      <div className="flex flex-col p-4 gap-4">
        <InputRaw
          label="Question *"
          placeholder="Enter your question"
          value={formState.title}
          onChange={e => handleInputChange("title", e)}
          disabled={props.disabled}
        />

        <FieldRadioGroup
          label="Choice Option"
          options={choices}
          defaultOption={choices.find(c => c.value === formState.choice_type)}
          onSelect={choice => handleInputChange("choice_type", choice)}
          readOnly={props.disabled}
        />

        <FieldRadioGroup
          label="Response Option"
          options={responseOptions}
          defaultOption={responseOptions.find(
            r => r.value === formState.response_option
          )}
          onSelect={response => handleInputChange("response_option", response)}
          readOnly={props.disabled}
        />
        {!isRepeatableSection && (
          <FieldRadioGroup
            label="Pre Population"
            options={prePopulationOptions}
            defaultOption={
              prePopulationOptions.find(
                option => option.value === formState.pre_population_rule_name
              ) || prePopulationOptions[0]
            }
            onSelect={response => {
              handleInputChange(
                "pre_population_rule_name",
                response === "None" ? null : response
              );
            }}
            readOnly={props.disabled}
          />
        )}

        {formState.options && formState.options.length > 0 && (
          <div className="border-gray-200 border-b divide-brand-gray-2 pb-4 flex flex-col gap-4">
            {formState.options.map((option, index) => (
              <OptionComponent
                key={option.value}
                option={option}
                index={index}
                responseOption={formState.response_option}
                onRemove={removeOption}
                onOptionChange={handleOptionChange}
                onImageUpload={handleImageUpload}
                disabled={props.disabled}
              />
            ))}
          </div>
        )}

        <Button
          label="Add Option"
          iconStart="plus_square"
          className="text-sm md:text-sm text-neutral-shade-75 font-semibold mb-2 leading-normal self-end"
          onClick={addOption as any}
          disabled={props.disabled}
        />

        <div className="border-gray-200 border-b divide-brand-gray-2 pb-4 flex gap-4">
          <Checkbox
            checked={formState.include_other_option}
            onClick={() => {
              handleInputChange(
                "include_other_option",
                !formState.include_other_option
              );
            }}
            disabled={props.disabled}
          >
            <span className="text-brand-gray-80 text-sm">
              {"Include 'Other' in response"}
            </span>
          </Checkbox>
          <Checkbox
            checked={formState.include_NA_option}
            onClick={() =>
              handleInputChange(
                "include_NA_option",
                !formState.include_NA_option
              )
            }
            disabled={props.disabled}
          >
            <span className="text-brand-gray-80 text-sm">
              {"Include 'N/A' in response"}
            </span>
          </Checkbox>
        </div>

        <div className="flex justify-between">
          <Checkbox
            checked={formState.is_mandatory}
            onClick={() =>
              handleInputChange("is_mandatory", !formState.is_mandatory)
            }
            disabled={props.disabled}
          >
            <span className="text-brand-gray-80 text-sm">Mandatory</span>
          </Checkbox>
          <Checkbox
            checked={formState.comments_allowed}
            onClick={() =>
              handleInputChange("comments_allowed", !formState.comments_allowed)
            }
            disabled={props.disabled}
          >
            <span className="text-brand-gray-80 text-sm">Comments</span>
          </Checkbox>
          <Checkbox
            checked={formState.attachments_allowed}
            onClick={() =>
              handleInputChange(
                "attachments_allowed",
                !formState.attachments_allowed
              )
            }
            disabled={props.disabled}
          >
            <span className="text-brand-gray-80 text-sm">Attachment</span>
          </Checkbox>
          <WidgetCheckbox
            checked={formState.include_in_widget}
            disabled={props.disabled}
            onToggle={value => handleInputChange("include_in_widget", value)}
          />
        </div>
      </div>
      <Foooter
        onAdd={() => props.onAdd(formState)}
        onClose={props.onClose}
        disabled={
          !isValidForm ||
          props.disabled ||
          formState.title.trim().length === 0 ||
          !areOptionsValid
        }
        mode={props.mode}
        hasDataEntered={
          formState.title.trim().length > 0 || formState.options.length > 0
        }
      />
    </>
  );
};

export default FormComponent;
