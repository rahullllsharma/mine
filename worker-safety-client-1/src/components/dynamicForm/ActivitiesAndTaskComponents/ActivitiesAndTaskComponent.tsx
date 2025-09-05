import type { ActivityAndTaskComponentProps } from "../../templatesComponents/customisedForm.types";
import { SectionHeading } from "@urbint/silica";
import { useState } from "react";
import ButtonSecondary from "@/components/shared/button/secondary/ButtonSecondary";
import { UserFormModeTypes } from "../../templatesComponents/customisedForm.types";
import CWFAddActivityModal from "./CWFAddActivityModal";
import { StaticTaskCard } from "./utils";
import { ActivitiesAndTasksCard } from "./ActivitiesAndTasksCard";

export default function ActivityAndTaskComponent({
  id,
  configs,
  mode,
  handleChangeInActivity,
  inSummary,
  errorMessage,
}: ActivityAndTaskComponentProps & {
  inSummary?: boolean;
  errorMessage?: string;
  id: string;
}): JSX.Element {
  const { title } = configs;
  const [isModalOpen, setIsModalOpen] = useState(false);

  const handleOpenModal = () => setIsModalOpen(true);
  const handleCloseModal = () => setIsModalOpen(false);

  // Update parent handler if provided
  const handleActivityChange = (newActivity: any) => {
    if (handleChangeInActivity) {
      handleChangeInActivity(newActivity);
    }
  };

  const content =
    mode == UserFormModeTypes.BUILD ? (
      <StaticTaskCard />
    ) : (
      <ActivitiesAndTasksCard
        handleChangeInActivity={handleActivityChange}
        readOnly={
          mode === UserFormModeTypes.PREVIEW ||
          mode === UserFormModeTypes.PREVIEW_PROPS
        }
        inSummary={inSummary}
        errorMessage={errorMessage}
      />
    );

  return (
    <>
      <div className="flex justify-between" id={id}>
        <SectionHeading className={`${inSummary ? "text-[20px]" : "text-xl"}`}>
          {title}
        </SectionHeading>
        {!inSummary && (
          <ButtonSecondary
            label="Add Tasks"
            iconStart="plus_circle_outline"
            onClick={handleOpenModal}
            disabled={
              mode === UserFormModeTypes.PREVIEW ||
              mode === UserFormModeTypes.PREVIEW_PROPS ||
              mode === UserFormModeTypes.BUILD
            }
          />
        )}
      </div>
      <div>{content}</div>

      {isModalOpen && (
        <CWFAddActivityModal
          isOpen={isModalOpen}
          closeModal={handleCloseModal}
          handleChangeInActivity={handleActivityChange}
        />
      )}
    </>
  );
}
