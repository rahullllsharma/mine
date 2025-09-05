import type { Option } from "fp-ts/lib/Option";
import type { Jsb, MedicalFacility } from "@/api/codecs";
import type { Either } from "fp-ts/lib/Either";
import { BodyText, Icon } from "@urbint/silica";
import { flow, pipe } from "fp-ts/lib/function";
import * as A from "fp-ts/lib/Array";
import * as NEA from "fp-ts/lib/NonEmptyArray";
import * as O from "fp-ts/lib/Option";
import { sequenceS } from "fp-ts/lib/Apply";
import * as E from "fp-ts/lib/Either";
import { OptionalView } from "@/components/common/Optional";
import formatTextToPhone from "@/utils/formatTextToPhone";
import { GroupDiscussionSection } from "../../Basic/GroupDiscussionSection";

export type MedicalEmergencySectionData = {
  emergencyContactName: string;
  emergencyContactPhone: string;
  emergencyContactName2: string;
  emergencyContactPhone2: string;
  selectedMedicalFacility: Option<MedicalFacility>;
  selectedMedicalDevice: string;
};

export const init = (jsb: Jsb): Either<string, MedicalEmergencySectionData> => {
  const contact1 = pipe(
    jsb.emergencyContacts,
    E.fromOption(() => "emergencyContacts is missing"),
    E.chain(
      flow(
        A.head,
        E.fromOption(() => "emergencyContacts is empty")
      )
    )
  );

  const contact2 = pipe(
    jsb.emergencyContacts,
    E.fromOption(() => "emergencyContacts is missing"),
    E.chain(
      flow(
        A.lookup(1),
        E.fromOption(() => "second emergency contact is missing")
      )
    )
  );

  const otherMedicalFacility: Option<MedicalFacility> = pipe(
    jsb.customNearestMedicalFacility,
    O.map(({ address }) => ({
      description: address || "",
      distanceFromJob: O.none,
      phoneNumber: O.none,
      address: O.none,
      city: O.none,
      state: O.none,
      zip: O.none,
    }))
  );

  return sequenceS(E.Apply)({
    emergencyContactName: pipe(
      contact1,
      E.map(contact => contact.name)
    ),
    emergencyContactPhone: pipe(
      contact1,
      E.map(contact => contact.phoneNumber)
    ),
    emergencyContactName2: pipe(
      contact2,
      E.map(contact => contact.name)
    ),
    emergencyContactPhone2: pipe(
      contact2,
      E.map(contact => contact.phoneNumber)
    ),
    selectedMedicalFacility: pipe(
      jsb.nearestMedicalFacility,
      O.alt(() => otherMedicalFacility),
      E.right
    ),
    selectedMedicalDevice: pipe(
      jsb.aedInformation,
      E.fromOption(() => "aedInformation is missing"),
      E.map(aed => aed.location)
    ),
  });
};

export type MedicalEmergencySectionProps = MedicalEmergencySectionData & {
  onClickEdit?: () => void;
};

const emergency911 = "911";
const atlantaDCC = "6786237000";
const maconDCC = "4787853700";
const PSOC = "4707851000";

export function View(props: MedicalEmergencySectionProps): JSX.Element {
  const {
    onClickEdit,
    emergencyContactName,
    emergencyContactPhone,
    emergencyContactName2,
    emergencyContactPhone2,
    selectedMedicalFacility,
    selectedMedicalDevice,
  } = props;
  return (
    <GroupDiscussionSection
      title="Medical & Emergency Information"
      onClickEdit={onClickEdit}
    >
      <div className="flex gap-4 flex-col">
        <div className="bg-white p-4">
          <BodyText className="text-sm text-neutral-shade-100 font-semibold mb-2">
            Emergency Contact 1
          </BodyText>
          <div className="flex justify-between">
            <span className="text-base font-normal text-neutral-shade-100">
              {emergencyContactName}
            </span>
            <div className="flex text-brand-urbint-50 items-center">
              <a href={`tel:${emergencyContactPhone}`}>
                <Icon name="phone" className="mr-1" />
                {formatTextToPhone(emergencyContactPhone)}
              </a>
            </div>
          </div>
        </div>

        <div className="bg-white p-4">
          <BodyText className="text-sm text-neutral-shade-100 font-semibold mb-2">
            Emergency Contact 2
          </BodyText>

          <div className="flex justify-between">
            <span className="text-base font-normal text-neutral-shade-100">
              {emergencyContactName2}
            </span>
            <div className="flex text-brand-urbint-50 items-center">
              <a href={`tel:${emergencyContactPhone2}`}>
                <Icon name="phone" className="mr-1" />
                {formatTextToPhone(emergencyContactPhone2)}
              </a>
            </div>
          </div>
        </div>

        <div className="bg-white p-4 flex flex-row justify-center text-center gap-12">
          <div>
            <BodyText className="text-sm text-neutral-shade-100 font-semibold mb-2">
              Emergency:
            </BodyText>
            <div className="flex text-brand-urbint-50 justify-center">
              <a href={`tel:${emergency911}`}>
                <Icon name="phone" className="mr-1" />
                {formatTextToPhone(emergency911)}
              </a>
            </div>
          </div>

          <div>
            <BodyText className="text-sm text-neutral-shade-100 font-semibold mb-2">
              Atlanta DCC:
            </BodyText>
            <div className="flex text-brand-urbint-50 justify-center">
              <a href={`tel:${atlantaDCC}`}>
                <Icon name="phone" className="mr-1" />
                {formatTextToPhone(atlantaDCC)}
              </a>
            </div>
          </div>
        </div>
        <div className="bg-white p-4 flex flex-row justify-center text-center gap-10">
          <div>
            <BodyText className="text-sm text-neutral-shade-100 font-semibold mb-2">
              Macon DCC:
            </BodyText>
            <div className="flex text-brand-urbint-50 justify-center">
              <a href={`tel:${maconDCC}`}>
                <Icon name="phone" className="mr-1" />
                {formatTextToPhone(maconDCC)}
              </a>
            </div>
          </div>

          <div>
            <BodyText className="text-sm text-neutral-shade-100 font-semibold mb-2">
              PSOC / Corporate Security:
            </BodyText>
            <div className="flex text-brand-urbint-50 justify-center">
              <a href={`tel:${PSOC}`}>
                <Icon name="phone" className="mr-1" />
                {formatTextToPhone(PSOC)}
              </a>
            </div>
          </div>
        </div>

        <OptionalView
          value={selectedMedicalFacility}
          render={facility => (
            <div className="bg-white p-4">
              <BodyText className="text-sm text-neutral-shade-100 font-semibold mb-2">
                Nearest Hospital / Emergency Response
              </BodyText>

              <MedicalFacility1 facility={facility} />
            </div>
          )}
        />
        <div className="bg-white p-4">
          <BodyText className="text-sm text-neutral-shade-100 font-semibold mb-2">
            AED Location
          </BodyText>
          <span className="text-base font-normal text-neutral-shade-100">
            {selectedMedicalDevice}
          </span>
        </div>
      </div>
    </GroupDiscussionSection>
  );
}

function MedicalFacility1(props: { facility: MedicalFacility }) {
  return (
    <div className="flex flex-row justify-between items-center">
      <div className="flex flex-col">
        <span className="text-base font-normal text-neutral-shade-100 mb-2">
          {props.facility.description}
        </span>
        <OptionalView
          value={props.facility.address}
          render={address => (
            <span className="text-base font-normal text-neutral-shade-100">
              {address}
            </span>
          )}
        />
        <OptionalView
          value={pipe(
            [
              props.facility.city,
              props.facility.state,
              pipe(
                props.facility.zip,
                O.map(zip => zip.toString())
              ),
            ],
            A.compact,
            NEA.fromArray,
            O.map(items => items.join(", "))
          )}
          render={fullAddress => (
            <span className="text-base font-normal text-neutral-shade-100">
              {fullAddress}
            </span>
          )}
        />
      </div>
      <OptionalView
        value={props.facility.phoneNumber}
        render={phone => (
          <span className="text-base font-normal text-brand-urbint-50">
            <a href={`tel:${phone}`}>
              <Icon name="phone" className="mr-1" />
              {phone}
            </a>
          </span>
        )}
      />
    </div>
  );
}
