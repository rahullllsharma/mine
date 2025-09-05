import { useState } from "react";
import { Icon, ActionLabel, CaptionText, BodyText } from "@urbint/silica";
import { type CrewSign, type CreatorSign, Status } from "@/types/natgrid/jobsafetyBriefing";
import Checkbox from "@/components/shared/checkbox/Checkbox";
import CreatorSignComponent from "./CreatorSign";

interface CrewSignOffProps {
  crewName: CrewSign[];
  crewSign: CrewSign[];
  discussionConducted?: boolean;
  creatorData: CreatorSign;
  status: string;
}

const CrewSignOff = ({
  crewName,
  crewSign,
  creatorData,
  status,
}: CrewSignOffProps) => {
  const [isExpanded, setIsExpanded] = useState(true);
  if (status === Status.IN_PROGRESS) {
    return null;
  }
  

  const toggleExpand = () => {
    setIsExpanded(!isExpanded);
  };

  return (
    <div className="rounded bg-brand-gray-10">
      <button
        onClick={toggleExpand}
        className="w-full flex items-center justify-between p-4 text-left hover:bg-gray-50"
        aria-expanded={isExpanded}
        aria-controls="crew-signoff-content"
      >
        <BodyText className="text-lg text-brand-gray-70 font-semibold">
          Sign-off
        </BodyText>
        <Icon
          name={isExpanded ? "chevron_down" : "chevron_right"}
          className="text-2xl"
        />
      </button>
      <div
        id="crew-signoff-content"
        className={`overflow-hidden transition-all duration-300 ease-in-out ${
          isExpanded ? "visible opacity-100" : "invisible opacity-0 h-0"
        }`}
      >
        <div className="flex flex-col gap-4 p-4">
          <CreatorSignComponent creatorData={creatorData} />
          {crewName?.map((crew, index) => {
            const name =
              crew.crewDetails?.name === "Other Personnel (Please specify)"
                ? crew.otherCrewDetails
                : crew.crewDetails?.name;
            const signedUrl = crewSign[index]?.signature?.signedUrl;
            const crewDiscussionConducted =
              crewSign[index]?.discussionConducted;

            return (
              <div
                key={index}
                className="flex flex-col gap-2 bg-white p-4 rounded "
              >
                {name && (
                  <div className="text-md font-normal text-gray-900">
                    {name}
                  </div>
                )}

                {crewDiscussionConducted && (
                  <div className="flex items-center gap-2 my-2">
                    <Checkbox
                      type="checkbox"
                      checked={crewDiscussionConducted}
                      readOnly
                      className="h-4 w-4"
                    />
                    <CaptionText className="text-sm">
                      Conducted discussion
                    </CaptionText>
                  </div>
                )}

                {signedUrl && (
                  <div className="flex flex-row gap-2 w-full justify-between items-end">
                    <div className="flex flex-col gap-1">
                      <ActionLabel className="text-gray-600 font-medium">
                        Signature
                      </ActionLabel>
                      <img
                        src={signedUrl.toString()}
                        alt={`Signature for ${name}`}
                        className="max-w-full max-h-full min-w-[200px] min-h-[60px] w-auto h-auto sm:min-w-[250px] md:min-w-[300px]"
                      />
                    </div>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};

export default CrewSignOff;
