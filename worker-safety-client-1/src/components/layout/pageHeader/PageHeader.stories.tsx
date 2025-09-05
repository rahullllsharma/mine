import type { ComponentMeta, ComponentStory } from "@storybook/react";
import type { PageHeaderAction } from "./components/headerActions/HeaderActions";
import React from "react";

import { noop } from "lodash-es";
import { RiskLevel } from "@/components/riskBadge/RiskLevel";
import RiskBadge from "@/components/riskBadge/RiskBadge";
import PageHeader from "./PageHeader";

export default {
  title: "Layout/PageHeader",
  component: PageHeader,
  argTypes: {
    argTypes: { onClick: { action: "clicked" } },
  },
} as ComponentMeta<typeof PageHeader>;

const TemplatePageHeaderView: ComponentStory<typeof PageHeader> = args => (
  <PageHeader {...args}></PageHeader>
);

export const Playground = TemplatePageHeaderView.bind({});

Playground.args = {
  pageTitle: "Page Title text",
  linkText: "Back button text",
  linkRoute: "/",
};

const singleAction: PageHeaderAction[] = [
  {
    title: "Edit",
    icon: "edit",
    onClick: noop,
  },
];

const multipleActions: PageHeaderAction[] = [
  {
    title: "Edit",
    icon: "edit",
    onClick: noop,
  },
  {
    title: "Delete",
    icon: "trash_empty",
    onClick: noop,
  },
];

export const WithSingleAction = TemplatePageHeaderView.bind({});
WithSingleAction.args = {
  pageTitle: "Page Title text",
  linkText: "Back button text",
  linkRoute: "/",
  actions: singleAction,
};

export const WithMultipleActions = TemplatePageHeaderView.bind({});
WithMultipleActions.args = {
  pageTitle: "Page Title text",
  linkText: "Back button text",
  linkRoute: "/",
  actions: multipleActions,
};

export const WithTooltipAction = TemplatePageHeaderView.bind({});
WithTooltipAction.args = {
  pageTitle: "Page Title text",
  linkText: "Back button text",
  linkRoute: "/",
  actions: {
    type: "tooltip",
    icon: "apple",
    title: "custom title",
  },
};

const TemplatePageHeaderViewCustom: ComponentStory<typeof PageHeader> =
  args => (
    <PageHeader {...args}>
      <h4 className="text-neutral-shade-100 mr-3">Page Title text</h4>
      <RiskBadge risk={RiskLevel.HIGH} label={`${RiskLevel.HIGH} risk`} />
    </PageHeader>
  );

export const CustomContent = TemplatePageHeaderViewCustom.bind({});

CustomContent.args = {
  linkText: "Back button text",
  linkRoute: "/",
};
