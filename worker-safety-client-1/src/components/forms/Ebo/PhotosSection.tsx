import type { Deferred } from "@/utils/deferred";
import type { StepSnapshot } from "../Utils";
import type { Api, ApiResult } from "@/api/api";
import type { ChildProps, Effect } from "@/utils/reducerWithEffect";
import type { Either } from "fp-ts/Either";
import type { Option } from "fp-ts/Option";
import type { Ebo, EboPhoto, FileUploadPolicy } from "@/api/codecs";
import type { NonEmptyArray } from "fp-ts/lib/NonEmptyArray";
import { array } from "fp-ts";
import * as A from "fp-ts/lib/Array";
import * as E from "fp-ts/lib/Either";
import * as Eq from "fp-ts/lib/Eq";
import * as Json from "fp-ts/lib/Json";
import * as M from "fp-ts/lib/Map";
import * as O from "fp-ts/lib/Option";
import * as Ord from "fp-ts/lib/Ord";
import * as R from "fp-ts/lib/Record";
import * as SG from "fp-ts/lib/Semigroup";
import { Eq as EqString, Ord as OrdString } from "fp-ts/lib/string";
import { constant, constNull, flow, pipe } from "fp-ts/lib/function";
import { useMemo } from "react";
import Image from "next/image";
import { Icon, SectionHeading } from "@urbint/silica";
import * as NEA from "fp-ts/lib/NonEmptyArray";
import StepLayout from "@/components/forms/StepLayout";
import * as UploadButton from "@/components/forms/Basic/UploadButton/UploadButton";
import * as Alert from "@/components/forms/Alert";
import { effectOfAsync, effectsBatch } from "@/utils/reducerWithEffect";
import { NotStarted, Resolved } from "@/utils/deferred";
import { fileUploadPolicyFieldsCodec } from "@/api/codecs";
import { snapshotMap } from "../Utils";
import { downscaleImageAsTask } from "../Basic/UploadButton/utils";

const maxFiles: Readonly<number> = 10;
export const maxFileSize: Readonly<number> = 5_000_000;
const allowMultiple: Readonly<boolean> = true;
const allowedExtensions = ".apng,.avif,.gif,.jpg,.jpeg,.png,.webp";
const formatAllowedExtensions = allowedExtensions
  .replace(/\./g, "")
  .replace(/\,/g, ", ")
  .toUpperCase();

type FileUploadValidationErrorTypes =
  | "no_file_selected"
  | "max_size_exceeded"
  | "too_many_files"
  | "fields_json_not_valid";

type FileUploadValidationError = {
  type: FileUploadValidationErrorTypes;
  msg: string;
};

export type FileProperties = {
  id: string;
  name: string;
  displayName: string;
  size: string;
  url: string;
  signedUrl: string;
};

export type FileWithUploadPolicy = {
  name: string;
  file: Option<File>;
  isUploaded: boolean;
  uploadPolicy: Deferred<ApiResult<FileUploadPolicy>>;
  properties: Option<FileProperties>;
};

const eqFileName = Eq.contramap((fileName: string) => fileName)(EqString);

export const ordFileName = Ord.contramap((fileName: string) => fileName)(
  OrdString
);

const eqUploadedFileTuple = Eq.contramap(
  (fileTuple: [string, FileWithUploadPolicy]) => fileTuple[0]
)(EqString);

const getFileNameWithoutMimetype = (fileName: string): string =>
  fileName.split(".")[0];

const validateAnyFileSelected = (
  sfs: File[]
): Either<FileUploadValidationError, File[]> =>
  pipe(
    sfs,
    E.fromPredicate(
      s => s.length !== 0,
      () => ({ type: "no_file_selected", msg: "No file is selected." })
    )
  );

const validateSelectedMaxFiles = (
  sfs: File[]
): Either<FileUploadValidationError, File[]> =>
  pipe(
    sfs,
    E.fromPredicate(
      s => s.length <= maxFiles,
      () => ({
        type: "too_many_files",
        msg: `Maximum allowed file count (${maxFiles}) is exceeded.`,
      })
    )
  );

// TODO: this function has been moved into `Utils` folder and the return type has been changed to `Either<ApiError, FormData`.
// Remove this and use the one from `Utils` folder.
const generateFileUploadFormData =
  (file: File) =>
  (fields: string): FormData => {
    const formData = new FormData();

    const appendFieldsToFormData = (fd: FormData): FormData => {
      pipe(
        pipe(
          fields,
          Json.parse,
          E.chainW(fileUploadPolicyFieldsCodec.decode),
          E.map(R.toUnfoldable(array))
        ),
        E.map(A.map(field => fd.append(field[0], field[1])))
      );

      return fd;
    };

    const appendFileToFormData = (fd: FormData): FormData => {
      fd.append("file", file);

      return fd;
    };

    return pipe(formData, appendFieldsToFormData, appendFileToFormData);
  };

const isUploading = (model: Model) =>
  pipe(
    model.uploadedFiles,
    M.toArray(ordFileName),
    A.some(f => !f[1].isUploaded)
  );

export type Model = {
  uploadedFiles: Map<string, FileWithUploadPolicy>;
};

export type PhotosEffect =
  | { type: "ComponentEffect"; effect: Effect<Action> }
  | { type: "AlertAction"; action: Alert.Action }
  | { type: "NoEffect" };

const ComponentEffect = (effect: Effect<Action>): PhotosEffect => ({
  type: "ComponentEffect",
  effect,
});

const AlertAction = (action: Alert.Action): PhotosEffect => ({
  type: "AlertAction",
  action,
});

const NoEffect = (): PhotosEffect => ({
  type: "NoEffect",
});

export function init(ebo: Option<Ebo>): Model {
  return pipe(
    ebo,
    O.chain(e => e.contents.photos),
    O.fold(
      () => ({
        uploadedFiles: new Map(),
      }),
      photos => ({
        uploadedFiles: pipe(
          photos,
          A.map(
            (p: EboPhoto): FileWithUploadPolicy => ({
              name: getFileNameWithoutMimetype(p.name),
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
                name: getFileNameWithoutMimetype(p.name),
                displayName: getFileNameWithoutMimetype(p.displayName),
                size: p.size,
                url: p.url,
                signedUrl: p.signedUrl,
              }),
            })
          ),
          A.map((p): [string, FileWithUploadPolicy] => [p.name, p]),
          M.fromFoldable(
            eqFileName,
            SG.first<FileWithUploadPolicy>(),
            A.Foldable
          )
        ),
      })
    )
  );
}

export const makeSnapshot = (model: Model): StepSnapshot => {
  return {
    uploadedFiles: pipe(
      model.uploadedFiles,
      M.map(ufs => ufs.properties),
      M.map(O.getOrElseW(constNull)),
      snapshotMap
    ),
  };
};

export const toSaveEboInput = (model: Model) => {
  return pipe(
    model.uploadedFiles,
    M.toArray(ordFileName),
    A.map(f => f[1].properties),
    A.compact,
    f => ({ photos: f }),
    E.of
  );
};

export type Action =
  | { type: "FilesSelected"; value: FileList }
  | { type: "DownscaleValidatedFiles"; file: File }
  | {
      type: "GenerateFileUploadPolicy";
      result: ApiResult<NonEmptyArray<FileUploadPolicy>>;
      name: string;
    }
  | {
      type: "UploadFileToGCS";
      result: ApiResult<unknown>;
      name: string;
      uploadPolicy: FileUploadPolicy;
    }
  | {
      type: "RemoveSelectedFile";
      name: string;
    };

export const FilesSelected = (value: FileList): Action => ({
  type: "FilesSelected",
  value,
});

export const DownscaleValidatedFiles = (file: File): Action => ({
  type: "DownscaleValidatedFiles",
  file,
});

export const GenerateFileUploadPolicy =
  (name: string) =>
  (result: ApiResult<NonEmptyArray<FileUploadPolicy>>): Action => ({
    type: "GenerateFileUploadPolicy",
    result,
    name,
  });

export const UploadFileToGCS =
  (name: string) =>
  (uploadPolicy: FileUploadPolicy) =>
  (result: ApiResult<unknown>): Action => ({
    type: "UploadFileToGCS",
    result,
    name,
    uploadPolicy,
  });

export const RemoveSelectedFile = (name: string): Action => ({
  type: "RemoveSelectedFile",
  name,
});

export const update =
  (api: Api) =>
  (model: Model, action: Action): [Model, PhotosEffect] => {
    switch (action.type) {
      case "FilesSelected": {
        return pipe(
          action.value,
          Array.from,
          validateAnyFileSelected,
          E.chain(validateSelectedMaxFiles),
          E.fold(
            (err): [Model, PhotosEffect] => [
              { ...model },
              pipe(err.msg, Alert.AlertRequested("error"), AlertAction),
            ],
            (fs: File[]): [Model, PhotosEffect] => {
              const selectedFiles: FileWithUploadPolicy[] = pipe(
                fs,
                A.map(f => ({
                  name: getFileNameWithoutMimetype(f.name),
                  file: O.some(f),
                  isUploaded: false,
                  uploadPolicy: NotStarted(),
                  properties: O.none,
                }))
              );

              const filteredSelectedFiles: FileWithUploadPolicy[] = pipe(
                selectedFiles,
                A.filter(f =>
                  pipe(
                    model.uploadedFiles,
                    M.lookupWithKey(eqFileName)(f.name),
                    O.isNone
                  )
                )
              );

              const updatedUploadedFiles: Map<string, FileWithUploadPolicy> =
                pipe(
                  filteredSelectedFiles,
                  A.map((f): [string, FileWithUploadPolicy] => [f.name, f]),
                  A.union(eqUploadedFileTuple)(
                    pipe(model.uploadedFiles, M.toArray(ordFileName))
                  ),
                  M.fromFoldable(
                    eqFileName,
                    SG.last<FileWithUploadPolicy>(),
                    A.Foldable
                  )
                );

              return [
                { ...model, uploadedFiles: updatedUploadedFiles },
                pipe(
                  fs,
                  A.map(file =>
                    effectOfAsync(
                      downscaleImageAsTask(file)(maxFileSize),
                      DownscaleValidatedFiles
                    )
                  ),
                  effectsBatch,
                  ComponentEffect
                ),
              ];
            }
          )
        );
      }
      case "DownscaleValidatedFiles": {
        const fileWithUploadPolicy: FileWithUploadPolicy = {
          name: getFileNameWithoutMimetype(action.file.name),
          file: O.some(action.file),
          isUploaded: false,
          uploadPolicy: NotStarted(),
          properties: O.none,
        };

        return [
          {
            ...model,
            uploadedFiles: pipe(
              model.uploadedFiles,
              M.upsertAt(eqFileName)(
                fileWithUploadPolicy.name,
                fileWithUploadPolicy
              )
            ),
          },
          pipe(
            fileWithUploadPolicy,
            f =>
              effectOfAsync(
                api.common.generateFileUploadPolicies(1),
                GenerateFileUploadPolicy(f.name)
              ),
            ComponentEffect
          ),
        ];
      }
      case "GenerateFileUploadPolicy": {
        const uploadPolicy = pipe(action.result, E.map(NEA.head), O.fromEither);

        const modifiedFile = pipe(
          model.uploadedFiles,
          M.lookupWithKey(eqFileName)(action.name),
          O.map(uf => uf[1]),
          O.map(f => ({
            ...f,
            uploadPolicy: Resolved(
              pipe(
                action.result,
                E.map(fup => NEA.head(fup))
              )
            ),
          }))
        );

        if (
          E.isRight(action.result) &&
          O.isSome(uploadPolicy) &&
          O.isSome(modifiedFile) &&
          O.isSome(modifiedFile.value.file)
        ) {
          const payload = generateFileUploadFormData(
            modifiedFile.value.file.value
          )(uploadPolicy.value.fields);

          return [
            {
              ...model,
              uploadedFiles: pipe(
                model.uploadedFiles,
                M.upsertAt(eqFileName)(action.name, modifiedFile.value)
              ),
            },
            pipe(
              effectOfAsync(
                api.common.uploadFileToGCS(uploadPolicy.value.url)(payload),
                UploadFileToGCS(action.name)(uploadPolicy.value)
              ),
              ComponentEffect
            ),
          ];
        } else {
          return [
            {
              ...model,
              uploadedFiles: pipe(
                model.uploadedFiles,
                M.deleteAt(eqFileName)(action.name)
              ),
            },
            NoEffect(),
          ];
        }
      }
      case "UploadFileToGCS": {
        const modifiedFile = pipe(
          model.uploadedFiles,
          M.lookupWithKey(eqFileName)(action.name),
          O.map(uf => uf[1]),
          O.map(f => ({
            ...f,
            isUploaded: true,
            properties: O.some({
              id: action.uploadPolicy.id,
              name: action.name,
              displayName: action.name,
              size: O.isSome(f.file)
                ? `${f.file.value.size / 1000} KB`
                : "0 KB",
              url: action.uploadPolicy.url + action.uploadPolicy.id,
              signedUrl: action.uploadPolicy.signedUrl,
            }),
          }))
        );

        if (E.isRight(action.result) && O.isSome(modifiedFile)) {
          return [
            {
              ...model,
              uploadedFiles: pipe(
                model.uploadedFiles,
                M.upsertAt(eqFileName)(action.name, modifiedFile.value)
              ),
            },
            NoEffect(),
          ];
        } else {
          return [
            {
              ...model,
              uploadedFiles: pipe(
                model.uploadedFiles,
                M.deleteAt(eqFileName)(action.name)
              ),
            },
            NoEffect(),
          ];
        }
      }
      case "RemoveSelectedFile": {
        return [
          {
            ...model,
            uploadedFiles: pipe(
              model.uploadedFiles,
              M.deleteAt(eqFileName)(action.name)
            ),
          },
          NoEffect(),
        ];
      }
    }
  };

export type Props = ChildProps<Model, Action> & {
  isReadOnly: boolean;
};

export function View(props: Props): JSX.Element {
  const { model, dispatch, isReadOnly } = props;

  const uploadButtonConfigs: UploadButton.UploadButtonConfigs = {
    icon: "image_alt",
    label: "Add photos",
    isLoading: isUploading(model),
    allowMultiple: allowMultiple,
    allowedExtensions: allowedExtensions,
    maxFileSize: 10 * 1024 * 1024, // 10 MB
  };

  const uploadedFilesCount = useMemo(
    () =>
      pipe(
        model.uploadedFiles,
        M.filter(f => f.isUploaded),
        M.size
      ),
    [model]
  );

  return (
    <StepLayout>
      <div className="p-4 md:p-0">
        <div className="max-w-[760px]  flex flex-col md:flex-row justify-start md:justify-between items-start mb-4">
          <div className="flex flex-col">
            <SectionHeading className="text-xl font-semibold">
              Photos ({uploadedFilesCount})
            </SectionHeading>
            <div className="text-xs font-normal text-neutral-shade-75 mt-0.5">
              <p>{formatAllowedExtensions}</p>
            </div>
          </div>
          {!isReadOnly && (
            <UploadButton.View
              configs={uploadButtonConfigs}
              className="mt-2 md:mt-0"
              onUpload={flow(FilesSelected, dispatch)}
            />
          )}
        </div>
        {uploadedFilesCount > 0 ? (
          <div className="w-full flex flex-row flex-wrap min-h-[80px] justify-start items-start gap-2 p-2 border-neutral-shade-18 border rounded">
            {pipe(
              model.uploadedFiles,
              M.filter(f => f.isUploaded),
              M.toArray(ordFileName),
              A.map(f => f[1]),
              A.map(f => (
                <div key={f.name} className="relative w-20 h-20">
                  <Image
                    src={pipe(
                      f.properties,
                      O.map(p => p.signedUrl),
                      O.getOrElse(() => "")
                    )}
                    height={80}
                    width={80}
                    alt={f.name}
                    className="absolute inset-0 z-0 object-cover object-left-top"
                  />
                  <Icon
                    name="off_outline_close"
                    className="absolute right-0.5 top-0.5 text-2xl leading-6 text-white bg-black bg-opacity-60 rounded-full cursor-pointer"
                    onClick={flow(
                      constant(f.name),
                      RemoveSelectedFile,
                      dispatch
                    )}
                  />
                </div>
              ))
            )}
          </div>
        ) : (
          <span className="font-normal text-base">No photos uploaded</span>
        )}
      </div>
    </StepLayout>
  );
}
