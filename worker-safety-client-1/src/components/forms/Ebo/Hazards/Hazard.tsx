import type { Hazard, HazardControl, HazardControlId } from "@/api/codecs";
import type {
  Action,
  HazardFieldValues,
} from "@/components/forms/Ebo/HighEnergyTaskSubSection/HighEnergyTaskSubSection";
import type { Option } from "fp-ts/lib/Option";
import * as A from "fp-ts/Array";
import * as O from "fp-ts/Option";
import * as S from "fp-ts/Set";
import {
  Eq as eqString,
  Ord as ordString,
  isEmpty as isEmptyString,
} from "fp-ts/string";
import cx from "classnames";
import { identity, pipe } from "fp-ts/function";
import { Icon } from "@urbint/silica";
import { useMemo } from "react";
import * as EQ from "fp-ts/Eq";
import { capitalize } from "lodash-es";
import { ControlType, ordHazardControlName } from "@/api/codecs";
import ButtonSecondary from "@/components/shared/button/secondary/ButtonSecondary";
import { MultiSelect } from "@/components/forms/Basic/MultiSelect";
import { EnergyType } from "@/api/generated/types";
import Switch from "@/components/switch/Switch";
import { FieldGroup } from "@/components/shared/FieldGroup";
import { AutoResizeTextArea } from "@/components/forms/Basic/AutoResizeTextarea";
import { useTenantStore } from "@/store/tenant/useTenantStore.store";
import {
  ChangeHazardDescription,
  ChangeEnergyLevel,
  CopyObservedHazard,
  DeleteObservedHazardCopy,
  HazardObserved,
  RemovedDirectControl,
  RemovedLimitedControl,
  ChangeDirectControlsDescription,
  ChangeLimitedControlsDescription,
  SelectedDirectControl,
  SelectedLimitedControl,
  SelectedNoDirectControlReason,
  ToggleIsDirectControlsImplemented,
  getOtherControlName,
  isOtherHazard,
  energyLevelValidation,
} from "../HighEnergyTaskSubSection/HighEnergyTaskSubSection";
import { Select } from "../../Basic/Select";
import { stringLabel } from "../../Basic/SelectOption";
import {
  getUncontrolledReasons,
  getLabels,
} from "../TenantLabel/LabelOnBasisOfTenant";

const TEXTAREA_ROW_COUNT = 1;
const EEI_CALCULATOR_LINK =
  "https://safetyapp.shinyapps.io/energy_calculator_public/?key=k6idwcep3sk7m_n1ef8uhq8cxnuatorzdh2uu9stz_tjs-tobatg7nzc1_g5";

export const IMAGE_MAP: Record<string, string> = {
  "Electrical - Contact with Source": "ElectricContactWithSource",
  "Electrical - Arc Flash": "ArchFlash",
  "Gravity - Fall from Elevation": "FallFromElevation",
  "Mechanical - Heavy Rotating Equipment": "HeavyRotatingEquipment",
  "Temperature - Steam": "Steam",
  "Pressure - Explosion": "Fire",
  "Chemical/Radiation - High Dose of Toxic Chemicals/Radiation": "Chemical",
  "Motion - Motor vehicle incident": "MotorVehicleIncident",
  "Motion - Mobile Equipment and Workers on Foot": "MotionMobileEquipment",
  "Gravity - Suspended Loads": "SuspendedLoad",
  "Temperature - High Temperature": "HighTemperature",
  "Temperature - Fire with Sustained Fuel Source":
    "FireWithSustainedFuelSource",
  "Pressure - Excavation or Trench": "ExcavationOfTrench",
};

export const getControlsByType =
  (controls: HazardControl[]) =>
  (type: ControlType): HazardControl[] =>
    pipe(
      controls,
      A.filter(c =>
        EQ.eqStrict.equals(O.isSome(c.controlType) && c.controlType.value, type)
      )
    );

type HazardComponentProps = {
  isBaseHazard: boolean;
  copyId?: Option<number>;
  hazard: Hazard;
  formValues: O.Option<HazardFieldValues>;
  dispatch: (action: Action) => void;
  additionalTitle: string;
  allowCopy: boolean;
  allowDelete: boolean;
  closeDropDownOnOutsideClick?: boolean;
  isReadOnly: boolean;
};

type LimitedControlsProps = {
  show: boolean;
  required: boolean;
};

const getLimitedControlsProps = (
  formValues: Option<HazardFieldValues>,
  UN_CONTROLLED_REASONS: { label: string }[]
): LimitedControlsProps => {
  let show = true;
  let required = false;

  if (O.isSome(formValues)) {
    const values = formValues.value;

    if (!O.isSome(values.isDirectControlsImplemented)) {
      show = false;
    } else if (O.isSome(values.noDirectControls)) {
      if (
        [
          UN_CONTROLLED_REASONS[3].label,
          UN_CONTROLLED_REASONS[4].label,
        ].includes(values.noDirectControls.value)
      ) {
        show = false;
      } else if (
        values.noDirectControls.value === UN_CONTROLLED_REASONS[2].label
      ) {
        required = true;
      }
    }
  }

  return { show, required };
};

const getOtherControlIdByControlType =
  (controlType: ControlType) =>
  (controls: HazardControl[]): Option<HazardControlId> =>
    pipe(
      controls,
      A.filter(
        control =>
          O.isSome(control.controlType) &&
          control.controlType.value === controlType
      ),
      A.filter(control => control.name === getOtherControlName(controlType)),
      A.map(control => control.id),
      A.head
    );

export const isOtherHazardControl =
  (control: HazardControl) => (controlType: ControlType) =>
    eqString.equals(control.name, getOtherControlName(controlType));

export const sortHazardControlsByOther =
  (controlType: ControlType) =>
  (controls: HazardControl[]): HazardControl[] => {
    return controls.sort((a: HazardControl, b: HazardControl): -1 | 0 | 1 => {
      if (isOtherHazardControl(a)(controlType)) return 1;
      if (isOtherHazardControl(b)(controlType)) return -1;

      return 0;
    });
  };

export const HazardComponent = ({
  isBaseHazard,
  copyId = O.none,
  hazard,
  formValues,
  dispatch,
  additionalTitle,
  allowCopy,
  allowDelete,
  closeDropDownOnOutsideClick = true,
  isReadOnly,
}: HazardComponentProps) => {
  const { name: tenantName } = useTenantStore().tenant;
  const UN_CONTROLLED_REASONS = getUncontrolledReasons(tenantName);

  const {
    directControlsLabel,
    directControlsImplementedLabel,
    chooseDirectControlsLabel,
    directControlDescriptionLabel,
    noDirectControlsReasonLabel,
    limitedControlsImplementedLabel,
    directControlTargeted,
    hazardsWithEnergy,
  } = getLabels(tenantName);

  const directControls = useMemo(
    () => getControlsByType(hazard.controls)(ControlType.DIRECT),
    [hazard]
  );

  const limitedControls = useMemo(
    () => getControlsByType(hazard.controls)(ControlType.INDIRECT),
    [hazard]
  );

  const limitedControlsProps = useMemo(
    (): LimitedControlsProps =>
      getLimitedControlsProps(formValues, UN_CONTROLLED_REASONS),
    [formValues, UN_CONTROLLED_REASONS]
  );

  const isDirectControlsDescriptionRequired = useMemo(() => {
    return pipe(
      hazard.controls,
      getOtherControlIdByControlType(ControlType.DIRECT),
      O.map(id =>
        pipe(
          formValues,
          O.map(fv => S.elem(EQ.eqString)(id, fv.directControls)),
          O.getOrElse(() => false)
        )
      ),
      O.getOrElse(() => false)
    );
  }, [hazard.controls, formValues]);

  const isLimitedControlsDescriptionRequired = useMemo(() => {
    return pipe(
      hazard.controls,
      getOtherControlIdByControlType(ControlType.INDIRECT),
      O.map(id =>
        pipe(
          formValues,
          O.map(fv => S.elem(EQ.eqString)(id, fv.limitedControls)),
          O.getOrElse(() => false)
        )
      ),
      O.getOrElse(() => false)
    );
  }, [hazard.controls, formValues]);

  return (
    <div id={hazard.id} className="shadow-10 rounded-lg box-border antialiased">
      <div className="flex flex-row justify-between items-center bg-neutral-shade-75 py-2 px-4 rounded-t-lg">
        <span className="text-white font-semibold">
          {O.isSome(hazard.energyType) &&
            `${
              hazard.energyType.value === EnergyType.NotDefined
                ? ""
                : capitalize(hazard.energyType.value)
            }  `}
          {hazard.name}
          {!pipe(additionalTitle, isEmptyString) && additionalTitle}
        </span>
        <div className="flex flex-row items-end gap-2">
          {allowCopy && !isReadOnly && (
            <Icon
              name="plus_circle"
              className="text-base text-white cursor-pointer"
              onClick={() => pipe(hazard.id, CopyObservedHazard, dispatch)}
            />
          )}
          {allowDelete && O.isSome(copyId) && (
            <Icon
              name="trash_empty"
              className="text-base text-white cursor-pointer"
              onClick={() =>
                pipe(
                  copyId.value,
                  DeleteObservedHazardCopy(hazard.id),
                  dispatch
                )
              }
            />
          )}
        </div>
      </div>
      <div
        className={cx("flex flex-col justify-start rounded-b-lg box-border", {
          ["border border-[#43565B]"]: hazard.isApplicable,
        })}
      >
        <div className="flex flex-col justify-center items-center gap-3 py-4">
          <div className="w-full h-20 relative flex justify-center">
            {/* eslint-disable @next/next/no-img-element  */}
            <img
              src={
                O.isSome(hazard.imageUrl)
                  ? hazard.imageUrl.value
                  : "https://restore-build-artefacts.s3.amazonaws.com/default_image.svg"
              }
              alt={hazard.name}
            />
          </div>
          <span className="text-neutral-shade-100 text-sm font-semibold antialiased">
            High-energy hazard observed/present
          </span>
          <Switch
            isDisabled={!isBaseHazard || isReadOnly}
            onToggle={s => pipe(s, HazardObserved(hazard.id), dispatch)}
            stateOverride={O.isSome(formValues)}
          />
        </div>
        {O.isSome(formValues) && O.isSome(copyId) && (
          <div className="flex flex-col p-4 gap-4">
            {isOtherHazard(hazard) && (
              <div className="flex flex-col gap-2">
                <p className="block text-sm font-semibold leading-normal">
                  Please use the EEI calculator in the following link to
                  calculate the energy for your other hazard
                </p>
                <div className="flex justify-center">
                  {!isReadOnly && (
                    <ButtonSecondary
                      iconStart="calculator"
                      label="Energy Calculator"
                      className="w-fit"
                      onClick={() => window.open(EEI_CALCULATOR_LINK, "_blank")}
                    />
                  )}
                </div>
                <div className="flex flex-col gap-1">
                  <label className="block text-sm font-semibold leading-normal">
                    How many foot-pounds are present for this high energy
                    hazard? *
                  </label>
                  <input
                    type="number"
                    placeholder="Enter the energy result in foot-pounds"
                    className={cx(
                      "w-full p-2 border-solid border-[1px] border-brand-gray-40 rounded",
                      formValues.value.energyLevel.dirty &&
                        !energyLevelValidation(formValues.value.energyLevel.raw)
                        ? "border-system-error-40"
                        : "border-brand-gray-40"
                    )}
                    value={formValues.value.energyLevel.raw}
                    onChange={e =>
                      pipe(
                        e.target.value,
                        ChangeEnergyLevel(hazard.id)(copyId.value),
                        dispatch
                      )
                    }
                    disabled={isReadOnly}
                  />
                  {formValues.value.energyLevel.dirty &&
                    !energyLevelValidation(
                      formValues.value.energyLevel.raw
                    ) && (
                      <span className="block text-sm leading-normal text-system-error-40">
                        {hazardsWithEnergy}
                      </span>
                    )}
                </div>
              </div>
            )}
            <div className="flex flex-col gap-1">
              <label className="block text-sm font-semibold leading-normal">
                Hazard Description
              </label>
              <AutoResizeTextArea
                rows={1}
                value={formValues.value.description}
                onChange={e =>
                  pipe(
                    e.target.value,
                    ChangeHazardDescription(hazard.id)(copyId.value),
                    dispatch
                  )
                }
                placeholder="Detailed description of the Hazard"
                disabled={isReadOnly}
              />
            </div>
            <div className="flex flex-col gap-1">
              <label className="block text-sm font-semibold leading-normal">
                {directControlsImplementedLabel} *
              </label>
              <span className="block text-sm font-normal">
                {directControlTargeted}
              </span>
              <div className="flex gap-2 pt-2">
                <ButtonSecondary
                  className={cx("flex-1", {
                    ["!text-white !bg-brand-urbint-40"]:
                      O.isSome(formValues.value.isDirectControlsImplemented) &&
                      formValues.value.isDirectControlsImplemented.value,
                  })}
                  label="Yes"
                  onClick={() =>
                    pipe(
                      pipe(
                        formValues.value.isDirectControlsImplemented,
                        O.map(curr => (curr ? O.none : O.some(true))),
                        O.getOrElse(() => O.some(true))
                      ),
                      ToggleIsDirectControlsImplemented(hazard.id)(
                        copyId.value
                      ),
                      dispatch
                    )
                  }
                  disabled={isReadOnly}
                />
                <ButtonSecondary
                  className={cx("flex-1", {
                    ["!text-white !bg-brand-urbint-40"]:
                      O.isSome(formValues.value.isDirectControlsImplemented) &&
                      !formValues.value.isDirectControlsImplemented.value,
                  })}
                  label="No"
                  onClick={() =>
                    pipe(
                      pipe(
                        formValues.value.isDirectControlsImplemented,
                        O.map(curr => (curr ? O.some(false) : O.none)),
                        O.getOrElse(() => O.some(false))
                      ),
                      ToggleIsDirectControlsImplemented(hazard.id)(
                        copyId.value
                      ),
                      dispatch
                    )
                  }
                  disabled={isReadOnly}
                />
              </div>
            </div>
            {O.isSome(formValues.value.isDirectControlsImplemented) &&
              formValues.value.isDirectControlsImplemented.value && (
                <div className="flex flex-col gap-1">
                  <label className="block text-sm font-semibold leading-normal">
                    {chooseDirectControlsLabel} *
                  </label>
                  <FieldGroup>
                    <div className="flex flex-col gap-1">
                      <label className="block text-sm font-semibold leading-normal">
                        {directControlsLabel}
                      </label>
                      <MultiSelect
                        typeahead
                        placeholder="Select options"
                        options={pipe(
                          directControls,
                          A.sort(ordHazardControlName),
                          sortHazardControlsByOther(ControlType.DIRECT),
                          A.map(c => ({ label: c.name, value: c.id }))
                        )}
                        renderLabel={identity}
                        optionKey={identity}
                        selected={pipe(
                          formValues.value.directControls,
                          S.toArray(ordString)
                        )}
                        onSelected={directControlId =>
                          pipe(
                            directControlId,
                            SelectedDirectControl(hazard.id)(copyId.value),
                            dispatch
                          )
                        }
                        onRemoved={directControlId =>
                          pipe(
                            directControlId,
                            RemovedDirectControl(hazard.id)(copyId.value),
                            dispatch
                          )
                        }
                        closeOnOutsideClick={closeDropDownOnOutsideClick}
                        disabled={isReadOnly}
                      />
                    </div>
                    <div className="flex flex-col gap-1">
                      <label className="block text-sm font-semibold leading-normal">
                        {directControlDescriptionLabel}{" "}
                        {isDirectControlsDescriptionRequired && "*"}
                      </label>
                      <AutoResizeTextArea
                        className="py-1"
                        containerClassName="after:py-1"
                        rows={TEXTAREA_ROW_COUNT}
                        required={isDirectControlsDescriptionRequired}
                        value={formValues.value.directControlDescription}
                        onChange={e =>
                          pipe(
                            e.target.value,
                            ChangeDirectControlsDescription(hazard.id)(
                              copyId.value
                            ),
                            dispatch
                          )
                        }
                        placeholder="Detailed description of the control"
                        disabled={isReadOnly}
                      />
                    </div>
                  </FieldGroup>
                </div>
              )}

            {O.isSome(formValues.value.isDirectControlsImplemented) &&
              !formValues.value.isDirectControlsImplemented.value && (
                <div className="flex flex-col gap-1">
                  <label className="block text-sm font-semibold leading-normal">
                    {noDirectControlsReasonLabel} *
                  </label>
                  <Select
                    placeholder="Select option"
                    options={pipe(
                      UN_CONTROLLED_REASONS,
                      A.map(reason => ({
                        value: reason.label,
                        label: reason.label,
                      }))
                    )}
                    renderLabel={label => (
                      <div className="">{stringLabel(label)}</div>
                    )}
                    optionKey={identity}
                    selected={pipe(
                      formValues.value.noDirectControls,
                      O.fold(
                        () => O.none,
                        v => O.some(v)
                      )
                    )}
                    onSelected={reason =>
                      pipe(
                        reason,
                        SelectedNoDirectControlReason(hazard.id)(copyId.value),
                        dispatch
                      )
                    }
                    closeOnOutsideClick={closeDropDownOnOutsideClick}
                    disabled={isReadOnly}
                  />
                </div>
              )}
            {limitedControlsProps.show && (
              <>
                <div className="flex flex-col gap-1">
                  <label className="block text-sm font-semibold leading-normal">
                    {limitedControlsImplementedLabel}{" "}
                    {limitedControlsProps.required ? "*" : ""}
                  </label>
                  <MultiSelect
                    typeahead
                    placeholder="Select options"
                    options={pipe(
                      limitedControls,
                      A.sort(ordHazardControlName),
                      sortHazardControlsByOther(ControlType.INDIRECT),
                      A.map(control => ({
                        value: control.id,
                        label: control.name,
                      }))
                    )}
                    renderLabel={identity}
                    optionKey={identity}
                    selected={pipe(
                      formValues.value.limitedControls,
                      S.toArray(ordString)
                    )}
                    onSelected={limitedControl =>
                      pipe(
                        limitedControl,
                        SelectedLimitedControl(hazard.id)(copyId.value),
                        dispatch
                      )
                    }
                    onRemoved={limitedControl =>
                      pipe(
                        limitedControl,
                        RemovedLimitedControl(hazard.id)(copyId.value),
                        dispatch
                      )
                    }
                    closeOnOutsideClick={closeDropDownOnOutsideClick}
                    disabled={isReadOnly}
                  />
                </div>
                <div className="flex flex-col gap-1">
                  <label className="block text-sm font-semibold leading-normal">
                    Limited Control Description{" "}
                    {isLimitedControlsDescriptionRequired && "*"}
                  </label>
                  <AutoResizeTextArea
                    className="py-1"
                    containerClassName="after:py-1"
                    rows={TEXTAREA_ROW_COUNT}
                    required={isLimitedControlsDescriptionRequired}
                    value={formValues.value.limitedControlDescription}
                    onChange={e =>
                      pipe(
                        e.target.value,
                        ChangeLimitedControlsDescription(hazard.id)(
                          copyId.value
                        ),
                        dispatch
                      )
                    }
                    placeholder="Detailed description of the control"
                    disabled={isReadOnly}
                  />
                </div>
              </>
            )}
          </div>
        )}
      </div>
    </div>
  );
};
