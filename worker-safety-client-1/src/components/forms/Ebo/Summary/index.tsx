import type * as t from "io-ts";
import type { Ebo, EboPhoto } from "@/api/codecs";
import type { ObservationDetailsSummarySectionProps } from "./observationDetailsSummary";
import type { AdditionalInformationSummarySectionProps } from "./additionalInformationSummary";
import type { HistoricIncidentsSummarySectionProps } from "./historicIncidentsSummary";
import type { HazardsSummarySectionProps } from "./hazardsSummary";
import type { PhotosSummarySectionProps } from "./photosSummary";
import type { FileWithUploadPolicy } from "../PhotosSection";
import type { ChildProps } from "@/utils/reducerWithEffect";
import type { Option } from "fp-ts/lib/Option";
import * as A from "fp-ts/lib/Array";
import * as E from "fp-ts/lib/Either";
import * as O from "fp-ts/lib/Option";
import { pipe } from "fp-ts/lib/function";
import { Eq as EqString } from "fp-ts/string";

import { SectionHeading } from "@urbint/silica";
import StepLayout from "@/components/forms/StepLayout";
import { Resolved } from "@/utils/deferred";
import ObservationDetailsSummarySection from "./observationDetailsSummary";
import AdditionalInformationSummarySection from "./additionalInformationSummary";
import PhotosSummarySection from "./photosSummary";
import HistoricIncidentsSummarySection from "./historicIncidentsSummary";
import HazardsSummarySection from "./hazardsSummary";

export type SummaryDataGenerationError = t.Errors | { message: string };

export type SummarySectionProps = {
  observationDetails: ObservationDetailsSummarySectionProps;
  hazards: HazardsSummarySectionProps;
  historicIncidents: HistoricIncidentsSummarySectionProps;
  additionalInformation: AdditionalInformationSummarySectionProps;
  photos: PhotosSummarySectionProps;
};

export type Model = {
  selectedPhoto: Option<FileWithUploadPolicy>;
  sectionErrors: string[];
};

export const HAS_ERROR_ON_OTHER_FORM_SECTIONS =
  "HAS_ERROR_ON_OTHER_FORM_SECTIONS";

const sectionErrorTexts = {
  HAS_ERROR_ON_OTHER_FORM_SECTIONS:
    "Please complete other form sections before completing the Energy Based Observation",
};

export const SetSectionErrors = (value: string[]): Action => ({
  type: "SetSectionErrors",
  value,
});

export const initiateSummaryModel = (
  ebo: Option<Ebo>
): Option<FileWithUploadPolicy> =>
  pipe(
    ebo,
    O.chain(e => e.contents.photos),
    O.chain(A.head),
    O.fold(
      () => O.none,
      (p: EboPhoto): Option<FileWithUploadPolicy> =>
        O.some({
          name: p.name,
          file: O.none,
          isUploaded: true,
          uploadPolicy: Resolved(
            E.right({
              id: p.id,
              url: p.url,
              signedUrl: p.signedUrl,
              fields: "",
            })
          ),
          properties: O.of({
            id: p.id,
            name: p.name,
            displayName: p.displayName,
            size: p.size,
            url: p.url,
            signedUrl: p.signedUrl,
          }),
        })
    )
  );

export function init(selectedPhoto: Option<FileWithUploadPolicy>): Model {
  return {
    selectedPhoto,
    sectionErrors: [],
  };
}

export const toSaveEboInput = () => {
  return E.of({ summary: { viewed: true } });
};

export type Action =
  | { type: "SelectedPhotoChanged"; photo: Option<FileWithUploadPolicy> }
  | { type: "SetSectionErrors"; value: string[] }; // Add this action type

export const SelectedPhotoChanged = (
  photo: Option<FileWithUploadPolicy>
): Action => ({
  type: "SelectedPhotoChanged",
  photo,
});

export const update = (model: Model, action: Action): Model => {
  switch (action.type) {
    case "SelectedPhotoChanged":
      return { ...model, selectedPhoto: action.photo };
    case "SetSectionErrors":
      return { ...model, sectionErrors: action.value };
    default:
      return model; // Add a default return statement
  }
};

export type Props = ChildProps<Model, Action> &
  SummarySectionProps & {
    isReadOnly: boolean;
  };

export const View = (props: Props) => {
  const { model, dispatch, isReadOnly } = props;

  return (
    <StepLayout>
      <div className="p-4 md:p-0">
        <div className="flex flex-col gap-4">
          {pipe(
            model.sectionErrors,
            A.elem(EqString)(HAS_ERROR_ON_OTHER_FORM_SECTIONS)
          ) && (
            <div className="font-semibold text-system-error-40 text-sm mt-4">
              {sectionErrorTexts[HAS_ERROR_ON_OTHER_FORM_SECTIONS]}
            </div>
          )}
          <SectionHeading className="text-xl font-semibold">
            Energy-Based Observation Summary
          </SectionHeading>
          <ObservationDetailsSummarySection
            {...props.observationDetails}
            isReadOnly={isReadOnly}
          />
          <HazardsSummarySection {...props.hazards} isReadOnly={isReadOnly} />
          <HistoricIncidentsSummarySection
            {...props.historicIncidents}
            isReadOnly={isReadOnly}
          />
          <AdditionalInformationSummarySection
            {...props.additionalInformation}
            isReadOnly={isReadOnly}
          />
          <PhotosSummarySection
            {...props.photos}
            model={model}
            dispatch={dispatch}
            isReadOnly={isReadOnly}
          />
        </div>
      </div>
    </StepLayout>
  );
};
