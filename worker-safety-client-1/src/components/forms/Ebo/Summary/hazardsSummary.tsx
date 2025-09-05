import type { SummarySectionWrapperOnClickEdit } from "./summarySectionWrapper";
import type { SummaryDataGenerationError } from ".";
import type {
  HazardId,
  LibraryTask,
  LibraryTaskId,
  Hazard as HazardType,
} from "@/api/codecs";
import type { Either } from "fp-ts/lib/Either";
import type { Option } from "fp-ts/lib/Option";
import type { SelectedActivityTaskIds } from "../HighEnergyTasks";
import * as E from "fp-ts/lib/Either";
import * as O from "fp-ts/lib/Option";
import cx from "classnames";
import Image from "next/image";
import { useMemo, useState } from "react";
import { capitalize } from "lodash-es";
import * as Ord from "fp-ts/lib/Ord";
import { match as matchBoolean } from "fp-ts/boolean";
import { Eq as EqString, Ord as OrdString } from "fp-ts/lib/string";
import { Ord as OrdNumber } from "fp-ts/lib/number";
import * as A from "fp-ts/lib/Array";
import * as M from "fp-ts/lib/Map";
import * as S from "fp-ts/lib/Set";
import * as string from "fp-ts/lib/string";
import { pipe } from "fp-ts/lib/function";
import { isSome } from "fp-ts/Option";
import { Badge, Icon } from "@urbint/silica";
import { ControlType, ordHazardControlName } from "@/api/codecs";
import { OptionalView } from "@/components/common/Optional";
import { EnergyType } from "@/api/generated/types";
import * as HighEnergyTasksSubSection from "../HighEnergyTaskSubSection/HighEnergyTaskSubSection";
import { TaskCard } from "../../Basic/TaskCard";
import { sortHazardControlsByOther } from "../Hazards/Hazard";
import SummarySectionWrapper from "./summarySectionWrapper";

export type HazardsData = {
  selectedActivityTaskIds: Map<string, SelectedActivityTaskIds>;
  tasksWithHazards: HighEnergyTasksSubSection.Model[];
  tasks: LibraryTask[];
  hazards: HazardType[];
};

export type HazardsSummarySectionProps = SummarySectionWrapperOnClickEdit & {
  data: Either<SummaryDataGenerationError, HazardsData>;
  onTaskClickEdit: (taskId: LibraryTaskId) => (instanceId: number) => void;
  isReadOnly?: boolean;
  originalTaskNames: Map<LibraryTaskId, string>;
};

export type SubSectionModelWithTaskInformation =
  HighEnergyTasksSubSection.Model & {
    task: Option<LibraryTask>;
  };

export const ordHazardId = Ord.contramap((id: HazardId) => id)(OrdString);

function HazardsSummarySection({
  onClickEdit,
  onTaskClickEdit,
  data,
  isReadOnly = false,
  originalTaskNames,
}: HazardsSummarySectionProps) {
  const expandedAllTasks = pipe(
    data,
    E.fold(
      () => new Set<string>(),
      d =>
        pipe(
          d.tasksWithHazards,
          A.reduce(
            new Map<
              string,
              Omit<SubSectionModelWithTaskInformation, "task">[]
            >(),
            (result, curr) =>
              pipe(
                result,
                M.modifyAt(EqString)(curr.activityName, subSections =>
                  pipe(subSections, A.append(curr))
                ),
                O.getOrElse(() =>
                  pipe(
                    result,
                    M.upsertAt(EqString)(curr.activityName, A.of(curr))
                  )
                )
              )
          ),
          M.toArray(OrdString),
          A.map(([_, subSections]) =>
            pipe(
              subSections,
              A.mapWithIndex(
                (idx, subSection) =>
                  `${subSection.activityName}-${subSection.taskId}-${idx}`
              )
            )
          ),
          A.flatten,
          S.fromArray(EqString)
        )
    )
  );

  const [expandedTaskHazardSummaries, setExpandedTaskHazardSummaries] =
    useState(expandedAllTasks);

  const getHazardForHazardId =
    (hazardId: HazardId) => (hazards: HazardType[]) =>
      pipe(
        hazards,
        A.findFirst(h => h.id === hazardId)
      );

  const toggleTaskHazardSummaryExpansion = (taskHazardKey: string) => {
    pipe(
      expandedTaskHazardSummaries,
      S.elem(EqString)(taskHazardKey),
      O.fromPredicate(a => a),
      O.fold(
        () =>
          setExpandedTaskHazardSummaries(
            pipe(expandedTaskHazardSummaries, S.insert(EqString)(taskHazardKey))
          ),
        () =>
          setExpandedTaskHazardSummaries(
            pipe(expandedTaskHazardSummaries, S.remove(EqString)(taskHazardKey))
          )
      )
    );
  };

  // This function will be removed and unnecessary on week 2 of March, due to the changes
  // regarding to the instanceId logic being implemented to the SubSection Models.
  const toggleAllTaskHazardSummaryExpansions = () =>
    pipe(
      expandedTaskHazardSummaries,
      O.fromPredicate(S.isEmpty),
      O.fold(
        () => setExpandedTaskHazardSummaries(new Set()),
        () => setExpandedTaskHazardSummaries(pipe(expandedAllTasks))
      )
    );

  return (
    <SummarySectionWrapper
      title="High Energy Hazards"
      isSectionContentCollapsed={S.isEmpty(expandedTaskHazardSummaries)}
      onSectionContentCollapse={toggleAllTaskHazardSummaryExpansions}
      onClickEdit={onClickEdit}
      isEmpty={E.isLeft(data)}
      isEmptyText="No high energy hazards is selected."
      isReadOnly={isReadOnly}
    >
      {E.isRight(data) && (
        <div className="flex flex-col gap-5 w-full">
          {pipe(
            data.right.tasksWithHazards,
            A.map(taskWithHazards => ({
              ...taskWithHazards,
              task: (() => {
                const originalTaskName = originalTaskNames?.get(
                  taskWithHazards.taskId
                );
                if (originalTaskName) {
                  return O.some({
                    id: taskWithHazards.taskId,
                    name: originalTaskName,
                    riskLevel: "LOW" as any,
                    workTypes: O.none,
                    hazards: [],
                    activitiesGroups: O.none,
                  });
                }
                return pipe(
                  data.right.tasks,
                  A.findFirst(task => task.id === taskWithHazards.taskId)
                );
              })(),
            })),
            A.reduce(
              new Map<string, SubSectionModelWithTaskInformation[]>(),
              (result, curr) =>
                pipe(
                  result,
                  M.modifyAt(EqString)(curr.activityName, subSections =>
                    pipe(subSections, A.append(curr))
                  ),
                  O.getOrElse(() =>
                    pipe(
                      result,
                      M.upsertAt(EqString)(curr.activityName, A.of(curr))
                    )
                  )
                )
            ),
            M.toArray(OrdString),
            A.map(([activityGroupName, subSections]) => (
              <div key={activityGroupName} className="flex flex-col gap-3">
                <span className="font-semibold text-neutral-shade-75">
                  {activityGroupName}
                </span>
                <div className="flex flex-col gap-4">
                  {pipe(
                    subSections,
                    A.mapWithIndex((idx, subSection) => {
                      const taskHazardKey = `${subSection.activityName}-${subSection.taskId}-${idx}`;

                      return (
                        <OptionalView
                          key={taskHazardKey}
                          value={subSection.task}
                          render={task => (
                            <div key={taskHazardKey}>
                              <TaskCard
                                title={task.name}
                                risk={task.riskLevel}
                                expandable={true}
                                isExpanded={S.elem(EqString)(taskHazardKey)(
                                  expandedTaskHazardSummaries
                                )}
                                toggleElementExpand={() =>
                                  toggleTaskHazardSummaryExpansion(
                                    taskHazardKey
                                  )
                                }
                                showRiskInformation={false}
                                showRiskText={false}
                                withLeftBorder={false}
                                onClickEdit={() =>
                                  onTaskClickEdit(subSection.taskId)(
                                    subSection.instanceId
                                  )
                                }
                                isReadOnly={isReadOnly}
                              >
                                {pipe(
                                  subSection.selectedHazards,
                                  sh => M.size(sh) !== 0,
                                  matchBoolean(
                                    () => (
                                      <div className="w-full flex justify-center items-center p-4">
                                        No hazards were observed for this task.
                                      </div>
                                    ),
                                    () => (
                                      <>
                                        {pipe(
                                          subSection.selectedHazards,
                                          M.toArray(ordHazardId),
                                          A.map(
                                            ([hazardId, duplicateHazards]) =>
                                              pipe(
                                                data.right.hazards,
                                                getHazardForHazardId(hazardId),
                                                O.map(hazardDetails => (
                                                  <>
                                                    {pipe(
                                                      duplicateHazards,
                                                      M.toArray(OrdNumber),
                                                      A.map(
                                                        ([
                                                          duplicateHazardId,
                                                          hazardControls,
                                                        ]) => (
                                                          <Hazard
                                                            key={`${subSection.activityName}-${subSection.taskId}-${idx}-${hazardId}-${duplicateHazardId}`}
                                                            hazardId={hazardId}
                                                            duplicateHazardId={
                                                              duplicateHazardId
                                                            }
                                                            duplicateHazardAmount={pipe(
                                                              duplicateHazards,
                                                              M.size
                                                            )}
                                                            hazard={
                                                              hazardDetails
                                                            }
                                                            hazardControls={
                                                              hazardControls
                                                            }
                                                          />
                                                        )
                                                      )
                                                    )}
                                                  </>
                                                )),
                                                O.getOrElse(() => <></>)
                                              )
                                          )
                                        )}
                                      </>
                                    )
                                  )
                                )}
                              </TaskCard>
                            </div>
                          )}
                        />
                      );
                    })
                  )}
                </div>
              </div>
            ))
          )}
        </div>
      )}
    </SummarySectionWrapper>
  );
}

export default HazardsSummarySection;

type HazardProps = {
  hazardId: HazardId;
  duplicateHazardId: number;
  duplicateHazardAmount: number;
  hazardControls: HighEnergyTasksSubSection.HazardFieldValues;
  hazard: HazardType;
};

function Hazard({
  hazardId,
  duplicateHazardId,
  duplicateHazardAmount,
  hazard,
  hazardControls,
}: HazardProps) {
  const hazardTitle = useMemo(() => {
    if (duplicateHazardAmount === 1) return hazard.name;

    return `${hazard.name} - ${
      duplicateHazardId + 1
    } / ${duplicateHazardAmount}`;
  }, [duplicateHazardId, duplicateHazardAmount, hazard.name]);

  return (
    <div key={hazardId} className="w-full shadow-10 rounded-lg box-border">
      <div className="flex flex-row justify-between items-center bg-neutral-shade-75 py-2 px-4 rounded-t-lg">
        <span className="text-white font-semibold antialiased">
          {O.isSome(hazard.energyType) &&
            `${
              hazard.energyType.value === EnergyType.NotDefined
                ? ""
                : capitalize(hazard.energyType.value)
            }  `}
          {hazardTitle}
        </span>
      </div>
      <div
        className={cx("flex flex-col justify-start rounded-b-lg box-border", {
          ["border border-[#43565B]"]: hazard.isApplicable,
        })}
      >
        <div className="flex flex-col justify-center items-center gap-4 p-4">
          <div className="w-full h-20 relative">
            <Image
              src={
                isSome(hazard.imageUrl)
                  ? hazard.imageUrl.value
                  : "https://restore-build-artefacts.s3.amazonaws.com/default_image.svg"
              }
              alt={hazard.name}
              layout="fill"
            />
          </div>

          {O.isSome(hazardControls.isDirectControlsImplemented) &&
          hazardControls.isDirectControlsImplemented.value ? (
            <Badge
              label="Success"
              iconStart="check_bold"
              className="whitespace-nowrap shadow-none text-base text-white bg-system-success-40 p-1 hazard-exposure-badge"
            />
          ) : (
            <Badge
              label="EXPOSURE"
              iconStart="warning"
              className="whitespace-nowrap shadow-none text-base text-white bg-system-error-40 p-1 hazard-exposure-badge"
            />
          )}

          {hazard.name === HighEnergyTasksSubSection.OTHER_HAZARD_NAME && (
            <div className="w-full flex flex-col gap-2">
              <span className="font-semibold text-sm text-neutral-shade-75">
                Hazard energy level
              </span>
              <span className="font-normal text-base text-neutral-shade-100">
                {hazardControls.energyLevel.raw} foot-pounds
              </span>
            </div>
          )}

          {!string.isEmpty(hazardControls.description) && (
            <div className="w-full flex flex-col gap-2">
              <span className="font-semibold text-sm text-neutral-shade-75">
                Hazard Description
              </span>
              <span className="font-normal text-base text-neutral-shade-100">
                {hazardControls.description}
              </span>
            </div>
          )}

          {O.isSome(hazardControls.isDirectControlsImplemented) &&
            hazardControls.isDirectControlsImplemented.value && (
              <>
                <div className="w-full flex flex-col gap-2">
                  <span className="font-semibold text-sm text-neutral-shade-75">
                    Direct Controls
                  </span>
                  <>
                    {pipe(
                      hazardControls.directControls,
                      S.toArray(OrdString),
                      A.filterMap(cId =>
                        pipe(
                          hazard.controls,
                          A.findFirst(control => control.id === cId)
                        )
                      ),
                      A.sort(ordHazardControlName),
                      sortHazardControlsByOther(ControlType.DIRECT),
                      A.map(c => (
                        <div
                          key={c.id}
                          className={cx(
                            "shadow-10 w-full rounded-md px-4 py-2 flex flex-row items-center gap-4",
                            "bg-system-success-10"
                          )}
                        >
                          <div className="flex flex-col justify-center h-10">
                            <Icon
                              name="circle_check"
                              className="text-green-600 text-2xl"
                            />
                          </div>
                          <span className="font-semibold text-base text-neutral-shade-100">
                            {c.name}
                          </span>
                        </div>
                      ))
                    )}
                  </>
                </div>
                {!pipe(
                  hazardControls.directControlDescription,
                  string.isEmpty
                ) && (
                  <div className="w-full flex flex-col gap-2">
                    <span className="font-semibold text-sm text-neutral-shade-75">
                      Direct control description
                    </span>
                    <span className="font-normal text-base text-neutral-shade-100">
                      {hazardControls.directControlDescription}
                    </span>
                  </div>
                )}
              </>
            )}

          {O.isSome(hazardControls.isDirectControlsImplemented) &&
            !hazardControls.isDirectControlsImplemented.value &&
            O.isSome(hazardControls.noDirectControls) && (
              <div className="w-full flex flex-col gap-2">
                <span className="font-semibold text-sm text-neutral-shade-75">
                  Why were no direct controls implemented?
                </span>

                <div
                  className={cx(
                    "shadow-10 w-full rounded-md px-4 py-2 flex flex-row items-center gap-4",
                    "bg-system-error-10"
                  )}
                >
                  <div className="flex flex-col justify-center h-10">
                    <Icon
                      name="warning_circle"
                      className="text-system-error-40 text-xl"
                    />
                  </div>
                  <span className="font-semibold text-base text-neutral-shade-100">
                    {hazardControls.noDirectControls.value}
                  </span>
                </div>
              </div>
            )}

          {pipe(
            hazardControls.limitedControls,
            S.toArray(OrdString),
            O.fromPredicate(A.isNonEmpty),
            O.fold(
              () => <></>,
              limitedControls => (
                <div className="w-full flex flex-col gap-2">
                  <span className="font-semibold text-sm text-neutral-shade-75">
                    Limited controls
                  </span>
                  <>
                    {pipe(
                      limitedControls,
                      A.filterMap(cId =>
                        pipe(
                          hazard.controls,
                          A.findFirst(control => control.id === cId)
                        )
                      ),
                      A.sort(ordHazardControlName),
                      sortHazardControlsByOther(ControlType.INDIRECT),
                      A.map(limitedControl => {
                        return (
                          <div
                            key={limitedControl.id}
                            className="shadow-10 w-full rounded-md p-4"
                          >
                            <span className="font-semibold text-base text-neutral-shade-100">
                              {limitedControl.name}
                            </span>
                          </div>
                        );
                      })
                    )}
                  </>
                </div>
              )
            )
          )}

          {!pipe(hazardControls.limitedControlDescription, string.isEmpty) && (
            <div className="w-full flex flex-col gap-2">
              <span className="font-semibold text-sm text-neutral-shade-75">
                Limited control description
              </span>
              <span className="font-normal text-base text-neutral-shade-100">
                {hazardControls.limitedControlDescription}
              </span>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
