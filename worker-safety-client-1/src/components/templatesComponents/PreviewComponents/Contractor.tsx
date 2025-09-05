import type {
  UserFormMode,
  ApiDetails,
  DropDownValue,
} from "@/components/templatesComponents/customisedForm.types";
import type { ResponseOption } from "@/components/dynamicForm/dropdown.types";
import { gql, useQuery } from "@apollo/client";
import { BodyText, ComponentLabel } from "@urbint/silica";
import useTemplateStore from "@/pages/store/useTemplateStore";
import DropDown from "./DropDown";

interface Contractor {
  id: string;
  name: string;
}

type ContractorFieldProps = {
  content: {
    type: string;
    properties: {
      title: string;
      is_mandatory: boolean;
      hint_text?: string;
      api_details: ApiDetails;
      user_value: string[] | null;
      include_in_widget?: boolean;
    };
    id?: string;
  };
  mode: UserFormMode;
  inSummary?: boolean;
  onChange: (value: DropDownValue) => void;
};

export const RenderContractorInSummary = (props: {
  properties: {
    title: string;
    is_mandatory: boolean;
    hint_text?: string;
    api_details: ApiDetails;
    user_value: string[] | null;
  };
  localValue: {
    label: string;
    value: string;
  }[];
}): JSX.Element => {
  const { properties, localValue } = props;

  return (
    <div className="flex gap-2 flex-col">
      <ComponentLabel className="text-sm font-semibold cursor-auto">
        {properties.title}
      </ComponentLabel>
      <BodyText className="text-base">{localValue[0].label}</BodyText>
    </div>
  );
};

const ContractorField = ({
  content,
  mode,
  inSummary,
  onChange,
}: ContractorFieldProps) => {
  const { projectContractorId } = useTemplateStore();

  const { data, loading } = useQuery<{ contractors: Contractor[] }>(
    gql(content.properties.api_details.request.query as string)
  );

  const contractors = data?.contractors || [];

  const dropdownContent = {
    type: content.type,
    id: content.id,
    properties: {
      title: content.properties.title,
      is_mandatory: content.properties.is_mandatory,
      hint_text: content.properties.hint_text || "",
      api_details: content.properties.api_details,
      options: contractors.map(contractor => ({
        value: contractor.id,
        label: contractor.name,
      })),
      response_option: "manual_entry" as ResponseOption,
      multiple_choice: false,
      include_other_option: false,
      include_NA_option: false,
      include_other_input_box: false,
      user_other_value: null,
      comments_allowed: false,
      attachments_allowed: false,
      user_value:
        content.properties.user_value ??
        (projectContractorId ? [projectContractorId] : null),
      pre_population_rule_name: null,
      user_comments: null,
      user_attachments: null,
      include_in_widget: content.properties.include_in_widget,
    },
  };

  const handleOnChange = (value: DropDownValue) => {
    if (!value || value.length === 0) {
      onChange([]);
      return;
    }

    const selectedValue =
      Array.isArray(value) && value.length > 0
        ? typeof value[0] === "string"
          ? value[0]
          : value[0].value
        : null;

    if (!selectedValue) {
      onChange([]);
      return;
    }

    const selectedContractor = contractors.find(
      contractor => contractor.id === selectedValue
    );
    if (selectedContractor) {
      onChange([
        { value: selectedContractor.id, label: selectedContractor.name },
      ]);
    }
  };

  if (loading) {
    return <div className="text-sm text-gray-500">Loading contractors...</div>;
  }

  return (
    <DropDown
      content={dropdownContent}
      mode={mode}
      onChange={handleOnChange}
      inSummary={inSummary}
      returnLabelAndValue={true}
    />
  );
};

export default ContractorField;
