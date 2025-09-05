import type {
  ApiDetails,
  UserFormMode,
} from "@/components/templatesComponents/customisedForm.types";
import type { LibraryRegion } from "@/types/project/LibraryRegion";
import type { ResponseOption } from "@/components/dynamicForm/dropdown.types";
import { gql, useQuery } from "@apollo/client";
import { useContext } from "react";
import { BodyText, ComponentLabel } from "@urbint/silica";
import { CF_REDUCER_CONSTANTS } from "@/utils/customisedFormUtils/customisedForm.constants";
import CustomisedFromStateContext from "@/context/CustomisedDataContext/CustomisedFormStateContext";
import DropDown from "./DropDown";

type RegionProperties = {
  title: string;
  is_mandatory: boolean;
  hint_text?: string;
  api_details: ApiDetails;
  user_value: string[] | null;
  include_in_widget?: boolean;
};

type RegionFieldProps = {
  content: {
    type: string;
    properties: RegionProperties;
    id?: string;
  };
  mode: UserFormMode;
  inSummary?: boolean;
  onChange: (value: string) => void;
};

export const RenderRegionInSummary = ({
  properties,
  localValue,
}: {
  properties: RegionProperties;
  localValue: { name?: string; id?: string };
}) => {
  return (
    <div className="flex gap-2 flex-col">
      <ComponentLabel className="text-sm font-semibold cursor-auto">
        {properties.title}
      </ComponentLabel>
      <BodyText className="text-base">{localValue?.name}</BodyText>
    </div>
  );
};

const RegionField = ({
  content: {
    id,
    type,
    properties: {
      title,
      is_mandatory,
      hint_text,
      api_details,
      user_value,
      include_in_widget,
    },
  },
  mode,
  inSummary,
  onChange,
}: RegionFieldProps) => {
  const { data, loading } = useQuery<{ regionsLibrary: LibraryRegion[] }>(
    gql(api_details.request.query as string)
  );
  const { state, dispatch } = useContext(CustomisedFromStateContext)!;

  const regions = data?.regionsLibrary || [];

  const getRegionId = () => {
    const { work_package_data, metadata } = state.form;
    if (metadata?.region?.id) return metadata.region.id;
    if (work_package_data?.region?.id) return work_package_data.region.id;
    return null;
  };
  const regionId = getRegionId();

  const options = regions.map(region => ({
    value: region.id,
    label: region.name,
  }));

  // Compute the value to show in the dropdown
  let computedUserValue: string[] | null = null;
  if (options.length > 0) {
    if (regionId) {
      computedUserValue = [regionId];
    } else if (user_value !== null && user_value !== undefined) {
      computedUserValue = user_value;
    }
  }

  const handleChange = (value: any) => {
    if (value) {
      const selectedRegion = regions.find(region => region.id === value[0]);
      if (selectedRegion) {
        dispatch({
          type: CF_REDUCER_CONSTANTS.UPDATE_METADATA,
          payload: {
            ...state.form.metadata,
            region: {
              id: selectedRegion.id,
              name: selectedRegion.name,
            },
          },
        });
      }
      onChange(value);
    }
  };

  const dropdownContent = {
    type,
    id,
    properties: {
      title,
      is_mandatory,
      hint_text: hint_text || "",
      api_details,
      options,
      response_option: "manual_entry" as ResponseOption,
      multiple_choice: false,
      include_other_option: false,
      include_NA_option: false,
      include_other_input_box: false,
      user_other_value: null,
      comments_allowed: false,
      attachments_allowed: false,
      user_value: computedUserValue,
      pre_population_rule_name: null,
      user_comments: null,
      user_attachments: null,
      include_in_widget: include_in_widget,
    },
  };

  if (loading) {
    return <div className="text-sm text-gray-500">Loading regions...</div>;
  }

  return (
    <DropDown
      content={dropdownContent}
      mode={mode}
      onChange={handleChange}
      inSummary={inSummary}
    />
  );
};

export default RegionField;
