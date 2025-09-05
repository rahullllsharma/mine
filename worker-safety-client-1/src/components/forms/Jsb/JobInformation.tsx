import type { FormField } from "@/utils/formField";
import type { ChildProps } from "@/utils/reducerWithEffect";
import type {
  GpsCoordinates,
  Jsb,
  LibraryRegion,
  ProjectLocation,
  State,
} from "@/api/codecs";
import type {
  SaveJobSafetyBriefingInput,
  WorkLocationInput,
} from "@/api/generated/types";
import type { ValidDateTime, ValidDuration } from "@/utils/validation";
import type { Option } from "fp-ts/Option";
import type {
  LastJsbContents,
  LastAdhocJsbContents,
} from "@/api/codecs/lastAddedJobSafetyBriefing";
import type { NonEmptyString } from "io-ts-types";
import type * as t from "io-ts";
import type { StepSnapshot } from "../Utils";
import type { Deferred } from "@/utils/deferred";
import type { ApiResult } from "@/api/api";
import * as E from "fp-ts/Either";
import * as O from "fp-ts/Option";
import { flow, identity, pipe } from "fp-ts/function";
import { sequenceS } from "fp-ts/lib/Apply";
import * as A from "fp-ts/lib/Array";
import { Apply as ApplyEither } from "fp-ts/lib/Either";
import * as tt from "io-ts-types";
import { useMemo } from "react";
import { DateTime } from "luxon";
import {
  nonEmptyStringCodec,
  optionFromString,
  validDateTimeCodecS,
  validDurationCodecS,
} from "@/utils/validation";
import {
  fieldDef,
  initFormField,
  setDirty,
  updateFormField,
} from "@/utils/formField";
import { getLocaleDateFormat } from "@/utils/date/helper";
import { Input } from "../Basic/Input";
import Labeled from "../Basic/Labeled";
import StepLayout from "../StepLayout";
import { FieldGroup } from "../../shared/FieldGroup";
import ButtonRegular from "../../shared/button/regular/ButtonRegular";
import InputDateSelect from "../../shared/inputDateSelect/InputDateSelect";
import { TextArea } from "../Basic/TextArea";
import { Select } from "../Basic/Select";
import { ErrorMessage } from "../Basic/ErrorMessage";

type WorkLocationFormField =
  | {
      type: "Description";
      description: FormField<t.Errors, string, NonEmptyString>;
      operatingHq: FormField<t.Errors, string, NonEmptyString>;
    }
  | {
      type: "AddressAndLocation";
      address: FormField<t.Errors, string, NonEmptyString>;
      location: FormField<t.Errors, string, NonEmptyString>;
    };

const Description = (
  address: string,
  operatingHq: string
): WorkLocationFormField => ({
  type: "Description",
  description: initFormField(nonEmptyStringCodec().decode)(address),
  operatingHq: initFormField(nonEmptyStringCodec().decode)(operatingHq),
});

const AddressAndLocation = (
  address: string,
  location: string
): WorkLocationFormField => ({
  type: "AddressAndLocation",
  address: formDef.address.init(address),
  location: formDef.workLocation.init(location),
});

const workLocationFormFieldResult =
  (state: State) =>
  (field: WorkLocationFormField): t.Validation<WorkLocationInput> => {
    switch (field.type) {
      case "Description":
        return sequenceS(E.Apply)({
          address: E.right(""),
          description: field.description.val,
          city: E.right(""),
          state: E.right(state),
          operatingHq: field.operatingHq.val,
        });
      case "AddressAndLocation":
        return sequenceS(E.Apply)({
          address: field.address.val,
          description: field.location.val,
          city: E.right(""),
          state: E.right(state),
        });
    }
  };

const setWorkLocationDirty = (field: WorkLocationFormField) => {
  switch (field.type) {
    case "Description":
      return {
        ...field,
        description: setDirty(field.description),
        operatingHq: setDirty(field.operatingHq),
      };
    case "AddressAndLocation":
      return {
        ...field,
        address: setDirty(field.address),
        location: setDirty(field.location),
      };
  }
};

export type Model = {
  /// Current and saved dates are used for validating briefing date
  currentDate: ValidDateTime; // to make past dates invalid
  savedBriefingDate: Option<ValidDateTime>; // except for previously saved date
  briefingDate: FormField<t.Errors, string, ValidDateTime>;
  briefingTime: FormField<t.Errors, string, ValidDuration>;
  workLocation: WorkLocationFormField;
  latitude: FormField<t.Errors, string, Option<number>>;
  longitude: FormField<t.Errors, string, Option<number>>;
  state: State;
  woCoords: Option<GpsCoordinates>;
  createdAt: Option<DateTime>;
};

const formDef = {
  // briefingDate codec is dynamic based on the current date and saved date
  // and it also uses different validation rules for init and update
  briefingTime: fieldDef(validDurationCodecS.decode),
  workLocation: fieldDef(nonEmptyStringCodec().decode),
  address: fieldDef(nonEmptyStringCodec().decode),
  description: fieldDef(nonEmptyStringCodec().decode),
  operatingHq: fieldDef(nonEmptyStringCodec().decode),
  longitude: fieldDef(optionFromString(tt.NumberFromString).decode),
  latitude: fieldDef(optionFromString(tt.NumberFromString).decode),
};

export function setFormDirty(model: Model): Model {
  return {
    ...model,
    briefingDate: setDirty(model.briefingDate),
    briefingTime: setDirty(model.briefingTime),
    workLocation: setWorkLocationDirty(model.workLocation),
    latitude: setDirty(model.latitude),
    longitude: setDirty(model.longitude),
  };
}

export function init(
  jsb: Option<Jsb>,
  projectLocation: Option<ProjectLocation>,
  dateTime: ValidDateTime,
  createdAt: Option<ValidDateTime>,
  lastJsb: Option<LastJsbContents>,
  lastAdhocJsb: Option<LastAdhocJsbContents>
): Model {
  const savedBriefingDate = pipe(
    jsb,
    O.chain(j => j.jsbMetadata),
    O.map(dt => dt.briefingDateTime)
  );

  const lastJsbWorkLocation = () =>
    pipe(
      lastJsb,
      O.chain(j => j.workLocation), // Option<WorkLocation>
      O.map(wl => wl.description) //Option<Option<WorkLocation>>
    );

  const lastAdhocJsbAddress = () =>
    pipe(
      lastAdhocJsb,
      O.chain(j => j.workLocation),
      O.map(wl => wl.address)
    );
  const lastOperatingHq = () =>
    pipe(
      lastAdhocJsb,
      O.chain(j => j.workLocation),
      O.map(wl => wl.operatingHq)
    );
  const lastJsbAddress = () =>
    pipe(
      lastJsb,
      O.chain(j => j.workLocation),
      O.map(wl => wl.address)
    );
  // converting utc time to local time
  const localBriefingTime = pipe(
    jsb,
    O.chain(j => j.jsbMetadata),
    O.chain(dt =>
      O.fromNullable(dt.briefingDateTime.toLocal().toFormat("HH:mm"))
    ),
    O.alt(() => O.fromNullable(dateTime.toLocal().toFormat("HH:mm"))),
    O.getOrElse(() => ""),
    formDef.briefingTime.init
  );

  const createdAtDate = pipe(
    createdAt,
    O.map(dt => dt)
  );

  const operatingHq = pipe(
    jsb,
    O.chain(j => j.workLocation),
    O.chain(wl => wl.operatingHq),
    O.alt(lastOperatingHq),
    O.fold(
      () => "",
      opHQ => opHQ
    )
  );

  return {
    currentDate: dateTime,
    savedBriefingDate,
    briefingDate: pipe(
      savedBriefingDate,
      O.chain(dt => O.fromNullable(dt.toLocal().toISODate())),
      O.alt(() => O.fromNullable(dateTime.toLocal().toISODate())),
      O.getOrElse(() => ""),
      initFormField(validDateTimeCodecS.decode)
    ),
    briefingTime: localBriefingTime,
    workLocation: pipe(
      projectLocation,
      O.fold(
        () =>
          pipe(
            jsb,
            O.chain(j => j.workLocation),
            O.map(wl => wl.description),
            O.alt(lastAdhocJsbAddress),
            O.getOrElse(() => ""),
            address => Description(address, operatingHq)
          ),
        pl =>
          AddressAndLocation(
            pipe(
              jsb,
              O.chain(j => j.workLocation),
              O.map(wl => wl.address),
              O.alt(lastJsbAddress),
              O.alt(() => pl.address),
              O.getOrElse(() => "")
            ),
            pipe(
              jsb,
              O.chain(j => j.workLocation),
              O.map(wl => wl.description),
              O.alt(lastJsbWorkLocation),
              O.getOrElse(() => "")
            )
          )
      )
    ),
    latitude: pipe(
      jsb,
      O.chain(j => j.gpsCoordinates),
      O.chain(
        flow(
          A.head,
          O.map(c => c.latitude.toString())
        )
      ),
      O.getOrElse(() => ""),
      formDef.latitude.init
    ),
    longitude: pipe(
      jsb,
      O.chain(j => j.gpsCoordinates),
      O.chain(
        flow(
          A.head,
          O.map(c => c.longitude.toString())
        )
      ),
      O.getOrElse(() => ""),
      formDef.longitude.init
    ),
    woCoords: pipe(
      projectLocation,
      O.map(p => ({ latitude: p.latitude, longitude: p.longitude }))
    ),
    state: "Georgia",
    createdAt: pipe(
      createdAtDate,
      O.chain(dt => O.fromNullable(dt.toLocal()))
    ),
  };
}

export function makeSnapshot(model: Model): StepSnapshot {
  const workLocationRaw = (wl: WorkLocationFormField): StepSnapshot => {
    switch (wl.type) {
      case "Description":
        return {
          description: wl.description.raw,
          operatingHq: wl.operatingHq.raw,
        };
      case "AddressAndLocation":
        return { address: wl.address.raw, location: wl.location.raw };
    }
  };

  return {
    briefingDate: model.briefingDate.raw,
    briefingTime: model.briefingTime.raw,
    workLocation: workLocationRaw(model.workLocation),
    latitude: model.latitude.raw,
    longitude: model.longitude.raw,
  };
}

export function toSaveJsbInput(
  model: Model
): t.Validation<SaveJobSafetyBriefingInput> {
  return pipe(
    sequenceS(ApplyEither)({
      briefingDate: model.briefingDate.val,
      briefingTime: model.briefingTime.val,
      workLocation: workLocationFormFieldResult(model.state)(
        model.workLocation
      ),
      latitude: model.latitude.val,
      longitude: model.longitude.val,
    }),
    E.map(
      (res): SaveJobSafetyBriefingInput => ({
        jsbMetadata: {
          briefingDateTime: formatDateTime(res.briefingDate, res.briefingTime),
        },
        workLocation: res.workLocation,
        gpsCoordinates: pipe(
          O.Do,
          O.bind("latitude", () => res.latitude),
          O.bind("longitude", () => res.longitude),
          O.fold(() => [], A.of)
        ),
      })
    )
  );
}

export type Action =
  | {
      type: "BriefingDateChanged";
      value: string;
    }
  | {
      type: "BriefingTimeChanged";
      value: string;
    }
  | {
      type: "WorkLocationChanged";
      value: string;
    }
  | {
      type: "AddressChanged";
      value: string;
    }
  | {
      type: "DescriptionChanged";
      value: string;
    }
  | {
      type: "OperatingHQChanged";
      value: string;
    }
  | {
      type: "LatitudeChanged";
      value: string;
    }
  | {
      type: "LongitudeChanged";
      value: string;
    }
  | {
      type: "LocationAcquired";
      position: GeolocationPosition;
    };

const BriefingDateChanged = (value: string): Action => ({
  type: "BriefingDateChanged",
  value,
});

const BriefingTimeChanged = (value: string): Action => ({
  type: "BriefingTimeChanged",
  value,
});

const WorkLocationChanged = (value: string): Action => ({
  type: "WorkLocationChanged",
  value,
});

const AddressChanged = (value: string): Action => ({
  type: "AddressChanged",
  value,
});

const DescriptionChanged = (value: string): Action => ({
  type: "DescriptionChanged",
  value,
});

const OperatingHQChanged = (value: string): Action => ({
  type: "OperatingHQChanged",
  value,
});

const LatitudeChanged = (value: string): Action => ({
  type: "LatitudeChanged",
  value,
});

const LongitudeChanged = (value: string): Action => ({
  type: "LongitudeChanged",
  value,
});

const LocationAcquired = (position: GeolocationPosition): Action => ({
  type: "LocationAcquired",
  position,
});

export const update = (model: Model, action: Action): Model => {
  switch (action.type) {
    case "BriefingDateChanged": {
      const decodeBriefingDate = (raw: string) =>
        pipe(
          validDateTimeCodecS.decode(raw),
          E.chain(dt => E.right(dt))
        );

      return {
        ...model,
        briefingDate: updateFormField(decodeBriefingDate)(action.value),
      };
    }
    case "BriefingTimeChanged":
      return {
        ...model,
        briefingTime: formDef.briefingTime.update(action.value),
      };

    case "WorkLocationChanged":
      return model.workLocation.type === "AddressAndLocation"
        ? {
            ...model,
            workLocation: {
              ...model.workLocation,
              location: formDef.workLocation.update(action.value),
            },
          }
        : model;
    case "AddressChanged":
      return model.workLocation.type === "AddressAndLocation"
        ? {
            ...model,
            workLocation: {
              ...model.workLocation,
              address: formDef.address.update(action.value),
            },
          }
        : model;
    case "DescriptionChanged":
      return model.workLocation.type === "Description"
        ? {
            ...model,
            workLocation: {
              ...model.workLocation,
              description: formDef.description.update(action.value),
            },
          }
        : model;
    case "OperatingHQChanged":
      if (model.workLocation.type !== "Description") return model;
      return {
        ...model,
        workLocation: {
          ...model.workLocation,
          operatingHq: formDef.description.update(action.value),
        },
      };

    case "LatitudeChanged":
      return {
        ...model,
        latitude: formDef.latitude.update(action.value),
      };
    case "LongitudeChanged":
      return {
        ...model,
        longitude: formDef.longitude.update(action.value),
      };

    case "LocationAcquired":
      return {
        ...model,
        latitude: formDef.latitude.update(
          action.position.coords.latitude.toString()
        ),
        longitude: formDef.longitude.update(
          action.position.coords.longitude.toString()
        ),
      };
  }
};

// TODO: null should not be possible here because we use validated date and time.
// Figure out a way to make the type system understand this.
function formatDateTime(
  date: ValidDateTime,
  time: ValidDuration
): string | null {
  const jsDateConverter = DateTime.fromJSDate(date.toJSDate());
  const dateTimeAppender = jsDateConverter.startOf("day").plus(time);
  const utcFormattedDate = dateTimeAppender.toUTC();
  return utcFormattedDate.toISO();
}

export type Props = ChildProps<Model, Action> & {
  libraryRegions: Deferred<ApiResult<LibraryRegion[]>>;
  isReadOnly: boolean;
};

export function View(props: Props): JSX.Element {
  const { model, dispatch, isReadOnly } = props;

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

  const libraryRegionOptions = useMemo(() => {
    switch (props.libraryRegions.status) {
      case "Resolved":
        return pipe(
          props.libraryRegions.value,
          E.fold(
            () => [],
            flow(
              A.map(lr => ({
                label: lr.name,
                value: lr.name,
              }))
            )
          )
        );
      case "NotStarted":
      case "InProgress":
      case "Updating":
        return [];
    }
  }, [props.libraryRegions]);

  const workLocationInputs = () => {
    switch (model.workLocation.type) {
      case "Description":
        return (
          <>
            <TextArea
              required={true}
              rows={4}
              disabled={isReadOnly}
              field={model.workLocation.description}
              onChange={flow(DescriptionChanged, dispatch)}
              label="Please list included addresses and scope of work *"
            />
            <Select
              optionKey={identity}
              label="Operating HQ *"
              options={libraryRegionOptions}
              placeholder={libraryRegionsPlaceholder}
              selected={O.fromEither(model.workLocation.operatingHq.val)}
              onSelected={flow(
                O.fold(
                  () => "",
                  val => val
                ),
                OperatingHQChanged,
                dispatch
              )}
              disabled={
                isReadOnly || props.libraryRegions.status !== "Resolved"
              }
              renderLabel={(name: string) => (
                <div className="flex flex-1 flex-row justify-between items-center">
                  <span className="truncate max-w-md">{name}</span>
                </div>
              )}
              hasError={
                model.workLocation.operatingHq.dirty &&
                E.isLeft(model.workLocation.operatingHq.val)
              }
            />
            {model.workLocation.operatingHq.dirty &&
              E.isLeft(model.workLocation.operatingHq.val) && (
                <ErrorMessage field={model.workLocation.operatingHq} />
              )}
          </>
        );
      case "AddressAndLocation":
        return (
          <>
            <Input
              type="text"
              label="Address *"
              field={model.workLocation.address}
              disabled={isReadOnly}
              onChange={flow(AddressChanged, dispatch)}
            />
            <Input
              type="text"
              label="Work Location *"
              field={model.workLocation.location}
              disabled={isReadOnly}
              onChange={flow(WorkLocationChanged, dispatch)}
              placeholder="e.g. cross street, nearby landmark, or location on the property"
            />
          </>
        );
    }
  };

  // date limiter for calendar selection
  const dateRestricter = useMemo(() => {
    return O.fold(
      () => DateTime.now(),
      (d: DateTime) => d
    )(model.createdAt);
  }, []);

  const libraryRegionsPlaceholder = useMemo(() => {
    switch (props.libraryRegions.status) {
      case "Resolved":
        return "Select Operating HQ";

      case "NotStarted":
      case "InProgress":
      case "Updating":
        return "Loading Operating HQ";
    }
  }, [props.libraryRegions]);

  const localeDateFormat = getLocaleDateFormat();

  const onKeyDownHandler = (e: any) => {
    if (e.key === "e" || e.key === "E") {
      e.preventDefault();
    }
  };

  return (
    <StepLayout>
      <FieldGroup legend="General Information">
        <InputDateSelect
          icon="calendar"
          label="Briefing Date *"
          hintText="Please select a date between yesterday and two weeks in the future."
          hintStyle="block text-tiny md:text-sm text-neutral-shade-75 !leading-[0.2]"
          disabled={isReadOnly}
          closeIcon={false}
          selectedDate={
            model.briefingDate.raw
              ? DateTime.fromISO(model.briefingDate.raw).toJSDate()
              : null
          }
          minDate={dateRestricter.minus({ days: 1 }).toJSDate()}
          maxDate={dateRestricter.plus({ days: 14 }).toJSDate()}
          onDateChange={date =>
            dispatch(
              BriefingDateChanged(
                date ? DateTime.fromJSDate(date).toISODate() ?? "" : ""
              )
            )
          }
          dateFormat={localeDateFormat}
        />
        <Input
          type="time"
          label="Briefing Time *"
          disabled={isReadOnly}
          field={model.briefingTime}
          onChange={flow(BriefingTimeChanged, dispatch)}
        />
      </FieldGroup>
      <FieldGroup legend="GPS Coordinates">
        <div className="flex flex-col sm:flex-row gap-4 w-full">
          <div className="flex flex-1 flex-col gap-3 min-w-0">
            {O.isSome(model.woCoords) && (
              <Labeled label="WO Latitude">
                <span className="break-all">
                  {model.woCoords.value.latitude}
                </span>
              </Labeled>
            )}
            <Input
              type="number"
              label="Current Latitude"
              field={model.latitude}
              disabled={isReadOnly}
              onChange={flow(LatitudeChanged, dispatch)}
              onKeyDown={onKeyDownHandler}
            />
          </div>
          <div className="flex flex-1 flex-col gap-3 min-w-0">
            {O.isSome(model.woCoords) && (
              <Labeled label="WO Longitude">
                <span className="break-all">
                  {model.woCoords.value.longitude}
                </span>
              </Labeled>
            )}
            <Input
              type="number"
              label="Current Longitude"
              field={model.longitude}
              disabled={isReadOnly}
              onChange={flow(LongitudeChanged, dispatch)}
              onKeyDown={onKeyDownHandler}
            />
          </div>
        </div>
        {E.isRight(getPosition) && !isReadOnly ? (
          <div className="flex flex-col sm:flex-row gap-4">
            <ButtonRegular
              iconStart="target"
              onClick={getPosition.right}
              label="Use current location"
              className="text-brand-urbint-40 w-full sm:w-auto"
            />
          </div>
        ) : (
          <></>
        )}
      </FieldGroup>
      <FieldGroup legend="Work Location">{workLocationInputs()}</FieldGroup>
    </StepLayout>
  );
}
