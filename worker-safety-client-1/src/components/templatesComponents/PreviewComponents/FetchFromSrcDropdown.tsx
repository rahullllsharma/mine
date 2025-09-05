import axiosRest from "@/api/restApi";
import type { FormState } from "@/components/dynamicForm/dropdown";
import ToastContext from "@/components/shared/toast/context/ToastContext";
import type { FetchFromSrcDropdownProps } from "@/components/templatesComponents/customisedForm.types";
import useRestMutation from "@/hooks/useRestMutation";
import { BodyText } from "@urbint/silica";
import type { AxiosError } from "axios";
import { useContext, useEffect, useState } from "react";
import DropDown from "./DropDown";

export const RenderFetchFromSrcDropdownInSummary = ({
  properties,
  localValue,
}: {
  properties: FormState;
  localValue: { name?: string; id?: string };
}) => {
  return (
    <div className="flex gap-2 flex-col">
      <BodyText className="text-base text-neutral-shade-100 font-semibold">
        {properties.title}
      </BodyText>
      <BodyText className="text-base text-neutral-shade-100">
        {localValue?.name}
      </BodyText>
    </div>
  );
};

const FetchFromSrcDropdown = ({
  content: { type, properties },
  mode,
  inSummary,
  onChange,
}: FetchFromSrcDropdownProps) => {
  const [fetchFromSrcDropdownOptions, setFetchFromSrcDropdownOptions] =
    useState<{ value: string; label: string }[]>([]);
  const [userOtherValue, setUserOtherValue] = useState<string>(
    properties.user_other_value || ""
  );

  const toastCtx = useContext(ToastContext);
  const { mutate: fetchFileImportedData, isLoading: isFetching } =
    useRestMutation({
      endpoint: properties.api_details?.endpoint as string,
      method: "get",
      axiosInstance: axiosRest,
      dtoFn: data => data,
      mutationOptions: {
        onSuccess: (responseData: any) => {
          const options = responseData.data.values.map((value: string) => ({
            value: value,
            label: value,
          }));
          options.sort((a: { label: string }, b: { label: string }) =>
            a.label.localeCompare(b.label)
          );
          setFetchFromSrcDropdownOptions(options);
        },
        onError: (error: AxiosError) => {
          console.log(error);
          toastCtx?.pushToast("error", "Error fetching data");
        },
      },
    });

  useEffect(() => {
    if (properties.api_details?.endpoint) {
      fetchFileImportedData({});
    }
  }, [properties.api_details?.endpoint]);

  const dropdownContent = {
    type: type,
    properties: {
      ...properties,
      hint_text: properties.hint_text || "",
      options: fetchFromSrcDropdownOptions as {
        value: string;
        label: string;
      }[],
      user_other_value: userOtherValue,
    },
  };

  const handleDropdownChange = (value: any) => {
    if (value && !value.includes("other")) {
      handleOtherValueChange("");
    }
    onChange(value);
  };

  const handleOtherValueChange = (value: string) => {
    setUserOtherValue(value);
    if (properties) {
      properties.user_other_value = value;
    }
  };

  if (isFetching) {
    return <div className="text-sm text-gray-500">Loading Dropdown...</div>;
  }

  return (
    <DropDown
      content={dropdownContent}
      mode={mode}
      onOtherValueChange={handleOtherValueChange}
      onChange={handleDropdownChange}
      inSummary={inSummary}
      returnLabelAndValue={false}
    />
  );
};

export default FetchFromSrcDropdown;
