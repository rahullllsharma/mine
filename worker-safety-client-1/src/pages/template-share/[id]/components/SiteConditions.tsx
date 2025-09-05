import type {
  FormElement,
  SiteCondition,
} from "@/components/templatesComponents/customisedForm.types";
import { BodyText } from "@urbint/silica";
import { TagCard } from "@/components/forms/Basic/TagCard";

const SiteConditions = ({
  siteCondition,
  item,
}: {
  siteCondition: SiteCondition[];
  item: FormElement;
}): JSX.Element => {
  return (
    <div className="flex flex-col p-4 gap-4">
      <BodyText className="text-[20px] font-semibold">
        {item.properties.title ?? "Site Conditions"}
      </BodyText>
      <div className="flex flex-col gap-4 bg-brand-gray-10 rounded-lg">
        {siteCondition?.length === 0 ? (
          <BodyText className="flex text-sm font-semibold">
            No information provided
          </BodyText>
        ) : (
          <div className="flex flex-col gap-4">
            {siteCondition
              .filter((condition: SiteCondition) => condition.selected === true)
              .map((condition: SiteCondition) => {
                return (
                  <div
                    key={condition.id}
                    className="flex flex-row w-full gap-4 items-center"
                  >
                    <TagCard className="border-data-blue-30 w-full">
                      <BodyText className="font-semibold">
                        {condition.name}
                      </BodyText>
                    </TagCard>
                  </div>
                );
              })}
          </div>
        )}
      </div>
    </div>
  );
};

export default SiteConditions;
