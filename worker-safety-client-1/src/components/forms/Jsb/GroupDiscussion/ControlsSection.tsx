import type { Either } from "fp-ts/lib/Either";
import type { Jsb } from "@/api/codecs";
import { BodyText } from "@urbint/silica";
import { pipe } from "fp-ts/lib/function";
import * as E from "fp-ts/lib/Either";
import { sequenceS } from "fp-ts/lib/Apply";
import { GroupDiscussionSection } from "../../Basic/GroupDiscussionSection";

export type ControlsSectionData = {
  notes?: string;
};

export type ControlsSectionProps = ControlsSectionData & {
  onClickEdit?: () => void;
};

export const init = (jsb: Jsb): Either<string, ControlsSectionData> =>
  sequenceS(E.Apply)({
    notes: pipe(
      jsb.hazardsAndControlsNotes,
      E.fromOption(() => "hazardsAndControlsNotes is missing")
    ),
  });
export function View({
  onClickEdit,
  notes,
}: ControlsSectionProps): JSX.Element {
  return notes ? (
    <GroupDiscussionSection
      title="Controls Assessment"
      onClickEdit={onClickEdit}
    >
      <div className="bg-white p-4 mt-4">
        <BodyText className="font-semibold text-sm mb-2">
          Additional Information
        </BodyText>
        <span className="font-normal text-base">{notes}</span>
      </div>
    </GroupDiscussionSection>
  ) : (
    <></>
  );
}
