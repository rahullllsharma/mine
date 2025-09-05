import { BodyText } from "@urbint/silica";
import { GroupDiscussionSection } from "../../Basic/GroupDiscussionSection";

export type PPESectionProps = {
  directControl: Array<string>;
};

const PPESection = ({ directControl }: PPESectionProps) => {
  const standardRequired = [
    "Hard Hat",
    "Gloves",
    "Safety toe shoes",
    "Safety glasses",
    "Safety vest",
  ];

  return (
    <GroupDiscussionSection title="PPE">
      <div className="flex flex-col gap-4">
        <div className="bg-white p-4 rounded">
          <BodyText className="text-base font-semibold text-neutral-shade-75 mb-2">
            Direct Control PPE
          </BodyText>
          <div className="flex flex-wrap gap-1">
            {directControl.map((item, index) => (
              <span
                key={`${item}-${index}`}
                className="bg-brand-urbint-10 border rounded border-brand-urbint-30 px-1.5 py-0.5 text-base font-normal text-neutral-shade-100"
              >
                {item}
              </span>
            ))}
          </div>
        </div>

        <div className="bg-white p-4">
          <BodyText className="text-base font-semibold text-neutral-shade-75 mb-2">
            Standard Required PPE
          </BodyText>
          <div className="flex flex-wrap gap-1">
            {standardRequired.map(item => (
              <span
                key={item}
                className="bg-brand-urbint-10 border rounded border-brand-urbint-30 px-1.5 py-0.5 text-base font-normal text-neutral-shade-100"
              >
                {item}
              </span>
            ))}
          </div>
        </div>
      </div>
    </GroupDiscussionSection>
  );
};

export { PPESection };
