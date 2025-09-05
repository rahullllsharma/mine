export const querySimpleMe = "{ me { id } }";

export const queryPermissions = `query Permissions {
  me {
    id
    name
    role
    permissions
    tenant {
      name
      configurations {
        entities {
          defaultLabel
          defaultLabelPlural
          key
          label
          labelPlural
          attributes {
            defaultLabel
            defaultLabelPlural
            key
            label
            labelPlural
            mandatory
            mappings
            visible
            required
            filterable
          }
        }
      }
    }
  }
}`;

export const queryGetProjects = `query getProjectIds ($search: String) {
  projects (search: $search){
    id
    name
  }
}`;

export const queryGetManagers = `query Managers {
  managers {
    id
    name
  }
}`;

export const queryGetSupervisors = `query Supervisors {
  supervisors {
    id
    firstName
    lastName
  }
}`;

export const queryGetContractors = `query Contractors {
  contractors {
    id
    name
  }
}`;

export const queryProjectTypesLibrary = `query ProjectTypesLibrary {
  projectTypesLibrary {
    id
    name
  }
}`;

export const queryDivisionsLibrary = `query DivisionsLibrary {
  divisionsLibrary {
    id
    name
  }
}`;

export const queryRegionsLibrary = `query RegionsLibrary {
  regionsLibrary {
    id
    name
  }
}`;

export const queryActivityTasks = `query ActivityTasks($orderBy: [LibraryTaskOrderBy!]) {
    tasksLibrary(orderBy: $orderBy) {
      id
      name
      category
    }
}`;

export const queryAllActivities = `query AllActivities {
  activities {
    id
    name
    tasks {
      id
      name
      libraryTask {
        id
        name
        hazards {
          id
          name
          controls {
            id
            name
          }
        }
      }
    }
  }
}`;

export const queryHazardsControlsLibrary = `query HazardsControlsLibrary($orderBy: [OrderBy!], $type: LibraryFilterType!) {
    hazardsLibrary(type: $type, orderBy: $orderBy) {
      id
      name
      isApplicable
      controls(orderBy: $orderBy) {
        id
        name
        isApplicable
      }
    }
    controlsLibrary(type: $type, orderBy: $orderBy) {
      id
      name
      isApplicable
    }
}`;

export const queryGetTasksLibrary = `query TasksLibrary {
  tasksLibrary {
    id
    name
    hazards {
      id
      name
      controls {
        id
        name
      }
    }
  }
}`;

export const queryGetHazardsLibrary = `query HazardsLibrary($libraryTaskId: UUID, $type: LibraryFilterType!) {
  hazardsLibrary(libraryTaskId: $libraryTaskId, type: $type) {
    id
    name
  }
}`;

export const queryGetControlsLibrary = `query ControlsLibrary($type: LibraryFilterType!, $libraryHazardId: UUID) {
  controlsLibrary(type: $type, libraryHazardId: $libraryHazardId) {
    id
    name
  }
}`;
