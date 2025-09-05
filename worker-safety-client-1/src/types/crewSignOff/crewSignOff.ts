import type { FormField } from "@/utils/formField";
import type { ChildProps } from "@/utils/reducerWithEffect";
import type { AsyncOperationStatus } from "@/utils/asyncOperationStatus";
import type { ApiResult } from "@/api/api";
import type { Deferred } from "@/utils/deferred";
import type { FileInput } from "@/api/generated/types";
import type * as tt from "io-ts-types";
import type * as t from "io-ts";
import type * as O from "fp-ts/lib/Option";

export type SketchPadModel = {
  name: tt.NonEmptyString;
  index: number;
  upload: Deferred<ApiResult<unknown>>;
};

export enum SignatureTypes {
  OTHER = "OTHER",
  PERSONNEL = "PERSONNEL",
  UNINITIALIZED = "UNINITIALIZED",
}

export type OtherCrewMemberSignature = {
  type: SignatureTypes.OTHER;
};

export type PersonnelCrewMemberSignature = {
  type: SignatureTypes.PERSONNEL;
  companyName?: string;
  department?: string;
  displayName?: string;
  email?: string;
  employeeNumber?: string;
  externalId?: string;
  jobTitle?: string;
  managerEmail?: string;
  managerId?: string;
  managerName?: string;
  primary?: boolean;
};

export type CrewMemberSignature = (
  | PersonnelCrewMemberSignature
  | OtherCrewMemberSignature
  | { type: SignatureTypes.UNINITIALIZED }
) & {
  signature: t.Validation<FileInput>;
  name: FormField<t.Errors, string, tt.NonEmptyString>;
};

export type Model = {
  signatures: CrewMemberSignature[];
  sketchPadDialog: O.Option<SketchPadModel>;
  errorsEnabled: boolean;
};

export type Action =
  | {
      type: "SignatureNameChanged";
      index: number;
      value: string;
    }
  | {
      type: "CrewMemberAdded";
    }
  | {
      type: "SignatureSelection";
      index: number;
      value: PersonnelCrewMemberSignature | OtherCrewMemberSignature;
    }
  | {
      type: "CrewMemberRemoved";
      index: number;
    }
  | {
      type: "SketchPadDialogOpened";
      name: tt.NonEmptyString;
      index: number;
    }
  | {
      type: "SketchPadDialogClosed";
    }
  | {
      type: "SignatureRemoved";
      index: number;
    }
  | {
      type: "UploadSignature";
      name: string;
      index: number;
      blob: Blob;
      operation: AsyncOperationStatus<ApiResult<FileInput>>;
    }
  | {
      type: "UpdateManagerInfo";
      payload: { [key: string]: ManagerInfo };
    };

export type Props = ChildProps<Model, Action> & {
  isReadOnly: boolean;
  jsbId: string;
};

export type WorkOSDirectoryUsersType = {
  id: string;
  idpId: string;
  directoryId: string;
  organizationId: string;
  firstName: string;
  lastName: string;
  jobTitle: string;
  username: string;
  state: string;
  customAttributes: {
    externalId: string;
    manager_id: string | null;
    division_name: string | null;
    employee_type: string | null;
    manager_email: string | null;
    department_name: string;
    employment_start_date: string | null;
    displayName: string;
    employeeNumber: string;
    emails: {
      type: string;
      value: string;
      primary: boolean;
    }[];
  };
  rawAttributes: {
    meta: {
      resourceType: string;
    };
    name: {
      formatted: string;
      givenName: string;
      familyName: string;
    };
    title: string;
    active: boolean;
    emails: {
      type: string;
      value: string;
      primary: boolean;
    }[];
    schemas: string[];
    userName: string;
    addresses: {
      type: string;
      region: string;
      country: string;
      primary: boolean;
      locality: string;
      formatted: string;
      postalCode: string;
      streetAddress: string;
    }[];
    externalId: string;
    manager_id: string;
    displayName: string;
    phoneNumbers: {
      type: string;
      value: string;
      primary: boolean;
    }[];
    "urn:ietf:params:scim:schemas:extension:enterprise:2.0:User": {
      department: string;
      employeeNumber: string;
    };
  };
  role: {
    slug: string;
  };
  slug: string;
  createdAt: string;
  updatedAt: string;
};

export type CrewMemberOptionProps = {
  isSelected: boolean;
  label: string;
  employeeNumber?: string;
  onClick: () => void;
};

export type ManagerInfo = {
  managerName: string;
  managerEmail: string;
  managerId: string;
};

export type SignatureProps = {
  value: O.Option<FileInput>;
  name: tt.NonEmptyString;
  errorsEnabled: boolean;
  disabled?: boolean;
  onOpen: () => void;
  onClear: () => void;
};

export type SketchPadDialogProps = {
  model: SketchPadModel;
  onSave: (_: O.Option<Blob>, name: string, index: number) => void;
  onClose: () => void;
};
