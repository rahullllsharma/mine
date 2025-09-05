import type { Hazard } from "@/types/project/Hazard";
import type { Control } from "@/types/project/Control";
import type { HazardAggregator } from "@/types/project/HazardAggregator";
import TaskCard from "@/components/layout/taskCard/TaskCard";
import TaskContentEdit from "@/components/layout/taskCard/content/TaskContentEdit";
import { excludeRecommendedHazards } from "@/utils/task";
import { useTenantStore } from "@/store/tenant/useTenantStore.store";
import { useHazardForm } from "../hooks";
import ButtonSecondary from "../../shared/button/secondary/ButtonSecondary";

type SiteCondition = Omit<
  HazardAggregator,
  "riskLevel" | "startDate" | "endDate" | "status"
>;

type SiteConditionDetailsProps = {
  siteCondition: SiteCondition;
  hazardsLibrary: Hazard[];
  controlsLibrary: Control[];
};

export default function SiteConditionDetailsForm({
  siteCondition,
  hazardsLibrary,
  controlsLibrary,
}: SiteConditionDetailsProps): JSX.Element {
  const { hazard, control } = useTenantStore(state => state.getAllEntities());

  const {
    hazards,
    isAddButtonDisabled,
    addHazardHandler,
    removeHazardHandler,
    selectHazardHandler,
  } = useHazardForm(siteCondition.hazards, hazardsLibrary);

  const siteConditionHeader = (
    <header
      data-testid="siteCondition-header"
      className="flex flex-1 flex-wrap items-center text-left text-sm font-semibold text-neutral-shade-75 px-4 pt-4"
    >
      <p className="flex flex-1">{`${hazard.label} / ${control.label} group`}</p>
      Applicable?
    </header>
  );

  const isDisabled = !siteCondition.isManuallyAdded;

  const canAddHazards = hazardsLibrary.length > 0 && !isDisabled;

  return (
    <>
      {canAddHazards && (
        <section>
          <ButtonSecondary
            label={`Add a ${hazard.label.toLowerCase()}`}
            iconStart="plus"
            size="sm"
            className="block mb-2 ml-auto"
            title={
              isAddButtonDisabled()
                ? `No more ${hazard.labelPlural.toLowerCase()} available`
                : ""
            }
            disabled={isAddButtonDisabled()}
            onClick={addHazardHandler}
          />
        </section>
      )}
      <section className="mt-2 bg-white">
        <TaskCard
          className="border-data-blue-30"
          taskHeader={siteConditionHeader}
        >
          <TaskContentEdit
            hazards={hazards}
            controlsLibrary={controlsLibrary}
            hazardsLibrary={excludeRecommendedHazards(
              hazardsLibrary,
              siteCondition.hazards
            )}
            onRemoveHazard={removeHazardHandler}
            onSelectHazard={selectHazardHandler}
            isDisabled={isDisabled}
          />
        </TaskCard>
      </section>
    </>
  );
}
