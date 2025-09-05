import type { Field } from "./FormHistoryType";
import { DateTime } from "luxon";
import { BodyText, Icon } from "@urbint/silica";
import { capitalize } from "lodash-es";
import { isISODateString } from "../Utils";

export function RenderFields({
  fields,
  level,
}: {
  fields: Field[] | undefined | null;
  level: number;
}) {
  const formatValue = (value: string | string[] = "") => {
    if (!value) {
      return "None";
    }

    if (Array.isArray(value)) {
      return value.join(", ");
    }

    if (value && isISODateString(value)) {
      return DateTime.fromISO(value).toLocal().toFormat("yyyy-MM-dd hh:mm a");
    }

    return value;
  };

  return (
    <>
      {fields?.map((field, index) => (
        <div
          key={index}
          className={`flex items-center space-x-2 w-full ${
            level >= 1 ? `pl-9` : `pl-0`
          }`}
        >
          <Icon className="text-xl flex-shrink-0" name="sub_right" />
          <div className="flex flex-1 min-w-0 items-center">
            <BodyText className="flex-shrink-0">
              {capitalize(field.name)},
            </BodyText>
            <div className="flex items-center flex-1 min-w-0 ml-1">
              <BodyText>{formatValue(field.old_value)}</BodyText>
              <Icon name="long_right" className="text-xl mx-2 flex-shrink-0" />
              <BodyText>{formatValue(field.new_value)}</BodyText>
            </div>
          </div>
        </div>
      ))}
    </>
  );
}

export default RenderFields;
