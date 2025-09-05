import type { TemplateSettingsFormProps } from "../../../customisedForm.types";
import { TemplateSettingsNavigationTab } from "../../../customisedForm.types";
import TemplateAvailability from "./TemplateAvailability/TemplateAvailability";
import EditPeriod from "./EditPeriod/EditPeriod";
import WorkTypes from "./WorkTypes/WorkTypes";
import LinkedForms from "./LinkedForms/LinkedForm";

const getNavigationTabOption = (index: number): TemplateSettingsNavigationTab =>
  Object.values(TemplateSettingsNavigationTab)[index];

export const isTemplateAvailabilityTab = (index: number): boolean =>
  getNavigationTabOption(index) ===
  TemplateSettingsNavigationTab.TEMPLATE_AVAILABILITY;

export const isWorkTypesTab = (index: number): boolean =>
  getNavigationTabOption(index) === TemplateSettingsNavigationTab.WORK_TYPES;

export const isEditPeriodTab = (index: number): boolean =>
  getNavigationTabOption(index) === TemplateSettingsNavigationTab.EDIT_PERIOD;

export const isLinkedFormTab = (index: number): boolean =>
  getNavigationTabOption(index) === TemplateSettingsNavigationTab.LINKED_FORMS;

interface ExtendedTemplateSettingsFormProps extends TemplateSettingsFormProps {
  onWorkTypesModified?: () => void;
}

export default function TemplateSettingsForm({
  selectedTab,
  settings,
  onWorkTypesModified,
}: ExtendedTemplateSettingsFormProps): JSX.Element {
  return (
    <>
      {isTemplateAvailabilityTab(selectedTab) && (
        <TemplateAvailability settings={settings} />
      )}
      {isEditPeriodTab(selectedTab) && <EditPeriod settings={settings} />}
      {isWorkTypesTab(selectedTab) && (
        <WorkTypes
          settings={settings}
          onWorkTypesModified={onWorkTypesModified}
        />
      )}
      {isLinkedFormTab(selectedTab) && <LinkedForms settings={settings} />}
    </>
  );
}
