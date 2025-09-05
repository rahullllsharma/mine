import type { DateTime } from "luxon";
import type { Effect } from "@/utils/reducerWithEffect";
import type {
  Activity,
  Hazard,
  Jsb,
  LibrarySiteCondition,
  LibrarySiteConditionId,
  LibraryTask,
  LibraryTaskId,
  ProjectLocation,
} from "@/api/codecs";
import type { ApiError } from "@/api/api";
import type { Either } from "fp-ts/lib/Either";
import type { NonEmptyString } from "io-ts-types";
import type * as Ord from "fp-ts/lib/Ord";
import type { UserPermission } from "@/types/auth/AuthUser";
import type { Option } from "fp-ts/lib/Option";
import type { GpsCoordinates } from "@/api/generated/types";
import type { CustomisedFromContextStateType } from "@/context/CustomisedDataContext/CustomisedFormStateContext";
import * as Eq from "fp-ts/lib/Eq";
import { flow, pipe } from "fp-ts/lib/function";
import * as A from "fp-ts/lib/Array";
import * as M from "fp-ts/lib/Map";
import * as S from "fp-ts/lib/Set";
import * as O from "fp-ts/lib/Option";
import * as SG from "fp-ts/lib/Semigroup";
import * as E from "fp-ts/lib/Either";
import * as R from "fp-ts/lib/Record";
import * as Json from "fp-ts/lib/Json";
import { array } from "fp-ts";
import { Eq as EqString, Ord as OrdString } from "fp-ts/lib/string";
import hash from "object-hash";
import { RiskLevel } from "@/api/generated/types";
import { DecodeError, JsonParseError } from "@/api/api";
import {
  eqHazardId,
  eqLibrarySiteConditionId,
  eqLibraryTaskId,
  fileUploadPolicyFieldsCodec,
} from "@/api/codecs";
import { effectOfFunc_ } from "@/utils/reducerWithEffect";
import {
  FormStatus,
  UserFormModeTypes,
} from "../templatesComponents/customisedForm.types";

export const eqNonEmptyString: Eq.Eq<NonEmptyString> = EqString;
export const ordNonEmptyString: Ord.Ord<NonEmptyString> = OrdString;

export const eqUserPermission: Eq.Eq<UserPermission> = EqString;

export const isSameDay =
  (d1: DateTime) =>
  (d2: DateTime): boolean =>
    d1.startOf("day").diff(d2.startOf("day")).toMillis() === 0;

export const eqSameDay = Eq.fromEquals((a: DateTime, b: DateTime) =>
  isSameDay(a)(b)
);

export const taskRiskLevels = (
  activities: Activity[],
  tasksLibrary: Map<LibraryTaskId, LibraryTask>
): Map<LibraryTaskId, RiskLevel> =>
  pipe(
    activities,
    A.chain(a => a.tasks),
    A.map((t): [LibraryTaskId, RiskLevel] =>
      pipe(
        tasksLibrary,
        M.lookup(eqLibraryTaskId)(t.libraryTask.id),
        O.fold(
          () => [t.libraryTask.id, RiskLevel.Unknown],
          task => [t.libraryTask.id, task.riskLevel]
        )
      )
    ),
    M.fromFoldable(eqLibraryTaskId, SG.last<RiskLevel>(), A.Foldable)
  );

// combines hazards from selected tasks and site conditions
export const relevantHazards =
  (tasksLibrary: LibraryTask[]) =>
  (siteConditionsLibrary: LibrarySiteCondition[]) =>
  (selectedTaskIds: Set<LibraryTaskId>) =>
  (selectedSiteConditionIds: Set<LibrarySiteConditionId>): Hazard[] => {
    const taskHazards = pipe(
      tasksLibrary,
      A.filter(task => S.elem(eqLibraryTaskId)(task.id)(selectedTaskIds)),
      A.chain(task => task.hazards)
    );
    const siteConditionHazards = pipe(
      siteConditionsLibrary,
      A.filter(sc =>
        S.elem(eqLibrarySiteConditionId)(sc.id)(selectedSiteConditionIds)
      ),
      A.chain(sc => sc.hazards)
    );

    return pipe(
      taskHazards,
      A.concat(siteConditionHazards),
      A.uniq(Eq.contramap((h: Hazard) => h.id)(eqHazardId))
    );
  };

export const generateFileUploadFormData =
  (file: Blob) =>
  (fields: string): Either<ApiError, FormData> => {
    const parsedFields = pipe(
      fields,
      Json.parse,
      E.mapLeft(JsonParseError),
      E.chain(flow(fileUploadPolicyFieldsCodec.decode, E.mapLeft(DecodeError))),
      E.map(R.toUnfoldable(array))
    );

    if (E.isRight(parsedFields)) {
      // a bit of imperative code here because FormData does not have an immutable interface
      // still ok though because it's not exposed outside of this function and the function is still pure
      const formData = new FormData();

      parsedFields.right.forEach(([key, value]) => {
        formData.append(key, value);
      });
      formData.append("file", file);

      return E.right(formData);
    } else {
      return E.left(parsedFields.left);
    }
  };

export function scrollTopEffect<T>(): Effect<T> {
  return effectOfFunc_(
    () =>
      document
        .getElementById("page-layout")
        ?.scrollTo({ top: 0, behavior: "smooth" }),
    undefined
  );
}

export interface StepSnapshot {
  [key: string]: StepSnapshotValue;
}

export type StepSnapshotValue =
  | string
  | null
  | number
  | boolean
  | string[]
  | StepSnapshotValue[]
  | [string, StepSnapshotValue][]
  | StepSnapshot;

export const snapshotHash = (snapshot: StepSnapshotValue): string =>
  hash.MD5(snapshot);

export const snapshotMap = <V extends StepSnapshotValue>(
  input: Map<string, V>
): StepSnapshot => {
  return pipe(
    input,
    M.toArray(OrdString),
    A.reduce({}, (acc, [k, v]) => ({ ...acc, [k]: v }))
  );
};

export const snapshotHashMap =
  <K extends NonNullable<StepSnapshotValue>, V>(ordInstance: Ord.Ord<K>) =>
  (input: Map<K, V>): StepSnapshot => {
    return pipe(
      input,
      M.toArray(ordInstance),
      A.reduce({}, (acc, [k, v]) => ({ ...acc, [snapshotHash(k)]: v }))
    );
  };

export const jsbCoordinates =
  (projectLocation: Option<ProjectLocation>) =>
  (jsb: Jsb): Option<GpsCoordinates> =>
    pipe(
      jsb.gpsCoordinates,
      O.chain(A.head),
      O.alt(() =>
        pipe(
          projectLocation,
          O.map(
            (pl): GpsCoordinates => ({
              latitude: pl.latitude,
              longitude: pl.longitude,
            })
          )
        )
      )
    );

export enum FormViewTabStates {
  FORM = "form",
  HISTORY = "history",
}

export const getNameFromEmail = (email: string) => {
  if (!email) return "";

  const [firstName, rest] = email.split("@")[0].split(".");
  const lastName = rest ?? "";

  return `${firstName} ${lastName}`.trim();
};

export const isISODateString = (value: string) => {
  return /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}[+-]\d{2}:\d{2}$/.test(value);
};

export const handleFormMode = (
  userPermissions: string[],
  isOwn: boolean,
  isCompleted: boolean
) => {
  if (isCompleted) {
    return UserFormModeTypes.PREVIEW;
  }
  if (userPermissions.includes("CREATE_CWF")) {
    if (userPermissions.includes("EDIT_DELETE_ALL_CWF")) {
      return UserFormModeTypes.EDIT;
    }
    if (isOwn && userPermissions.includes("EDIT_DELETE_OWN_CWF")) {
      return UserFormModeTypes.EDIT;
    }
    if (
      userPermissions.includes("ALLOW_EDITS_AFTER_EDIT_PERIOD") &&
      isCompleted
    ) {
      return UserFormModeTypes.EDIT;
    }
    return UserFormModeTypes.PREVIEW;
  } else {
    return UserFormModeTypes.PREVIEW;
  }
};

export const isCopyAndRebriefAllowed = (
  isOwn: boolean,
  userPermissions: string[],
  isCopyOrRebriefEnabled: boolean | undefined,
) => {
  if(isCopyOrRebriefEnabled) {
    if (userPermissions.includes("EDIT_DELETE_ALL_CWF")) {
      return true;
    }
    if (isOwn && userPermissions.includes("EDIT_DELETE_OWN_CWF")) {
      return true;
    }
  }
  return false;
}

export const handleFormViewMode = (userPermissions: string[]) => {
  if (userPermissions.includes("CREATE_CWF")) {
    return true;
  }
  return false;
};

export const isFormReopenable = (
  isOwn: boolean,
  status: string,
  permissions: string[]
) => {
  return (
    status === FormStatus.Completed &&
    (permissions.includes("REOPEN_ALL_CWF") ||
      (isOwn && permissions.includes("REOPEN_OWN_CWF")))
  );
};

export const isTaskLibraryEditable = (
  formState: CustomisedFromContextStateType,
  permissions: string[]
) => {
  return (
    formState.form.properties.status === FormStatus.InProgress ||
    new Date(formState.form?.edit_expiry_time ?? 0).getTime() >
      new Date().getTime() ||
    permissions.includes("ALLOW_EDITS_AFTER_EDIT_PERIOD" as UserPermission)
  );
};

export const isFormDeletable = (
  isOwn: boolean,
  status: string,
  permissions: string[]
) => {
  return (
    status === FormStatus.InProgress &&
    (permissions.includes("EDIT_DELETE_ALL_CWF") ||
      (isOwn && permissions.includes("EDIT_DELETE_OWN_CWF")))
  );
};
