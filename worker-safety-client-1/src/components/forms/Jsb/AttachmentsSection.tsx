import type { Deferred } from "@/utils/deferred";
import type { Api, ApiError, ApiResult } from "@/api/api";
import type { ChildProps, Effect } from "@/utils/reducerWithEffect";
import type { Either } from "fp-ts/Either";
import type { Option } from "fp-ts/Option";
import type {
  JsbPhoto,
  FileUploadPolicy,
  Jsb,
  JsbDocument,
} from "@/api/codecs";
import type { NonEmptyArray } from "fp-ts/lib/NonEmptyArray";
import type { MenuItemProps } from "@/components/shared/dropdown/Dropdown";
import type { EditedFile } from "./EditDocument";
import type { FileCategory } from "@/api/generated/types";
import type { StepSnapshot } from "../Utils";
import * as A from "fp-ts/lib/Array";
import * as E from "fp-ts/lib/Either";
import * as M from "fp-ts/lib/Map";
import * as O from "fp-ts/lib/Option";
import * as SG from "fp-ts/lib/Semigroup";
import { Eq as EqString, Ord as OrdString } from "fp-ts/lib/string";
import {
  constNull,
  constant,
  flow,
  pipe,
  constUndefined,
} from "fp-ts/lib/function";
import { useMemo } from "react";
import Image from "next/image";
import { Icon, SectionHeading } from "@urbint/silica";
import * as NEA from "fp-ts/lib/NonEmptyArray";
import { snd } from "fp-ts/lib/Tuple";
import StepLayout from "@/components/forms/StepLayout";
import * as UploadButton from "@/components/forms/Basic/UploadButton/UploadButton";
import * as Alert from "@/components/forms/Alert";
import { effectOfAsync, effectsBatch } from "@/utils/reducerWithEffect";
import { InProgress, NotStarted, Resolved } from "@/utils/deferred";
import Dropdown from "@/components/shared/dropdown/Dropdown";
import { download } from "@/components/upload/utils";
import Modal from "@/components/shared/modal/Modal";
import { convertDateToString, convertToDate } from "@/utils/date/helper";
import { generateFileUploadFormData, snapshotMap } from "../Utils";
import EditDocument from "./EditDocument";

export type AttachmentsData = {
  photos: Map<string, FileWithUploadPolicy>;
  documents: Map<string, FileWithUploadPolicy>;
};

function fileUploadSnapshot(file: FileWithUploadPolicy): StepSnapshot {
  return {
    name: file.name,
    file: pipe(
      file.file,
      O.fold(constNull, f => ({ name: f.name, size: f.size }))
    ),
    properties: O.getOrElseW(constNull)(file.properties),
  };
}

const maxFiles: Readonly<number> = 10;
const maxFileSize: Readonly<number> = 10_000_000;
const maxFileSizeText: Readonly<number> = maxFileSize / 1_000_000;
const allowMultiple: Readonly<boolean> = true;
const allowedPhotoExtensions =
  ".apng,.avif,.gif,.jpg,.jpeg,.png,.svg,.webp";
const formatAllowedPhotoExtensions = allowedPhotoExtensions
  .replace(/\./g, "")
  .replace(/\,/g, ", ")
  .toUpperCase();

const allowedDocumentExtensions = ".pdf,.doc,.docx,.xls,.xlsx,.ppt,.pptx";
const formatAllowedDocumentExtensions = allowedDocumentExtensions
  .replace(/\./g, "")
  .replace(/\,/g, ", ")
  .toUpperCase();

enum FileUploadValidationErrorTypes {
  no_file_selected,
  max_size_exceeded,
  too_many_files,
  fields_json_not_valid,
}

type FileUploadValidationError =
  | { type: FileUploadValidationErrorTypes.no_file_selected }
  | { type: FileUploadValidationErrorTypes.max_size_exceeded; fileSize: number }
  | { type: FileUploadValidationErrorTypes.too_many_files; filesCount: number }
  | { type: FileUploadValidationErrorTypes.fields_json_not_valid };

function showFileUploadValidationError(
  error: FileUploadValidationError
): string {
  switch (error.type) {
    case FileUploadValidationErrorTypes.no_file_selected:
      return "No file is selected.";
    case FileUploadValidationErrorTypes.max_size_exceeded:
      return `Maximum file size exceeds. (${error.fileSize / 1_000_000}MB)`;
    case FileUploadValidationErrorTypes.too_many_files:
      return `Maximum allowed file count is exceeded. (${error.filesCount})`;
    case FileUploadValidationErrorTypes.fields_json_not_valid:
      return "Fields JSON is not valid.";
  }
}

export type FileProperties = {
  id: string;
  name: string;
  displayName: string;
  size: string;
  url: string;
  signedUrl: string;
  category?: FileCategory;
  date?: string;
  time?: string;
};

export type FileWithUploadPolicy = {
  name: string;
  file: Option<File>;
  isUploaded: boolean;
  uploadPolicy: Deferred<ApiResult<FileUploadPolicy>>;
  properties: Option<FileProperties>;
};

export type UploadType = "photos" | "documents";

const validateAnyFileSelected = (sfs: File[]): Either<string, File[]> =>
  pipe(
    sfs,
    E.fromPredicate(
      s => s.length !== 0,
      () =>
        showFileUploadValidationError({
          type: FileUploadValidationErrorTypes.no_file_selected,
        })
    )
  );

const validateMaxFileSize =
  (limit: number) =>
  (sfs: File): Either<string, File> =>
    pipe(
      sfs,
      E.fromPredicate(
        s => s.size < limit,
        () =>
          showFileUploadValidationError({
            type: FileUploadValidationErrorTypes.max_size_exceeded,
            fileSize: limit,
          })
      )
    );

const validateSelectedMaxFiles =
  (limit: number) =>
  (sfs: File[]): Either<string, File[]> =>
    pipe(
      sfs,
      E.fromPredicate(
        s => s.length <= limit,
        () =>
          showFileUploadValidationError({
            type: FileUploadValidationErrorTypes.too_many_files,
            filesCount: limit,
          })
      )
    );

const isPhotoUploading = (model: Model) =>
  pipe(
    model.photos,
    M.toArray(OrdString),
    A.some(f => !snd(f).isUploaded)
  );

const isDocumentUploading = (model: Model) =>
  pipe(
    model.documents,
    M.toArray(OrdString),
    A.some(f => !snd(f).isUploaded)
  );

export type Model = {
  photos: Map<string, FileWithUploadPolicy>;
  documents: Map<string, FileWithUploadPolicy>;
  editedDocument: Option<FileProperties>;
};

export function makeSnapshot(model: Model): StepSnapshot {
  return {
    photos: pipe(model.photos, M.map(fileUploadSnapshot), snapshotMap),
    documents: pipe(model.documents, M.map(fileUploadSnapshot), snapshotMap),
  };
}

export type AttachmentsEffect =
  | { type: "ComponentEffect"; effect: Effect<Action> }
  | { type: "AlertAction"; action: Alert.Action }
  | { type: "NoEffect" };

const ComponentEffect = (effect: Effect<Action>): AttachmentsEffect => ({
  type: "ComponentEffect",
  effect,
});

const AlertAction = (action: Alert.Action): AttachmentsEffect => ({
  type: "AlertAction",
  action,
});

const NoEffect = (): AttachmentsEffect => ({
  type: "NoEffect",
});

export function init(jsb: Option<Jsb>): Model {
  const photosData = pipe(
    jsb,
    O.chain(j => j.photos),
    O.fold(
      () => new Map<string, FileWithUploadPolicy>(),
      photos =>
        pipe(
          photos,
          A.map(
            (p: JsbPhoto): FileWithUploadPolicy => ({
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
                date: pipe(p.date, O.getOrElseW(constUndefined)),
                time: pipe(p.time, O.getOrElseW(constUndefined)),
              }),
            })
          ),
          A.map((p): [string, FileWithUploadPolicy] => [p.name, p]),
          M.fromFoldable(EqString, SG.first<FileWithUploadPolicy>(), A.Foldable)
        )
    )
  );

  const documentsData = pipe(
    jsb,
    O.chain(j => j.documents),
    O.fold(
      () => new Map<string, FileWithUploadPolicy>(),
      documents =>
        pipe(
          documents,
          A.map(
            (p: JsbDocument): FileWithUploadPolicy => ({
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
                date: pipe(p.date, O.getOrElseW(constUndefined)),
                time: pipe(p.time, O.getOrElseW(constUndefined)),
                category: pipe(
                  p.category as Option<FileCategory>,
                  O.getOrElseW(constUndefined)
                ),
              }),
            })
          ),
          A.map((p): [string, FileWithUploadPolicy] => [p.name, p]),
          M.fromFoldable(EqString, SG.first<FileWithUploadPolicy>(), A.Foldable)
        )
    )
  );

  return {
    photos: photosData,
    documents: documentsData,
    editedDocument: O.none,
  };
}

export const toSaveJsbInput = (model: Model) => {
  return pipe(
    {
      photos: pipe(
        model.photos,
        M.toArray(OrdString),
        A.filterMap(f => snd(f).properties)
      ),
      documents: pipe(
        model.documents,
        M.toArray(OrdString),
        A.filterMap(f => snd(f).properties)
      ),
    },
    E.of
  );
};

export type Action =
  | { type: "PhotoFilesSelected"; value: FileList }
  | { type: "DocumentFilesSelected"; value: FileList }
  | {
      type: "GeneratePhotoFileUploadPolicy";
      result: ApiResult<NonEmptyArray<FileUploadPolicy>>;
      name: string;
    }
  | {
      type: "GenerateDocumentFileUploadPolicy";
      result: ApiResult<NonEmptyArray<FileUploadPolicy>>;
      name: string;
    }
  | {
      type: "UploadPhotoFileToGCS";
      result: ApiResult<unknown>;
      name: string;
      uploadPolicy: FileUploadPolicy;
    }
  | {
      type: "UploadDocumentFileToGCS";
      result: ApiResult<unknown>;
      name: string;
      uploadPolicy: FileUploadPolicy;
    }
  | {
      type: "RemoveSelectedPhotoFile";
      name: string;
    }
  | {
      type: "RemoveSelectedDocumentFile";
      name: string;
    }
  | {
      type: "DownloadSelectedDocumentFile";
      name: string;
      signedUrl: string;
    }
  | {
      type: "CloseEditModal";
      name: string;
    }
  | {
      type: "OpenEditModal";
      name: string;
    }
  | {
      type: "UpdateDocumentFile";
      file: EditedFile;
    };

export const PhotoFilesSelected = (value: FileList): Action => ({
  type: "PhotoFilesSelected",
  value,
});

export const DocumentFilesSelected = (value: FileList): Action => ({
  type: "DocumentFilesSelected",
  value,
});

export const GeneratePhotoFileUploadPolicy =
  (name: string) =>
  (result: ApiResult<NonEmptyArray<FileUploadPolicy>>): Action => ({
    type: "GeneratePhotoFileUploadPolicy",
    result,
    name,
  });

export const GenerateDocumentFileUploadPolicy =
  (name: string) =>
  (result: ApiResult<NonEmptyArray<FileUploadPolicy>>): Action => ({
    type: "GenerateDocumentFileUploadPolicy",
    result,
    name,
  });

export const UploadPhotoFileToGCS =
  (name: string) =>
  (uploadPolicy: FileUploadPolicy) =>
  (result: ApiResult<unknown>): Action => ({
    type: "UploadPhotoFileToGCS",
    result,
    name,
    uploadPolicy,
  });

export const UploadDocumentFileToGCS =
  (name: string) =>
  (uploadPolicy: FileUploadPolicy) =>
  (result: ApiResult<unknown>): Action => ({
    type: "UploadDocumentFileToGCS",
    result,
    name,
    uploadPolicy,
  });

export const RemoveSelectedPhotoFile = (name: string): Action => ({
  type: "RemoveSelectedPhotoFile",
  name,
});

export const RemoveSelectedDocumentFile = (name: string): Action => ({
  type: "RemoveSelectedDocumentFile",
  name,
});

export const DownloadSelectedDocumentFile =
  (name: string) =>
  (signedUrl: string): Action => ({
    type: "DownloadSelectedDocumentFile",
    name,
    signedUrl,
  });

export const CloseEditModal = (name: string): Action => ({
  type: "CloseEditModal",
  name,
});

export const OpenEditModal = (name: string): Action => {
  return {
    type: "OpenEditModal",
    name,
  };
};

export const UpdateDocumentFile = (file: EditedFile): Action => {
  return {
    type: "UpdateDocumentFile",
    file,
  };
};

export const update =
  (api: Api) =>
  (model: Model, action: Action): [Model, AttachmentsEffect] => {
    switch (action.type) {
      case "PhotoFilesSelected": {
        return pipe(
          action.value,
          Array.from,
          validateAnyFileSelected,
          E.chain(A.traverse(E.Applicative)(validateMaxFileSize(maxFileSize))),
          E.chain(validateSelectedMaxFiles(maxFiles)),
          E.fold(
            (errMsg): [Model, AttachmentsEffect] => [
              { ...model },
              pipe(errMsg, Alert.AlertRequested("error"), AlertAction),
            ],
            (fs): [Model, AttachmentsEffect] => {
              const selectedFiles: FileWithUploadPolicy[] = pipe(
                fs,
                A.map(f => ({
                  name: model.photos.get(f.name)
                    ? `${Date.now()}-${f.name}`
                    : f.name,
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
                    model.photos,
                    M.lookupWithKey(EqString)(f.name),
                    O.isNone
                  )
                )
              );

              const updatedUploadedFiles: Map<string, FileWithUploadPolicy> =
                pipe(
                  [...filteredSelectedFiles, ...model.photos.values()],
                  A.map((f): [string, FileWithUploadPolicy] => [f.name, f]),
                  M.fromFoldable(
                    EqString,
                    SG.last<FileWithUploadPolicy>(),
                    A.Foldable
                  )
                );

              return [
                { ...model, photos: updatedUploadedFiles },
                pipe(
                  filteredSelectedFiles,
                  A.map(file =>
                    effectOfAsync(
                      api.common.generateFileUploadPolicies(1),
                      GeneratePhotoFileUploadPolicy(file.name)
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
      case "DocumentFilesSelected": {
        return pipe(
          action.value,
          Array.from,
          validateAnyFileSelected,
          E.chain(A.traverse(E.Applicative)(validateMaxFileSize(maxFileSize))),
          E.chain(validateSelectedMaxFiles(maxFiles)),
          E.fold(
            (errMsg): [Model, AttachmentsEffect] => [
              { ...model },
              pipe(errMsg, Alert.AlertRequested("error"), AlertAction),
            ],
            (fs): [Model, AttachmentsEffect] => {
              const selectedFiles: FileWithUploadPolicy[] = pipe(
                fs,
                A.map(f => ({
                  name: f.name,
                  file: O.some(f),
                  isUploaded: false,
                  uploadPolicy: InProgress(),
                  properties: O.none,
                }))
              );

              const filteredSelectedFiles: FileWithUploadPolicy[] = pipe(
                selectedFiles,
                A.filter(f =>
                  pipe(
                    model.documents,
                    M.lookupWithKey(EqString)(f.name),
                    O.isNone
                  )
                )
              );

              const updatedUploadedFiles: Map<string, FileWithUploadPolicy> =
                pipe(
                  [...filteredSelectedFiles, ...model.documents.values()],
                  A.map((f): [string, FileWithUploadPolicy] => [f.name, f]),
                  M.fromFoldable(
                    EqString,
                    SG.last<FileWithUploadPolicy>(),
                    A.Foldable
                  )
                );

              return [
                { ...model, documents: updatedUploadedFiles },
                pipe(
                  filteredSelectedFiles,
                  A.map(file =>
                    effectOfAsync(
                      api.common.generateFileUploadPolicies(1),
                      GenerateDocumentFileUploadPolicy(file.name)
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
      case "GeneratePhotoFileUploadPolicy": {
        return pipe(
          O.Do,
          O.bind("uploadPolicy", () =>
            pipe(O.fromEither(action.result), O.map(NEA.head))
          ),
          O.bind("fileItem", () =>
            M.lookup(EqString)(action.name)(model.photos)
          ),
          O.bind("payload", ({ uploadPolicy, fileItem }) =>
            pipe(
              fileItem.file,
              O.chain(file =>
                O.fromEither(
                  generateFileUploadFormData(file)(uploadPolicy.fields)
                )
              )
            )
          ),
          O.fold(
            (): [Model, AttachmentsEffect] => [
              {
                ...model,
                photos: pipe(model.photos, M.deleteAt(EqString)(action.name)),
              },
              NoEffect(),
            ],
            ({ fileItem, uploadPolicy, payload }) => [
              {
                ...model,
                photos: pipe(
                  model.photos,
                  M.upsertAt(EqString)(action.name, {
                    ...fileItem,
                    uploadPolicy: Resolved(
                      E.right<ApiError, FileUploadPolicy>(uploadPolicy)
                    ),
                  })
                ),
              },
              pipe(
                effectOfAsync(
                  api.common.uploadFileToGCS(uploadPolicy.url)(payload),
                  UploadPhotoFileToGCS(action.name)(uploadPolicy)
                ),
                ComponentEffect
              ),
            ]
          )
        );
      }
      case "GenerateDocumentFileUploadPolicy": {
        return pipe(
          O.Do,
          O.bind("uploadPolicy", () =>
            pipe(O.fromEither(action.result), O.map(NEA.head))
          ),
          O.bind("fileItem", () =>
            M.lookup(EqString)(action.name)(model.documents)
          ),
          O.bind("payload", ({ uploadPolicy, fileItem }) =>
            pipe(
              fileItem.file,
              O.chain(file =>
                O.fromEither(
                  generateFileUploadFormData(file)(uploadPolicy.fields)
                )
              )
            )
          ),
          O.fold(
            (): [Model, AttachmentsEffect] => [
              {
                ...model,
                documents: pipe(
                  model.documents,
                  M.deleteAt(EqString)(action.name)
                ),
              },
              NoEffect(),
            ],
            ({ fileItem, uploadPolicy, payload }) => [
              {
                ...model,
                documents: pipe(
                  model.documents,
                  M.upsertAt(EqString)(action.name, {
                    ...fileItem,
                    uploadPolicy: Resolved(
                      E.right<ApiError, FileUploadPolicy>(uploadPolicy)
                    ),
                  })
                ),
              },
              pipe(
                effectOfAsync(
                  api.common.uploadFileToGCS(uploadPolicy.url)(payload),
                  UploadDocumentFileToGCS(action.name)(uploadPolicy)
                ),
                ComponentEffect
              ),
            ]
          )
        );
      }
      case "UploadPhotoFileToGCS": {
        const date = convertToDate();
        const time = date.toLocaleString("en-US", {
          hour: "numeric",
          hour12: true,
          minute: "numeric",
        });

        return pipe(
          action.result,
          O.fromEither,
          O.chain(() =>
            M.modifyAt(EqString)(
              action.name,
              (f: FileWithUploadPolicy): FileWithUploadPolicy => ({
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
                  date: convertDateToString(date),
                  time,
                }),
              })
            )(model.photos)
          ),
          O.getOrElse(() => M.deleteAt(EqString)(action.name)(model.photos)),
          photos => [
            {
              ...model,
              photos,
            },
            NoEffect(),
          ]
        );
      }
      case "UploadDocumentFileToGCS": {
        const date = convertToDate();
        const time = date.toLocaleString("en-US", {
          hour: "numeric",
          hour12: true,
          minute: "numeric",
        });

        const modifiedFile = pipe(
          model.documents,
          M.lookupWithKey(EqString)(action.name),
          O.map(uf => snd(uf)),
          O.map(
            (f): FileWithUploadPolicy => ({
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
                date: convertDateToString(date),
                time: time,
              }),
            })
          )
        );

        if (E.isRight(action.result) && O.isSome(modifiedFile)) {
          return [
            {
              ...model,
              documents: pipe(
                model.documents,
                M.upsertAt(EqString)(action.name, modifiedFile.value)
              ),
            },
            NoEffect(),
          ];
        } else {
          return [
            {
              ...model,
              documents: pipe(
                model.documents,
                M.deleteAt(EqString)(action.name)
              ),
            },
            NoEffect(),
          ];
        }
      }
      case "RemoveSelectedPhotoFile": {
        return [
          {
            ...model,
            photos: pipe(model.photos, M.deleteAt(EqString)(action.name)),
          },
          NoEffect(),
        ];
      }
      case "RemoveSelectedDocumentFile": {
        return [
          {
            ...model,
            documents: pipe(model.documents, M.deleteAt(EqString)(action.name)),
          },
          NoEffect(),
        ];
      }
      case "DownloadSelectedDocumentFile": {
        download(action.signedUrl, action.name);

        return [
          {
            ...model,
          },
          NoEffect(),
        ];
      }
      case "CloseEditModal": {
        return [
          {
            ...model,
            editedDocument: O.none,
          },
          NoEffect(),
        ];
      }
      case "OpenEditModal": {
        return [
          {
            ...model,
            editedDocument:
              model.documents.get(action.name)?.properties ?? O.none,
          },
          NoEffect(),
        ];
      }

      case "UpdateDocumentFile": {
        const document = pipe(
          model.documents,
          M.lookupWithKey(EqString)(action.file.name),
          O.map(uf => uf[1])
        );

        return [
          {
            ...model,
            documents: O.isSome(document)
              ? pipe(
                  model.documents,
                  M.deleteAt(EqString)(action.file.name),
                  M.upsertAt(EqString)(
                    action.file.displayName,
                    pipe(document.value, a => ({
                      ...document.value,
                      name: action.file.displayName,
                      properties: pipe(
                        a.properties,
                        O.map(o => ({
                          ...o,
                          ...action.file,
                          name: action.file.displayName,
                        }))
                      ),
                      file: pipe(
                        a.file,
                        O.map(o => ({ ...o, name: action.file.displayName }))
                      ),
                    }))
                  )
                )
              : model.documents,
            editedDocument: O.none,
          },
          NoEffect(),
        ];
      }
    }
  };

type DocumentItemProps = {
  document: FileProperties | null;
  readOnly?: boolean;
  onEdit: (event: React.MouseEvent<HTMLButtonElement>) => void;
  onDownload: (event: React.MouseEvent<HTMLButtonElement>) => void;
  onDelete: (event: React.MouseEvent<HTMLButtonElement>) => void;
};

const DocumentItem = ({
  document,
  readOnly = false,
  onEdit,
  onDownload,
  onDelete,
}: DocumentItemProps): JSX.Element => {
  const getDocumentOptions = (): MenuItemProps[][] => {
    const downloadMenuItem: MenuItemProps = {
      label: "Download",
      icon: "download",
      onClick: onDownload,
    };

    const editMenuItem: MenuItemProps = {
      label: "Edit",
      icon: "edit",
      onClick: onEdit,
    };

    const deleteMenuItem: MenuItemProps = {
      label: "Delete",
      icon: "trash_empty",
      onClick: onDelete,
    };

    return pipe(
      [
        O.some([downloadMenuItem]),
        pipe(
          [editMenuItem, deleteMenuItem],
          O.fromPredicate(() => !readOnly)
        ),
      ],
      A.compact
    );
  };

  const documentDetails = [
    document?.size ?? "",
    document?.category ?? "",
    document?.date ?? "",
    document?.time ?? "",
  ]
    .filter(Boolean)
    .join(" • ");

  return (
    <div
      className="h-14 w-full border border-neutral-shade-38 rounded flex items-center px-2"
      data-testid="document-item"
    >
      <Icon name="file_blank_outline" className="text-2xl" />
      <div className="ml-2 truncate">
        <p className="text-sm font-semibold text-neutral-shade-100">
          {document?.displayName ?? ""}
        </p>
        <p className="text-xs text-neutral-shade-58">{documentDetails}</p>
      </div>
      <div className="ml-auto">
        <Dropdown className="z-30" menuItems={getDocumentOptions()}>
          <button className="text-xl">
            <Icon name="more_horizontal" />
          </button>
        </Dropdown>
      </div>
    </div>
  );
};

export type Props = ChildProps<Model, Action> & {
  isReadOnly: boolean;
};

export function View(props: Props): JSX.Element {
  const { model, dispatch, isReadOnly } = props;

  const uploadPhotosButtonConfigs: UploadButton.UploadButtonConfigs = {
    icon: "image_alt",
    label: "Add photos",
    isLoading: isPhotoUploading(model),
    allowMultiple: allowMultiple,
    allowedExtensions: allowedPhotoExtensions,
  };

  const uploadDocumentsButtonConfigs: UploadButton.UploadButtonConfigs = {
    icon: "file_blank_outline",
    label: "Add documents",
    isLoading: isDocumentUploading(model),
    allowMultiple: allowMultiple,
    allowedExtensions: allowedDocumentExtensions,
  };

  const uploadedPhotosCount = useMemo(
    () =>
      pipe(
        model.photos,
        M.filter(f => f.isUploaded),
        M.size
      ),
    [model]
  );

  const uploadedDocumentsCount = useMemo(
    () =>
      pipe(
        model.documents,
        M.filter(f => f.isUploaded),
        M.size
      ),
    [model]
  );

  return (
    <StepLayout>
      <div className="max-w-[760px] flex flex-col md:flex-row justify-start md:justify-between items-start">
        <div className="flex flex-col">
          <SectionHeading className="text-xl font-semibold">
            Photos ({uploadedPhotosCount})
          </SectionHeading>
          <div className="text-xs font-normal text-neutral-shade-75 mt-0.5">
            <p>{formatAllowedPhotoExtensions}</p>
            <p>Max file size: {maxFileSizeText}MB</p>
          </div>
        </div>
        {!isReadOnly && (
          <UploadButton.View
            configs={uploadPhotosButtonConfigs}
            className="mt-2 md:mt-0"
            onUpload={flow(PhotoFilesSelected, dispatch)}
          />
        )}
      </div>
      {uploadedPhotosCount > 0 ? (
        <div className="w-full flex flex-row flex-wrap min-h-[80px] justify-start items-start gap-4 p-2 border-neutral-shade-18 border rounded">
          {pipe(
            model.photos,
            M.filter(f => f.isUploaded),
            M.toArray(OrdString),
            A.map(f => snd(f)),
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
                {!isReadOnly && (
                  <Icon
                    name="off_outline_close"
                    className="absolute right-0.5 top-0.5 text-2xl leading-6 text-white bg-black bg-opacity-60 rounded-full cursor-pointer"
                    onClick={flow(
                      constant(f.name),
                      RemoveSelectedPhotoFile,
                      dispatch
                    )}
                  />
                )}
              </div>
            ))
          )}
        </div>
      ) : (
        <span className="font-normal text-base">No photos uploaded</span>
      )}

      <div className="max-w-[760px] flex flex-col md:flex-row justify-start md:justify-between items-start">
        <div className="flex flex-col">
          <SectionHeading className="text-xl font-semibold">
            Documents ({uploadedDocumentsCount})
          </SectionHeading>
          <div className="text-xs font-normal text-neutral-shade-75 mt-0.5">
            <p>{formatAllowedDocumentExtensions}</p>
            <p>Max file size: {maxFileSizeText}MB</p>
          </div>
        </div>
        {!isReadOnly && (
          <UploadButton.View
            configs={uploadDocumentsButtonConfigs}
            className="mt-2 md:mt-0"
            onUpload={flow(DocumentFilesSelected, dispatch)}
          />
        )}
      </div>
      {uploadedDocumentsCount > 0 ? (
        <div className="w-full flex flex-row flex-wrap min-h-[80px] justify-start items-start gap-4 p-2 border-neutral-shade-18 border rounded">
          {pipe(
            model.documents,
            M.filter(f => f.isUploaded),
            M.toArray(OrdString),
            A.map(f => f[1]),
            A.map(f => (
              <div key={f.name} className="w-full">
                <DocumentItem
                  readOnly={props.isReadOnly}
                  onDownload={() => {
                    dispatch(
                      DownloadSelectedDocumentFile(f.name)(
                        pipe(
                          f.properties,
                          O.map(p => p.signedUrl),
                          O.getOrElse(() => "")
                        )
                      )
                    );
                  }}
                  onDelete={flow(
                    constant(f.name),
                    RemoveSelectedDocumentFile,
                    dispatch
                  )}
                  document={pipe(
                    f.properties,
                    O.getOrElse((): FileProperties | null => null)
                  )}
                  onEdit={() => {
                    dispatch(OpenEditModal(f.name));
                  }}
                />
              </div>
            ))
          )}
        </div>
      ) : (
        <span className="font-normal text-base">No documents uploaded</span>
      )}

      {O.isSome(model.editedDocument) && (
        <Modal
          title={"Edit Modal"}
          isOpen={O.isSome(model.editedDocument)}
          closeModal={flow(
            constant(model.editedDocument.value.name),
            CloseEditModal,
            dispatch
          )}
        >
          <EditDocument
            file={model.editedDocument.value}
            allowCategories={true}
            onSave={(editedFile: EditedFile) => {
              dispatch(UpdateDocumentFile(editedFile));
            }}
            onCancel={flow(
              constant(model.editedDocument.value.name),
              CloseEditModal,
              dispatch
            )}
          />
        </Modal>
      )}
    </StepLayout>
  );
}
