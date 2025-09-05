import type {
  FormElementsType,
  PersonnelUserValue,
  PersonnelAttribute,
} from "@/components/templatesComponents/customisedForm.types";
import React from "react";
import { ActionLabel, BodyText } from "@urbint/silica";
import Image from "next/image";
import { formatLocal } from "@/components/templatesComponents/PreviewComponents/dateUtils";

const Personnel = ({ content }: { content: FormElementsType }): JSX.Element => {
  const { user_value, title } = content.properties ?? {};
  const selectedAttributeNames = (selectedIds: string[]) => {
    return content?.properties?.attributes
      .filter((attr: PersonnelAttribute) =>
        selectedIds.includes(attr.attribute_id)
      )
      .map((attr: PersonnelAttribute) => attr.attribute_name);
  };
  return (
    <div className="flex flex-col gap-4 p-4 bg-brand-gray-10 rounded-lg">
      <BodyText className="text-[20px] font-semibold">
        {title ?? "Sign Off"}
      </BodyText>
      {user_value.length === 0 ? (
        <BodyText className="flex text-sm font-semibold">
          No information provided
        </BodyText>
      ) : (
        user_value.map((value: PersonnelUserValue, index: number) => {
          const { display_name, name, job_title, employee_number, signature } =
            value.crew_details;
          return (
            <div key={index} className="flex flex-col gap-2">
              <div className="flex">
                <ActionLabel className="text-base">
                  {display_name || name} {job_title && `(${job_title})`}
                </ActionLabel>
                <BodyText className="ml-1 text-base">
                  {employee_number}
                </BodyText>
              </div>
              {value.selected_attribute_ids.length > 0 && (
                <>
                  <BodyText>
                    {selectedAttributeNames(value.selected_attribute_ids).join(
                      ", "
                    )}
                  </BodyText>
                </>
              )}
              <Image
                src={signature.signedUrl || ""}
                alt={signature.display_name || ""}
                className="mt-2 w-full h-[100px] bg-white object-contain rounded-lg"
                width={800}
                height={128}
                unoptimized
                priority
              />
              {signature?.date && signature?.time && (
                <BodyText className="mt-1 text-[13px] text-neutrals-tertiary">
                  Signed on {formatLocal(signature.date, signature.time)}
                </BodyText>
              )}
            </div>
          );
        })
      )}
    </div>
  );
};

export default Personnel;
