import type { ComponentMeta, ComponentStory } from "@storybook/react";

import type { FilterProject } from "@/container/insights/utils";
import ProjectFilters from "./ProjectFilters";

export default {
  title: "Container/Insights/Filters/Project",
  component: ProjectFilters,
  argTypes: { onChange: { control: "onChange" } },
  decorators: [
    Story => (
      <div className="w-80">
        <Story />
      </div>
    ),
  ],
} as ComponentMeta<typeof ProjectFilters>;

const projects: FilterProject[] = [
  {
    id: "7114445f-966a-42e2-aa3b-0e4d5365075d",
    name: "5th Street Main Relocation",
    externalKey: "123",
    locations: [
      {
        id: "1",
        name: "Location 1",
      },
      {
        id: "2",
        name: "Location 2",
      },
    ],
  },
  {
    id: "7114445f-966a-42e2-aa3b-0e4d53650751a",
    name: "N. Washington Street Bridge",
    externalKey: "123",
    locations: [
      {
        id: "3",
        name: "Location 3",
      },
      {
        id: "4",
        name: "Location 4",
      },
    ],
  },
  {
    id: "7114445f-966a-42e2-aa3b-0e4d53650751b",
    name: "22nd Street Main Intersection",
    externalKey: "123",
    locations: [
      {
        id: "5",
        name: "Location 5",
      },
      {
        id: "6",
        name: "Location 6",
      },
    ],
  },
];

const Template: ComponentStory<typeof ProjectFilters> = args => (
  <ProjectFilters {...args} />
);

export const Playground = Template.bind({});
Playground.args = {
  projects,
};
