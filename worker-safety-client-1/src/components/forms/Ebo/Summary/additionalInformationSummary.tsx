import type { SummarySectionWrapperOnClickEdit } from "./summarySectionWrapper";
import type { SummaryDataGenerationError } from ".";
import type { Either } from "fp-ts/lib/Either";
import * as E from "fp-ts/lib/Either";
import SummarySectionWrapper from "./summarySectionWrapper";

export type AdditionalInformationData = {
  notes: string;
};

export type AdditionalInformationSummarySectionProps =
  SummarySectionWrapperOnClickEdit & {
    data: Either<SummaryDataGenerationError, AdditionalInformationData>;
    isReadOnly?: boolean;
  };

function AdditionalInformationSummarySection({
  onClickEdit,
  data,
  isReadOnly = false,
}: AdditionalInformationSummarySectionProps) {
  return (
    <SummarySectionWrapper
      title="Additional Information"
      onClickEdit={onClickEdit}
      isEmpty={E.isLeft(data)}
      isEmptyText="No additional information provided"
      isReadOnly={isReadOnly}
    >
      {E.isRight(data) && <span>{data.right.notes}</span>}
    </SummarySectionWrapper>
  );
}

export default AdditionalInformationSummarySection;
