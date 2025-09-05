import type { CheckboxQuestionPropertiesType } from "@/components/templatesComponents/customisedForm.types";
import { BodyText, ComponentLabel } from "@urbint/silica";
import Link from "@/components/shared/link/Link";

const isEmptyValue = (value: any): boolean => {
  if (value === null || value === undefined) return true;
  if (Array.isArray(value) && value.length === 0) return true;
  return false;
};

const Checkbox = ({
  checkboxProperties,
}: {
  checkboxProperties: CheckboxQuestionPropertiesType;
}) => {
  const { url, url_display_text } = checkboxProperties?.options?.[0] || {};

  if (isEmptyValue(checkboxProperties?.user_value)) {
    return (
      <div className="flex flex-col gap-2 bg-brand-gray-10 p-4 rounded-lg">
        <ComponentLabel className="text-sm font-semibold">
          {checkboxProperties.title}
        </ComponentLabel>
        <BodyText className="text-base text-neutrals-tertiary">
          No information provided
        </BodyText>
      </div>
    );
  }

  return (
    <>
      {checkboxProperties?.user_value?.includes("1") ? (
        <div className="flex flex-col gap-2 bg-brand-gray-10 p-4 rounded-lg">
          <BodyText className="text-base">{checkboxProperties.title}</BodyText>
          {url && url_display_text && (
            <Link
              href={url}
              target="_blank"
              rel="noopener noreferrer"
              label={url_display_text}
              iconRight="external_link"
              className="text-base font-normal"
            />
          )}
        </div>
      ) : null}
    </>
  );
};

export default Checkbox;
