import type { ChildProps } from "@/utils/reducerWithEffect";
import type { CrewMember, Ebo, PersonnelId } from "@/api/codecs";
import type { Option } from "fp-ts/Option";
import type { StepSnapshot } from "../Utils";
import { useEffect, useMemo } from "react";
import { Eq as EqString } from "fp-ts/string";
import * as A from "fp-ts/lib/Array";
import * as E from "fp-ts/lib/Either";
import * as O from "fp-ts/lib/Option";
import * as Eq from "fp-ts/lib/Eq";
import * as string from "fp-ts/lib/string";
import { constNull, flow, identity, pipe } from "fp-ts/lib/function";
import { match as matchBoolean } from "fp-ts/boolean";
import { SectionHeading } from "@urbint/silica";
import { useAuthStore } from "@/store/auth/useAuthStore.store";
import StepLayout from "@/components/forms/StepLayout";
import { MultiSelect } from "../Basic/MultiSelect";

export const NotAvailable = {
  label: "N/A",
  value: { id: O.none, name: "not_available" },
};

const roleNames = {
  observer: "observer",
  crewMember: "crew member",
  crewLeader: "crew leader",
};

type Personnel = {
  id: Option<PersonnelId | string>;
  name: string;
};

const eqPersonnelName = Eq.contramap((name: string) => name)(EqString);

const eqPersonnelByName = Eq.contramap(
  (personnel: Personnel) => personnel.name
)(eqPersonnelName);

export const formElementIds = {
  crewMembers: "crewMembers",
};

export const HAS_ERROR_ON_OTHER_FORM_SECTIONS =
  "HAS_ERROR_ON_OTHER_FORM_SECTIONS";

const sectionErrorTexts = {
  HAS_ERROR_ON_OTHER_FORM_SECTIONS:
    "Please complete other form sections before completing the Energy Based Observation",
};

export type Model = {
  observer: Personnel;
  crewMembers: Option<Personnel[]>;
  sectionErrors: string[];
};

export function init(ebo: Option<Ebo>): Model {
  const eboContents = pipe(
    ebo,
    O.chain(e => e.contents.personnel)
  );

  const lookupCrewMemberPersonnel: Option<Personnel[]> = pipe(
    eboContents,
    O.map(
      A.filter(
        personnel =>
          EqString.equals(personnel.role, roleNames.crewMember) ||
          EqString.equals(personnel.role, roleNames.crewLeader)
      )
    ),
    O.map(A.map(p => ({ id: p.id, name: p.name })))
  );

  return {
    crewMembers: lookupCrewMemberPersonnel,
    observer: pipe(
      ebo,
      O.map(e => ({ id: O.of(e.createdBy.id), name: e.createdBy.name })),
      O.getOrElse(() => ({ id: O.of("not_available"), name: "" }))
    ),
    sectionErrors: [],
  };
}

export const makeSnapshot = (model: Model): StepSnapshot => {
  return {
    observer: {
      ...model.observer,
      id: pipe(model.observer.id, O.getOrElseW(constNull)),
    },
    crewMembers: pipe(
      model.crewMembers,
      O.map(A.map(cm => ({ ...cm, id: pipe(cm.id, O.getOrElseW(constNull)) }))),
      O.getOrElseW(constNull)
    ),
  };
};

export const toSaveEboInput = (model: Model) => {
  const getObserver = pipe(model.observer, obs => ({
    id: pipe(obs.id, O.getOrElseW(constNull)),
    name: obs.name,
    role: roleNames.observer,
  }));

  const getCrewMembers = pipe(
    model.crewMembers,
    O.map(
      A.map(cm => ({
        id: pipe(cm.id, O.getOrElseW(constNull)),
        name: cm.name,
        role: roleNames.crewMember,
      }))
    )
  );

  return pipe(
    getCrewMembers,
    O.map(A.append(getObserver)),
    O.getOrElse(() => [getObserver]),
    data => ({ personnel: data }),
    E.of
  );
};

export type Action =
  | { type: "ObserverNameChanged"; value: Personnel }
  | { type: "CrewMemberChanged"; value: Personnel }
  | { type: "CrewMemberRemoved"; value: Personnel }
  | { type: "SetSectionErrors"; value: string[] };

export const ObserverNameChanged = (value: Personnel): Action => ({
  type: "ObserverNameChanged",
  value,
});

export const CrewMemberChanged = (value: Personnel): Action => ({
  type: "CrewMemberChanged",
  value,
});

export const CrewMemberRemoved = (value: Personnel): Action => ({
  type: "CrewMemberRemoved",
  value,
});

export const SetSectionErrors = (value: string[]): Action => ({
  type: "SetSectionErrors",
  value,
});

export const update = (model: Model, action: Action): Model => {
  switch (action.type) {
    case "ObserverNameChanged":
      return { ...model, observer: action.value };
    case "CrewMemberChanged": {
      return pipe(
        action.value,
        v => v.name === NotAvailable.value.name,
        matchBoolean(
          () => {
            return {
              ...model,
              crewMembers: pipe(
                model.crewMembers,
                O.map(cms =>
                  pipe(
                    cms,
                    A.filter(cm => cm.name !== NotAvailable.value.name),
                    fcm => [...fcm, action.value]
                  )
                ),
                O.getOrElse(() => [action.value]),
                O.of
              ),
            };
          },
          () => {
            return { ...model, crewMembers: O.of([NotAvailable.value]) };
          }
        )
      );
    }
    case "CrewMemberRemoved": {
      return {
        ...model,
        crewMembers: pipe(
          model.crewMembers,
          O.map(A.filter(cl => cl.name !== action.value.name))
        ),
      };
    }
    case "SetSectionErrors": {
      return {
        ...model,
        sectionErrors: action.value,
      };
    }
  }
};

export type Props = ChildProps<Model, Action> & {
  crewLeaders: CrewMember[];
  isReadOnly: boolean;
};

export function View(props: Props): JSX.Element {
  const auth = useAuthStore();
  const { model, crewLeaders, dispatch, isReadOnly } = props;

  useEffect(() => {
    pipe(
      model.observer.name,
      O.fromPredicate(string.isEmpty),
      O.map(() => pipe({ id: O.of(auth.me.id), name: auth.me.name })),
      O.getOrElse(() => model.observer),
      flow(ObserverNameChanged, dispatch)
    );
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [auth]);

  const crewMemberOptions = useMemo(
    () =>
      pipe(
        crewLeaders,
        A.map(cl => ({
          label: cl.name,
          value: { id: O.of(cl.id), name: cl.name },
        })),
        cls => [NotAvailable, ...cls]
      ),
    [crewLeaders]
  );

  return (
    <StepLayout>
      <div className="p-4 md:p-0 flex flex-col gap-4">
        {pipe(
          model.sectionErrors,
          A.elem(EqString)(HAS_ERROR_ON_OTHER_FORM_SECTIONS)
        ) && (
          <div className="font-semibold text-system-error-40 text-sm mt-4">
            {sectionErrorTexts[HAS_ERROR_ON_OTHER_FORM_SECTIONS]}
          </div>
        )}
        <SectionHeading className="text-xl font-semibold">
          Personnel
        </SectionHeading>
        <div className="flex flex-col gap-4">
          <MultiSelect
            id={formElementIds.crewMembers}
            typeahead
            placeholder="Select a Crew Member name"
            labelClassName="block text-tiny md:text-sm text-neutral-shade-75 font-semibold mb-2 leading-normal"
            label="Crew Members *"
            options={crewMemberOptions}
            valueEq={eqPersonnelByName}
            selected={
              O.isSome(model.crewMembers) ? model.crewMembers.value : []
            }
            onSelected={flow(CrewMemberChanged, dispatch)}
            onRemoved={flow(CrewMemberRemoved, dispatch)}
            renderLabel={identity}
            optionKey={v => v.name}
            disabled={isReadOnly}
            hasError={pipe(
              model.sectionErrors,
              A.elem(EqString)(formElementIds.crewMembers)
            )}
          />
          <div className="flex flex-col gap-2">
            <label className="block text-tiny md:text-sm text-neutral-shade-75 font-semibold leading-normal">
              Observer Name
            </label>
            <span className="text-base font-normal text-neutral-shade-100">
              {model.observer.name}
            </span>
          </div>
        </div>
      </div>
    </StepLayout>
  );
}
