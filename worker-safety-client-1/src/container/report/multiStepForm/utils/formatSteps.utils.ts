import type { NavigationStatus } from "@/components/navigation/Navigation";
import type {
  MultiStepFormStateItem,
  MultiStepFormStep,
} from "../state/reducer";

const formatSteps = (
  initialSteps: MultiStepFormStep[]
): MultiStepFormStateItem[] => {
  const hasSelectedStep = initialSteps.some(
    step => typeof step?.isSelected === "boolean"
  );

  if (hasSelectedStep) {
    return initialSteps as MultiStepFormStateItem[];
  }

  return initialSteps.map((step, index) => ({
    ...step,
    isSelected: index === 0, // automatically select the first step
    status: step?.status || ("default" as NavigationStatus),
  }));
};

export { formatSteps };
