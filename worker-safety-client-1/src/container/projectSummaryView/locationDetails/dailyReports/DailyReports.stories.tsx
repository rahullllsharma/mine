import type { ComponentMeta, ComponentStory } from "@storybook/react";
import { DailyReportStatus } from "@/types/report/DailyReportStatus";
import DailyReports from "./DailyReports";

export default {
  title: "Container/SummaryView/LocationDetails/DailyReport",
  component: DailyReports,
} as ComponentMeta<typeof DailyReports>;

const TemplateDailyReports: ComponentStory<typeof DailyReports> = args => (
  <DailyReports {...args} />
);

export const DailyReportInProgress = TemplateDailyReports.bind({});

DailyReportInProgress.args = {
  elements: [
    {
      id: "6162b039-40ad-486f-b6f7-2efb3822c437",
      createdBy: {
        id: "bab6fc84-63c3-4fe5-b7a6-137e26189ad9",
        name: "Test User",
      },
      createdAt: "2022-02-02T09:32:20.464954",
      status: DailyReportStatus.IN_PROGRESS,
    },
  ],
};

export const DailyReportComplete = TemplateDailyReports.bind({});

DailyReportComplete.args = {
  elements: [
    {
      id: "6162b039-40ad-486f-b6f7-2efb3822c437",
      createdBy: {
        id: "bab6fc84-63c3-4fe5-b7a6-137e26189ad9",
        name: "Test User",
      },
      createdAt: "2022-02-02T09:32:20.464954",
      completedBy: {
        id: "bab6fc84-63c3-4fe5-b7a6-137e26189ad9",
        name: "Test User",
      },
      completedAt: "2022-02-02T09:32:20.464954",
      status: DailyReportStatus.COMPLETE,
    },
  ],
};
