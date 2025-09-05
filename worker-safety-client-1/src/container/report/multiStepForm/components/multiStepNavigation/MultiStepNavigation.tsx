import type {
  NavigationOption,
  NavigationStatus,
} from "@/components/navigation/Navigation";
import type { IconName } from "@urbint/silica";
import type { MultiStepFormState } from "../../state/reducer";
import { useEffect } from "react";
import Navigation from "@/components/navigation/Navigation";
import {
  useMultiStepActions,
  useMultiStepState,
} from "../../hooks/useMultiStep";

/**
 * Replace URL with the proper navigation for the section.
 *
 * @description
 * This will handle all the navigation changes including the first render
 * and a special case where Keycloak attaches a hashbang with #state so it
 * proper redirects after a reload.
 */
const replaceHashbangWithSection = (section: string): string => {
  const fragmentedUrl = new URL(window.location.href);
  fragmentedUrl.hash = section;
  return fragmentedUrl.toString();
};

export const getNavIcon = (status: NavigationStatus): IconName => {
  switch (status) {
    case "completed":
      return "circle_check";
    case "error":
      return "error";
    default:
      return "circle";
  }
};

const getNavigationOptions = (steps: MultiStepFormState): NavigationOption[] =>
  steps.map((step, index) => ({
    id: index,
    name: step.name,
    icon: getNavIcon(step.status),
    iconSize: "lg",
    status: step.status,
  }));

export default function MultiStepNavigation(): JSX.Element {
  const { steps, current } = useMultiStepState();
  const { moveTo } = useMultiStepActions();

  const selectedIndex = steps.findIndex(step => step.id === current.id);

  useEffect(() => {
    if (!history?.state?.as?.includes(current.path)) {
      const newSectionHistoryState = {
        ...history.state,
        idx: history.state?.idx + 1 || 0,
        as: replaceHashbangWithSection(current.path),
      };

      history.replaceState(
        newSectionHistoryState,
        "",
        newSectionHistoryState.as
      );
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [current.id]);

  return (
    <Navigation
      options={getNavigationOptions(steps)}
      onChange={index => {
        moveTo(steps[index].id);
      }}
      withStatus
      selectedIndex={selectedIndex}
    />
  );
}
