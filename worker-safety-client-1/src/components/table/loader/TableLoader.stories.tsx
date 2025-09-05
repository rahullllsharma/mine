import type { Meta, Story } from "@storybook/react";
import type { TableLoaderProps } from "./TableLoader";
import { TableLoader } from "./TableLoader";

export default {
  title: "Components/Table/Loader",
  component: TableLoader,
} as Meta;

const Template: Story<TableLoaderProps> = args => <TableLoader {...args} />;

export const Playground = Template.bind({});

Playground.args = {
  columnsSize: 3,
};
