/* eslint-disable @next/next/no-img-element */
import type { Jsb } from "@/api/codecs";
import type { Effect } from "@/utils/reducerWithEffect";
import type { AsyncOperationStatus } from "@/utils/asyncOperationStatus";
import type { ApiResult } from "@/api/api";
import type { CommonApi } from "@/api/requests/common";
import type { JsbApi } from "@/api/requests/jsb";
import type { Either } from "fp-ts/lib/Either";
import type { StepSnapshot } from "../Utils";
import type {
  CrewType,
  FileInput,
  SaveJobSafetyBriefingInput,
} from "@/api/generated/types";
import type {
  SketchPadModel,
  OtherCrewMemberSignature,
  PersonnelCrewMemberSignature,
  CrewMemberSignature,
  Model,
  Action,
  Props,
  WorkOSDirectoryUsersType,
  CrewMemberOptionProps,
  ManagerInfo,
  SignatureProps,
  SketchPadDialogProps,
} from "@/types/crewSignOff/crewSignOff";
import * as tt from "io-ts-types";
import * as t from "io-ts";
import { BodyText, ComponentLabel, Icon, SectionHeading } from "@urbint/silica";
import * as A from "fp-ts/lib/Array";
import * as E from "fp-ts/lib/Either";
import * as O from "fp-ts/lib/Option";
import {
  constNull,
  constUndefined,
  constant,
  flow,
  identity,
  pipe,
} from "fp-ts/lib/function";
import SignatureCanvas from "react-signature-canvas";
import { Fragment, useCallback, useState, useRef, useEffect } from "react";
import * as TE from "fp-ts/lib/TaskEither";
import * as NEA from "fp-ts/lib/NonEmptyArray";
import { Lens, Optional } from "monocle-ts";
import { sequenceS } from "fp-ts/lib/Apply";
import { useQuery } from "@apollo/client";
import { FileCategory } from "@/api/generated/types";
import {
  nonEmptyStringCodec,
  stringEnum,
  validDateTimeCodecS,
} from "@/utils/validation";
import {
  noEffect,
  effectOfAsync,
  effectOfFunc_,
} from "@/utils/reducerWithEffect";
import { initFormField, setDirty, updateFormField } from "@/utils/formField";
import { OptionalView } from "@/components/common/Optional";
import ButtonPrimary from "@/components/shared/button/primary/ButtonPrimary";
import { Finished, Started } from "@/utils/asyncOperationStatus";
import {
  NotStarted,
  Resolved,
  isInProgress,
  isUpdating,
  updatingDeferred,
} from "@/utils/deferred";
import Modal from "@/components/shared/modal/Modal";
import { useTenantStore } from "@/store/tenant/useTenantStore.store";
import EmptyContent from "@/components/emptyContent/EmptyContent";
import Loader from "@/components/shared/loader/Loader";
import { SignatureTypes } from "@/types/crewSignOff/crewSignOff";
import { Input, InputRaw } from "../Basic/Input";
import Labeled from "../Basic/Labeled";
import StepLayout from "../StepLayout";
import ButtonIcon from "../../shared/button/icon/ButtonIcon";
import ButtonSecondary from "../../shared/button/secondary/ButtonSecondary";
import { Dialog } from "../Basic/Dialog";
import { generateFileUploadFormData, getNameFromEmail } from "../Utils";
import workosDirectoryUsers from "../../../../graphql/workosDirectoryUsers.gql";
import ShareWidget from "./ShareWidget";

export type { Model, Props, Action };

const fileCategoryCodec = stringEnum<typeof FileCategory>(
  FileCategory,
  "FileCategory"
);

function decodeFileInputCodec(input: FileInput): t.Validation<FileInput> {
  return sequenceS(E.Apply)({
    category: input.category
      ? fileCategoryCodec.decode(input.category)
      : t.undefined.decode(input.category),
    crc32c: tt.fromNullable(t.string, input.crc32c ?? "").decode(input?.crc32c),
    date: tt
      .fromNullable(t.string.pipe(validDateTimeCodecS), input?.date)
      .decode(input?.date),
    displayName: nonEmptyStringCodec().decode(input.displayName),
    id: tt.fromNullable(t.string, input?.id ?? "").decode(input?.id),
    md5: tt.fromNullable(t.string, input?.md5 ?? "").decode(input?.md5),
    mimetype: tt
      .fromNullable(t.string, input?.mimetype ?? "")
      .decode(input?.mimetype),
    name: nonEmptyStringCodec().decode(input.name),
    signedUrl: tt
      .fromNullable(t.string, input?.signedUrl ?? "")
      .decode(input?.signedUrl),
    size: tt.fromNullable(t.string, input?.size ?? "").decode(input?.size),
    time: tt.fromNullable(t.string, input?.time ?? "").decode(input?.time),
    url: tt.fromNullable(t.string, input?.url ?? "").decode(input?.url),
  });
}

export function setFormDirty(model: Model): Model {
  return {
    ...model,
    errorsEnabled: true,
    signatures: model.signatures.map(s => ({
      ...s,
      name: setDirty(s.name),
    })),
  };
}

export function makeSnapshot(model: Model): StepSnapshot {
  return {
    signatures: pipe(
      model.signatures,
      A.map(s => ({
        name: s.name.raw,
        file: pipe(
          s.signature,
          E.fold(constNull, f => f.md5 ?? null)
        ),
      }))
    ),
  };
}

export const init = (jsb: O.Option<Jsb>): Model => {
  const defaultSignature = {
    type: SignatureTypes.UNINITIALIZED,
    name: initFormField(nonEmptyStringCodec().decode)(""),
    signature: decodeFileInputCodec({} as FileInput),
  };

  const signatures = pipe(
    jsb,
    O.chain(j => j.crewSignOff),
    O.fold(
      constant([]),
      A.map(signatureData => {
        const data = pipe(
          signatureData.signature ?? O.none,
          O.map(s => ({
            id: s.id,
            name: s.name,
            displayName: s.displayName,
            size: pipe(s.size, O.getOrElseW(constUndefined)),
            url: s.url,
            signedUrl: s.signedUrl,
          }))
        );

        return {
          type:
            (signatureData.type as unknown as SignatureTypes.PERSONNEL) ??
            SignatureTypes.OTHER,
          name: initFormField(nonEmptyStringCodec().decode)(
            signatureData.name ?? ""
          ),
          externalId: signatureData.externalId,
          signature: O.isSome(data)
            ? decodeFileInputCodec(data.value)
            : decodeFileInputCodec({} as FileInput),
          jobTitle: signatureData.jobTitle ?? "",
          employeeNumber: signatureData.employeeNumber ?? "",
        };
      })
    )
  );

  return {
    signatures: signatures.length > 0 ? signatures : [defaultSignature],
    sketchPadDialog: O.none,
    errorsEnabled: false,
  };
};

const withSketchPadDialogClosed = (model: Model): Model => ({
  ...model,
  sketchPadDialog: O.none,
});

const withSignatureUpdated =
  (signature: Either<unknown, FileInput>) =>
  (index: number) =>
  (model: Model): Model =>
    pipe(
      model.signatures,
      A.modifyAt(index, s => ({
        ...s,
        signature: E.isRight(signature)
          ? decodeFileInputCodec(signature.right)
          : decodeFileInputCodec({} as FileInput),
      })),
      O.fold(
        () => model,
        signatures => ({ ...model, signatures })
      )
    );

export function toSaveJsbInput(
  model: Model
): t.Validation<SaveJobSafetyBriefingInput> {
  return pipe(
    model.signatures,
    A.traverse(E.Applicative)(s => {
      const signature = (() => {
        if (s.type === SignatureTypes.PERSONNEL) {
          return {
            type: E.right(s.type as unknown as CrewType),
            companyName: E.right(s.companyName),
            department: E.right(s.department),
            jobTitle: E.right(s.jobTitle),
            email: E.right(s.email),
            managerEmail: E.right(s.managerEmail),
            managerId: E.right(s.managerId),
            managerName: E.right(s.managerName),
            employeeNumber: E.right(s.employeeNumber),
            externalId: E.right(s.externalId),
            name: s.name.val,
            signature: s.signature,
          };
        } else {
          return {
            type: E.right(s.type as unknown as CrewType),
            name: s.name.val,
            signature: s.signature,
            companyName: E.right(""),
            department: E.right(""),
            jobTitle: E.right(""),
            email: E.right(""),
            managerEmail: E.right(""),
            managerId: E.right(""),
            managerName: E.right(""),
            employeeNumber: E.right(""),
            externalId: E.right(""),
          };
        }
      })();

      return sequenceS(E.Apply)(signature);
    }),
    E.map(signatures => ({ crewSignOff: signatures }))
  );
}

export const SignatureNameChanged =
  (index: number) =>
  (value: string): Action => ({
    type: "SignatureNameChanged",
    index,
    value,
  });

export const CrewMemberAdded = (): Action => ({
  type: "CrewMemberAdded",
});

export const CrewMemberRemoved = (index: number): Action => ({
  type: "CrewMemberRemoved",
  index,
});

export const SketchPadDialogOpened =
  (index: number) =>
  (name: tt.NonEmptyString): Action => ({
    type: "SketchPadDialogOpened",
    name,
    index,
  });

export const SketchPadDialogClosed = (): Action => ({
  type: "SketchPadDialogClosed",
});

export const SignatureRemoved = (index: number): Action => ({
  type: "SignatureRemoved",
  index,
});

export const UploadSignature =
  (blob: Blob, name: string, index: number) =>
  (operation: AsyncOperationStatus<ApiResult<FileInput>>): Action => ({
    type: "UploadSignature",
    blob,
    name,
    index,
    operation: operation,
  });

export const UpdateManagerInfo = (payload: {
  [key: string]: ManagerInfo;
}): Action => ({
  type: "UpdateManagerInfo",
  payload,
});

export const update =
  (api: { common: CommonApi; jsb: JsbApi }) =>
  (model: Model, action: Action): [Model, Effect<Action>] => {
    switch (action.type) {
      case "SignatureNameChanged":
        return [
          {
            ...model,
            signatures: model.signatures.map((s, i) =>
              i === action.index
                ? {
                    ...s,
                    name: updateFormField(nonEmptyStringCodec().decode)(
                      action.value
                    ),
                  }
                : s
            ),
          },
          noEffect,
        ];

      case "SignatureSelection":
        const getSignatureData = (
          action_local: PersonnelCrewMemberSignature | OtherCrewMemberSignature
        ) => {
          if (action_local.type === SignatureTypes.OTHER) {
            return {
              type: action_local.type,
            };
          } else {
            return {
              type: action_local.type,
              companyName: action_local?.companyName,
              department: action_local?.department,
              displayName: action_local?.displayName,
              email: action_local?.email,
              employeeNumber: action_local?.employeeNumber,
              externalId: action_local?.externalId,
              jobTitle: action_local?.jobTitle,
              managerEmail: action_local?.managerEmail,
              managerId: action_local?.managerId,
              managerName: action_local?.managerName,
              primary: action_local?.primary,
              name: updateFormField(nonEmptyStringCodec().decode)(
                action_local.displayName ?? ""
              ),
            };
          }
        };

        return [
          {
            ...model,
            signatures: model.signatures.map((s, i) =>
              i === action.index
                ? {
                    ...s,
                    ...getSignatureData(action.value),
                  }
                : s
            ),
          },
          noEffect,
        ];

      case "CrewMemberAdded":
        return [
          {
            ...model,
            signatures: [
              ...model.signatures,
              {
                type: SignatureTypes.UNINITIALIZED,
                name: initFormField(nonEmptyStringCodec().decode)(""),
                signature: decodeFileInputCodec({} as FileInput),
              },
            ],
          },
          noEffect,
        ];

      case "CrewMemberRemoved":
        return [
          {
            ...model,
            signatures: model.signatures.filter((_, i) => i !== action.index),
          },
          noEffect,
        ];

      case "SketchPadDialogOpened":
        return [
          {
            ...model,
            sketchPadDialog: O.some({
              name: action.name,
              index: action.index,
              upload: NotStarted(),
            }),
          },
          noEffect,
        ];

      case "SketchPadDialogClosed":
        return [pipe(model, withSketchPadDialogClosed), noEffect];

      case "SignatureRemoved":
        return [
          {
            ...model,
            signatures: pipe(
              model.signatures,
              A.modifyAt(action.index, s => ({
                ...s,
                signature: decodeFileInputCodec({} as FileInput),
              })),
              O.getOrElse(() => model.signatures)
            ),
          },
          noEffect,
        ];

      case "UploadSignature":
        const uploadPropLens = Optional.fromOptionProp<Model>()(
          "sketchPadDialog"
        ).composeLens(Lens.fromProp<SketchPadModel>()("upload"));

        switch (action.operation.status) {
          case "Started":
            const task = pipe(
              TE.Do,
              TE.bind("policy", () =>
                pipe(api.common.generateFileUploadPolicies(1), TE.map(NEA.head))
              ),
              TE.bind("payload", ({ policy }) =>
                TE.fromEither(
                  generateFileUploadFormData(action.blob)(policy.fields)
                )
              ),
              TE.chain(({ policy, payload }) =>
                pipe(
                  api.common.uploadFileToGCS(policy.url)(payload),
                  TE.map(_ => ({
                    id: policy.id,
                    name: action.name,
                    displayName: action.name,
                    size: `${action.blob.size / 1000} KB`,
                    url: policy.url + policy.id,
                    signedUrl: policy.signedUrl,
                  }))
                )
              )
            );
            return [
              uploadPropLens.modify(updatingDeferred)(model),
              effectOfAsync(
                task,
                flow(
                  Finished,
                  UploadSignature(action.blob, action.name, action.index)
                )
              ),
            ];
          case "Finished": {
            const withCurrentSignature = pipe(
              O.of(action.index),
              O.fold(
                () => identity,
                withSignatureUpdated(action.operation.result)
              )
            );

            return [
              pipe(
                model,
                uploadPropLens.set(Resolved(action.operation.result)),
                withSketchPadDialogClosed,
                withCurrentSignature
              ),
              pipe(
                action.operation.result,
                E.fold(
                  err => effectOfFunc_(() => console.error(err), undefined),
                  _ => noEffect
                )
              ),
            ];
          }
        }

      case "UpdateManagerInfo":
        return [
          {
            ...model,
            signatures: pipe(
              model.signatures,
              A.map(s =>
                pipe(
                  Object.entries(action.payload),
                  A.findFirst(([employeeNumber, _]) => {
                    return (
                      s.type === SignatureTypes.PERSONNEL &&
                      employeeNumber === s.employeeNumber
                    );
                  }),
                  O.fold(
                    () => s,
                    ([_, managerInfo]) => ({
                      ...s,
                      ...managerInfo,
                    })
                  )
                )
              )
            ),
          },
          noEffect,
        ];
    }
  };

function CrewMemberOption(props: CrewMemberOptionProps): JSX.Element {
  return (
    <div
      className="flex flex-row gap-6 items-center cursor-pointer"
      onClick={props.onClick}
    >
      <div className="w-[15px] flex items-center justify-center">
        {props.isSelected && (
          <svg
            xmlns="http://www.w3.org/2000/svg"
            width="15"
            height="15"
            viewBox="0,0,256,256"
          >
            <g
              fill="#017899"
              fillRule="nonzero"
              stroke="none"
              strokeWidth="1"
              strokeLinecap="butt"
              strokeLinejoin="miter"
              strokeMiterlimit="10"
              strokeDasharray=""
              strokeDashoffset="0"
              fontFamily="none"
              fontWeight="none"
              fontSize="none"
              textAnchor="none"
            >
              <g transform="scale(10.66667,10.66667)">
                <path d="M20.29297,5.29297l-11.29297,11.29297l-4.29297,-4.29297l-1.41406,1.41406l5.70703,5.70703l12.70703,-12.70703z"></path>
              </g>
            </g>
          </svg>
        )}
      </div>
      <div className="flex flex-col gap-2 w-full">
        <div className="flex flex-row justify-between w-full">
          <span className="w-3/4">{props.label}</span>
          {props.employeeNumber && (
            <div className="text-base">{props.employeeNumber}</div>
          )}
        </div>
        {!props.label.includes("Other") && <hr className="border-gray-10"></hr>}
      </div>
    </div>
  );
}

export function View(props: Props): JSX.Element {
  const { model, dispatch, isReadOnly } = props;

  const onSave = useCallback(
    (blob: O.Option<Blob>, name: string, index: number) => {
      const action: Action = pipe(
        blob,
        O.fold(SketchPadDialogClosed, b =>
          flow(Started, UploadSignature(b, name, index))()
        )
      );
      dispatch(action);
    },
    [dispatch]
  );

  const signatureIdx = useRef(0);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const selectedSignature = useRef<CrewMemberSignature | null>(null);
  const [workosDirectoryIds, setWorkosDirectoryIds] = useState<string[]>([]);
  const [filteredCrewMembers, setFilteredCrewMembers] = useState<
    WorkOSDirectoryUsersType[]
  >([]);

  const { data: crewMemberData, loading: loadingCrewMemberData } = useQuery(
    workosDirectoryUsers,
    {
      variables: { directoryIds: workosDirectoryIds },
      skip: !workosDirectoryIds.length,
    }
  );

  useEffect(() => {
    const tenantWorkOSIds = (
      useTenantStore.getState().tenant.workos as unknown as {
        workosDirectoryId: string;
      }[]
    ).map(entry => entry.workosDirectoryId);

    setWorkosDirectoryIds(tenantWorkOSIds);

    if (crewMemberData) {
      setFilteredCrewMembers(crewMemberData.workosDirectoryUsers.data);
    }
  }, [isReadOnly, crewMemberData]);

  const isManagerDataMissing = useRef(false);

  useEffect(() => {
    if (crewMemberData && isManagerDataMissing.current === false) {
      handleMissingManagerInfo();
    }
  }, [crewMemberData, dispatch, model.signatures]);

  const handleMissingManagerInfo = () => {
    const missingManagerInfo: { [key: string]: ManagerInfo } = {};

    model.signatures.forEach(s => {
      if (s.type === SignatureTypes.PERSONNEL) {
        if (
          !(s.managerId || s.managerEmail || s.managerName) &&
          s.employeeNumber
        ) {
          const [filteredMember] = (
            crewMemberData?.workosDirectoryUsers?.data ?? []
          ).filter((entry: WorkOSDirectoryUsersType) =>
            (entry.customAttributes?.employeeNumber ?? "").includes(
              s.employeeNumber ?? ""
            )
          );

          if (!filteredMember) return;

          missingManagerInfo[s.employeeNumber] = {
            managerName:
              getNameFromEmail(
                filteredMember?.customAttributes?.manager_email
              ) ?? "",
            managerEmail: filteredMember?.customAttributes?.manager_email ?? "",
            managerId: filteredMember?.customAttributes?.manager_id ?? "",
          };
        }
      }
    });
    dispatch({
      type: "UpdateManagerInfo",
      payload: missingManagerInfo,
    });
    isManagerDataMissing.current = true;
  };

  const handleNameSelection = (
    member: PersonnelCrewMemberSignature | OtherCrewMemberSignature,
    index: number
  ) => {
    if (member.type === SignatureTypes.OTHER) {
      dispatch({ type: "SignatureNameChanged", index, value: "" });
    }
    dispatch({ type: "SignatureSelection", index, value: member });
    dispatch({ type: "SignatureRemoved", index });
    closeModal();
  };

  const removeSignatureAndSelectedOption = (
    s: CrewMemberSignature,
    index: number
  ) => {
    dispatch({ type: "SignatureNameChanged", index, value: "" });
    dispatch({ type: "SignatureRemoved", index });
    if (model.signatures.length > 1) {
      dispatch(CrewMemberRemoved(index));
    }
    s.type = SignatureTypes.UNINITIALIZED;
  };

  const openModal = (s: CrewMemberSignature, i: number) => {
    signatureIdx.current = i;
    selectedSignature.current = s;
    setIsModalOpen(true);
  };
  const closeModal = () => {
    setIsModalOpen(false);
    setFilteredCrewMembers(crewMemberData?.workosDirectoryUsers?.data || []);
  };

  const getFilteredCrewMembers = (searchedMember: string) => {
    if (!crewMemberData?.workosDirectoryUsers?.data) return;

    const search = searchedMember.toLowerCase();

    const filteredMembers = crewMemberData.workosDirectoryUsers.data.filter(
      (entry: WorkOSDirectoryUsersType) => {
        const customDisplayName =
          entry.customAttributes?.displayName?.toLowerCase() ?? "";
        const customEmployeeNumber =
          entry.customAttributes?.employeeNumber ?? "";

        const rawDisplayName =
          entry.rawAttributes?.displayName?.toLowerCase() ?? "";
        const rawEmployeeNumber =
          entry.rawAttributes?.[
            "urn:ietf:params:scim:schemas:extension:enterprise:2.0:User"
          ]?.employeeNumber ?? "";

        return (
          customDisplayName.includes(search) ||
          customEmployeeNumber.includes(searchedMember) ||
          rawDisplayName.includes(search) ||
          rawEmployeeNumber.includes(searchedMember)
        );
      }
    );

    setFilteredCrewMembers(filteredMembers);
  };

  return (
    <>
      <StepLayout>
        <div className="flex flex-row justify-between">
          <div className="flex flex-col gap-2">
            <SectionHeading className="text-xl font-semibold">
              Sign-Off
            </SectionHeading>
            {!isReadOnly && (
              <ButtonSecondary
                label="Add Name"
                iconStart="plus_circle_outline"
                onClick={flow(CrewMemberAdded, dispatch)}
              />
            )}
          </div>
          <div>
            <ShareWidget externalJsbId={props.jsbId} />
          </div>
        </div>
        <div className="flex flex-col gap-4 bg-[#F7F8F8] p-4">
          {model.signatures.map((s, i) => (
            <Fragment key={i}>
              <div className="flex flex-col bg-white p-4 gap-4" key={i}>
                <Labeled label="Name *" className="flex flex-col gap-2">
                  <div className="flex flex-row items-center gap-2">
                    <div
                      className={`flex flex-row justify-between bg-white w-full max-h-36 mt-2 rounded-md border-solid border-[1px] border-brand-gray-40 p-2 ${
                        isReadOnly
                          ? "bg-gray-100 cursor-not-allowed text-gray-500"
                          : "cursor-pointer"
                      }`}
                      onClick={() => {
                        if (!isReadOnly) {
                          openModal(s, i);
                        }
                      }}
                    >
                      <div className="flex flex-col justify-center w-3/4">
                        <span
                          className={
                            s.type === SignatureTypes.UNINITIALIZED
                              ? "text-gray-400"
                              : ""
                          }
                        >
                          {s.type === SignatureTypes.UNINITIALIZED
                            ? "Search by Name or Employee ID Number"
                            : s.type === SignatureTypes.OTHER
                            ? "Other"
                            : `${s.name.raw} (${s.jobTitle})`}
                        </span>
                      </div>
                      <div className="flex flex-col justify-center item-center">
                        <div className="flex flex-row gap-6">
                          {s.type === SignatureTypes.PERSONNEL &&
                            s.employeeNumber}
                          <Icon
                            name="chevron_big_down"
                            className="text-base text-black cursor-pointer"
                            onClick={() => openModal(s, i)}
                          />
                        </div>
                      </div>
                    </div>
                    <div className="flex flex-col mt-2 pl-2 pr-4">
                      {!isReadOnly && (
                        <Icon
                          name="trash_empty"
                          className="border-[1px] rounded-md border-brand-gray-40 flex flex-col items-center justify-center w-10 h-10 cursor-pointer"
                          onClick={() => removeSignatureAndSelectedOption(s, i)}
                        />
                      )}
                    </div>
                  </div>
                  {s.type === SignatureTypes.OTHER && (
                    <Labeled
                      label="Please enter other name *"
                      className="flex flex-row gap-2"
                    >
                      <Input
                        type="text"
                        field={s.name}
                        placeholder="Please enter other name"
                        disabled={isReadOnly}
                        className="flex-1"
                        onChange={value => {
                          flow(
                            constant(value),
                            SignatureNameChanged(i),
                            dispatch
                          )();
                          flow(constant(i), SignatureRemoved, dispatch)();
                        }}
                      />
                    </Labeled>
                  )}
                </Labeled>
                <OptionalView
                  value={O.fromEither(s.name.val)}
                  render={name => (
                    <div className="flex flex-row justify-start">
                      <Signature
                        name={name as tt.NonEmptyString}
                        errorsEnabled={model.errorsEnabled}
                        value={
                          E.isRight(s.signature)
                            ? O.some(s.signature.right)
                            : O.none
                        }
                        disabled={isReadOnly}
                        onOpen={flow(
                          constant(name as tt.NonEmptyString),
                          SketchPadDialogOpened(i),
                          dispatch
                        )}
                        onClear={flow(constant(i), SignatureRemoved, dispatch)}
                      />
                    </div>
                  )}
                />
              </div>
            </Fragment>
          ))}
        </div>
      </StepLayout>
      <OptionalView
        value={model.sketchPadDialog}
        render={dialogModel => (
          <SketchPadDialog
            model={dialogModel}
            onClose={flow(SketchPadDialogClosed, dispatch)}
            onSave={onSave}
          />
        )}
      />
      <Modal
        title={"Select a Name"}
        isOpen={isModalOpen}
        closeModal={closeModal}
        className="h-full flex flex-col"
      >
        <div className="flex flex-col gap-4">
          <div className="flex flex-col justify-center item-center">
            <InputRaw
              icon="search"
              onChange={e => {
                getFilteredCrewMembers(e);
              }}
              placeholder="Search by Name or Employee ID Number"
            />
          </div>
          <div
            className="flex flex-col flex-grow max-h-full"
            style={{ height: "500px" }}
          >
            {loadingCrewMemberData && <Loader />}

            {!loadingCrewMemberData && (
              <div className="flex flex-col gap-4 h-full">
                {!loadingCrewMemberData && (
                  <CrewMemberOption
                    isSelected={
                      selectedSignature.current?.type === SignatureTypes.OTHER
                    }
                    label="Other (name not listed)"
                    onClick={() =>
                      handleNameSelection(
                        { type: SignatureTypes.OTHER },
                        signatureIdx.current
                      )
                    }
                  />
                )}

                <hr className="solid 3px #000" />
                {filteredCrewMembers?.length > 0 && !loadingCrewMemberData && (
                  <div className="flex overflow-y-auto flex-col">
                    <div className="flex flex-col gap-4 h-full">
                      {filteredCrewMembers?.map(
                        (crewData: WorkOSDirectoryUsersType) => (
                          <div key={crewData.id} className="flex flex-col">
                            <CrewMemberOption
                              isSelected={
                                selectedSignature.current?.type ===
                                  SignatureTypes.PERSONNEL &&
                                selectedSignature?.current?.externalId ===
                                  crewData.customAttributes?.externalId
                              }
                              label={`${
                                crewData.customAttributes?.displayName ?? ""
                              } (${crewData.jobTitle ?? ""})`}
                              employeeNumber={
                                crewData.customAttributes?.employeeNumber ?? ""
                              }
                              onClick={() =>
                                handleNameSelection(
                                  {
                                    type: SignatureTypes.PERSONNEL,
                                    displayName:
                                      crewData.customAttributes?.displayName ??
                                      "",
                                    companyName:
                                      crewData.customAttributes
                                        .department_name ?? "",
                                    department:
                                      crewData.customAttributes
                                        .department_name ?? "",
                                    email:
                                      crewData.customAttributes.emails.filter(
                                        email => email.primary
                                      )[0].value ?? "",
                                    employeeNumber:
                                      crewData.customAttributes
                                        ?.employeeNumber ?? "",
                                    externalId:
                                      crewData.customAttributes?.externalId ??
                                      "",
                                    jobTitle: crewData.jobTitle ?? "",
                                    managerName: getNameFromEmail(
                                      crewData.customAttributes.manager_email ??
                                        ""
                                    ),
                                    managerEmail:
                                      crewData.customAttributes.manager_email ??
                                      "",
                                    managerId:
                                      crewData.customAttributes.manager_id ??
                                      "",
                                    primary: false,
                                  },
                                  signatureIdx.current
                                )
                              }
                            />
                          </div>
                        )
                      )}
                    </div>
                  </div>
                )}

                {filteredCrewMembers?.length === 0 && !loadingCrewMemberData && (
                  <div className="flex flex-col justify-center w-full h-full">
                    <EmptyContent
                      title="No names to show"
                      description="Please select Other and type the name to add"
                    />
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </Modal>
    </>
  );
}

function Signature(props: SignatureProps): JSX.Element {
  return (
    <>
      {pipe(
        props.value,
        O.fold(
          () => {
            if (props.disabled) {
              return null;
            }
            return (
              <div>
                <ButtonSecondary
                  iconStart="edit"
                  label={`Sign for ${props.name}`}
                  onClick={props.onOpen}
                />
                {props.errorsEnabled && (
                  <BodyText className="text-red-500">
                    Signature is mandatory.
                  </BodyText>
                )}
              </div>
            );
          },
          data => (
            <div className="flex flex-row gap-2 w-full justify-between items-end">
              <div className="flex flex-col gap-1">
                <Labeled label="Signature">
                  <img
                    src={data.signedUrl?.toString()}
                    alt={`Signature for ${props.name}`}
                    className="max-w-full max-h-28"
                  />
                </Labeled>
              </div>
              <div className="flex flex-col pl-2 pr-4">
                {!props.disabled && (
                  <ButtonIcon
                    iconName="close_big"
                    onClick={props.onClear}
                    className="border-[1px] rounded-md border-brand-gray-40 flex flex-col items-center justify-center w-10 h-10 cursor-pointer"
                  />
                )}
              </div>
            </div>
          )
        )
      )}
    </>
  );
}

function pngToBinary(base64string: string): Blob {
  // TODO: consider adding a check for the valid data type
  const [_, data] = base64string.split(",");

  const byteString = Buffer.from(data, "base64");
  return new Blob([byteString], { type: "image/png" });
}

function SketchPadDialog({
  model,
  onClose,
  onSave,
}: SketchPadDialogProps): JSX.Element {
  const signatureRef = useRef<SignatureCanvas>(null);
  const [isSignAttempted, setIsSignAttempted] = useState(false);

  const isSignatureCanvasEmpty =
    !signatureRef.current || signatureRef.current.isEmpty();

  const [height, width] = [
    Math.min(window.innerHeight * 0.8, 300),
    Math.min(window.innerWidth * 0.8, 680),
  ];

  const handleSign = () => {
    setIsSignAttempted(true);
    if (!signatureRef.current) return;

    if (signatureRef.current.isEmpty()) return;

    const signatureData = signatureRef.current.toDataURL();
    pipe(O.some(signatureData), O.map(pngToBinary), b =>
      onSave(b, model.name, model.index)
    );
  };

  return (
    <Dialog
      size="flex"
      header={<DialogHeader name={model.name} onClose={onClose} />}
      footer={
        <div className="flex flex-col gap-2">
          {isSignAttempted && isSignatureCanvasEmpty && (
            <ComponentLabel className="text-red-500 text-sm">
              Signature is required.
            </ComponentLabel>
          )}
          <div className="flex flex-row justify-end gap-2">
            <ButtonSecondary label="Cancel" onClick={onClose} />
            <ButtonPrimary
              label="Sign"
              loading={isInProgress(model.upload) || isUpdating(model.upload)}
              onClick={handleSign}
            />
          </div>
        </div>
      }
    >
      <div className="flex flex-col gap-2">
        <Labeled label="Please sign your name in the box below">
          <SignatureCanvas
            ref={signatureRef}
            canvasProps={{
              width: width,
              height: height,
              className: "border border-gray-400",
            }}
          />
        </Labeled>
      </div>
    </Dialog>
  );
}

function DialogHeader({
  name,
  onClose,
}: {
  name: string;
  onClose: () => void;
}): JSX.Element {
  return (
    <div className="flex flex-row justify-between">
      <SectionHeading className="text-xl font-semibold">
        Sign for {name}
      </SectionHeading>
      <ButtonIcon iconName="close_big" onClick={onClose} />
    </div>
  );
}
