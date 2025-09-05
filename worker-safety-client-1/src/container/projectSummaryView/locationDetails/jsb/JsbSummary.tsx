import type { GpsCoordinates } from "@/api/codecs";
import type { JsbInfo } from "@/types/project/JsbInfo";
import type { IconName } from "@urbint/silica";
import type { Option } from "fp-ts/lib/Option";
import type { Validation } from "io-ts";
import type { ReactElement, ReactNode } from "react";
import type { MenuItemProps } from "@/components/shared/dropdown/Dropdown";
import { Icon } from "@urbint/silica";
import cx from "classnames";
import * as A from "fp-ts/lib/Array";
import * as E from "fp-ts/lib/Either";
import * as O from "fp-ts/lib/Option";
import { pipe } from "fp-ts/lib/function";
import { useEffect, useMemo, useState } from "react";
import router from "next/router";
import { FormStatus } from "@/api/generated/types";
import { OptionalView } from "@/components/common/Optional";
import TaskCard from "@/components/layout/taskCard/TaskCard";
import ButtonIcon from "@/components/shared/button/icon/ButtonIcon";
import StatusBadge from "@/components/statusBadge/StatusBadge";
import { getFormattedDate, getFormattedShortTime } from "@/utils/date/helper";
import formatTextToPhone from "@/utils/formatTextToPhone";
import Dropdown from "@/components/shared/dropdown/Dropdown";

export type JsbSummaryProps = {
  jsbInfo: Validation<JsbInfo>;
  gpsCoords: Option<GpsCoordinates>;
  edit: () => void;
  location?: string;
};

export default function JsbSummary({
  jsbInfo,
  gpsCoords,
  edit,
  location,
}: JsbSummaryProps): JSX.Element {
  useEffect(() => {
    if (E.isLeft(jsbInfo)) {
      console.error(jsbInfo.left);
    }
  }, [jsbInfo]);
  return E.isRight(jsbInfo) ? (
    <JsbSummaryView
      jsbInfo={jsbInfo.right}
      gpsCoords={gpsCoords}
      edit={edit}
      location={location}
    />
  ) : (
    <div>Invalid or Missng JSB Information</div>
  );
}

const lookupEmergencyContact = (jsbInfo: JsbInfo, index: number) =>
  pipe(
    jsbInfo.contents.emergencyContacts,
    O.chain(A.lookup(index)),
    O.map(({ name, phoneNumber }) => (
      <>
        <InfoItem label={`Emergency contact ${index + 1}`}>
          <InfoItemValue value={name} />
          <div className="flex text-brand-urbint-50 items-center">
            <a
              href={`tel:${formatTextToPhone(phoneNumber)}`}
              className="text-base"
            >
              <Icon name="phone" className="mr-1" />
              <InfoItemValue value={formatTextToPhone(phoneNumber)} />
            </a>
          </div>
        </InfoItem>
      </>
    ))
  );

const lookupWorkLocation = (jsbInfo: JsbInfo) =>
  pipe(
    jsbInfo.contents.workLocation,
    O.map(wl => (
      <>
        <InfoItem label="Work Location">
          <InfoItemValue value={wl.description} />
        </InfoItem>
      </>
    ))
  );

const lookupAedLocation = (jsbInfo: JsbInfo) =>
  pipe(
    jsbInfo.contents.aedInformation,
    O.map(aed => (
      <>
        <InfoItem label="AED Location">
          <InfoItemValue value={aed.location} />
        </InfoItem>
      </>
    ))
  );

const lookupGpsCoords = (jsbInfo: JsbInfo, gpsCoords: Option<GpsCoordinates>) =>
  pipe(
    jsbInfo.contents.gpsCoordinates,
    O.chain(A.head),
    O.alt(() => gpsCoords),
    O.map(({ latitude, longitude }) => (
      <>
        <InfoItem label="GPS Coordinates">
          <InfoItemValue value={`${latitude}, ${longitude}`} />
        </InfoItem>
      </>
    ))
  );

const lookupNearestMedicalFacility = (jsbInfo: JsbInfo) => {
  return pipe(
    jsbInfo.contents.nearestMedicalFacility,
    O.map(mfl =>
      pipe(
        mfl.address,
        O.map(mfla => (
          <>
            <InfoItem label="Nearest Medical Facility">
              <InfoItemValue value={mfla} />
            </InfoItem>
          </>
        ))
      )
    ),
    O.getOrElse(() =>
      pipe(
        jsbInfo.contents.customNearestMedicalFacility,
        O.map(nmf => (
          <>
            <InfoItem label="Nearest Medical Facility">
              <InfoItemValue value={nmf.address} />
            </InfoItem>
          </>
        ))
      )
    )
  );
};

type JsbSummaryViewProps = {
  jsbInfo: JsbInfo;
  gpsCoords: Option<GpsCoordinates>;
  edit: () => void;
  location?: string;
};

function JsbSummaryView({
  jsbInfo,
  gpsCoords,
  edit,
  location,
}: JsbSummaryViewProps): JSX.Element {
  // if any additional logic is introduced, refactor into a reducer
  const [isOpen, setIsOpen] = useState(false);

  const toggle: Option<() => void> = useMemo(
    () =>
      jsbInfo.status === FormStatus.Complete
        ? O.some(() => setIsOpen(!isOpen))
        : O.none,
    [setIsOpen, isOpen, jsbInfo.status]
  );

  return (
    <TaskCard
      className={cx({
        ["border-brand-gray-60"]: jsbInfo.status === FormStatus.InProgress,
        ["border-brand-urbint-40"]: jsbInfo.status === FormStatus.Complete,
      })}
      taskHeader={
        <JsbHeader
          jsbInfo={jsbInfo}
          isOpen={jsbInfo.status === FormStatus.Complete && isOpen}
          toggle={toggle}
          edit={edit}
          location={location}
        />
      }
      isOpen={isOpen}
    >
      <div className="flex flex-col gap-4">
        <div className="grid grid-cols-2 gap-4">
          {A.compact([
            lookupEmergencyContact(jsbInfo, 0),
            lookupEmergencyContact(jsbInfo, 1),
            lookupWorkLocation(jsbInfo),
            lookupAedLocation(jsbInfo),
            lookupGpsCoords(jsbInfo, gpsCoords),
            lookupNearestMedicalFacility(jsbInfo),
          ])}
        </div>

        <OptionalView
          value={jsbInfo.contents.energySourceControl}
          render={({ ewp }) => (
            <>
              {ewp.map(({ id, equipmentInformation }) => (
                <div className="border border-brand-gray-40 p-4" key={id}>
                  <InfoItem label="EWP #">
                    <InfoItemValue value={id} />
                  </InfoItem>
                  <div className="grid grid-cols-2 gap-4 mt-4">
                    {equipmentInformation.map(({ circuitBreaker }) => (
                      <div
                        className="bg-brand-gray-10 p-4"
                        key={circuitBreaker}
                      >
                        <InfoItem label="Circuit Breaker #">
                          <InfoItemValue value={circuitBreaker} />
                        </InfoItem>
                      </div>
                    ))}
                  </div>
                </div>
              ))}
            </>
          )}
        />

        <OptionalView
          value={jsbInfo.contents.nearestMedicalFacility}
          render={({ description, phoneNumber, address, city, state, zip }) => (
            <div className="border border-brand-gray-40 p-4">
              <InfoItem label="Nearest hospital / Emergency response">
                <div className="flex justify-between">
                  <InfoItemValue
                    value={
                      <p>
                        {description}
                        <OptionalView
                          value={address}
                          render={addr => (
                            <>
                              <br />
                              {addr}
                            </>
                          )}
                        />
                        <br />
                        <OptionalView value={city} render={c => <>{c}, </>} />
                        <OptionalView
                          value={state}
                          render={s => <>{s.toUpperCase()} </>}
                        />
                        <OptionalView value={zip} render={z => <>{z} </>} />
                      </p>
                    }
                  />
                  <OptionalView
                    value={phoneNumber}
                    render={pNo => (
                      <div className="flex text-brand-urbint-50 items-center">
                        <a href={`tel:${pNo}`} className="text-base">
                          <Icon name="phone" className="mr-1" />
                          <InfoItemValue value={pNo} />
                        </a>
                      </div>
                    )}
                  />
                </div>
              </InfoItem>
            </div>
          )}
        />
      </div>
    </TaskCard>
  );
}

type InfoItemProps = {
  label: string;
  children: ReactNode;
};

function InfoItem({ label, children }: InfoItemProps): JSX.Element {
  return (
    <div className="flex flex-col gap-2">
      <label className="text-sm text-neutral-shade-100 font-semibold">
        {label}
      </label>
      {children}
    </div>
  );
}

function InfoItemValue({
  value,
}: {
  value: number | string | ReactElement;
}): JSX.Element {
  return <span className="text-base font-normal">{value}</span>;
}

function JsbStatus({ status }: { status: FormStatus }): JSX.Element {
  return <StatusBadge status={status} />;
}

type JsbHeaderProps = {
  jsbInfo: JsbInfo;
  isOpen: boolean;
  toggle: Option<() => void>;
  edit: () => void;
  location?: string;
};
function JsbHeader({
  jsbInfo,
  isOpen,
  toggle,
  edit,
  location,
}: JsbHeaderProps): JSX.Element {
  const iconName: IconName = isOpen ? "chevron_big_down" : "chevron_big_right";

  const getSubTitle = function (): Option<string> {
    if (jsbInfo.status === FormStatus.Complete) {
      if (O.isSome(jsbInfo.completedAt) && O.isSome(jsbInfo.completedBy)) {
        return O.some(
          `Completed on ${getFormattedDate(
            jsbInfo.completedAt.value.toISODate() ?? "",
            "long"
          )} at ${getFormattedShortTime(
            jsbInfo.completedAt.value.toISO() ?? ""
          )} by ${jsbInfo.completedBy.value.name}`
        );
      } else {
        return O.none;
      }
    } else {
      if (O.isSome(jsbInfo.createdAt) && O.isSome(jsbInfo.createdBy)) {
        return O.some(
          `Created on ${getFormattedDate(
            jsbInfo.createdAt.value.toISODate() ?? "",
            "long"
          )} at ${getFormattedShortTime(
            jsbInfo.createdAt.value.toISO() ?? ""
          )} by ${jsbInfo.createdBy.value.name}`
        );
      } else {
        return O.none;
      }
    }
  };

  const actionsMenuItems: MenuItemProps[] = [
    {
      label: "Edit",
      icon: "edit" as IconName,
      onClick: edit,
    },

    ...(jsbInfo.status === "COMPLETE"
      ? [
          {
            label: "Download PDF",
            icon: "download" as IconName,
            onClick: () => {
              router.push(
                `/jsb-share/${jsbInfo.id}?locationId=${location}&printPage=true`
              );
            },
          },
        ]
      : []),
  ];

  return (
    <div className="flex flex-row flex-1 justify-between items-center p-3">
      <div className="text-left text-base text-neutral-shade-100 font-bold flex flex-auto m-0 items-center gap-3 w-full md:flex-initial md:gap-4 md:w-auto md:ml-3 md:mr-4">
        <OptionalView
          value={toggle}
          render={t => <Icon name={iconName} className="text-xl" onClick={t} />}
        />
        <div className="flex flex-col gap-2">
          <div className="flex flex-row gap-2">
            {pipe(
              jsbInfo.name,
              O.getOrElse(() => "Job Safety Briefing")
            )}
            <JsbStatus status={jsbInfo.status} />
          </div>
          <OptionalView
            value={getSubTitle()}
            render={s => (
              <span className="text-tiny font-medium text-neutral-shade-58">
                {s}
              </span>
            )}
          />
        </div>
      </div>

      <Dropdown menuItems={[actionsMenuItems]}>
        <ButtonIcon iconName="hamburger" />
      </Dropdown>
    </div>
  );
}
