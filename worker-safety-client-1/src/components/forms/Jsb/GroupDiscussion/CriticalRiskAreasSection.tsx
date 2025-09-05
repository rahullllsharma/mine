import type { CriticalRisk, Jsb } from "@/api/codecs";
import type { Either } from "fp-ts/lib/Either";
import * as E from "fp-ts/lib/Either";
import * as A from "fp-ts/lib/Array";
import { pipe } from "fp-ts/lib/function";
import { sequenceS } from "fp-ts/lib/Apply";
import { RiskCard } from "../../Basic/RiskCard";
import { GroupDiscussionSection } from "../../Basic/GroupDiscussionSection";

export type CriticalRiskAreasSectionData = {
  risks: CriticalRisk[];
};

export const init = (jsb: Jsb): Either<string, CriticalRiskAreasSectionData> =>
  sequenceS(E.Apply)({
    risks: pipe(
      jsb.criticalRiskAreaSelections,
      E.fromOption(() => "criticalRiskAreaSelections is missing"),
      E.map(A.map(({ name }) => name))
    ),
  });

export type CriticalRiskAreasSectionProps = CriticalRiskAreasSectionData & {
  onClickEdit?: () => void;
};

export function View({
  risks,
  onClickEdit,
}: CriticalRiskAreasSectionProps): JSX.Element {
  return (
    <GroupDiscussionSection
      title="Critical Risk Areas"
      onClickEdit={onClickEdit}
    >
      <div className="flex flex-wrap gap-4">
        {risks.map(risk => (
          <RiskCard
            className="grow w-full"
            headerClassName="bg-white"
            key={risk}
            risk={risk}
          />
        ))}
      </div>
    </GroupDiscussionSection>
  );
}
