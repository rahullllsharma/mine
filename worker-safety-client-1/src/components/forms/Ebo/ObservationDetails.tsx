import type { Option } from "fp-ts/lib/Option";
import type { FormField } from "@/utils/formField";
import type { ChildProps } from "@/utils/reducerWithEffect";
import type { ValidDateTime, ValidDuration } from "@/utils/validation";
import type {
  Ebo,
  GpsCoordinates,
  LibraryTask,
  LibraryTaskId,
  WorkType,
} from "@/api/codecs";
import type { EnergyBasedObservationInput } from "@/api/generated/types";
import type { OpCo } from "@/types/opcos/opcos";
import type { Department } from "@/types/departments/departments";
import type { StepSnapshot } from "../Utils";
import type { SelectedDuplicateActivities } from "./HighEnergyTasks";
import { isSome } from "fp-ts/lib/Option";
import * as O from "fp-ts/lib/Option";
import * as t from "io-ts";
import { constNull, constant, flow, identity, pipe } from "fp-ts/lib/function";
import { useEffect, useMemo } from "react";
import * as A from "fp-ts/lib/Array";
import * as E from "fp-ts/lib/Either";
import * as M from "fp-ts/lib/Map";
import * as S from "fp-ts/lib/Set";
import * as Tup from "fp-ts/lib/Tuple";
import { isString, Eq as EqString, Ord as OrdString } from "fp-ts/lib/string";
import { Ord as OrdNumber } from "fp-ts/lib/number";
import { Apply as ApplyEither } from "fp-ts/lib/Either";
import * as tt from "io-ts-types";
import { sequenceS } from "fp-ts/lib/Apply";
import { DateTime } from "luxon";
import { isEmpty } from "lodash-es";
import {
  nonEmptyStringCodec,
  validDateTimeCodecS,
  validDurationCodecS,
} from "@/utils/validation";
import {
  gpsCoordinatesCodec,
  workTypeCodec,
  eqWorkTypeById,
  ordLibraryTaskId,
} from "@/api/codecs";
import { fieldDef, initFormField, updateFormField } from "@/utils/formField";
import TaskHeader from "@/components/layout/taskCard/header/TaskHeader";
import * as Alert from "@/components/forms/Alert";
import { MultiSelect } from "@/components/forms/Basic/MultiSelect";
import StepLayout from "@/components/forms/StepLayout";
import { OptionalView } from "@/components/common/Optional";
import { stringLabel } from "@/components/forms/Basic/SelectOption";
import useRestQuery from "@/hooks/useRestQuery";
import { FieldGroup } from "@/components/shared/FieldGroup";
import TaskCard from "@/components/layout/taskCard/TaskCard";
import ButtonRegular from "@/components/shared/button/regular/ButtonRegular";
import { useAuthStore } from "@/store/auth/useAuthStore.store";
import { useTenantStore } from "@/store/tenant/useTenantStore.store";
import { Input, InputRaw } from "../Basic/Input";
import { Select } from "../Basic/Select";
import { HecaRulesForExelon, HecaRulesForXcelEnergy } from "./HecaRules";
import { changeLabelOnBasisOfTenant } from "./TenantLabel/LabelOnBasisOfTenant";
import EboLocationAutocomplete from "./Location/EboLocationAutocomplete";

const stringFromOptionString = flow(
  O.fold<string, string>(constant(""), identity),
  nonEmptyStringCodec().decode
);

type WorkLocationInput = {
  location: string;
  latitude: string;
  longitude: string;
  isManualCoordinates: boolean;
};

type ValidWorkLocation =
  | {
      type: "Location";
      location: tt.NonEmptyString;
      coordinates: Option<GpsCoordinates>;
    }
  | { type: "GPS"; coordinates: GpsCoordinates };

const validateWorkLocation = (
  input: WorkLocationInput
): t.Validation<ValidWorkLocation> => {
  const validLocation: t.Validation<ValidWorkLocation> = sequenceS(E.Apply)({
    type: E.right("Location" as const),
    location: nonEmptyStringCodec().decode(input.location),
    coordinates: pipe(
      gpsCoordinatesCodec.decode({
        latitude: input.latitude,
        longitude: input.longitude,
      }),
      O.fromEither,
      E.right
    ),
  });

  return pipe(
    validLocation,
    E.alt(
      (): t.Validation<ValidWorkLocation> =>
        pipe(
          gpsCoordinatesCodec.decode({
            latitude: input.latitude,
            longitude: input.longitude,
          }),
          E.map(gps => ({ type: "GPS" as const, coordinates: gps }))
        )
    )
  );
};

export const isSelectedActivitiesPartOfSelectedWorkTypes =
  (workTypes: WorkType[]) =>
  (selectedActivities: SelectedDuplicateActivities) =>
  (tasks: LibraryTask[]): boolean => {
    const getWorkTypesByTaskId = (taskId: LibraryTaskId): WorkType[] =>
      pipe(
        tasks,
        A.findFirst(task => task.id === taskId),
        O.chain(task => task.workTypes),
        O.getOrElse((): WorkType[] => [])
      );

    const workTypesOfSelectedActivities: WorkType[] = pipe(
      selectedActivities,
      M.toArray(OrdString),
      A.map(Tup.snd),
      A.chain(M.toArray(OrdNumber)),
      A.map(Tup.snd),
      A.map(activityItem => activityItem.taskIds),
      A.chain(S.toArray(ordLibraryTaskId)),
      A.map(getWorkTypesByTaskId),
      A.flatten,
      A.uniq(eqWorkTypeById)
    );

    return pipe(
      workTypesOfSelectedActivities,
      A.map(wtsa => A.elem(eqWorkTypeById)(wtsa)(workTypes)),
      A.some(isPresent => isPresent === false)
    );
  };

export type Model = {
  observationDate: FormField<t.Errors, string, ValidDateTime>;
  observationTime: FormField<t.Errors, string, ValidDuration>;
  workOrderNumber: string;
  workLocation: FormField<t.Errors, WorkLocationInput, ValidWorkLocation>;
  departmentObserved: FormField<t.Errors, Option<string>, string>;
  opCoType: FormField<t.Errors, Option<string>, string>;
  subOpCoType: FormField<t.Errors, Option<string>, string>;
  workType: WorkType[];
  isHecaRulesOpen: boolean;
  OpCos: OpCo[];
  departments: Department[];
  formElementIdsWithError: string[];
  errorsEnabled: boolean;
};

const formDef = {
  observationTime: fieldDef(validDurationCodecS.decode),
  observationDate: fieldDef(validDateTimeCodecS.decode),
  departmentObserved: fieldDef(tt.optionFromNullable(t.string).decode),
  workType: fieldDef(tt.optionFromNullable(t.array(workTypeCodec)).decode),
  opCoType: fieldDef(tt.optionFromNullable(t.string).decode),
  subOpCoType: fieldDef(tt.optionFromNullable(t.string).decode),
};

const formElementIds = {
  observationDate: "observationDate",
  observationTime: "observationTime",
  workOrderNumber: "workOrderNumber",
  opCoType: "opCoType",
  subOpCoType: "subOpCoType",
  departmentObserved: "departmentObserved",
  workTypes: "workTypes",
  workLocation: "workLocation",
};

export type ObservationDetailsEffect =
  | { type: "AlertAction"; action: Alert.Action }
  | { type: "NoEffect" };

const AlertAction = (action: Alert.Action): ObservationDetailsEffect => ({
  type: "AlertAction",
  action,
});

const NoEffect = (): ObservationDetailsEffect => ({
  type: "NoEffect",
});

export function init(ebo: Option<Ebo>): Model {
  const eboContents = pipe(
    ebo,
    O.map(e => e.contents)
  );

  const savedObservationDate = pipe(
    eboContents,
    O.chain(e => e.details),
    O.map(ed => ed.observationDate)
  );

  const savedObservationTime = pipe(
    eboContents,
    O.chain(e => e.details),
    O.map(ed => ed.observationTime)
  );

  return {
    observationDate: pipe(
      savedObservationDate,
      O.chain(dt => O.fromNullable(dt.toISODate())),
      O.alt(() => O.fromNullable(DateTime.now().toISODate())),
      O.getOrElse(() => ""),
      formDef.observationDate.init
    ),
    observationTime: pipe(
      savedObservationTime,
      O.chain(dt =>
        O.fromNullable(
          dt.toISOTime({
            suppressMilliseconds: true,
            suppressSeconds: true,
          })
        )
      ),
      O.alt(() =>
        O.fromNullable(
          DateTime.now().setLocale(navigator.language).toFormat("HH:mm")
        )
      ),
      O.getOrElse(() => ""),
      formDef.observationTime.init
    ),
    workOrderNumber: pipe(
      eboContents,
      O.chain(c => c.details),
      O.chain(c => c.workOrderNumber),
      O.getOrElse(() => "")
    ),
    departmentObserved: pipe(
      eboContents,
      O.chain(c => c.details),
      O.chain(c => c.departmentObserved.id),
      initFormField(stringFromOptionString)
    ),
    workType: pipe(
      eboContents,
      O.chain(c => c.details),
      O.map(c => c.workType),
      O.fold(
        () => [],
        wt => wt
      )
    ),
    workLocation: initFormField(validateWorkLocation)({
      location: pipe(
        eboContents,
        O.chain(c => c.details),
        O.chain(c => c.workLocation),
        O.getOrElse(() => "")
      ),
      latitude: pipe(
        eboContents,
        O.chain(c => c.gpsCoordinates),
        O.chain(
          flow(
            A.head,
            O.map(c => c.latitude.toString())
          )
        ),
        O.getOrElse(() => "")
      ),
      longitude: pipe(
        eboContents,
        O.chain(c => c.gpsCoordinates),
        O.chain(
          flow(
            A.head,
            O.map(c => c.longitude.toString())
          )
        ),
        O.getOrElse(() => "")
      ),
      isManualCoordinates: false,
    }),
    isHecaRulesOpen: false,
    formElementIdsWithError: [],
    opCoType: pipe(
      eboContents,
      O.chain(c => c.details),
      O.chain(c => c.opcoObserved.id),
      initFormField(stringFromOptionString)
    ),
    subOpCoType: pipe(
      eboContents,
      O.chain(c => c.details),
      O.chain(c => c.subopcoObserved),
      O.fold(
        () => initFormField(stringFromOptionString)(O.none),
        s => initFormField(stringFromOptionString)(s.id)
      )
    ),
    OpCos: [],
    departments: [],
    errorsEnabled: false,
  };
}

export const makeSnapshot = (model: Model): StepSnapshot => {
  return {
    observationDate: model.observationDate.raw,
    observationTime: model.observationTime.raw,
    workOrderNumber: model.workOrderNumber,
    workLocation: model.workLocation.raw,
    departmentObserved: pipe(
      model.departmentObserved.raw,
      O.getOrElseW(constNull)
    ),
    opCoType: pipe(model.opCoType.raw, O.getOrElseW(constNull)),
    subOpCoType: pipe(model.subOpCoType.raw, O.getOrElseW(constNull)),
    workType: pipe(
      model.workType,
      A.map(wt => wt.name)
    ),
  };
};

export const getAllFormElementIdWithError = (model: Model): string[] => {
  const isSubOpCoTypeRequired = pipe(
    model.opCoType.val,
    E.map(opCo =>
      pipe(
        model.OpCos,
        A.findFirst(o => o.attributes.parent_id === opCo),
        O.map(o => !!o.attributes.parent_id),
        O.getOrElse(() => false)
      )
    ),
    E.getOrElse(() => false)
  );

  return pipe(
    [
      E.isLeft(model.observationDate.val) && formElementIds.observationDate,
      E.isLeft(model.observationTime.val) && formElementIds.observationTime,
      E.isLeft(model.opCoType.val) && formElementIds.opCoType,
      isSubOpCoTypeRequired &&
        E.isLeft(model.subOpCoType.val) &&
        formElementIds.subOpCoType,
      E.isLeft(model.departmentObserved.val) &&
        formElementIds.departmentObserved,
      E.isLeft(model.workLocation.val) && formElementIds.workLocation,
      A.isEmpty(model.workType) && formElementIds.workTypes,
    ],
    A.filter(isString)
  );
};

export const validateEboInput = (
  model: Model
): t.Validation<EnergyBasedObservationInput> => {
  return pipe(
    sequenceS(ApplyEither)({
      observationDate: model.observationDate.val,
      observationTime: model.observationTime.val,
      departmentObserved: model.departmentObserved.val,
      opCoType: model.opCoType.val,
      workLocation: model.workLocation.val,
      subOpCoType: pipe(
        model.opCoType.val,
        E.chain(opCo =>
          pipe(
            model.OpCos,
            A.findFirst(o => o.attributes.parent_id === opCo),
            O.map(o =>
              o.attributes.parent_id ? model.subOpCoType.val : E.right("")
            ),
            O.getOrElse(() => E.right(""))
          )
        )
      ),
    }),
    E.map((input): EnergyBasedObservationInput => {
      return {
        details: {
          observationDate: input.observationDate.toISODate(),
          observationTime: input.observationTime.toISOTime(),
          workOrderNumber: model.workOrderNumber,
          workType: model.workType.map(wt => ({
            id: wt.id,
            name: wt.name,
          })),
          workLocation:
            input.workLocation.type === "Location"
              ? input.workLocation.location
              : "",
          departmentObserved: {
            id: input.departmentObserved,
            name: pipe(
              model.departments,
              A.findFirst(d => d.id === input.departmentObserved),
              O.fold(
                () => "",
                d => d.attributes.name
              )
            ),
          },
          opcoObserved: {
            id: input.opCoType,
            name: pipe(
              model.OpCos,
              A.findFirst(d => d.id === input.opCoType),
              O.fold(
                () => "",
                d => d.attributes.name
              )
            ),
            fullName: pipe(
              model.OpCos,
              A.findFirst(d => d.id === input.opCoType),
              O.fold(
                () => "",
                d => d.attributes.full_name
              )
            ),
          },
          subopcoObserved: O.isSome(model.subOpCoType.raw)
            ? {
                id: input.subOpCoType,
                name: pipe(
                  model.OpCos,
                  A.findFirst(d => d.id === input.subOpCoType),
                  O.fold(
                    () => "",
                    d => d.attributes.name
                  )
                ),
                fullName: pipe(
                  model.OpCos,
                  A.findFirst(d => d.id === input.subOpCoType),
                  O.fold(
                    () => "",
                    d => d.attributes.full_name
                  )
                ),
              }
            : undefined,
        },
        gpsCoordinates: pipe(
          input.workLocation,
          wl =>
            wl.type === "Location" ? wl.coordinates : O.some(wl.coordinates),
          O.fold(constNull, A.of)
        ),
      };
    })
  );
};

export const toSaveEboInput = (
  model: Model
): t.Validation<EnergyBasedObservationInput> => {
  return validateEboInput(model);
};

export type Action =
  | { type: "ObservationDateChanged"; value: string }
  | { type: "ObservationTimeChanged"; value: string }
  | { type: "WorkOrderNumberChanged"; value: string }
  | { type: "WorkLocationChanged"; value: WorkLocationInput }
  | { type: "DepartmentObservedChanged"; value: Option<string> }
  | { type: "WorkTypeChanged"; value: WorkType }
  | { type: "WorkTypeRemoved"; value: WorkType }
  | { type: "LocationAcquired"; position: GeolocationPosition }
  | { type: "ToggleHecaRules" }
  | { type: "SetFormElementIdsWithError"; value: string[] }
  | { type: "OpCoChanged"; value: Option<string> }
  | { type: "SubOpCoChanged"; value: Option<string> }
  | { type: "SetOpCos"; value: OpCo[] }
  | { type: "SetDepartments"; value: Department[] };

export const ObservationDateChanged = (value: string): Action => ({
  type: "ObservationDateChanged",
  value,
});

export const ObservationTimeChanged = (value: string): Action => ({
  type: "ObservationTimeChanged",
  value,
});

export const WorkOrderNumberChanged = (value: string): Action => ({
  type: "WorkOrderNumberChanged",
  value,
});

export const WorkLocationChanged = (value: WorkLocationInput): Action => ({
  type: "WorkLocationChanged",
  value,
});

export const DepartmentObservedChanged = (value: Option<string>): Action => ({
  type: "DepartmentObservedChanged",
  value,
});

export const WorkTypeChanged = (value: WorkType): Action => ({
  type: "WorkTypeChanged",
  value,
});

export const WorkTypeRemoved = (value: WorkType): Action => ({
  type: "WorkTypeRemoved",
  value,
});

export const OpCoChanged = (value: Option<string>): Action => ({
  type: "OpCoChanged",
  value,
});

export const SubOpCoChanged = (value: Option<string>): Action => ({
  type: "SubOpCoChanged",
  value,
});

const LocationAcquired = (position: GeolocationPosition): Action => ({
  type: "LocationAcquired",
  position,
});

export const ToggleHecaRules = (): Action => ({
  type: "ToggleHecaRules",
});

export const SetFormElementIdsWithError = (value: string[]): Action => ({
  type: "SetFormElementIdsWithError",
  value,
});

export const SetOpCos = (value: OpCo[]): Action => ({
  type: "SetOpCos",
  value,
});

export const SetDepartments = (value: Department[]): Action => ({
  type: "SetDepartments",
  value,
});

export function update(
  model: Model,
  action: Action
): [Model, ObservationDetailsEffect] {
  switch (action.type) {
    case "ObservationDateChanged": {
      return pipe(
        action.value,
        dt => DateTime.fromISO(dt).startOf("day"),
        E.fromPredicate(
          dt => dt <= DateTime.now().startOf("day"),
          () => "The observation date must be before or equal to today's date."
        ),
        E.fold(
          err => [
            { ...model },
            pipe(err, Alert.AlertRequested("error"), AlertAction),
          ],
          () => [
            {
              ...model,
              observationDate: formDef.observationDate.update(action.value),
            },
            NoEffect(),
          ]
        )
      );
    }
    case "ObservationTimeChanged":
      return [
        {
          ...model,
          observationTime: formDef.observationTime.update(action.value),
        },
        NoEffect(),
      ];
    case "WorkOrderNumberChanged":
      return [{ ...model, workOrderNumber: action.value }, NoEffect()];
    case "WorkLocationChanged":
      return [
        {
          ...model,
          workLocation: updateFormField(validateWorkLocation)(action.value),
        },
        NoEffect(),
      ];
    case "DepartmentObservedChanged":
      return [
        {
          ...model,
          departmentObserved: updateFormField(stringFromOptionString)(
            action.value
          ),
        },
        NoEffect(),
      ];
    case "WorkTypeChanged": {
      return [
        {
          ...model,
          workType: pipe(model.workType, A.append(action.value)),
        },
        NoEffect(),
      ];
    }
    case "WorkTypeRemoved": {
      const updatedWorkTypes = pipe(
        model.workType,
        A.filter(wt => wt.id !== action.value.id)
      );

      return [
        {
          ...model,
          workType: updatedWorkTypes,
        },
        NoEffect(),
      ];
    }
    case "OpCoChanged":
      return [
        {
          ...model,
          opCoType: updateFormField(stringFromOptionString)(action.value),
          subOpCoType: updateFormField(stringFromOptionString)(O.none),
          departmentObserved: updateFormField(stringFromOptionString)(O.none),
        },
        NoEffect(),
      ];
    case "SubOpCoChanged":
      return [
        {
          ...model,
          subOpCoType: updateFormField(stringFromOptionString)(action.value),
        },
        NoEffect(),
      ];
    case "LocationAcquired":
      return [
        {
          ...model,
          workLocation: updateFormField(validateWorkLocation)({
            location: model.workLocation.raw.location,
            latitude: action.position.coords.latitude.toString(),
            longitude: action.position.coords.longitude.toString(),
            isManualCoordinates: true,
          }),
        },
        NoEffect(),
      ];
    case "ToggleHecaRules":
      return [
        {
          ...model,
          isHecaRulesOpen: !model.isHecaRulesOpen,
        },
        NoEffect(),
      ];
    case "SetFormElementIdsWithError": {
      return [
        {
          ...model,
          formElementIdsWithError: action.value,
        },
        NoEffect(),
      ];
    }
    case "SetOpCos":
      return [
        {
          ...model,
          OpCos: action.value,
        },
        NoEffect(),
      ];

    case "SetDepartments":
      return [
        {
          ...model,
          departments: action.value,
        },
        NoEffect(),
      ];
  }
}

export type Props = ChildProps<Model, Action> & {
  workTypes: Option<WorkType[]>;
  isReadOnly: boolean;
};

export function View(props: Props): JSX.Element {
  const { model, workTypes, dispatch, isReadOnly } = props;

  const { data: opcos } = useRestQuery<{ data: OpCo[] }, { data: OpCo[] }>({
    key: ["opcos"],
    endpoint: "/opcos",
    axiosConfig: {
      params: {
        "page[limit]": 100,
      },
    },
    queryOptions: {
      select(data) {
        return {
          data: data.data,
        };
      },
    },
  });

  const { data: departmentsData, refetch: refetchDepartments } = useRestQuery<
    { data: Department[] },
    { data: Department[] }
  >({
    key: ["opco-department"],
    endpoint: `/departments?opco_id=${
      O.isSome(model.opCoType.raw) && model.opCoType.raw.value
    }`,
    axiosConfig: {
      params: {
        "page[limit]": 200,
      },
    },
    queryOptions: {
      enabled: O.isSome(model.opCoType.raw),
      select(data) {
        return {
          data: data.data,
        };
      },
    },
  });

  const getPosition = useMemo(
    () =>
      pipe(
        E.tryCatch(
          () => navigator.geolocation,
          () => "Geolocation is not supported"
        ),
        E.chain(E.fromNullable("Geolocation is not supported")),
        E.map(
          g => () =>
            g.getCurrentPosition(flow(LocationAcquired, dispatch), e =>
              console.error(e)
            )
        )
      ),
    [dispatch]
  );

  const parentOpCos = useMemo(() => {
    if (opcos && !isEmpty(opcos.data)) {
      dispatch(SetOpCos(opcos.data));
      return pipe(
        opcos.data,
        A.filter(opco => !opco.attributes.parent_id)
      );
    }
    return [];
  }, [opcos]);

  const subOpCos = useMemo(() => {
    if (isSome(model.opCoType.raw) && opcos && !isEmpty(opcos.data)) {
      const opCoTypeId = model.opCoType.raw.value;
      return pipe(
        opcos.data,
        A.filter(opco => opco.attributes.parent_id === opCoTypeId)
      );
    }
    return [];
  }, [model.opCoType.raw, opcos]);

  useEffect(() => {
    // Trigger the departments when opCoType changes
    if (isSome(model.opCoType.raw)) {
      refetchDepartments();
    }
  }, [model.opCoType.raw]);

  const departments = useMemo(() => {
    if (departmentsData && !isEmpty(departmentsData.data)) {
      dispatch(SetDepartments(departmentsData.data));
      return departmentsData.data;
    }
    return [];
  }, [departmentsData]);

  const user = useAuthStore();
  const { name: tenantName } = useTenantStore().tenant;
  const departmentObservedLabel = changeLabelOnBasisOfTenant(
    tenantName,
    "Department Observed"
  );
  const subOpCoObservedLabel = changeLabelOnBasisOfTenant(
    tenantName,
    "Sub OpCo Observed"
  );

  useEffect(() => {
    if (user.me.opco && E.isLeft(model.opCoType.val)) {
      pipe(user.me.opco.id, O.of, OpCoChanged, dispatch);
    }
  }, [user]);

  const displayHECARulesByTenant = (nameOfTenant: string) => {
    switch (nameOfTenant) {
      case "xcelenergy":
      case "test-xcelenergy":
      case "test-xcelenergy1":
        return <HecaRulesForXcelEnergy />;
      default:
        return <HecaRulesForExelon />;
    }
  };
  return (
    <StepLayout>
      <div className="p-4 md:p-0">
        <TaskCard
          isOpen={model.isHecaRulesOpen}
          taskHeader={
            <TaskHeader
              onClick={flow(ToggleHecaRules, dispatch)}
              icon={
                model.isHecaRulesOpen ? "chevron_big_down" : "chevron_big_right"
              }
              headerText={"HECA Rules"}
            />
          }
        >
          {displayHECARulesByTenant(tenantName)}
        </TaskCard>
        <FieldGroup legend="Job Details">
          <Input
            id={formElementIds.observationDate}
            type="date"
            label="Observation Date *"
            field={model.observationDate}
            onChange={flow(ObservationDateChanged, dispatch)}
            disabled={isReadOnly}
            hasError={pipe(
              model.formElementIdsWithError,
              A.elem(EqString)(formElementIds.observationDate)
            )}
          />
          <Input
            id={formElementIds.observationTime}
            type="time"
            label="Observation Time *"
            field={model.observationTime}
            onChange={flow(ObservationTimeChanged, dispatch)}
            disabled={isReadOnly}
            hasError={pipe(
              model.formElementIdsWithError,
              A.elem(EqString)(formElementIds.observationTime)
            )}
          />
          <InputRaw
            id={formElementIds.workOrderNumber}
            label="WO Number"
            placeholder="Ex: 583409"
            value={model.workOrderNumber}
            onChange={flow(WorkOrderNumberChanged, dispatch)}
            disabled={isReadOnly}
            hasError={pipe(
              model.formElementIdsWithError,
              A.elem(EqString)(formElementIds.workOrderNumber)
            )}
          />
          <Select
            id={formElementIds.opCoType}
            label="OpCo Observed *"
            options={parentOpCos.map(m => ({
              label: m.attributes.name,
              value: m.id,
            }))}
            selected={model.opCoType.raw}
            onSelected={flow(OpCoChanged, dispatch)}
            renderLabel={stringLabel}
            optionKey={identity}
            disabled={isReadOnly}
            hasError={pipe(
              model.formElementIdsWithError,
              A.elem(EqString)(formElementIds.opCoType)
            )}
          />
          <OptionalView
            value={A.isNonEmpty(subOpCos) ? O.some(subOpCos) : O.none}
            render={() => (
              <Select
                id={formElementIds.subOpCoType}
                label={`${subOpCoObservedLabel} *`}
                options={subOpCos.map(m => ({
                  label: m.attributes.name,
                  value: m.id,
                }))}
                selected={model.subOpCoType.raw}
                onSelected={flow(SubOpCoChanged, dispatch)}
                renderLabel={stringLabel}
                optionKey={identity}
                disabled={isReadOnly}
                hasError={pipe(
                  model.formElementIdsWithError,
                  A.elem(EqString)(formElementIds.subOpCoType)
                )}
              />
            )}
          />
          <Select
            id={formElementIds.departmentObserved}
            label={`${departmentObservedLabel} *`}
            labelClassName="block text-tiny md:text-sm text-neutral-shade-75 font-semibold mb-2 leading-normal"
            options={departments.map(d => ({
              label: d.attributes.name,
              value: d.id,
            }))}
            selected={model.departmentObserved.raw}
            onSelected={flow(DepartmentObservedChanged, dispatch)}
            renderLabel={stringLabel}
            typeaheadOptionLabel={identity}
            optionKey={identity}
            disabled={isReadOnly}
            hasError={pipe(
              model.formElementIdsWithError,
              A.elem(EqString)(formElementIds.departmentObserved)
            )}
          />
          <MultiSelect
            id={formElementIds.workTypes}
            labelClassName="block text-tiny md:text-sm text-neutral-shade-75 font-semibold mb-2 leading-normal"
            label="Work type *"
            placeholder="Choose the observed work types"
            valueEq={eqWorkTypeById}
            options={pipe(
              workTypes,
              O.map((tenantWorkTypes: WorkType[]) => {
                const existingWorkTypes = model.workType;
                const allWorkTypes = pipe(
                  A.concat(tenantWorkTypes)(existingWorkTypes),
                  A.uniq(eqWorkTypeById)
                );
                return A.map((wt: WorkType) => ({ label: wt.name, value: wt }))(
                  allWorkTypes
                );
              }),
              O.getOrElse((): { label: string; value: WorkType }[] =>
                // If no tenant work types are available, still show existing work types
                pipe(
                  model.workType,
                  A.map((wt: WorkType) => ({ label: wt.name, value: wt }))
                )
              )
            )}
            selected={model.workType}
            onSelected={flow(WorkTypeChanged, dispatch)}
            onRemoved={flow(WorkTypeRemoved, dispatch)}
            renderLabel={identity}
            optionKey={w => w.name}
            disabled={isReadOnly}
            hasError={
              pipe(
                model.formElementIdsWithError,
                A.elem(EqString)(formElementIds.workTypes)
              ) && A.isEmpty(model.workType)
            }
          />
        </FieldGroup>
        <FieldGroup id={formElementIds.workLocation} legend="Work Location *">
          <div className="flex flex-col gap-4 w-full">
            <EboLocationAutocomplete
              value={model.workLocation.raw.location}
              locationDetails={model.workLocation.raw}
              onPlaceSelected={val =>
                pipe(
                  {
                    ...model.workLocation.raw,
                    location: val.place,

                    latitude: val.latitude || model.workLocation.raw.latitude,
                    longitude:
                      val.longitude || model.workLocation.raw.longitude,
                    isManualCoordinates:
                      model.workLocation.raw.isManualCoordinates,
                  },
                  WorkLocationChanged,
                  dispatch
                )
              }
              isManualCoordinates={model.workLocation.raw.isManualCoordinates}
              disabled={isReadOnly}
              hasError={pipe(
                model.formElementIdsWithError,
                A.elem(EqString)(formElementIds.workLocation)
              )}
            ></EboLocationAutocomplete>
            <label className="text-neutral-shade-75 font-semibold leading-normal">
              GPS Coordinate
            </label>
            <div className="flex flex-row flex-wrap gap-4 w-full">
              <InputRaw
                type="number"
                label="Current Latitude"
                value={model.workLocation.raw.latitude}
                onChange={val =>
                  pipe(
                    {
                      ...model.workLocation.raw,
                      latitude: val,
                      isManualCoordinates: true,
                    },
                    WorkLocationChanged,
                    dispatch
                  )
                }
                disabled={isReadOnly}
                hasError={pipe(
                  model.formElementIdsWithError,
                  A.elem(EqString)(formElementIds.workLocation)
                )}
              />
              <InputRaw
                type="number"
                label="Current Longitude"
                value={model.workLocation.raw.longitude}
                onChange={val =>
                  pipe(
                    {
                      ...model.workLocation.raw,
                      longitude: val,
                      isManualCoordinates: true,
                    },
                    WorkLocationChanged,
                    dispatch
                  )
                }
                disabled={isReadOnly}
                hasError={pipe(
                  model.formElementIdsWithError,
                  A.elem(EqString)(formElementIds.workLocation)
                )}
              />
            </div>
          </div>
          <div className="flex flex-col gap-4 w-full">
            {E.isRight(getPosition) && (
              <div className="flex flex-row gap-4">
                <ButtonRegular
                  iconStart="target"
                  onClick={getPosition.right}
                  label="Use my current location"
                  className="text-brand-urbint-40"
                  disabled={isReadOnly}
                />
              </div>
            )}
          </div>
        </FieldGroup>
      </div>
    </StepLayout>
  );
}

export default View;
