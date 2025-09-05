import type {
  CWFLocationType,
  FieldRendererProps,
} from "@/components/templatesComponents/customisedForm.types";
import { useRouter } from "next/router";
import { useContext } from "react";
import { ResponseOption } from "@/components/dynamicForm/dropdown.types";
import LocationInSummary from "@/components/dynamicForm/LocationComponent/LocationInSummary";
import CustomisedFromStateContext from "@/context/CustomisedDataContext/CustomisedFormStateContext";
import { CF_REDUCER_CONSTANTS } from "@/utils/customisedFormUtils/customisedForm.constants";
import CheckboxPreview from "./Checkbox";
import Choice, { RenderChoiceInSummary } from "./Choice";
import ContractorField, { RenderContractorInSummary } from "./Contractor";
import DateTime from "./DateTimeComponents/DateTime";
import DropDown, { RenderDropDownInSummary } from "./DropDown";
import Email, { RenderEmailInSummary } from "./Email";
import FetchFromSrcDropdown from "./FetchFromSrcDropdown";
import LocationInput from "./LocationInput";
import NumberText, { RenderNumberTextInSummary } from "./NumberText";
import PhoneNumber, { RenderPhoneNumberInSummary } from "./PhoneNumber";
import RegionField, { RenderRegionInSummary } from "./Region";
import Text, { RenderShortTextInSummary } from "./Text";
import TextArea, { RenderTextAreaInSummary } from "./TextArea";
import withAttachmentComment from "./WithAttachment";
import YesOrNo from "./YesOrNo";

const FieldRenderer = (props: FieldRendererProps): JSX.Element => {
  const { content, mode, inSummary } = props;
  const { state, dispatch } = useContext(CustomisedFromStateContext)!;
  const router = useRouter();

  const isWorkpackageForm = !!router.query.project && !!router.query.location;
  const isAdhocForm = !isWorkpackageForm;

  const OnChange = (value: any) => {
    dispatch({
      type: CF_REDUCER_CONSTANTS.FIELD_VALUE_CHANGE,
      payload: {
        parentData: props.activePageDetails,
        fieldData: { user_value: value, order: props.order },
        section: props.section,
      },
    });
  };

  switch (content.type) {
    case "input_phone_number":
      return inSummary ? (
        <RenderPhoneNumberInSummary
          properties={content.properties}
          localValue={content.properties.user_value}
        />
      ) : (
        <PhoneNumber
          content={content}
          mode={mode}
          onChange={OnChange}
          inSummary={inSummary}
        />
      );

    case "input_date_time":
      return (
        <DateTime
          content={content}
          mode={mode}
          onChange={OnChange}
          inSummary={inSummary}
        />
      );

    case "report_date":
      return (
        <DateTime
          content={content}
          mode={mode}
          onChange={val => OnChange(val)}
          withConfirmationDialog={!isAdhocForm}
          reportDate={true}
          inSummary={inSummary}
        />
      );
    case "contractor":
      return inSummary ? (
        <RenderContractorInSummary
          properties={content.properties}
          localValue={content.properties.user_value}
        />
      ) : (
        <ContractorField
          content={content}
          mode={mode}
          onChange={OnChange}
          inSummary={inSummary}
        />
      );
    case "dropdown":
      if (content.properties.response_option === ResponseOption.Fetch) {
        return inSummary ? (
          <RenderDropDownInSummary
            properties={content.properties}
            localValue={content.properties?.user_value}
          />
        ) : (
          <FetchFromSrcDropdown
            content={content}
            mode={mode}
            inSummary={inSummary}
            onChange={OnChange}
          />
        );
      } else {
        return inSummary ? (
          <RenderDropDownInSummary
            properties={content.properties}
            localValue={content.properties.user_value}
          />
        ) : (
          <DropDown content={content} mode={mode} onChange={OnChange} />
        );
      }

    case "yes_or_no":
      return (
        <YesOrNo
          content={content}
          mode={mode}
          onChange={OnChange}
          inSummary={inSummary}
        />
      );

    case "choice":
      return inSummary ? (
        <RenderChoiceInSummary
          properties={content.properties}
          localValue={content.properties.user_value}
        />
      ) : (
        <Choice
          content={content}
          mode={mode}
          onChange={OnChange}
          inSummary={inSummary}
        />
      );
    case "input_location":
      return inSummary ? (
        <LocationInSummary
          item={content as CWFLocationType}
          type={content.type}
        />
      ) : (
        <LocationInput
          content={content}
          mode={mode}
          onChange={OnChange}
          inSummary={inSummary}
        />
      );
    case "input_text":
      return content.properties.input_type === "short_text" ? (
        inSummary ? (
          <RenderShortTextInSummary
            properties={content.properties}
            localValue={content.properties.user_value}
          />
        ) : (
          <Text
            content={content}
            onTextboxUpdate={(value: string) => OnChange(value)}
            mode={mode}
            inSummary={inSummary}
          />
        )
      ) : inSummary ? (
        <RenderTextAreaInSummary
          properties={content.properties}
          localValue={content.properties.user_value}
        />
      ) : (
        <TextArea
          content={content}
          onTextboxUpdate={(value: string) => OnChange(value)}
          mode={mode}
          inSummary={inSummary}
        />
      );

    case "input_number":
      return inSummary ? (
        <RenderNumberTextInSummary
          properties={content.properties}
          localValue={content.properties.user_value}
        />
      ) : (
        <NumberText
          content={content}
          onTextboxUpdate={value => OnChange(value)}
          mode={mode}
          inSummary={inSummary}
        />
      );
    case "input_email":
      return inSummary ? (
        <RenderEmailInSummary
          properties={content.properties}
          localValue={content.properties.user_value}
        />
      ) : (
        <Email
          content={content}
          onTextboxUpdate={value => OnChange(value)}
          mode={mode}
          inSummary={inSummary}
        />
      );
    case "region":
      return inSummary ? (
        <RenderRegionInSummary
          properties={content.properties}
          localValue={state.form.metadata?.region ?? { id: "", name: "" }}
        />
      ) : (
        <RegionField
          content={content}
          mode={mode}
          onChange={OnChange}
          inSummary={inSummary}
        />
      );
    case "checkbox":
      return (
        <CheckboxPreview
          content={content}
          mode={mode}
          inSummary={inSummary}
          onChange={OnChange}
        />
      );

    default:
      return <span />;
  }
};

const FieldRendererWithAttachment = withAttachmentComment(FieldRenderer);
export default FieldRendererWithAttachment;
