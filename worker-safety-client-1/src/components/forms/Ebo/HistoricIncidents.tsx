import type { ChildProps } from "@/utils/reducerWithEffect";
import type {
  Ebo,
  Incident,
  IncidentId,
  LibraryTask,
  LibraryTaskId,
} from "@/api/codecs";
import type { StepSnapshot } from "../Utils";
import type { TaskHistoricalIncidents } from "@/components/forms/Ebo/Wizard";
import type { SelectedDuplicateActivities } from "./HighEnergyTasks";
import type { Deferred } from "@/utils/deferred";
import type { ApiResult } from "@/api/api";
import { SectionHeading } from "@urbint/silica";
import orderBy from "lodash/orderBy";
import slice from "lodash/slice";
import { flow, pipe } from "fp-ts/lib/function";
import * as EQ from "fp-ts/Eq";
import { elem } from "fp-ts/Set";
import * as A from "fp-ts/lib/Array";
import * as E from "fp-ts/lib/Either";
import * as M from "fp-ts/lib/Map";
import * as O from "fp-ts/lib/Option";
import * as S from "fp-ts/lib/Set";
import * as Tup from "fp-ts/lib/Tuple";
import { Ord as OrdString } from "fp-ts/lib/string";
import { Ord as OrdNumber } from "fp-ts/lib/number";
import {
  ordIncidentTaskId,
  ordLibraryTaskId,
  eqLibraryTaskId,
} from "@/api/codecs";
import StepLayout from "@/components/forms/StepLayout";
import EboIncidentCard from "@/components/incidentCard/EboIncidentCard";
import { isResolved } from "@/utils/deferred";
import { messages } from "@/locales/messages";
import { TaskCard } from "../Basic/TaskCard";
import { eqHistoricalIncidentId } from "./Summary/historicIncidentsSummary";

export type Model = {
  selectedIncidentIds: Set<IncidentId>;
};

export function init(ebo: O.Option<Ebo>): Model {
  const eboContents = pipe(
    ebo,
    O.map(e => e.contents)
  );

  return {
    selectedIncidentIds: pipe(
      eboContents,
      O.chain(h => h.historicIncidents),
      O.fold(
        () => new Set<IncidentId>(),
        a => new Set<IncidentId>(a)
      )
    ),
  };
}

export const makeSnapshot = (model: Model): StepSnapshot => {
  return {
    selectedIncidentIds: pipe(model.selectedIncidentIds, S.toArray(OrdString)),
  };
};

export const generateSelectedTaskIdsFromSelectedDuplicateActivities = (
  selectedActivities: SelectedDuplicateActivities
): Set<LibraryTaskId> =>
  pipe(
    selectedActivities,
    M.toArray(OrdString),
    A.map(Tup.snd),
    A.map(M.toArray(OrdNumber)),
    A.chain(A.map(Tup.snd)),
    A.map(a => a.taskIds),
    A.chain(S.toArray(ordLibraryTaskId)),
    S.fromArray(eqLibraryTaskId)
  );

export const filterSelectedHistoricalIncidentsBasedOnSelectedActivities =
  (selectedActivities: SelectedDuplicateActivities) =>
  (selectedTaskIncidents: Deferred<ApiResult<TaskHistoricalIncidents[]>>) =>
  (model: Model): Model => {
    if (
      isResolved(selectedTaskIncidents) &&
      E.isRight(selectedTaskIncidents.value)
    ) {
      const allowedSelectedIncidentIds = pipe(
        selectedTaskIncidents.value.right,
        A.filter(taskIncidents =>
          pipe(
            selectedActivities,
            generateSelectedTaskIdsFromSelectedDuplicateActivities,
            S.elem(eqLibraryTaskId)(taskIncidents.taskId)
          )
        ),
        A.chain(a => a.result),
        A.map(a => a.id),
        S.fromArray(ordIncidentTaskId)
      );

      return {
        ...model,
        selectedIncidentIds: pipe(
          model.selectedIncidentIds,
          S.toArray(ordIncidentTaskId),
          A.filter(incidenTaskId =>
            pipe(
              allowedSelectedIncidentIds,
              S.elem(eqHistoricalIncidentId)(incidenTaskId)
            )
          ),
          S.fromArray(ordIncidentTaskId)
        ),
      };
    } else {
      return { ...model };
    }
  };

export const toSaveEboInput = (model: Model) => {
  return E.of({
    historicIncidents: pipe(
      model.selectedIncidentIds,
      S.toArray(ordIncidentTaskId)
    ),
  });
};

export type Action = {
  type: "IncidentsSelected";
  value: IncidentId;
};

export const IncidentsSelected = (value: IncidentId): Action => ({
  type: "IncidentsSelected",
  value,
});

export const update = (model: Model, action: Action): Model => {
  switch (action.type) {
    case "IncidentsSelected": {
      const selectedIncidentIds = new Set(model.selectedIncidentIds);
      if (elem(EQ.eqStrict)(action.value, selectedIncidentIds)) {
        selectedIncidentIds.delete(action.value);
      } else {
        selectedIncidentIds.add(action.value);
      }
      return { ...model, selectedIncidentIds };
    }
  }
};

export type Props = ChildProps<Model, Action> & {
  tasks: LibraryTask[];
  selectedTaskIds: Set<LibraryTaskId>;
  selectedTaskIncidents: TaskHistoricalIncidents[];
  isReadOnly: boolean;
  originalTaskNames: Map<LibraryTaskId, string>;
};

type IncidentsProps = {
  selectedIncidents: Set<IncidentId>;
  onSelect: (id: IncidentId) => void;
  incidents: Incident[];
  isReadOnly: boolean;
};

export function Incidents({
  selectedIncidents,
  onSelect,
  incidents,
  isReadOnly,
}: IncidentsProps): JSX.Element {
  const filteredIncidents: Incident[] = pipe(
    incidents,
    (i: Incident[]) => orderBy(i, ["incidentDate"], ["desc"]),
    (i: Incident[]) => slice(i, 0, 5)
  );

  if (pipe(filteredIncidents, A.isEmpty)) {
    return (
      <div className="flex flex-col justify-center items-center pt-4">
        No historical incidents related to this task were found.
      </div>
    );
  }

  return (
    <>
      {filteredIncidents.map(incident => (
        <EboIncidentCard
          incident={incident}
          selected={elem(EQ.eqStrict)(incident.id, selectedIncidents)}
          onSelect={onSelect}
          key={incident.id}
          isReadOnly={isReadOnly}
        />
      ))}
    </>
  );
}

export function View(props: Props): JSX.Element {
  const selectedTasks = pipe(
    props.selectedTaskIds,
    S.toArray(ordLibraryTaskId),
    A.filterMap(taskId => {
      const originalTaskName = props.originalTaskNames.get(taskId);
      if (originalTaskName) {
        return O.some({
          id: taskId,
          name: originalTaskName,
          riskLevel: "LOW" as any,
          workTypes: O.none,
          hazards: [],
          activitiesGroups: O.none,
        });
      }
      return pipe(
        props.tasks,
        A.findFirst(task => task.id === taskId)
      );
    })
  );

  return (
    <StepLayout>
      <div className="p-4 md:p-0 flex flex-col gap-4">
        <SectionHeading className="text-xl font-semibold">
          {messages.EboHistoricalIncidentsSectionTitle}
        </SectionHeading>
        <p>{messages.EboHistoricalIncidentsSectionSubTitle}</p>
        <div className="flex flex-col gap-2">
          {selectedTasks.map(task => (
            <TaskCard
              key={task.id}
              title={task.name}
              risk={task.riskLevel}
              showRiskInformation={false}
              showRiskText={false}
              withLeftBorder={false}
              isExpanded={true}
            >
              <Incidents
                onSelect={flow(IncidentsSelected, props.dispatch)}
                selectedIncidents={props.model.selectedIncidentIds}
                incidents={pipe(
                  props.selectedTaskIncidents,
                  A.findFirst(r => EQ.eqStrict.equals(r.taskId, task.id)),
                  O.fold(
                    () => [],
                    r => r.result
                  )
                )}
                isReadOnly={props.isReadOnly}
              />
            </TaskCard>
          ))}
        </div>
      </div>
    </StepLayout>
  );
}

export default View;
