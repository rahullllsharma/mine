import type { SaveJobSafetyBriefingInput } from "@/api/generated/types";
import type { FormField } from "@/utils/formField";
import type { ChildProps, Effect } from "@/utils/reducerWithEffect";
import type { ValidPhoneNumber } from "@/utils/validation";
import type { Option } from "fp-ts/Option";
import type { ApiResult } from "@/api/api";
import type { Deferred } from "@/utils/deferred";
import type { LastJsbContents } from "@/api/codecs/lastAddedJobSafetyBriefing";
import type { StepSnapshot, StepSnapshotValue } from "../Utils";
import type { Jsb, MedicalFacility } from "@/api/codecs";
import type * as t from "io-ts";
import * as E from "fp-ts/Either";
import * as O from "fp-ts/Option";
import { sequenceS } from "fp-ts/lib/Apply";
import * as A from "fp-ts/lib/Array";
import * as NEA from "fp-ts/lib/NonEmptyArray";
import { constNull, flow, identity, pipe } from "fp-ts/lib/function";
import { NonEmptyString, optionFromNullable } from "io-ts-types";
import { useMemo } from "react";
import { Eq as eqString } from "fp-ts/lib/string";
import * as Eq from "fp-ts/lib/Eq";
import { boolean } from "fp-ts";
import { medicalFacilityCodec } from "@/api/codecs";
import { nonEmptyStringCodec, validPhoneNumberCodec } from "@/utils/validation";
import { fieldDef, setDirty } from "@/utils/formField";
import { noEffect } from "@/utils/reducerWithEffect";
import { OptionalView } from "@/components/common/Optional";
import { Input } from "../Basic/Input";
import { Select } from "../Basic/Select";
import StepLayout from "../StepLayout";
import { FieldGroup } from "../../shared/FieldGroup";
import { TelephoneInput } from "../Basic/Input/TelephoneInput";
import { stringLabel } from "../Basic/SelectOption";

const medicalDevices = A.prepend({
  value: "Cab of truck",
  label: "Cab of truck",
})([
  {
    value: "Truck driver side compartment",
    label: "Truck driver side compartment",
  },
  {
    value: "Other",
    label: "Other",
  },
]);

const lookupAedLocation = (location: string): Option<string> =>
  pipe(
    medicalDevices,
    A.findFirst(({ value }) => value === location),
    O.fold(
      () =>
        pipe(
          medicalDevices,
          A.findFirst(({ value }) => value === "Other"),
          O.map(({ value }) => value)
        ),
      loc => O.of(loc.value)
    )
  );

// const mockMedicalFacilities: Deferred<ApiResult<MedicalFacility[]>> = Resolved(
//   E.right([
//     {
//       description: literalNES("F.F. THOMPSON HOSPITAL"),
//       address: O.some(literalNES("350 PARRISH STREET")),
//       city: O.some(literalNES("350 PARRISH STREET")),
//       distanceFromJob: O.some(7.063562543103555),
//       phoneNumber: O.some(literalNES("(716) 396-6527")),
//       state: O.some(literalNES("NY")),
//       zip: O.some(14424 as t.Int),
//     },
//     {
//       description: literalNES("CLIFTON SPRINGS HOSPITAL AND CLINIC"),
//       address: O.some(literalNES("2 COULTER ROAD")),
//       city: O.some(literalNES("2 COULTER ROAD")),
//       distanceFromJob: O.some(15.305668369406616),
//       phoneNumber: O.some(literalNES("(315) 462-1311")),
//       state: O.some(literalNES("NY")),
//       zip: O.some(14432 as t.Int),
//     },
//     {
//       description: literalNES("EMORY JOHNS CREEK HOSPITAL"),
//       address: O.some(literalNES("6325 HOSPITAL PARKWAY")),
//       city: O.some(literalNES("6325 HOSPITAL PARKWAY")),
//       distanceFromJob: O.some(8.8207306957579),
//       phoneNumber: O.some(literalNES("(678) 474-7000")),
//       state: O.some(literalNES("GA")),
//       zip: O.some(30097 as t.Int),
//     },
//   ])
// );

type MedicalFacilityLabel = {
  name: string;
  distance: Option<number>;
};

type MedicalFacilityValue =
  | {
      type: "Listed";
      facility: MedicalFacility;
    }
  | {
      type: "Other";
    };

const eqMedicalFacilityValue: Eq.Eq<MedicalFacilityValue> = Eq.fromEquals(
  (a, b) => {
    if (a.type === "Listed" && b.type === "Listed") {
      return a.facility.description === b.facility.description;
    } else {
      return a.type === b.type;
    }
  }
);

type MedicalFacilityOption = {
  label: MedicalFacilityLabel;
  value: MedicalFacilityValue;
};

export type Model = {
  emergencyContactName: FormField<t.Errors, string, NonEmptyString>;
  emergencyContactPhone: FormField<t.Errors, string, ValidPhoneNumber>;
  emergencyContactName2: FormField<t.Errors, string, NonEmptyString>;
  emergencyContactPhone2: FormField<t.Errors, string, ValidPhoneNumber>;
  selectedMedicalFacility: Option<MedicalFacilityValue>;
  otherMedicalFacilityDescription: FormField<t.Errors, string, NonEmptyString>;
  selectedMedicalDevice: string;
  otherSelectedMedicalDevice: FormField<t.Errors, string, NonEmptyString>;
};

export function setFormDirty(model: Model): Model {
  return {
    ...model,
    emergencyContactName: setDirty(model.emergencyContactName),
    emergencyContactPhone: setDirty(model.emergencyContactPhone),
    emergencyContactName2: setDirty(model.emergencyContactName2),
    emergencyContactPhone2: setDirty(model.emergencyContactPhone2),
    otherMedicalFacilityDescription: setDirty(
      model.otherMedicalFacilityDescription
    ),
    otherSelectedMedicalDevice: setDirty(model.otherSelectedMedicalDevice),
  };
}

export function withoutNearestMedicalFacilities(model: Model): Model {
  return {
    ...model,
    selectedMedicalFacility: O.some({ type: "Other" }),
  };
}

// holding the below function as we are not taking medical facility from lat long change manually
export function resetSelectedMedicalFacility(model: Model): Model {
  return {
    ...model,
    selectedMedicalFacility: O.none,
    otherMedicalFacilityDescription:
      formDef.otherMedicalFacilityDescription.update(""),
  };
}

export function makeSnapshot(model: Model): StepSnapshot {
  const selectedMedicalFacility: StepSnapshotValue | null = pipe(
    model.selectedMedicalFacility,
    O.fold(constNull, facility =>
      facility.type === "Listed"
        ? {
            description: facility.facility.description,
            address: O.getOrElseW(constNull)(facility.facility.address),
            city: O.getOrElseW(constNull)(facility.facility.city),
            distance: O.getOrElseW(constNull)(
              facility.facility.distanceFromJob
            ),
            phoneNumber: O.getOrElseW(constNull)(facility.facility.phoneNumber),
            state: O.getOrElseW(constNull)(facility.facility.state),
            zip: O.getOrElseW(constNull)(facility.facility.zip),
          }
        : {
            description: model.otherMedicalFacilityDescription.raw,
            address: null,
            city: null,
            distance: null,
            phoneNumber: null,
            state: null,
            zip: null,
          }
    )
  );

  return {
    emergencyContactName: model.emergencyContactName.raw,
    emergencyContactPhone: model.emergencyContactPhone.raw,
    emergencyContactName2: model.emergencyContactName2.raw,
    emergencyContactPhone2: model.emergencyContactPhone2.raw,
    selectedMedicalFacility,
    selectedMedicalDevice: model.selectedMedicalDevice,
    otherSelectedMedicalDevice: model.otherSelectedMedicalDevice.raw,
  };
}

export function toSaveJsbInput(model: Model) {
  const selectedListedMedicalFacility = pipe(
    model.selectedMedicalFacility,
    O.filterMap(selection =>
      selection.type === "Listed" ? O.some(selection.facility) : O.none
    )
  );

  return pipe(
    sequenceS(E.Apply)({
      emergencyContactName: model.emergencyContactName.val,
      emergencyContactPhone: model.emergencyContactPhone.val,
      emergencyContactName2: model.emergencyContactName2.val,
      emergencyContactPhone2: model.emergencyContactPhone2.val,
      selectedMedicalFacility: E.right(selectedListedMedicalFacility),
      otherMedicalFacility: O.isNone(selectedListedMedicalFacility)
        ? pipe(model.otherMedicalFacilityDescription.val, E.map(O.some))
        : E.right(O.none),
      // used to trigger the "required" validation for medical facility
      // the logic is "description should come from somewhere".
      // It can be from the selected listed medical facility or from user input for "other" medical facility
      medicalFacilityDescription: pipe(
        model.selectedMedicalFacility,
        O.fold(
          () => model.otherMedicalFacilityDescription.val,
          selection =>
            selection.type === "Listed"
              ? E.right(selection.facility.description)
              : model.otherMedicalFacilityDescription.val
        )
      ),
      otherSelectedMedicalDevice: pipe(
        model.selectedMedicalDevice,
        smd => smd === "Other",
        boolean.match(
          (): E.Either<t.Errors, string> =>
            E.right(model.selectedMedicalDevice),
          () => model.otherSelectedMedicalDevice.val
        )
      ),
    }),
    E.map(
      (res): SaveJobSafetyBriefingInput => ({
        emergencyContacts: [
          {
            name: res.emergencyContactName?.trim(),
            phoneNumber: res.emergencyContactPhone,
            primary: true,
          },
          {
            name: res.emergencyContactName2?.trim(),
            phoneNumber: res.emergencyContactPhone2,
            primary: false,
          },
        ],
        nearestMedicalFacility: pipe(
          res.selectedMedicalFacility,
          O.fold(constNull, medicalFacilityCodec.encode)
        ),
        customNearestMedicalFacility: pipe(
          res.otherMedicalFacility,
          O.fold(constNull, description => ({ address: description }))
        ),
        aedInformation: {
          location:
            model.selectedMedicalDevice === "Other"
              ? res.otherSelectedMedicalDevice
              : model.selectedMedicalDevice,
        },
      })
    )
  );
}

const formDef = {
  emergencyContactName: fieldDef(nonEmptyStringCodec().decode),
  emergencyContactPhone: fieldDef(validPhoneNumberCodec.decode),
  emergencyContactName2: fieldDef(nonEmptyStringCodec().decode),
  emergencyContactPhone2: fieldDef(validPhoneNumberCodec.decode),
  selectedMedicalFacility: fieldDef(optionFromNullable(NonEmptyString).decode),
  otherMedicalFacilityDescription: fieldDef(nonEmptyStringCodec().decode),
  otherSelectedMedicalDevice: fieldDef(nonEmptyStringCodec().decode),
};

export const init = (
  jsb: Option<Jsb>,
  lastJsb: Option<LastJsbContents>
): Model => {
  const lastJsbSelectedMedicalDevice = () =>
    pipe(
      lastJsb,
      O.chain(j => j.aedInformation),
      O.chain(aed => lookupAedLocation(aed.location))
    );

  const lastJsbSelectedMedicalDeviceValue = () =>
    pipe(
      lastJsb,
      O.chain(j => j.aedInformation),
      O.map(aed => aed.location)
    );

  const lastEmergencyContactName = () =>
    pipe(
      lastJsb,
      O.chain(j => j.emergencyContacts),
      O.chain(A.lookup(0)),
      O.map(eco => eco.name)
    );

  const lastEmergencyContactPhone = () =>
    pipe(
      lastJsb,
      O.chain(j => j.emergencyContacts),
      O.chain(A.lookup(0)),
      O.map(eco => eco.phoneNumber)
    );

  const lastEmergencyContactName2 = () =>
    pipe(
      lastJsb,
      O.chain(j => j.emergencyContacts),
      O.chain(A.lookup(1)),
      O.map(eco => eco.name)
    );

  const lastEmergencyContactPhone2 = () =>
    pipe(
      lastJsb,
      O.chain(j => j.emergencyContacts),
      O.chain(A.lookup(1)),
      O.map(eco => eco.phoneNumber)
    );

  const lastJsbSelectedMedicalFacility = () =>
    pipe(
      lastJsb,
      O.chain(j => j.nearestMedicalFacility)
    );

  const medicalFacility = pipe(
    jsb,
    O.chain(j => j.nearestMedicalFacility),
    O.alt(lastJsbSelectedMedicalFacility)
  );

  const otherMedicalFacilityDescription = pipe(
    jsb,
    O.chain(j => j.customNearestMedicalFacility),
    O.map(cf => cf.address)
  );

  return {
    emergencyContactName: pipe(
      jsb,
      O.chain(j => j.emergencyContacts),
      O.chain(A.lookup(0)),
      O.map(eco => eco.name),
      O.alt(lastEmergencyContactName),
      O.getOrElse(() => ""),
      formDef.emergencyContactName.init
    ),
    emergencyContactPhone: pipe(
      jsb,
      O.chain(j => j.emergencyContacts),
      O.chain(A.lookup(0)),
      O.map(eco => eco.phoneNumber),
      O.alt(lastEmergencyContactPhone),
      O.getOrElse(() => ""),
      formDef.emergencyContactPhone.init
    ),
    emergencyContactName2: pipe(
      jsb,
      O.chain(j => j.emergencyContacts),
      O.chain(A.lookup(1)),
      O.map(eco => eco.name),
      O.alt(lastEmergencyContactName2),
      O.getOrElse(() => ""),
      formDef.emergencyContactName2.init
    ),
    emergencyContactPhone2: pipe(
      jsb,
      O.chain(j => j.emergencyContacts),
      O.chain(A.lookup(1)),
      O.map(eco => eco.phoneNumber),
      O.alt(lastEmergencyContactPhone2),
      O.getOrElse(() => ""),
      formDef.emergencyContactPhone2.init
    ),
    selectedMedicalFacility: pipe(
      otherMedicalFacilityDescription,
      O.fold(
        () =>
          pipe(
            medicalFacility,
            O.map(facility => ({ type: "Listed", facility }))
          ),
        _ => O.some<MedicalFacilityValue>({ type: "Other" })
      )
    ),
    otherMedicalFacilityDescription: pipe(
      otherMedicalFacilityDescription,
      O.fold(
        () => formDef.otherMedicalFacilityDescription.init(""),
        formDef.otherMedicalFacilityDescription.init
      )
    ),
    selectedMedicalDevice: pipe(
      jsb,
      O.chain(j => j.aedInformation),
      O.chain(aed => lookupAedLocation(aed.location)),
      O.alt(lastJsbSelectedMedicalDevice),
      O.getOrElse(() => NEA.head(medicalDevices).value)
    ),
    otherSelectedMedicalDevice: pipe(
      jsb,
      O.chain(j => j.aedInformation),
      O.chain(aed => lookupAedLocation(aed.location)),
      O.alt(lastJsbSelectedMedicalDevice),
      O.fold(
        () => "",
        loc =>
          pipe(
            eqString.equals(loc, "Other"),
            boolean.fold(
              () => "",
              () =>
                pipe(
                  jsb,
                  O.chain(j => j.aedInformation),
                  O.map(aed => aed.location),
                  O.alt(lastJsbSelectedMedicalDeviceValue),
                  O.getOrElse(() => "")
                )
            )
          )
      ),
      formDef.otherSelectedMedicalDevice.init
    ),
  };
};

export type Action =
  | {
      type: "EmergencyContactNameChanged";
      value: string;
    }
  | {
      type: "EmergencyContactPhoneChanged";
      value: string;
    }
  | {
      type: "EmergencyContactName2Changed";
      value: string;
    }
  | {
      type: "EmergencyContactPhone2Changed";
      value: string;
    }
  | {
      type: "SelectedMedicalFacilityChanged";
      value: Option<MedicalFacilityValue>;
    }
  | {
      type: "OtherMedicalFacilityDescriptionChanged";
      value: string;
    }
  | {
      type: "SelectedMedicalDeviceChanged";
      value: Option<string>;
    }
  | {
      type: "OtherSelectedMedicalDeviceChanged";
      value: string;
    };

const trimSpaces = (value: string) => {
  let trimmedValue = value;
  if (value.length === 1 && value === " ") {
    trimmedValue = value.trim();
  } else if (
    value[value.length - 1] === " " &&
    value[value.length - 2] === " "
  ) {
    trimmedValue = value.substring(0, value.length - 1);
  }

  return trimmedValue;
};

const EmergencyContactNameChanged = (value: string): Action => ({
  type: "EmergencyContactNameChanged",
  value: trimSpaces(value),
});

const EmergencyContactPhoneChanged = (value: string): Action => ({
  type: "EmergencyContactPhoneChanged",
  value,
});

const EmergencyContactName2Changed = (value: string): Action => ({
  type: "EmergencyContactName2Changed",
  value: trimSpaces(value),
});

const EmergencyContactPhone2Changed = (value: string): Action => ({
  type: "EmergencyContactPhone2Changed",
  value,
});

const SelectedMedicalFacilityChanged = (
  value: Option<MedicalFacilityValue>
): Action => ({
  type: "SelectedMedicalFacilityChanged",
  value,
});

const OtherMedicalFacilityDescriptionChanged = (value: string): Action => ({
  type: "OtherMedicalFacilityDescriptionChanged",
  value,
});

const SelectedMedicalDeviceChanged = (value: Option<string>): Action => ({
  type: "SelectedMedicalDeviceChanged",
  value,
});

const OtherSelectedMedicalDeviceChanged = (value: string): Action => ({
  type: "OtherSelectedMedicalDeviceChanged",
  value,
});

export const update = (
  model: Model,
  action: Action
): [Model, Effect<Action>] => {
  switch (action.type) {
    case "EmergencyContactNameChanged":
      return [
        {
          ...model,
          emergencyContactName: formDef.emergencyContactName.update(
            action.value
          ),
        },
        noEffect,
      ];
    case "EmergencyContactPhoneChanged":
      return [
        {
          ...model,
          emergencyContactPhone: formDef.emergencyContactPhone.update(
            action.value
          ),
        },
        noEffect,
      ];
    case "EmergencyContactName2Changed":
      return [
        {
          ...model,
          emergencyContactName2: formDef.emergencyContactName2.update(
            action.value
          ),
        },
        noEffect,
      ];

    case "EmergencyContactPhone2Changed":
      return [
        {
          ...model,
          emergencyContactPhone2: formDef.emergencyContactPhone2.update(
            action.value
          ),
        },
        noEffect,
      ];

    case "SelectedMedicalFacilityChanged":
      const shouldResetOtherMedicalFacilityDescription = (): boolean => {
        return (
          O.isNone(action.value) ||
          (O.isSome(action.value) && action.value.value.type !== "Other")
        );
      };

      return [
        {
          ...model,
          selectedMedicalFacility: action.value,
          ...(shouldResetOtherMedicalFacilityDescription() && {
            otherMedicalFacilityDescription:
              formDef.otherMedicalFacilityDescription.init(""),
          }),
        },
        noEffect,
      ];

    case "OtherMedicalFacilityDescriptionChanged":
      return [
        {
          ...model,
          otherMedicalFacilityDescription:
            formDef.otherMedicalFacilityDescription.update(action.value),
        },
        noEffect,
      ];

    case "SelectedMedicalDeviceChanged":
      return [
        {
          ...model,
          selectedMedicalDevice: pipe(
            action.value,
            O.getOrElse(() => "")
          ),
        },
        noEffect,
      ];

    case "OtherSelectedMedicalDeviceChanged":
      return [
        {
          ...model,
          otherSelectedMedicalDevice: formDef.otherSelectedMedicalDevice.update(
            action.value
          ),
        },
        noEffect,
      ];
  }
};

const showDistance = (distance: number): string =>
  `${Math.round(distance * 10) / 10}mi`;

export type Props = ChildProps<Model, Action> & {
  nearestMedicalFacilities: Deferred<ApiResult<MedicalFacility[]>>;
  isReadOnly: boolean;
};

export function View(props: Props): JSX.Element {
  const { model, dispatch, isReadOnly } = props;

  const medicalFacilitiesPlaceholder = useMemo(
    () => {
      switch (props.nearestMedicalFacilities.status) {
        case "NotStarted":
          return "Other";
        case "Resolved":
          return "Select nearest medical facility";

        case "InProgress":
        case "Updating":
          return "Loading nearest medical facilities...";
      }
    },
    // pipe(
    //   props.nearestMedicalFacilities,
    //   deferredToOption,
    //   O.fold(
    //     () => "Loading nearest medical facilities...",
    //     _ => "Select nearest medical facility"
    //   )
    // ),
    [props.nearestMedicalFacilities]
  );

  const medicalFacilityOptions = useMemo(() => {
    const otherOption: MedicalFacilityOption = {
      label: { name: "Other", distance: O.none },
      value: { type: "Other" },
    };

    switch (props.nearestMedicalFacilities.status) {
      case "NotStarted":
        return [otherOption];
      case "Resolved":
        return pipe(
          props.nearestMedicalFacilities.value,
          E.fold(
            (_): MedicalFacilityOption[] => [otherOption],
            flow(
              A.map(
                (facility): MedicalFacilityOption => ({
                  label: {
                    name: facility.description,
                    distance: facility.distanceFromJob,
                  },
                  value: { type: "Listed", facility },
                })
              ),
              A.append<MedicalFacilityOption>(otherOption)
            )
          )
        );

      case "InProgress":
        9;
      case "Updating":
        return [];
    }
  }, [props.nearestMedicalFacilities]);

  return (
    <StepLayout>
      <FieldGroup legend="Emergency Contacts">
        <Input
          type="text"
          label="Emergency Contact 1 (e.g. Supervisor) *"
          field={model.emergencyContactName}
          disabled={isReadOnly}
          onChange={flow(EmergencyContactNameChanged, dispatch)}
        />

        <TelephoneInput
          label="Emergency Contact 1 Phone Number *"
          field={model.emergencyContactPhone}
          disabled={isReadOnly}
          onChange={flow(EmergencyContactPhoneChanged, dispatch)}
        />

        <Input
          type="text"
          label="Emergency Contact 2 (e.g. Safety Supervisor) *"
          field={model.emergencyContactName2}
          disabled={isReadOnly}
          onChange={flow(EmergencyContactName2Changed, dispatch)}
        />

        <TelephoneInput
          label="Emergency Contact 2 Phone Number *"
          field={model.emergencyContactPhone2}
          disabled={isReadOnly}
          onChange={flow(EmergencyContactPhone2Changed, dispatch)}
        />
      </FieldGroup>

      <FieldGroup legend="Nearest Medical Facility *">
        <Select
          options={medicalFacilityOptions}
          placeholder={medicalFacilitiesPlaceholder}
          label="Selected Medical Facility"
          selected={model.selectedMedicalFacility}
          disabled={
            isReadOnly || props.nearestMedicalFacilities.status === "NotStarted"
          }
          onSelected={flow(SelectedMedicalFacilityChanged, dispatch)}
          valueEq={eqMedicalFacilityValue}
          renderLabel={({ name, distance }) => (
            <div className="flex flex-1 flex-row justify-between items-center">
              <span className="truncate max-w-md">{name}</span>
              <OptionalView
                value={distance}
                render={d => (
                  <span className="text-sm text-brand-gray-70">
                    {showDistance(d)}
                  </span>
                )}
              />
            </div>
          )}
          optionKey={value =>
            value.type === "Listed" ? value.facility.description : "other"
          }
        />

        <OptionalView
          value={pipe(
            model.selectedMedicalFacility,
            O.filterMap(f => (f.type === "Other" ? O.some({}) : O.none)),
            O.alt(() =>
              props.nearestMedicalFacilities.status === "NotStarted"
                ? O.some({})
                : O.none
            )
          )}
          render={() => (
            <Input
              required={true}
              type="text"
              label="Please specify the nearest medical facility *"
              field={model.otherMedicalFacilityDescription}
              disabled={isReadOnly}
              onChange={flow(OtherMedicalFacilityDescriptionChanged, dispatch)}
            />
          )}
        />
      </FieldGroup>

      <FieldGroup legend="Medical Devices">
        <Select
          options={medicalDevices}
          label="AED Location"
          selected={O.some(model.selectedMedicalDevice)}
          disabled={isReadOnly}
          onSelected={flow(SelectedMedicalDeviceChanged, dispatch)}
          renderLabel={stringLabel}
          optionKey={identity}
        />
        {model.selectedMedicalDevice === "Other" && (
          <Input
            type="text"
            label="Other AED Location *"
            field={model.otherSelectedMedicalDevice}
            disabled={isReadOnly}
            onChange={flow(OtherSelectedMedicalDeviceChanged, dispatch)}
          />
        )}
      </FieldGroup>
    </StepLayout>
  );
}
