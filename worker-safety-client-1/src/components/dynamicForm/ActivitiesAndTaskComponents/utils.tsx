import { ActionLabel, BodyText } from "@urbint/silica";
import { Checkbox } from "../../forms/Basic/Checkbox/Checkbox";
import { RiskLevel } from "../../riskBadge/RiskLevel";
import { CWFTaskCard } from "./CWFTaskCard";

const StaticTaskCard = () => {
  return (
    <div className="mt-2.5">
      <Checkbox
        className="w-full gap-4"
        checked={true}
        disabled={true}
        onClick={() => void 0}
      >
        <ActionLabel className="mt-2.5">Activity Title</ActionLabel>
      </Checkbox>
      <Checkbox
        className="w-full gap-4 mt-2.5"
        checked={true}
        disabled={true}
        labelClassName="w-full"
        onClick={() => void 0}
      >
        <CWFTaskCard
          title={"Task Title"}
          risk={RiskLevel.UNKNOWN}
          showRiskInformation={true}
          showRiskText={true}
          withLeftBorder={true}
        />
      </Checkbox>
    </div>
  );
};

const TasksBlankField = ({ errorMessage }: { errorMessage?: string }) => {
  return (
    <div className="flex flex-col items-center sm:flex-row gap-2 sm:gap-4 p-2 sm:p-4 bg-gray-100 h-24 sm:h-32 w-full mt-5">
      <BodyText className="text-neutrals-secondary">
        There are currently no Activities or Tasks for the selected Work Dates
        and Times.
        {errorMessage && (
          <>
            <div className="text-system-error-40 text-sm pt-2 block text-center">
              {errorMessage}
            </div>
          </>
        )}
      </BodyText>
    </div>
  );
};

export { StaticTaskCard, TasksBlankField };
