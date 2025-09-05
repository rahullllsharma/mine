import type { Field, Section } from "./FormHistoryType";
import { BodyText, Icon } from "@urbint/silica";
import AccordionItem from "./AccordionItem";
import {
  getFilteredFields,
  getFormattedEventType,
  tempMutation,
} from "./FormHistory";
import RenderFields from "./RenderFields";

export function NestedSection({
  sections,
  title,
  level,
  fields,
}: {
  sections: Section[] | undefined | null;
  title: React.ReactNode;
  level: number;
  fields: Field[] | undefined | null;
}) {
  if (level > 3) {
    return null;
  }

  function processAndMergeChunks(data: Field[], chunkSize = 3) {
    const result: any[] = [];

    for (let i = 0; i < data.length; i += chunkSize) {
      const chunk = data.slice(i, i + chunkSize);

      const typeField = chunk.find(item => item.name === "Type");
      const typeName = typeField
        ? typeField.old_value === "None"
          ? typeField.new_value
          : typeField.old_value
        : "";

      const oldValues = [];
      const newValues = [];

      let valueStrOld = "",
        valueStrNew = "";
      let unitOld = "",
        unitNew = "";

      chunk.forEach(item => {
        if (item.name === "Value Str") {
          valueStrOld =
            item.old_value === "None" || item.old_value === undefined
              ? ""
              : item.old_value;
          valueStrNew =
            item.new_value === "None" || item.new_value === undefined
              ? ""
              : item.new_value;
        }
        if (item.name === "Unit") {
          unitOld =
            item.old_value === "None" || item.old_value === undefined
              ? ""
              : item.old_value;
          unitNew =
            item.new_value === "None" || item.new_value === undefined
              ? ""
              : item.new_value;
        }
      });

      oldValues.push(valueStrOld ? `${valueStrOld} ${unitOld}`.trim() : "None");
      newValues.push(valueStrNew ? `${valueStrNew} ${unitNew}`.trim() : "None");

      result.push({
        name: typeName,
        old_value: oldValues,
        new_value: newValues,
      });
    }

    return result;
  }

  return (
    <>
      <AccordionItem title={title}>
        {sections
          ?.filter(
            section =>
              !tempMutation.sectionsToBeSkipped.includes(section.name) &&
              !(
                section.name === "Signature" &&
                section.operation_type === "update"
              )
          )
          .map((section, index) => {
            if (
              getFilteredFields(section.fields ?? []).length === 0 &&
              section.sections?.length === 0
            ) {
              return (
                <div
                  key={index}
                  className={`flex items-center space-x-2 ${
                    level == 1 ? "pl-9" : "pl-0"
                  }`}
                >
                  <Icon className="text-xl flex-shrink-0" name="sub_right" />
                  <div className="flex items-center flex-wrap">
                    <BodyText>
                      {getFormattedEventType(section.operation_type)}
                    </BodyText>
                    <BodyText className="font-semibold ml-1">
                      {section.name}
                    </BodyText>
                  </div>
                </div>
              );
            }
            let processedFields = section.fields;
            if (section.name === "Voltages" && section.fields) {
              processedFields = processAndMergeChunks(section.fields);
            }
            return (
              <div key={index} className="flex items-center">
                <NestedSection
                  sections={section.sections}
                  title={
                    <div
                      className={`flex items-center space-x-2 ${
                        level >= 1 ? "pl-9" : "pl-0"
                      }`}
                    >
                      <Icon
                        className="text-xl flex-shrink-0"
                        name="sub_right"
                      />
                      <div className="flex items-center flex-wrap">
                        <BodyText>
                          {getFormattedEventType(section.operation_type)}
                        </BodyText>
                        <BodyText className="font-semibold ml-1">
                          {section.name === "Ewp"
                            ? section.name.toUpperCase()
                            : section.name}
                        </BodyText>
                      </div>
                    </div>
                  }
                  level={level + 1}
                  fields={
                    section.name === "Voltages"
                      ? processedFields
                      : getFilteredFields(section.fields ?? [])
                  }
                />
              </div>
            );
          })}

        <RenderFields fields={getFilteredFields(fields ?? [])} level={level} />
      </AccordionItem>
    </>
  );
}

export default NestedSection;
