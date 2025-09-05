import type { ComponentMeta, ComponentStory } from "@storybook/react";
import type { NavigationOption } from "./Navigation";
import { useEffect, useState } from "react";

import Navigation from "./Navigation";

export default {
  title: "Components/Navigation",
  component: Navigation,
  decorators: [
    Story => (
      <div className="w-72">
        <Story />
      </div>
    ),
  ],
} as ComponentMeta<typeof Navigation>;

const Template: ComponentStory<typeof Navigation> = args => {
  const [selectedIndex, setSelectedIndex] = useState(args.selectedIndex);
  useEffect(() => {
    setSelectedIndex(args.selectedIndex);
  }, [args.selectedIndex]);

  return (
    <Navigation
      options={args.options}
      selectedIndex={selectedIndex}
      onChange={setSelectedIndex}
      withStatus={args.withStatus}
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
  withStatus: true,
};
