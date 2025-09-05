import type { ComponentMeta, ComponentStory } from "@storybook/react";

import type { FilterProject } from "../utils";
import type { LibraryRegion } from "@/types/project/LibraryRegion";
import type { LibraryDivision } from "@/types/project/LibraryDivision";
import type { Contractor } from "@/types/project/Contractor";
import { projectStatusOptions } from "@/types/project/ProjectStatus";
import PortfolioFilters from "./PortfolioFilters";

export default {
  title: "Container/Insights/Filters/Portfolio",
  component: PortfolioFilters,
  argTypes: { onChange: { control: "onChange" } },
  decorators: [
    Story => (
      <div className="w-80">
        <Story />
      </div>
    ),
  ],
} as ComponentMeta<typeof PortfolioFilters>;

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

const regions: LibraryRegion[] = [
  {
    id: "8e255eb4-09f2-45aa-a6c8-79f2f45a5120",
    name: "DNY (Downstate New York)",
  },
  {
    id: "f99ddad3-a34b-4380-bff8-f0aa94acda23",
    name: "UNY (Upstate New York)",
  },
  {
    id: "61910ead-90d1-4afd-846c-e053fad35921",
    name: "NE (New England)",
  },
];

const divisions: LibraryDivision[] = [
  {
    id: "26188e20-01bc-4afe-80c1-2e9d0ad1a341",
    name: "Gas",
  },
  {
    id: "9f86e0d2-de57-43a7-bcda-53c18029708e",
    name: "Electric",
  },
];

const contractors: Contractor[] = [
  {
    id: "383fbe30-2eef-441f-898e-b07f8c53bb68",
    name: "Kiewit Power",
  },
  {
    id: "841b37e4-f9ac-42a1-b273-ce0c7eed6678",
    name: "Kiewit Energy Group Inc. And Subsidiaries",
  },
];

const Template: ComponentStory<typeof PortfolioFilters> = args => (
  <PortfolioFilters {...args} />
);

export const Playground = Template.bind({});
Playground.args = {
  projects,
  projectStatuses: projectStatusOptions(),
  regions,
  divisions,
  contractors,
};
