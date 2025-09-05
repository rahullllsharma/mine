import { BodyText } from "@urbint/silica";
import { GroupDiscussionSection } from "../GroupDiscussionSection";

export type HazardsSectionData = {
  hazards: Array<string>;
};

export type HazardsSectionProps = HazardsSectionData & {
  onClickEdit: () => void;
};

const HazardsSection = ({ onClickEdit, hazards }: HazardsSectionProps) => {
  return (
    <GroupDiscussionSection title="Hazards" onClickEdit={onClickEdit}>
      <div className="flex flex-col gap-1">
        {hazards.map(hazard => (
          <div key={hazard} className="bg-white p-4 shadow-10">
            <BodyText className="text-base font-semibold text-neutral-shade-75">
              {hazard}
            </BodyText>
          </div>
        ))}
      </div>
    </GroupDiscussionSection>
  );
};

export { HazardsSection };
