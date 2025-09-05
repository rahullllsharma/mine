import type { Option } from "fp-ts/lib/Option";
import type { Semigroup } from "fp-ts/lib/Semigroup";
import type { ChildProps } from "@/utils/reducerWithEffect";
import type { NonEmptyArray } from "fp-ts/lib/NonEmptyArray";
import type { Either } from "fp-ts/lib/Either";
import type {
  ActivitiesGroupId,
  LibraryTask,
  LibraryTaskId,
} from "@/api/codecs";
import type { NonEmptyString } from "io-ts-types";
import { Eq as EqString, Ord as OrdString } from "fp-ts/lib/string";
import * as E from "fp-ts/lib/Either";
import * as Eq from "fp-ts/lib/Eq";
import * as Ord from "fp-ts/lib/Ord";
import * as S from "fp-ts/lib/Set";
import { constant, flow, identity, pipe } from "fp-ts/lib/function";
import * as NEA from "fp-ts/lib/NonEmptyArray";
import * as A from "fp-ts/lib/Array";
import * as O from "fp-ts/lib/Option";
import * as M from "fp-ts/lib/Map";
import { useCallback, useMemo } from "react";
import { Badge } from "@urbint/silica";
import * as SG from "fp-ts/lib/Semigroup";
import {
  eqActivitiesGroupId,
  eqLibraryTaskId,
  ordActivitiesGroupId,
  ordLibraryTaskId,
} from "@/api/codecs";
import Accordion from "@/components/shared/accordion/Accordion";
import { OptionalView } from "@/components/common/Optional";
import { InputRaw } from "../Basic/Input";
import { Checkbox } from "../Basic/Checkbox";

type GroupItem = {
  id: ActivitiesGroupId;
  name: NonEmptyString;
};

const eqGroupItemById = Eq.contramap((groupItem: GroupItem) => groupItem.id)(
  EqString
);
const ordGroupItemById = Ord.contramap((groupItem: GroupItem) => groupItem.id)(
  OrdString
);
const eqLibraryTaskById = Eq.contramap((task: LibraryTask) => task.id)(
  EqString
);

const uniqueTasksSemigroup: Semigroup<LibraryTask[]> = {
  concat: (xs, ys) => pipe(xs, A.concat(ys), A.uniq(eqLibraryTaskById)),
};

export type Model = {
  selectedTaskIds: Map<ActivitiesGroupId, Set<LibraryTaskId>>;
  search: string;
};

export const init = (
  prevSelectedTaskIds: Map<ActivitiesGroupId, Set<LibraryTaskId>>
): Model => ({
  selectedTaskIds: prevSelectedTaskIds,
  search: "",
});

export const result = (
  model: Model
): Either<string, NonEmptyArray<LibraryTaskId>> =>
  pipe(
    model.selectedTaskIds,
    M.foldMap(ordActivitiesGroupId)(S.getUnionMonoid(eqLibraryTaskId))(
      identity
    ),
    S.toArray(ordLibraryTaskId),
    NEA.fromArray,
    E.fromOption(() => "No tasks selected")
  );

export type Action =
  | {
      type: "TaskToggled";
      groupId: ActivitiesGroupId;
      taskId: LibraryTaskId;
    }
  | {
      type: "SearchChanged";
      value: string;
    };

export const TaskToggled =
  (groupId: ActivitiesGroupId) =>
  (taskId: LibraryTaskId): Action => ({
    type: "TaskToggled",
    groupId,
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
        selectedTaskIds: pipe(
          model.selectedTaskIds,
          M.modifyAt(eqActivitiesGroupId)(
            action.groupId,
            S.toggle(eqLibraryTaskId)(action.taskId)
          ),
          O.getOrElse(() =>
            M.upsertAt(eqActivitiesGroupId)(
              action.groupId,
              S.singleton(action.taskId)
            )(model.selectedTaskIds)
          )
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
    if (search === "") {
      return O.some([group, tasks]);
    }

    const lcSearch = search.toLowerCase();
    if (group.name.toLowerCase().includes(lcSearch)) {
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

  // for efficient task lookup
  const tasksMap = useMemo(
    () =>
      pipe(
        props.tasks,
        A.map((task): [LibraryTaskId, LibraryTask] => [task.id, task]),
        M.fromFoldable(eqLibraryTaskId, SG.first<LibraryTask>(), A.Foldable)
      ),
    [props.tasks]
  );

  const groups = useMemo(
    () =>
      pipe(
        props.tasks,
        A.chain(task =>
          pipe(
            task.activitiesGroups,
            O.fold(() => [], identity)
          )
        ),
        A.map((group): [GroupItem, LibraryTask[]] => [
          { id: group.id, name: group.name },
          pipe(
            group.tasks,
            A.filterMap(task => M.lookup(eqLibraryTaskId)(task.id)(tasksMap))
          ),
        ]),
        A.filterMap(filterTaskGroup(model.search)),
        M.fromFoldable(eqGroupItemById, uniqueTasksSemigroup, A.Foldable),
        M.toArray(ordGroupItemById),
        NEA.fromArray
      ),
    [props.tasks, tasksMap, model.search]
  );

  const groupHasSelectedTasks = useCallback(
    (groupId: ActivitiesGroupId) =>
      pipe(
        model.selectedTaskIds,
        M.lookup(eqActivitiesGroupId)(groupId),
        O.filter(s => !S.isEmpty(s)),
        O.isSome
      ),
    [model.selectedTaskIds]
  );

  const isTaskSelected = useCallback(
    (taskId: LibraryTaskId, groupId: ActivitiesGroupId) =>
      pipe(
        model.selectedTaskIds,
        M.lookup(eqActivitiesGroupId)(groupId),
        O.filter(S.elem(eqLibraryTaskId)(taskId)),
        O.isSome
      ),
    [model.selectedTaskIds]
  );

  return (
    <div className="flex flex-col gap-4 h-full">
      <InputRaw
        placeholder={`Search by task or activity group`}
        icon="search"
        onChange={flow(SearchChanged, dispatch)}
      />
      <div className="overflow-y-scroll flex flex-col gap-4 py-4 pl-4 pr-2 border-brand-gray-40 border rounded-lg">
        <OptionalView
          value={groups}
          render={gs => (
            <>
              {gs.map(([group, ts]) => (
                <Accordion
                  key={group.id}
                  header={<ActivityHeader groupName={group.name} ts={ts} />}
                  isDefaultOpen={groupHasSelectedTasks(group.id)}
                >
                  <div className="flex flex-col gap-2 pl-4">
                    {ts.map(task => (
                      <Checkbox
                        key={task.id}
                        checked={isTaskSelected(task.id, group.id)}
                        onClick={flow(
                          constant(task.id),
                          TaskToggled(group.id),
                          dispatch
                        )}
                      >
                        <span className="text-brand-gray-80 text-sm">
                          {task.name}
                        </span>
                      </Checkbox>
                    ))}
                  </div>
                </Accordion>
              ))}
            </>
          )}
          renderNone={() => <>No match found</>}
        />
      </div>
    </div>
  );
}

const ActivityHeader = ({
  groupName,
  ts,
}: {
  groupName: NonEmptyString;
  ts: LibraryTask[];
}) => {
  return (
    <div className="inline-flex flex-row items-center gap-2">
      <span className="text-brand-gray-80">{groupName}</span>
      <Badge label={ts.length.toString()} className="text-brand-gray-70" />
    </div>
  );
};
