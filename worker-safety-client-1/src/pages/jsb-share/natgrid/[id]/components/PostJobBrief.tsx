import type { DiscussionItems } from "@/types/natgrid/jobsafetyBriefing";
import { useState } from "react";
import { BodyText, Icon } from "@urbint/silica";

const DISCUSSION_ITEMS = [
  {
    key: "nearMissOccuredDuringActivities",
    question: "Did any near misses occur during the activities?",
  },
  {
    key: "jobBriefAdequateCommunication",
    question:
      "Was the Job Brief communication adequate to cover the task and hazards?",
  },
  {
    key: "safetyConcernsIdentifiedDuringWork",
    question:
      "Were any safety concerns NOT identified in the Job Brief discovered after beginning work?",
  },
  {
    key: "changesInProcedureWork",
    question: "Are any changes to procedures or work methods needed?",
  },
  {
    key: "crewMemebersAdequateTrainingProvided",
    question:
      "Did crew members have adequate training and knowledge to perform the tasks safely?",
  },
  {
    key: "otherLessonLearnt",
    question: "Any other lessons learned from this activity?",
  },
  {
    key: "jobWentAsPlanned",
    question: "Job went as planned / no issues",
  },
] as const;

type DiscussionItemKeys = typeof DISCUSSION_ITEMS[number]["key"];

const questions: Record<DiscussionItemKeys, string> = DISCUSSION_ITEMS.reduce(
  (acc, { key, question }) => ({
    ...acc,
    [key]: question,
  }),
  {} as Record<DiscussionItemKeys, string>
);

const PostJobBrief = ({
  DiscussionItem,
  postJobDiscussionNotes,
}: {
  DiscussionItem: DiscussionItems;
  postJobDiscussionNotes: string;
}) => {
  const [isExpanded, setIsExpanded] = useState(true);

  const toggleExpand = () => {
    setIsExpanded(!isExpanded);
  };

  const formattedDiscussionItems = DiscussionItem
    ? Object.entries(DiscussionItem)
        .filter(([key]) => !key.endsWith("Description") && key !== "__typename")
        .map(([key, value]) => ({
          key,
          value,
          question: questions[key as DiscussionItemKeys] || "",
        }))
    : [];

    if (!DiscussionItem && !postJobDiscussionNotes) {
      return null;
    }
    if (formattedDiscussionItems.length === 0 && !postJobDiscussionNotes) {
      return null;
    }
  
  return (
    <>
      <br />

      <div className="rounded bg-brand-gray-10">
        <button
          onClick={toggleExpand}
          className="w-full flex items-center justify-between p-4 text-left hover:bg-gray-50"
          aria-expanded={isExpanded}
          aria-controls="post-job-brief-content"
        >
          <BodyText className="text-lg text-brand-gray-70 font-semibold">
            Post Job Brief Discussion
          </BodyText>
          <Icon
            name={isExpanded ? "chevron_down" : "chevron_right"}
            style={{ fontSize: "28px" }}
          />
        </button>

        <div
          id="post-job-brief-content"
          className={`transition-all duration-200 ease-in-out ${
            isExpanded
              ? "max-h-[2000px] opacity-100"
              : "max-h-0 opacity-0 overflow-hidden"
          }`}
        >
          <div className="p-4">
            <div className="flex flex-col gap-3">
              <div className="list-disc list-inside p-4">
                {formattedDiscussionItems.map((item, index) => {
                  const descriptionKey =
                    item.key.replace("DuringActivities", "") + "Description";
                  const description =
                    DiscussionItem[descriptionKey as keyof DiscussionItems];

                  return (
                    <div key={index} className="mb-4">
                      <div className="flex flex-col gap-2">
                        <div className="flex items-center gap-2 justify-between">
                          <div className=" text-brand-gray-70 text-sm font-semibold">
                            {item.question}
                          </div>
                          <div className="p-2 rounded bg-white w-14 text-center">
                            <BodyText className="font-semibold">
                              {item.value ? "Yes" : "No"}
                            </BodyText>
                          </div>
                        </div>
                        {description && (
     
                            <div className="w-full h-27 border-2 rounded bg-white p-2">
                              <BodyText className=" text-brand-gray-70 font-medium">Comment</BodyText> 
                              <BodyText className=" text-brand-gray-70 font-normal">{description}</BodyText>
                            </div>
             
                        )}
                      </div>
                    </div>
                  );
                })}
              </div>
        <div className="p-4">
            {postJobDiscussionNotes && (
                <div className="w-full h-27 border-2 rounded bg-white p-2">
                  <BodyText className="text-brand-gray-70 font-semibold">
                     Post Job Discussion, Hazardous Conditions and Near Misses – Notes:
                  </BodyText>
                  <BodyText className="text-brand-gray-70 font-normal">
                   {postJobDiscussionNotes}
                  </BodyText>
                </div>
            )}
         </div>
            </div>
          </div>
        </div>
      </div>
    </>
  );
};

export default PostJobBrief;