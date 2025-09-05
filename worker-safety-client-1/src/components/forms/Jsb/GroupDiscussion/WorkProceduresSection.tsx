import type { Either } from "fp-ts/lib/Either";
import type { Jsb, WorkProcedure } from "@/api/codecs";
import * as O from "fp-ts/lib/Option";
import {
  ActionLabel,
  BodyText,
  CaptionText,
  SectionHeading,
  SectionSubheading,
} from "@urbint/silica";
import { sequenceS } from "fp-ts/lib/Apply";
import * as E from "fp-ts/lib/Either";
import { pipe } from "fp-ts/lib/function";
import { useState } from "react";
import Image from "next/image";
import ButtonIcon from "@/components/shared/button/icon/ButtonIcon";
import madImage from "public/assets/mad.png";
import Link from "@/components/shared/link/Link";
import FourRulesOfCoverUp from "public/assets/4rulesofcoverup.png";
import { WorkProcedureLinks } from "src/components/forms/Jsb/WorkProcedureLinks";
import { wpLabel } from "../WorkProcedures";
import { Dialog } from "../../Basic/Dialog/Dialog";
import { GroupDiscussionSection } from "../../Basic/GroupDiscussionSection";

export type WorkProceduresSectionData = {
  workProcedures: WorkProcedure[];
  otherWorkProcedures: string | null;
};

export const init = (jsb: Jsb): Either<string, WorkProceduresSectionData> =>
  sequenceS(E.Apply)({
    workProcedures: pipe(
      jsb.workProcedureSelections,
      E.fromOption(() => "workProcedures is missing")
    ),
    otherWorkProcedures: E.right(
      pipe(
        jsb.otherWorkProcedures,
        O.fold(
          () => null,
          value => value
        )
      )
    ),
  });

export type WorkProceduresSectionProps = WorkProceduresSectionData & {
  onClickEdit?: () => void;
};

export function View({
  onClickEdit,
  workProcedures,
  otherWorkProcedures,
}: WorkProceduresSectionProps): JSX.Element {
  const [showMADImage, setShowMADImage] = useState(false);
  const [showFourRulesOfCoverUpImage, setShowFourRulesOfCoverUpImage] =
    useState(false);

  const toggleMADImage = (e: React.MouseEvent) => {
    e.preventDefault();
    setShowMADImage(!showMADImage);
  };

  const toggleFourRulesofcoverupImage = (e: React.MouseEvent) => {
    e.preventDefault();
    setShowFourRulesOfCoverUpImage(!showFourRulesOfCoverUpImage);
  };

  return (
    <GroupDiscussionSection title="Work Procedures" onClickEdit={onClickEdit}>
      <div className="bg-white py-5 px-4">
        {workProcedures.map(workProcedure => (
          <div key={workProcedure.id} className="mb-4 gap-4">
            <ActionLabel className="font-semibold text-gray-600 block">
              {wpLabel(workProcedure.id)}
            </ActionLabel>

            {workProcedure.id === "mad" && (
              <>
                <Link
                  label="Minimum Approach Distance"
                  onClick={toggleMADImage}
                  iconRight="external_link"
                  className="gap-2 flex items-center w-full md:w-auto"
                />
                <SectionSubheading className="text-base font-medium text-gray-600 mb-2">
                  Minimum Approach Distance
                </SectionSubheading>
                {showMADImage && (
                  <Dialog
                    header={
                      <div className="flex flex-row justify-between">
                        <SectionHeading className="text-xl font-semibold">
                          Minimum Approach Distance
                        </SectionHeading>
                        <ButtonIcon
                          iconName="close_big"
                          onClick={toggleMADImage}
                        />
                      </div>
                    }
                  >
                    <Image
                      src={madImage}
                      alt="Minimum Approach Distance"
                      objectFit="contain"
                    />
                  </Dialog>
                )}
              </>
            )}
            {workProcedure.id === "four_rules_of_cover_up" && (
              <div>
                <Link
                  label="4 Rules of Cover-Up"
                  onClick={toggleFourRulesofcoverupImage}
                  iconRight="external_link"
                  className="gap-2 flex items-center w-full md:w-auto"
                />
                {showFourRulesOfCoverUpImage && (
                  <Dialog
                    size="flex"
                    header={
                      <div className="flex flex-row justify-between">
                        <SectionHeading className="text-xl font-semibold">
                          4 Rules of cover up
                        </SectionHeading>
                        <ButtonIcon
                          iconName="close_big"
                          onClick={toggleFourRulesofcoverupImage}
                        />
                      </div>
                    }
                  >
                    <Image
                      src={FourRulesOfCoverUp}
                      alt="4 Rules of Cover-Up"
                      width={630}
                      height={300}
                      layout="intrinsic"
                    />
                  </Dialog>
                )}
              </div>
            )}
            <WorkProcedureLinks id={workProcedure.id} />
            {workProcedure.values.length > 0 && (
              <ul className="list-disc list-inside ml-4 mb-2">
                {workProcedure.values.map(item => (
                  <li key={item}>
                    <BodyText className="text-base font-normal text-neutral-shade-75 inline">
                      {item}
                    </BodyText>
                  </li>
                ))}
              </ul>
            )}
          </div>
        ))}
        <WorkProcedureLinks id="best_work_practices" />
        {otherWorkProcedures && (
          <div>
            <CaptionText className="block mt-6 md:text-sm text-neutral-shade-75 font-semibold leading-normal mb-2">
              If applicable, specify other work procedures or special
              precautions
            </CaptionText>
            <BodyText>{otherWorkProcedures}</BodyText>
          </div>
        )}
      </div>
    </GroupDiscussionSection>
  );
}
