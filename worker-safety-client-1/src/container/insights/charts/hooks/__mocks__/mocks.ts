import type { FiltersDescriptionsParams } from "../useFiltersDescriptions";

type Descriptions = FiltersDescriptionsParams["descriptions"];

export const descriptions = {
  projectStatusOptions: [
    {
      id: "1",
      name: "Active",
    },
    {
      id: "2",
      name: "Pending",
    },
    {
      id: "3",
      name: "Inactive",
    },
  ],
  projects: [
    {
      id: "1",
      name: "project #1",
      externalKey: 123,
      number: 123,
      locations: [
        {
          id: "1",
          name: "location #1",
        },
        {
          id: "2",
          name: "location #2",
        },
      ],
    },
    {
      id: "2",
      name: "project #2",
      externalKey: 456,
      number: 456,
      locations: [
        {
          id: "3",
          name: "location #3",
        },
        {
          id: "4",
          name: "location #4",
        },
      ],
    },
  ],
  regions: [
    {
      id: "1",
      name: "region #1",
    },
    {
      id: "2",
      name: "region #2",
    },
    {
      id: "3",
      name: "region #3",
    },
  ],
  divisions: [
    {
      id: "1",
      name: "division #1",
    },
    {
      id: "2",
      name: "division #2",
    },
  ],
  contractors: [
    {
      id: "1",
      name: "contractor #1",
    },
    {
      id: "2",
      name: "contractor #2",
    },
    {
      id: "3",
      name: "contractor #3",
    },
    {
      id: "4",
      name: "contractor #4",
    },
  ],
} as unknown as Descriptions;
