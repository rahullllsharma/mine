import type { LibraryDivision } from "@/types/project/LibraryDivision";
import type { LibraryProjectType } from "@/types/project/LibraryProjectType";
import type { LibraryRegion } from "@/types/project/LibraryRegion";
import type { ComponentMeta, ComponentStory } from "@storybook/react";
import type { User } from "@/types/User";
import MapFilters from "./MapFilters";

export default {
  title: "Components/Map/Filters/MapFilters",
  component: MapFilters,
  decorators: [
    Story => (
      <div className="w-full md:w-[300px] h-[500px] py-3 shadow-20 overflow-y-auto">
        <Story />
      </div>
    ),
  ],
} as ComponentMeta<typeof MapFilters>;

const projectTypesLibrary: LibraryProjectType[] = [
  {
    id: "e457127f-cf50-4ef1-a245-f2372be79564",
    name: "LNG/CNG",
  },
  {
    id: "23c6273d-1843-4975-8b1c-7764db536bbd",
    name: "Distribution",
  },
  {
    id: "00d803b2-b928-4ba2-8c60-b46b222c7d77",
    name: "Lining",
  },
  {
    id: "723ee7a6-258d-4b2a-a694-9f836d4e25e4",
    name: "Reg Stations / Heaters",
  },
  {
    id: "02099c38-4654-45e8-9b4c-1b19bfadc24f",
    name: "Transmission",
  },
  {
    id: "3ca5a15e-f5b3-4e7f-ab94-52c8e6512a26",
    name: "Facilities",
  },
  {
    id: "ff7929dd-fee1-4941-90a0-3e6fbfd684db",
    name: "Other",
  },
];

const divisionsLibrary: LibraryDivision[] = [
  {
    id: "26188e20-01bc-4afe-80c1-2e9d0ad1a341",
    name: "Gas",
  },
  {
    id: "9f86e0d2-de57-43a7-bcda-53c18029708e",
    name: "Electric",
  },
];

const regionsLibrary: LibraryRegion[] = [
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

const supervisors: User[] = [
  { id: "1", name: "El" },
  { id: "2", name: "Barto" },
  { id: "3", name: "Barney Gumble" },
  { id: "4", name: "Moe Szyslak" },
];

const contractors: User[] = [
  {
    id: "383fbe30-2eef-441f-898e-b07f8c53bb68",
    name: "Kiewit Power",
  },
  {
    id: "841b37e4-f9ac-42a1-b273-ce0c7eed6678",
    name: "Kiewit Energy Group Inc. And Subsidiaries",
  },
];

const Template: ComponentStory<typeof MapFilters> = args => {
  return <MapFilters {...args} />;
};

export const Playground = Template.bind({});
Playground.args = {
  projectTypesLibrary,
  divisionsLibrary,
  regionsLibrary,
  supervisors,
  contractors,
  isOpen: true,
};
