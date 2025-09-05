import type { ComponentMeta, ComponentStory } from "@storybook/react";
import ProjectPrintSection from "./ProjectPrintSection";

export default {
  title: "Container/Report/Print/ProjectInformation/Section",
  component: ProjectPrintSection,
} as ComponentMeta<typeof ProjectPrintSection>;

const Template: ComponentStory<typeof ProjectPrintSection> = args => {
  return <ProjectPrintSection {...args} />;
};

export const Playground = Template.bind({});
Playground.args = {
  header: "Project information",
  items: [
    {
      title: "Project name",
      description: "North Grand St. Bridge",
    },
    {
      title: "Project number",
      description: "12345678",
    },
    {
      title: "Description",
    },
    {
      title: "Additional project supervisor(s)",
      description: ["Christina Ou", "Mat Hebert", "João Lemos"],
    },
  ],
};
