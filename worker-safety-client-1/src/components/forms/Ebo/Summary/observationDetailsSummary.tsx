import type { SummarySectionWrapperOnClickEdit } from "./summarySectionWrapper";
import type { SummaryDataGenerationError } from ".";
import type { WorkType } from "@/api/codecs";
import type { Either } from "fp-ts/lib/Either";
import type { Option } from "fp-ts/lib/Option";
import type * as tt from "io-ts-types";
import * as A from "fp-ts/lib/Array";
import * as E from "fp-ts/lib/Either";
import * as O from "fp-ts/lib/Option";
import { pipe } from "fp-ts/lib/function";
import { BodyText, Subheading } from "@urbint/silica";
import { OptionalView } from "@/components/common/Optional";
import { useTenantStore } from "@/store/tenant/useTenantStore.store";
import { changeLabelOnBasisOfTenant } from "../TenantLabel/LabelOnBasisOfTenant";
import SummarySectionWrapper from "./summarySectionWrapper";

export type ObservationDetailsData = {
  observationDate: string;
  observationTime: string;
  workOrderNumber: string;
  workLocation: string | tt.NonEmptyString;
  departmentObserved: string;
  opCoObserved: string;
  subOpCoObserved?: string;
  workType: WorkType[];
  latitude: Option<number>;
  longitude: Option<number>;
};

export type ObservationDetailsSummarySectionProps =
  SummarySectionWrapperOnClickEdit & {
    data: Either<SummaryDataGenerationError, ObservationDetailsData>;
    isReadOnly?: boolean;
  };

function ObservationDetailsSummarySection({
  onClickEdit,
  data,
  isReadOnly = false,
}: ObservationDetailsSummarySectionProps) {
  const { name: tenantName } = useTenantStore().tenant;
  const departmentObservedLabel = changeLabelOnBasisOfTenant(
    tenantName,
    "Department Observed"
  );
  const subOpCoObservedLabel = changeLabelOnBasisOfTenant(
    tenantName,
    "Sub OpCo Observed"
  );
  return (
    <SummarySectionWrapper
      title="Observation Details"
      subtitle="Job Details"
      onClickEdit={onClickEdit}
      isEmpty={E.isLeft(data)}
      isReadOnly={isReadOnly}
    >
      {E.isRight(data) && (
        <div className="grid grid-cols-2 gap-4">
          <div className="flex-1">
            <BodyText className="text-sm text-neutral-shade-100 font-semibold mb-1">
              Observation Date
            </BodyText>
            <span className="text-base font-normal">
              {data.right.observationDate}
            </span>
          </div>
          <div className="flex-1">
            <BodyText className="text-sm text-neutral-shade-100 font-semibold mb-1">
              Observation Time
            </BodyText>
            <span className="text-base font-normal">
              {data.right.observationTime}
            </span>
          </div>
          <div className="flex-1">
            <BodyText className="text-sm text-neutral-shade-100 font-semibold mb-1">
              WO Number
            </BodyText>
            <span className="text-base font-normal">
              {data.right.workOrderNumber}
            </span>
          </div>
          <div className="flex-1">
            <BodyText className="text-sm text-neutral-shade-100 font-semibold mb-1">
              OpCo Observed
            </BodyText>
            <span className="text-base font-normal">
              {data.right.opCoObserved}
            </span>
          </div>
          <OptionalView
            value={
              data.right.subOpCoObserved
                ? O.some(data.right.subOpCoObserved)
                : O.none
            }
            render={subOpCo => (
              <div className="flex-1">
                <BodyText className="text-sm text-neutral-shade-100 font-semibold mb-1">
                  {subOpCoObservedLabel}
                </BodyText>
                <span className="text-base font-normal">{subOpCo}</span>
              </div>
            )}
          />
          <div className="flex-1">
            <BodyText className="text-sm text-neutral-shade-100 font-semibold mb-1">
              {departmentObservedLabel}
            </BodyText>
            <span className="text-base font-normal">
              {data.right.departmentObserved}
            </span>
          </div>
          <div className="flex-1">
            <BodyText className="text-sm text-neutral-shade-100 font-semibold mb-1">
              Work Type(s)
            </BodyText>
            <span className="text-base font-normal">
              {pipe(
                data.right.workType,
                A.map(wt => wt.name)
              ).join(" - ")}
            </span>
          </div>
          <div>
            <Subheading className="text-lg font-semibold text-neutral-shade-75">
              Location Details
            </Subheading>
          </div>
          <div className="col-span-2">
            <BodyText className="text-sm text-neutral-shade-100 font-semibold mb-1 ">
              Work Location
            </BodyText>
            <div className="text-base font-normal">
              {data.right.workLocation}
            </div>
          </div>
          <div className="flex-1">
            <BodyText className="text-sm text-neutral-shade-100 font-semibold mb-1">
              Latitude
            </BodyText>
            <span className="text-base font-normal">
              {O.isSome(data.right.latitude) ? data.right.latitude.value : "-"}
            </span>
          </div>
          <div className="flex-1">
            <BodyText className="text-sm text-neutral-shade-100 font-semibold mb-1">
              Longitude
            </BodyText>
            <span className="text-base font-normal">
              {O.isSome(data.right.longitude)
                ? data.right.longitude.value
                : "-"}
            </span>
          </div>
        </div>
      )}
    </SummarySectionWrapper>
  );
}

export default ObservationDetailsSummarySection;
