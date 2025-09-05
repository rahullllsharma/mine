export const sampleDates = {
  startDate: "2022-01-29",
  endDate: "2022-02-03",
};

export const samplePortfolioFilters = {
  ...sampleDates,
  projectIds: [],
  projectStatuses: [],
  regionIds: [],
  divisionIds: [],
  contractorIds: [],
};

export const samplePortfolioFiltersDesc = [
  {
    "Project Name": "name",
    "Project number": "123",
  },
];

const projectId = "7114445f-966a-42e2-aa3b-0e4d5365075d";

export const sampleProjectFilters = {
  ...sampleDates,
  projectId: projectId,
  locationIds: [],
};

export const sampleProjectFiltersDesc = [
  {
    "Start date": "2022/02/02",
  },
];
