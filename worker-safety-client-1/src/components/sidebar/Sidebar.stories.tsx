import type { ComponentMeta, ComponentStory } from "@storybook/react";
import type { NavigationOption } from "../navigation/Navigation";
import { useEffect, useState } from "react";

import Sidebar from "./Sidebar";

export default {
  title: "Components/Sidebar",
  component: Sidebar,
  decorators: [
    Story => (
      <div className="w-60 p-3 border rounded">
        <Story />
      </div>
    ),
  ],
} as ComponentMeta<typeof Sidebar>;

const Template: ComponentStory<typeof Sidebar> = args => {
  const [selectedIndex, setSelectedIndex] = useState(args.selectedIndex);
  useEffect(() => {
    setSelectedIndex(args.selectedIndex);
  }, [args.selectedIndex]);

  return (
    <Sidebar
      options={args.options}
      selectedIndex={selectedIndex}
      onChange={setSelectedIndex}
    />
  );
};

const options: NavigationOption[] = [
  {
    id: 0,
    name: "Details",
    icon: "settings_filled",
  },
  {
    id: 1,
    name: "Locations",
    icon: "location",
  },
  {
    id: 2,
    name: "History",
    icon: "history",
  },
];

const optionsWithStatus: NavigationOption[] = [
  {
    id: 0,
    name: "Work Schedule",
    icon: "dot_05_xl",
  },
  {
    id: 1,
    name: "Crew",
    icon: "circle_check",
    status: "completed",
  },
  {
    id: 2,
    name: "Job Hazard Analysis",
    icon: "error",
    status: "error",
  },
];

export const Playground = Template.bind({});
Playground.args = {
  selectedIndex: 0,
  options,
};

export const WithStatus = Template.bind({});
WithStatus.args = {
  selectedIndex: 0,
  options: optionsWithStatus,
};
