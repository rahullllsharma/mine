import { ActionLabel, CaptionText } from "@urbint/silica";

const EmptyPersonnelDescription = () => {
  return (
    <div className="bg-gray-100 p-4 rounded-md flex flex-col items-center justify-center text-center">
      <ActionLabel className="text-sm font-semibold text-neutral-800">
        Document Participants
      </ActionLabel>
      <CaptionText className="text-sm text-neutral-700">
        Start by adding team members and other individuals who participated in
        this form&#39;s discussion or activity.
      </CaptionText>
    </div>
  );
};

export default EmptyPersonnelDescription;
