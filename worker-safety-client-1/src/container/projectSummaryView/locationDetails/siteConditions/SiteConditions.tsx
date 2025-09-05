import type { HazardAggregator } from "@/types/project/HazardAggregator";
import type { WithEmptyStateProps } from "../withEmptyState";
import { useAuthStore } from "@/store/auth/useAuthStore.store";
import { countTotalControls } from "@/container/Utils";
import TaskHeader from "@/components/layout/taskCard/header/TaskHeader";
import TaskContent from "@/components/layout/taskCard/content/TaskContent";
import TaskCard from "@/components/layout/taskCard/TaskCard";
import { messages } from "@/locales/messages";

type SiteConditionsSectionProps = {
  siteConditions: HazardAggregator;
  isOpen: boolean;
  onToggle: (siteCondition: HazardAggregator) => void;
  onSiteConditionClicked: (siteCondition: HazardAggregator) => void;
};

function SiteConditionsSection({
  siteConditions,
  isOpen,
  onToggle,
  onSiteConditionClicked,
}: SiteConditionsSectionProps): JSX.Element {
  const { hasPermission } = useAuthStore();
  const iconName = isOpen ? "chevron_big_down" : "chevron_big_right";
  const isAutoPopulatedSiteCondition = !siteConditions.isManuallyAdded;
  const menuIconName = isAutoPopulatedSiteCondition ? "show" : "edit";

  const onClick = () => onToggle(siteConditions);
  const onMenuClickHandler = () => onSiteConditionClicked(siteConditions);

  const taskHeader = (
    <TaskHeader
      icon={iconName}
      headerText={siteConditions.name}
      onClick={onClick}
      showSummaryCount={!isOpen}
      totalHazards={siteConditions.hazards.length}
      totalControls={countTotalControls(siteConditions.hazards)}
      // The menu should be hidden if the user can not use it. Following
      // approach is a tradeoff of and does appear opaque
      menuIcon={menuIconName}
      hasInfoIcon={isAutoPopulatedSiteCondition}
      infoIconTooltipText={messages.autoPopulatedSiteConditionMessage}
      onMenuClicked={
        hasPermission("EDIT_SITE_CONDITIONS") ? onMenuClickHandler : undefined
      }
    />
  );

  return (
    <TaskCard
      className="border-data-blue-30"
      isOpen={isOpen}
      taskHeader={taskHeader}
    >
      <TaskContent hazards={siteConditions.hazards}></TaskContent>
    </TaskCard>
  );
}

export type SiteConditionsProps = WithEmptyStateProps<HazardAggregator> & {
  isCardOpen: (element: HazardAggregator) => boolean;
  onCardToggle: (element: HazardAggregator) => void;
};

export default function SiteConditions({
  elements,
  onElementClick,
  isCardOpen,
  onCardToggle,
}: SiteConditionsProps): JSX.Element {
  return (
    <>
      {elements.map(aggregator => (
        <SiteConditionsSection
          key={aggregator.id}
          siteConditions={aggregator}
          isOpen={isCardOpen(aggregator)}
          onToggle={onCardToggle}
          onSiteConditionClicked={onElementClick}
        />
      ))}
    </>
  );
}
