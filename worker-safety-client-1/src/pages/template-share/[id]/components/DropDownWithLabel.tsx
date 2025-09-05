import type { ReferenceContentType } from "@/components/templatesComponents/customisedForm.types";
import { BodyText, ComponentLabel } from "@urbint/silica";
import Region from "./Region";

const isLabelValueObject = (
  item: unknown
): item is { label: string; value: string } => {
  return (
    typeof item === "object" &&
    item !== null &&
    "label" in item &&
    "value" in item
  );
};

type DropDownWithLabelProps = {
  content: ReferenceContentType;
};

const DropDownWithLabel = ({
  content: {
    properties: { title, api_details, user_value },
  },
}: DropDownWithLabelProps) => {
  const renderLabels = () => {
    if (!user_value || !Array.isArray(user_value) || user_value.length === 0) {
      return (
        <BodyText className="text-base text-neutrals-tertiary">
          No information provided
        </BodyText>
      );
    }

    return (
      <div className="text-sm">
        {user_value.map((item, index) => {
          if (isLabelValueObject(item)) {
            return (
              <div key={item.value}>
                <BodyText>{item.label}</BodyText>
              </div>
            );
          }
          return (
            <Region
              key={index}
              api_details={api_details}
              user_value={user_value}
            />
          );
        })}
      </div>
    );
  };

  return (
    <div className="flex flex-col gap-2 bg-brand-gray-10 p-4 rounded-lg">
      <ComponentLabel className="text-md font-semibold">{title}</ComponentLabel>
      {renderLabels()}
    </div>
  );
};

export default DropDownWithLabel;
