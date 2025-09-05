import type { CreatorSign } from "@/types/natgrid/jobsafetyBriefing";
import { ActionLabel, CaptionText } from "@urbint/silica";
import Checkbox from "@/components/shared/checkbox/Checkbox";

interface CreatorSignOffProps {
  creatorData: CreatorSign;
}

const CreatorSignComponent = ({ creatorData }: CreatorSignOffProps) => {
  const creatorName = creatorData?.crewDetails?.name;
  const isCreatorDiscussionConducted = creatorData?.discussionConducted;
  const signedUrlOfCreator = creatorData?.signature?.signedUrl;
  return (
    <div className="flex flex-col gap-2 bg-white p-4 rounded ">
      {creatorName && (
        <div className="text-md font-normal text-gray-900">
          Created By {creatorName}
        </div>
      )}
      {isCreatorDiscussionConducted && (
        <div className="flex items-center gap-2 my-2">
          <Checkbox
            type="checkbox"
            checked={isCreatorDiscussionConducted}
            readOnly
            className="h-4 w-4"
          />
          <CaptionText className="text-sm">Conducted discussion</CaptionText>
        </div>
      )}
      {signedUrlOfCreator && (
        <div className="flex flex-row gap-2 w-full justify-between items-end">
          <div className="flex flex-col gap-1">
            <ActionLabel className="text-gray-600 font-medium">
              Signature
            </ActionLabel>
            <img
              src={signedUrlOfCreator.toString()}
              alt={`Signature for ${creatorName}`}
              className="max-w-full max-h-full min-w-[200px] min-h-[60px] w-auto h-auto sm:min-w-[250px] md:min-w-[300px]"
            />
          </div>
        </div>
      )}
    </div>
  );
};

export default CreatorSignComponent;
