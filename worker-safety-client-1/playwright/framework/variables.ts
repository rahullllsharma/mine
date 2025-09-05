// Variables used for queries
export const queryHazardsControlsLibraryVars = {
  type: "TASK",
  orderBy: [
    {
      field: "NAME",
      direction: "ASC",
    },
  ],
};

export const queryGetProjectsVars = (
  searchText: string
): Record<string, string> => ({
  search: searchText,
});

export const queryGetHazardsLibraryVars = (
  libraryTaskId: string,
  libraryFilterType: string
): Record<string, string> => ({
  libraryTaskId: libraryTaskId,
  type: libraryFilterType,
});

export const queryGetControlsLibraryVars = (
  libraryHazardId: string,
  libraryFilterType: string
): Record<string, string> => ({
  libraryHazardId: libraryHazardId,
  type: libraryFilterType,
});

// Variables used for mutations

export const mutationDeleteProjectVars = (
  id: string
): Record<string, string> => ({
  deleteProjectId: id,
});

export const mutationCreateProjectVars = {
  project: {
    name: "Automation API dummy project",
    externalKey: "73197",
    libraryProjectTypeId: "0b982026-69f5-44dc-99f1-0c3cb0176a15",
    status: "ACTIVE",
    startDate: "2015-08-12",
    endDate: "2029-03-26",
    libraryDivisionId: "8cc132b0-33e1-4541-b5b8-1fccc85a797c",
    libraryRegionId: "6bf37c9c-0f5f-4b4e-997f-beb3f5329db4",
    managerId: "e5e29a81-a66a-4332-9a78-1169a7f3c8d0",
    supervisorId: "ca2dd5aa-ba00-4580-b713-c90e7aef07d7",
    contractorId: "98eb14a1-d924-4ce1-b4fe-e5ae1fae9600",
    locations: [
      {
        name: "7574 Morar Throughway",
        latitude: "89.6696",
        longitude: "-70.1492",
        supervisorId: "ca2dd5aa-ba00-4580-b713-c90e7aef07d7",
      },
    ],
  },
};

export const mutationCreateActivityVars = {
  activityData: {
    startDate: "2022-10-07",
    locationId: "a6282c70-03f8-49bc-8506-fbaaf2df6255",
    name: "Commissioning of facility",
    endDate: "2022-10-07",
    status: "NOT_STARTED",
    tasks: [
      {
        hazards: [
          {
            libraryHazardId: "23b011d4-4cb2-4526-9761-e247d506557a",
            isApplicable: true,
            controls: [
              {
                libraryControlId: "d8251088-33df-44b9-8286-3e11d80645d1",
                isApplicable: true,
              },
            ],
          },
          {
            libraryHazardId: "98c1f174-ca8d-4c5a-98d7-827ebfc2a1c8",
            isApplicable: true,
            controls: [
              {
                libraryControlId: "ff161bca-e057-4045-a3fe-708b6569ab8a",
                isApplicable: true,
              },
              {
                libraryControlId: "53a4afff-cfd5-4b30-89af-3d875f62722a",
                isApplicable: true,
              },
            ],
          },
          {
            libraryHazardId: "ab2071b5-e299-454a-adf0-f42ac141c936",
            isApplicable: true,
            controls: [
              {
                libraryControlId: "ff161bca-e057-4045-a3fe-708b6569ab8a",
                isApplicable: true,
              },
            ],
          },
          {
            libraryHazardId: "be591329-a272-4e0f-8277-98df369fc821",
            isApplicable: true,
            controls: [
              {
                libraryControlId: "359a02e2-7330-4175-a5b6-ef918e7d4158",
                isApplicable: true,
              },
            ],
          },
        ],
        libraryTaskId: "3fc9c105-f594-41be-9f24-c5c74cb495ad",
      },
    ],
  },
};

export const mutationCreateProjectVarsTyped = (
  name: string,
  externalKey: string,
  libraryProjectTypeId: string,
  status: string,
  startDate: string,
  endDate: string,
  libraryDivisionId: string,
  libraryRegionId: string,
  managerId: string,
  supervisorId: string,
  contractorId: string,
  locationName: string,
  latitude: string,
  longitude: string
): Record<string, any> => ({
  project: {
    name,
    externalKey,
    libraryProjectTypeId,
    status,
    startDate,
    endDate,
    libraryDivisionId,
    libraryRegionId,
    managerId,
    supervisorId,
    contractorId,
    locations: [
      {
        name: locationName,
        latitude,
        longitude,
        supervisorId,
      },
    ],
  },
});

export const mutationCreateActivityVarsTyped = (
  startDate: string,
  locationId: string,
  name: string,
  endDate: string,
  status: string,
  libraryTaskId: string,
  libraryHazardId: string,
  libraryControlId: string
): any => ({
  activityData: {
    startDate,
    locationId,
    name,
    endDate,
    status,
    tasks: [
      {
        hazards: [
          {
            libraryHazardId,
            isApplicable: true,
            controls: [
              {
                libraryControlId,
                isApplicable: true,
              },
            ],
          },
        ],
        libraryTaskId,
      },
    ],
  },
});

export const mutationCreateActivitySeedTenTasksVarsTyped = (
  startDate: string,
  locationId: string,
  name: string,
  endDate: string,
  status: string,
  seedTasks: any
): any => ({
  activityData: {
    startDate,
    locationId,
    name,
    endDate,
    status,
    tasks: seedTasks,
  },
});
