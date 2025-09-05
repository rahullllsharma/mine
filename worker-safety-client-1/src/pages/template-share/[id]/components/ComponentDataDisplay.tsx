import type {
  YesOrNoQuestionType,
  FormComponentPayloadType,
} from "@/components/templatesComponents/customisedForm.types";
import { BodyText, ComponentLabel } from "@urbint/silica";
import {
  ThumbUP,
  ThumbDown,
} from "@/components/templatesComponents/PreviewComponents/ThumbSwitch";

const renderAnswer = (properties: YesOrNoQuestionType["properties"]) => {
  if (properties.toggle_style === "thums") {
    if (properties.user_value === null) return "No answer";
    return properties.user_value ? <ThumbUP /> : <ThumbDown />;
  }
  if (
    properties.toggle_style === "text" &&
    Array.isArray(properties.toggle_options)
  ) {
    if (properties.user_value === null) return "No answer";
    return properties.user_value
      ? properties.toggle_options[0]?.label || "Yes"
      : properties.toggle_options[1]?.label || "No";
  }
  // simple or fallback
  if (properties.user_value === null) return "No answer";
  return properties.user_value ? "Yes" : "No";
};

const ComponentDataDisplay = ({
  content,
}: {
  content: FormComponentPayloadType;
}) => {
  const { properties } = content;

  const yesOrNoProperties =
    properties as unknown as YesOrNoQuestionType["properties"];
  return (
    <div className="flex flex-col gap-2 bg-brand-gray-10 p-4 rounded-lg">
      <ComponentLabel className="text-sm font-semibold">
        {yesOrNoProperties.title}
      </ComponentLabel>
      <BodyText className="text-base">
        {renderAnswer(yesOrNoProperties)}
      </BodyText>
    </div>
  );
};

export default ComponentDataDisplay;
