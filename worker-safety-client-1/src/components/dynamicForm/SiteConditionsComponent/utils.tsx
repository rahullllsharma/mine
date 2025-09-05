import type {
  SiteCondition,
  StaticSiteConditionCardProps,
} from "@/components/templatesComponents/customisedForm.types";
import { ActionLabel, BodyText, SectionHeading } from "@urbint/silica";
import { TagCard } from "@/components/forms/Basic/TagCard";
import { Checkbox } from "../../forms/Basic/Checkbox/Checkbox";
import ButtonIcon from "@/components/shared/button/icon/ButtonIcon";
import { useState } from "react";
import { gql, useMutation } from "@apollo/client";
import ButtonSecondary from "@/components/shared/button/secondary/ButtonSecondary";
import ButtonPrimary from "@/components/shared/button/primary/ButtonPrimary";

export const StaticSiteConditionCard = ({
  item,
}: StaticSiteConditionCardProps) => {
  return (
    <>
      <div className="gap-3 w-full">
        <SectionHeading className="text-xl text-neutral-shade-100 font-semibold">
          {item?.properties?.title ?? "Site Conditions"}
        </SectionHeading>
        <BodyText>
          Review the site conditions below and see if they apply to your
          location.
        </BodyText>
        <div className="flex flex-col gap-4 pt-4 w-full">
          <div className="flex w-full items-center">
            <Checkbox
              className="flex-shrink-0"
              checked={true}
              disabled={true}
              onClick={() => void 0}
            />
            <ActionLabel className="mt-2.5 ml-2">Select all</ActionLabel>
          </div>

          <div className="flex w-full items-center">
            <Checkbox
              className="flex-shrink-0"
              checked={true}
              disabled={true}
              onClick={() => void 0}
            />
            <TagCard className="ml-2 flex-grow border-neutrals-tertiary">
              <span className="font-semibold">Site condition title</span>
            </TagCard>
          </div>
        </div>
      </div>
    </>
  );
};

type DialogHeaderProps = {
  onClose: () => void;
};
export const DialogHeader = ({ onClose }: DialogHeaderProps) => (
  <div className="flex flex-row justify-between">
    <SectionHeading className="text-xl font-semibold">
      Add Site Conditions
    </SectionHeading>
    <ButtonIcon iconName="close_big" onClick={onClose} />
  </div>
);

type DialogContentProps = {
  siteConditions: SiteCondition[];
  onCancel: () => void;
  onAdd: (updatedConditions: SiteCondition[]) => void;
  librarySiteConditionIds: string[];
  locationId?: string;
  manual_location: boolean;
};

export const DialogContent = ({
  siteConditions,
  onAdd,
  onCancel,
  librarySiteConditionIds,
  locationId,
  manual_location,
}: DialogContentProps) => {
  const [dialogSiteConditions, setDialogSiteConditions] = useState(
    siteConditions || []
  );
  const handleDialogCheckboxChange = (id: string) => {
    setDialogSiteConditions(prevConditions =>
      prevConditions.map(condition =>
        condition.librarySiteCondition.id === id
          ? {
              ...condition,
              checked: !condition.checked,
              selected: !condition.checked,
            }
          : condition
      )
    );
  };
  const [createSiteCondition, { loading }] = useMutation(creteSiteConditions);
  const handleOnAdd = async () => {
    onAdd(dialogSiteConditions);
    if (locationId && !manual_location) {
      const checkedConditions = dialogSiteConditions.filter(
        condition => condition.checked
      );
      for (const condition of checkedConditions) {
        if (
          !librarySiteConditionIds.includes(condition?.librarySiteCondition?.id)
        ) {
          try {
            await createSiteCondition({
              variables: {
                siteConditionData: {
                  locationId,
                  librarySiteConditionId: condition?.librarySiteCondition?.id,
                  hazards: condition?.hazards?.map(hazard => ({
                    libraryHazardId: hazard.id,
                    isApplicable: hazard.isApplicable,
                    controls: hazard?.controls?.map(control => ({
                      libraryControlId: control.id,
                      isApplicable: control.isApplicable,
                    })),
                  })),
                },
              },
            });
          } catch (e) {
            console.error(e);
          }
        }
      }
    }
    onCancel();
  };

  const checkedSiteConditions = dialogSiteConditions.filter(
    condition => condition.checked
  );
  const unCheckedSiteConditions = dialogSiteConditions.filter(
    condition => !condition.checked
  );
  return (
    <>
      <BodyText className="mb-2 text-lg">{`Applicable site conditions (${checkedSiteConditions.length}) `}</BodyText>
      {checkedSiteConditions?.map(condition => (
        <div className="flex flex-row gap-2" key={condition.id}>
          <input
            type="checkbox"
            checked={condition.checked}
            onChange={() =>
              handleDialogCheckboxChange(condition?.librarySiteCondition?.id)
            }
          />
          <BodyText>{condition.name}</BodyText>
        </div>
      ))}
      <BodyText className="my-2 text-lg">{`Other site conditions (${unCheckedSiteConditions.length}) `}</BodyText>
      {unCheckedSiteConditions?.map(condition => (
        <div className="flex flex-row gap-2" key={condition.id}>
          <input
            type="checkbox"
            checked={condition.checked}
            onChange={() =>
              handleDialogCheckboxChange(condition?.librarySiteCondition?.id)
            }
          />
          <BodyText>{condition.name}</BodyText>
        </div>
      ))}

      <div className="flex flex-row justify-end gap-2">
        <ButtonSecondary label="Cancel" onClick={onCancel} />
        <ButtonPrimary label="Add" onClick={handleOnAdd} disabled={loading} />
      </div>
    </>
  );
};

const creteSiteConditions = gql`
  mutation CreateSiteCondition($siteConditionData: CreateSiteConditionInput!) {
    createSiteCondition(data: $siteConditionData) {
      id
      location {
        id
      }
    }
  }
`;
