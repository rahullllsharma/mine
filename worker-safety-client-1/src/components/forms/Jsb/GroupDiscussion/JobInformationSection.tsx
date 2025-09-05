import type { Option } from "fp-ts/lib/Option";
import type { GpsCoordinates, Jsb, ProjectLocation } from "@/api/codecs";
import type { Either } from "fp-ts/lib/Either";
import type { ValidDateTime } from "@/utils/validation";
import { BodyText } from "@urbint/silica";
import { pipe } from "fp-ts/lib/function";
import { sequenceS } from "fp-ts/lib/Apply";
import * as O from "fp-ts/lib/Option";
import * as A from "fp-ts/lib/Array";
import * as E from "fp-ts/lib/Either";
import { OptionalView } from "@/components/common/Optional";
import { getFormattedDate } from "@/utils/date/helper";
import { GroupDiscussionSection } from "../../Basic/GroupDiscussionSection";

export const init = (
  jsb: Jsb,
  projectLocation: Option<ProjectLocation>
): Either<string, JobInformationSectionData> =>
  sequenceS(E.Apply)({
    briefingDateTime: pipe(
      jsb.jsbMetadata,
      E.fromOption(() => "jsbMetadata is missing"),
      E.map(meta => meta.briefingDateTime)
    ),
    address: pipe(
      jsb.workLocation,
      E.fromOption(() => "workLocation is missing"),
      E.map(loc => loc.address)
    ),
    workLocationDescription: pipe(
      jsb.workLocation,
      E.fromOption(() => "workLocation is missing"),
      E.map(loc => loc.description)
    ),
    // woCoordinates is optional
    woCoordinates: E.right(
      pipe(
        projectLocation,
        O.map(loc => ({
          latitude: loc.latitude,
          longitude: loc.longitude,
        }))
      )
    ),
    // gpsCoordinates is optional
    gpsCoordinates: E.right(pipe(jsb.gpsCoordinates, O.chain(A.head))),
    operatingHq: pipe(
      jsb.workLocation,
      E.fromOption(() => "workLocation is missing"),
      E.map(loc => loc.operatingHq)
    ),
    isAdHocJsb: E.right(O.isNone(projectLocation)),
  });

export type JobInformationSectionData = {
  briefingDateTime: ValidDateTime;
  address: string;
  workLocationDescription: string;
  woCoordinates: Option<GpsCoordinates>;
  gpsCoordinates: Option<GpsCoordinates>;
  operatingHq: Option<string>;
  isAdHocJsb: boolean;
};

export type JobInformationSectionProps = JobInformationSectionData & {
  onClickEdit?: () => void;
};

export function View(props: JobInformationSectionProps): JSX.Element {
  const {
    onClickEdit,
    briefingDateTime,
    address,
    workLocationDescription,
    woCoordinates,
    gpsCoordinates,
    operatingHq,
    isAdHocJsb,
  } = props;
  return (
    <GroupDiscussionSection title="Job Information" onClickEdit={onClickEdit}>
      <div className="flex justify-between gap-2 mb-4">
        <div className="flex-1">
          <BodyText className="text-sm text-neutral-shade-100 font-semibold mb-2">
            Briefing Date
          </BodyText>
          <span className="text-base font-normal">
            {getFormattedDate(
              briefingDateTime.toISODate() ?? "",
              "long",
              "numeric",
              "numeric",
              "long"
            )}
          </span>
        </div>

        <div className="flex-1">
          <BodyText className="text-sm text-neutral-shade-100 font-semibold mb-2">
            Briefing Time
          </BodyText>
          <span className="text-base font-normal">
            {briefingDateTime.toLocal().toFormat("hh:mm a")}
          </span>
        </div>
      </div>

      <div className="flex justify-between gap-2 mb-4">
        <OptionalView
          value={address.length > 0 ? O.some(address) : O.none}
          render={addr => (
            <div className="flex-1">
              <BodyText className="text-sm text-neutral-shade-100 font-semibold mb-2">
                Address
              </BodyText>
              <span className="text-base font-normal">{addr}</span>
            </div>
          )}
        />

        <OptionalView
          value={
            workLocationDescription.length > 0
              ? O.some(workLocationDescription)
              : O.none
          }
          render={desc => (
            <div className="flex-1">
              <BodyText className="text-sm text-neutral-shade-100 font-semibold mb-2">
                Work Location
              </BodyText>
              <span className="text-base font-normal whitespace-pre-wrap">
                {desc}
              </span>
            </div>
          )}
        />

        {isAdHocJsb && (
          <OptionalView
            value={operatingHq}
            render={desc => (
              <div className="flex-1">
                <BodyText className="text-sm text-neutral-shade-100 font-semibold mb-2">
                  Operating HQ
                </BodyText>
                <span className="text-base font-normal whitespace-pre-wrap">
                  {desc}
                </span>
              </div>
            )}
          />
        )}
      </div>

      <div className="flex justify-between gap-2 mb-4">
        <OptionalView
          value={woCoordinates}
          render={({ latitude, longitude }) => (
            <div className="flex-1">
              <BodyText className="text-sm text-neutral-shade-100 font-semibold mb-2">
                WO Coordinates
              </BodyText>
              <span className="text-base font-normal">{`${latitude}, ${longitude}`}</span>
            </div>
          )}
        />
        <OptionalView
          value={gpsCoordinates}
          render={({ latitude, longitude }) => (
            <div className="flex-1">
              <BodyText className="text-sm text-neutral-shade-100 font-semibold mb-2">
                GPS Coordinates
              </BodyText>
              <span className="text-base font-normal">{`${latitude}, ${longitude}`}</span>
            </div>
          )}
        />
      </div>
    </GroupDiscussionSection>
  );
}
