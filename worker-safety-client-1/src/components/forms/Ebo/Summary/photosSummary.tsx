/* eslint-disable @next/next/no-img-element */
import type { SummarySectionWrapperOnClickEdit } from "./summarySectionWrapper";
import type {
  SummaryDataGenerationError,
  Model as SummaryModel,
  Action as SummaryAction,
} from ".";
import type { FileWithUploadPolicy } from "../PhotosSection";
import type { Either } from "fp-ts/lib/Either";
import * as A from "fp-ts/lib/Array";
import * as E from "fp-ts/lib/Either";
import * as M from "fp-ts/lib/Map";
import * as O from "fp-ts/lib/Option";
import cx from "classnames";
import { pipe, flow, constant } from "fp-ts/lib/function";
import { isResolved } from "@/utils/deferred";
import { ordFileName } from "../PhotosSection";
import SummarySectionWrapper from "./summarySectionWrapper";
import { SelectedPhotoChanged } from ".";

export type PhotosData = {
  uploadedFiles: Map<string, FileWithUploadPolicy>;
};

export type PhotosSummarySectionProps = SummarySectionWrapperOnClickEdit & {
  data: Either<SummaryDataGenerationError, PhotosData>;
  model: SummaryModel;
  dispatch: (action: SummaryAction) => void;
  isReadOnly?: boolean;
};

function PhotosSummarySection({
  onClickEdit,
  data,
  model,
  dispatch,
  isReadOnly = false,
}: PhotosSummarySectionProps) {
  return (
    <SummarySectionWrapper
      title={
        E.isLeft(data)
          ? "Photos (0)"
          : `Photos (${M.size(data.right.uploadedFiles)})`
      }
      onClickEdit={onClickEdit}
      isEmpty={E.isLeft(data)}
      isEmptyText="No photos selected to upload"
      isReadOnly={isReadOnly}
    >
      {E.isRight(data) && (
        <div className="max-w-[720px] flex flex-col gap-5">
          {O.isSome(model.selectedPhoto) &&
            isResolved(model.selectedPhoto.value.uploadPolicy) &&
            E.isRight(model.selectedPhoto.value.uploadPolicy.value) && (
              <>
                <img
                  src={
                    model.selectedPhoto.value.uploadPolicy.value.right.signedUrl
                  }
                  alt={model.selectedPhoto.value.name}
                  className="w-full object-contain"
                />
                <div className="w-full flex flex-row gap-4 overflow-x-scroll justify-start">
                  {pipe(
                    data.right.uploadedFiles,
                    M.filter(f => f.isUploaded),
                    M.toArray(ordFileName),
                    A.map(f => f[1]),
                    A.map(f => (
                      <img
                        key={f.name}
                        src={pipe(
                          f.properties,
                          O.map(p => p.signedUrl),
                          O.getOrElse(() => "")
                        )}
                        alt={f.name}
                        onClick={flow(
                          constant(pipe(f, O.of)),
                          SelectedPhotoChanged,
                          dispatch
                        )}
                        className={cx(
                          "rounded-sm w-24 h-24 cursor-pointer object-cover object-left-top",
                          {
                            ["border-2 border-[#005870]"]:
                              O.isSome(model.selectedPhoto) &&
                              model.selectedPhoto.value.name === f.name,
                          }
                        )}
                      />
                    ))
                  )}
                </div>
              </>
            )}
        </div>
      )}
    </SummarySectionWrapper>
  );
}

export default PhotosSummarySection;
