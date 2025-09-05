import type { PersonnelComponentType } from "@/components/templatesComponents/customisedForm.types";
import Image from "next/image";
import { BodyText, SectionHeading } from "@urbint/silica";
import { formatLocal } from "@/components/templatesComponents/PreviewComponents/dateUtils";

export const RenderPersonnelComponentInSummary = ({
  item,
}: {
  item: PersonnelComponentType;
}) => {
  return (
    <div className="flex flex-col gap-6">
      <div className="flex items-center justify-between">
        <SectionHeading className="text-[20px] cursor-auto">
          {item.properties.title}
        </SectionHeading>
      </div>
      {item.properties.user_value?.map(user => {
        const { external_id, display_name, name, job_title, employee_number } =
          user.crew_details;
        const { signedUrl, url, date, time } = user.crew_details.signature;

        return (
          <div key={external_id} className="flex flex-col gap-2">
            <div className="flex flex-row gap-2">
              <BodyText className="text-base font-semibold">
                {display_name || name}
              </BodyText>
              {job_title && (
                <BodyText className="text-base font-semibold">
                  ({job_title})
                </BodyText>
              )}
              {employee_number && (
                <BodyText className="text-base text-neutral-shade-100">
                  {employee_number}
                </BodyText>
              )}
            </div>
            <div className="flex flex-row gap-2">
              {user.selected_attribute_ids &&
                user.selected_attribute_ids.length > 0 && (
                  <BodyText className="text-base text-neutral-shade-100">
                    {user.selected_attribute_ids
                      .map(attrId => {
                        const attribute = item.properties.attributes?.find(
                          attr => attr.attribute_id === attrId
                        );
                        return attribute?.attribute_name || attrId;
                      })
                      .filter(Boolean)
                      .join(", ")}
                  </BodyText>
                )}
            </div>
            <div className="flex flex-col gap-2">
              <div className="relative w-full bg-white border border-neutral-200 rounded-lg">
                <Image
                  src={signedUrl || url || ""}
                  alt={`${display_name || name} signature`}
                  width={800}
                  height={128}
                  className="w-full h-32 object-contain"
                  unoptimized
                  priority
                />
              </div>
              <div className="flex flex-col gap-1">
                {date && time && (
                  <BodyText className="mt-1 text-[13px] text-neutrals-tertiary">
                    Signed on {formatLocal(date, time)}
                  </BodyText>
                )}
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
};
