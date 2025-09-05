import type { Meta, Story } from "@storybook/react";
import type { AttributesTableProps } from "./AttributesTable";
import { TenantMock } from "@/store/tenant/utils/tenantMock";
import { AttributesTable } from "./AttributesTable";

export default {
  title: "Components/TenantAttributes/AttributesTable",
  component: AttributesTable,
  argTypes: {
    columns: { table: { disable: true } },
    data: { table: { disable: true } },
  },
} as Meta;

const Template: Story<AttributesTableProps> = args => (
  <AttributesTable {...args} />
);

export const Playground = Template.bind({});
Playground.args = {
  data: TenantMock.entities[0].attributes,
};
