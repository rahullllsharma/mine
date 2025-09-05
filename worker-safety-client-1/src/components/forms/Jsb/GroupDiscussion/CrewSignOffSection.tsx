import type { CrewSignOffData } from "@/types/jsbShare/jsbShare";
import { BodyText } from "@urbint/silica";
import { SignatureTypes } from "@/types/crewSignOff/crewSignOff";
import { GroupDiscussionSection } from "../../Basic/GroupDiscussionSection";

const CrewSignOffSection = ({ crewSignOffData }: any) => {
  return (
    <GroupDiscussionSection title="Sign-Off">
      <div className="bg-white p-4 ">
        {crewSignOffData.crewList.map(
          (element: CrewSignOffData, index: number) => (
            <div key={element?.signature?.id}>
              <BodyText className="font-semibold text-sm mb-2">
                Name {index + 1}
              </BodyText>
              {element.type === SignatureTypes.OTHER ? (
                <span className="font-normal text-base"> {element?.name}</span>
              ) : (
                <span className="font-normal text-base">
                  <span className="font-normal text-base">
                    {element?.name} ({element?.jobTitle})
                  </span>
                  <span className="font-normal text-base ml-8">
                    {element?.employeeNumber}
                  </span>
                </span>
              )}

              <div className="flex flex-row gap-2">
                <div className="flex flex-col gap-1">
                  <img
                    src={element.signature.signedUrl?.toString()}
                    alt={`Signature for ${element?.name}`}
                    className="max-w-full max-h-28"
                  />
                </div>
              </div>
            </div>
          )
        )}
      </div>
    </GroupDiscussionSection>
  );
};

export default CrewSignOffSection;
