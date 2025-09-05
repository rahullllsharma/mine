import type { Option } from "fp-ts/lib/Option";
import type { ChildProps } from "@/utils/reducerWithEffect";
import type { Either } from "fp-ts/lib/Either";
import type {
  ActivitiesGroupId,
  LibraryTask,
  LibraryTaskId,
} from "@/api/codecs";
import type { SelectedDuplicateActivities } from "../HighEnergyTasks";
import * as E from "fp-ts/lib/Either";
import * as O from "fp-ts/lib/Option";
import { Eq as EqString, Ord as OrdString } from "fp-ts/lib/string";
import * as Eq from "fp-ts/lib/Eq";
import * as Ord from "fp-ts/lib/Ord";
import * as S from "fp-ts/lib/Set";
import { constant, flow, pipe } from "fp-ts/lib/function";
import * as A from "fp-ts/lib/Array";
import * as M from "fp-ts/lib/Map";
import * as Tup from "fp-ts/lib/Tuple";
import { useCallback, useMemo } from "react";
import { Badge } from "@urbint/silica";
import {
  eqActivitiesGroupId,
  eqLibraryTaskId,
  ordActivitiesGroupId,
} from "@/api/codecs";
import Accordion from "@/components/shared/accordion/Accordion";
import { InputRaw } from "../../Basic/Input";
import { Checkbox } from "../../Basic/Checkbox";

type GroupItem = {
  activityId: ActivitiesGroupId;
  activityName: string;
  aliases?: string[];
};

export type SelectedActivities = Map<
  string,
  {
    activityGroup: GroupItem;
    taskIds: Set<LibraryTaskId>;
  }
>;

const eqGroupItemById = Eq.contramap(
  (groupItem: GroupItem) => groupItem.activityId
)(eqActivitiesGroupId);
const ordGroupItemById = Ord.contramap(
  (groupItem: GroupItem) => groupItem.activityId
)(ordActivitiesGroupId);
const eqLibraryTaskById = Eq.contramap((task: LibraryTask) => task.id)(
  eqLibraryTaskId
);

const ordByActivityGroupName = Ord.contramap((a: [GroupItem, LibraryTask[]]) =>
  pipe(a, Tup.fst, s => s.activityName)
)(OrdString);

const ordByLibraryTaskName = pipe(
  OrdString,
  Ord.contramap((t: LibraryTask) => t.name)
);

export type Model = {
  selectedActivities: SelectedActivities;
  allSelectedActivities: SelectedDuplicateActivities;
  search: string;
};

export const init = (
  prevSelectedActivitiesInSection: SelectedActivities,
  allSelectedActivities: SelectedDuplicateActivities
): Model => ({
  selectedActivities: prevSelectedActivitiesInSection,
  allSelectedActivities,
  search: "",
});

export const result = (model: Model): Either<string, SelectedActivities> =>
  pipe(
    model.selectedActivities,
    E.fromPredicate(
      activities => !M.isEmpty(activities),
      () => "No tasks selected"
    )
  );

export type Action =
  | {
      type: "TaskToggled";
      activityGroup: GroupItem;
      taskId: LibraryTaskId;
    }
  | {
      type: "SearchChanged";
      value: string;
    };

export const TaskToggled =
  (activityGroup: GroupItem) =>
  (taskId: LibraryTaskId): Action => ({
    type: "TaskToggled",
    activityGroup,
    taskId,
  });

export const SearchChanged = (value: string): Action => ({
  type: "SearchChanged",
  value,
});

export const update = (model: Model, action: Action): Model => {
  switch (action.type) {
    case "TaskToggled":
      return {
        ...model,
        selectedActivities: pipe(
          model.selectedActivities,
          M.lookup(EqString)(action.activityGroup.activityName),
          O.map(() =>
            pipe(
              model.selectedActivities,
              M.modifyAt(EqString)(action.activityGroup.activityName, sa => ({
                ...sa,
                taskIds: pipe(
                  sa.taskIds,
                  S.toggle(eqLibraryTaskId)(action.taskId)
                ),
              })),
              O.getOrElse(() => model.selectedActivities)
            )
          ),
          O.getOrElse(() =>
            pipe(
              model.selectedActivities,
              M.upsertAt(EqString)(action.activityGroup.activityName, {
                activityGroup: action.activityGroup,
                taskIds: new Set([action.taskId]),
              })
            )
          ),
          M.filter(a => !S.isEmpty(a.taskIds))
        ),
      };

    case "SearchChanged":
      return {
        ...model,
        search: action.value,
      };
  }
};

const filterTaskGroup =
  (search: string) =>
  ([group, tasks]: [GroupItem, LibraryTask[]]): Option<
    [GroupItem, LibraryTask[]]
  > => {
    if (search === "") return O.some([group, tasks]);

    const lcSearch = search.toLowerCase();

    // Check if search matches activity name or any alias
    const matchesActivityName = group.activityName
      .toLowerCase()
      .includes(lcSearch);
    const matchesAlias =
      group.aliases &&
      group.aliases.some(
        alias => alias && alias.toLowerCase().includes(lcSearch)
      );

    if (matchesActivityName || matchesAlias) {
      return O.some([group, tasks]);
    }

    const filteredTasks = pipe(
      tasks,
      A.filter(task => task.name.toLowerCase().includes(lcSearch))
    );

    return filteredTasks.length > 0 ? O.some([group, filteredTasks]) : O.none;
  };

export type Props = ChildProps<Model, Action> & {
  tasks: LibraryTask[];
};

export function View(props: Props): JSX.Element {
  const { model, dispatch } = props;

  const groups = useMemo(
    () =>
      pipe(
        props.tasks,
        A.chain(task =>
          Array.isArray(task.activitiesGroups)
            ? task.activitiesGroups
            : task.activitiesGroups
            ? (task.activitiesGroups as any)
            : []
        ),
        A.map((group: any): [GroupItem, LibraryTask[]] => [
          {
            activityId: group.id,
            activityName:
              group.aliases && group.aliases.length > 0
                ? group.aliases[0]
                : group.name,
            aliases: group.aliases,
          },
          pipe(
            group.tasks,
            A.filterMap((task: any) =>
              pipe(
                props.tasks,
                A.findFirst(t => t.id === task.id)
              )
            )
          ),
        ]),
        A.filterMap(filterTaskGroup(model.search)),
        M.fromFoldable(
          eqGroupItemById,
          A.getSemigroup<LibraryTask>(),
          A.Foldable
        ),
        M.map(A.uniq(eqLibraryTaskById)),
        M.toArray(ordGroupItemById),
        A.sort(ordByActivityGroupName)
      ),
    [props.tasks, model.search]
  );

  const groupHasSelectedTasks = useCallback(
    (groupId: ActivitiesGroupId) =>
      pipe(
        groups,
        A.findFirst(([group]) => group.activityId === groupId),
        O.fold(
          () => false,
          ([group, tasks]) =>
            pipe(
              model.selectedActivities,
              M.lookup(EqString)(group.activityName),
              O.fold(
                () => false,
                a =>
                  pipe(
                    tasks,
                    A.findFirst(task =>
                      S.elem(eqLibraryTaskId)(task.id)(a.taskIds)
                    ),
                    O.isSome
                  )
              )
            )
        )
      ),
    [groups, model.selectedActivities]
  );

  return (
    <div className="flex flex-col gap-4 h-full">
      <p>Search and select a task from the list below.</p>
      <InputRaw
        placeholder="Search by task or activity group"
        icon="search"
        onChange={flow(SearchChanged, dispatch)}
      />
      <div className="overflow-y-scroll flex flex-col gap-4 py-4 pl-4 pr-2 border-brand-gray-40 border rounded-lg">
        {groups.map(([group, ts]) => (
          <Accordion
            key={group.activityId}
            header={<ActivityHeader group={group} ts={ts} />}
            isDefaultOpen={groupHasSelectedTasks(group.activityId)}
            forceOpen={!!model.search}
          >
            <div className="flex flex-col gap-2 pl-4">
              {pipe(
                ts,
                A.sort(ordByLibraryTaskName),
                A.map(task => (
                  <Checkbox
                    key={task.id}
                    checked={pipe(
                      M.lookup(EqString)(
                        group.activityName,
                        model.selectedActivities
                      ),
                      O.fold(
                        () => false,
                        a => S.elem(eqLibraryTaskId)(task.id, a.taskIds)
                      )
                    )}
                    onClick={flow(
                      constant(task.id),
                      TaskToggled(group),
                      dispatch
                    )}
                  >
                    <span className="text-brand-gray-80 text-sm">
                      {task.name}
                    </span>
                  </Checkbox>
                ))
              )}
            </div>
          </Accordion>
        ))}
      </div>
    </div>
  );
}

const ActivityHeader = ({
  group,
  ts,
}: {
  group: GroupItem;
  ts: LibraryTask[];
}) => {
  return (
    <div className="inline-flex flex-row items-center gap-2">
      <span className="text-brand-gray-80">{group.activityName}</span>
      <Badge label={ts.length.toString()} className="text-brand-gray-70" />
    </div>
  );
};
