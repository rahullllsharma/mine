---
author: Aaron Trachtman
---

# Project Daily Summary View

<https://urbint.atlassian.net/browse/WS-152>

# Types

## Notes

-   Strawberry `Date` scalar type follows ISO-8601
    (<https://strawberry.rocks/docs/types/scalars>)

## Projects

``` graphql
type Project {
  id: ID
  name: String!
  riskLevel: RiskLevel
  startDate: Date!
  endDate: Date!
  locations(projectLocationId:ID): [ProjectLocation]
}
```

-   if `projectLocationId` is omitted, all project locations are
    returned

## Project Locations

``` graphql
type ProjectLocation {
  id: ID
  name: String!
  siteConditions(date: Date!): [SiteCondition]
  tasks(date: Date!): [Task]
}
```

-   This has `siteConditions` and `tasks` being specific to a day but
    how that works is not yet fully defined by product (\<2021-11-15
    Mon>)

## Site Conditions

``` graphql
type SiteCondition {
  id: ID
  name: String!
  riskLevel: RiskLevel
  hazards: [Hazard]
}
```

## Tasks

``` graphql
type Task {
  id: ID
  name: String!
  riskLevel: RiskLevel
  hazards: [Hazard]
}
```

## Hazards

``` graphql
type Hazard {
  id: ID
  name: String!
  controls: [Control]
}
```

## Controls

``` graphql
type Control {
  id: ID
  name: String!
  status: ControlStatus!
}
```

## ControlStatus

``` graphql
enum ControlStatus {
  IMPLEMENTED
  NOT_IMPLEMENTED
  NOT_APPLICABLE
}
```

## RiskLevel

``` graphql
enum RiskLevel {
  HIGH
  MEDIUM
  LOW
}
```

# Interfaces

No interfaces at this time. They may be useful in the future,
specifically around site conditions and tasks.

# Queries

## Definition

``` graphql
type query {

  # Get the details of a specific project
  project(id: ID!): Project

  # Get site conditions for a project location on a specific day
  siteConditions(projectLocationId: ID!, date: Date!): [SiteCondition]

  # Get tasks for a project location on a specific day
  tasks(projectLocationId: ID!, date: Date!): [Task]
}
```

## Sample Queries

### Full project query

``` graphql
query project {
  project(id:123){
    name
    riskScore
    locations {
      id
      name
      siteConditions(date: "2022-01-01"): { # could use fragments here
        name
        riskLevel
        hazards {
          name
          controls {
            name
            status
          }
        }
      }
      tasks(date: "2022-01-01"): {
        name
        riskLevel
        hazards {
          name
          controls {
            name
            status
          }
        }
      }
    }
  }
}
```

### Get a project and its locations

``` graphql
query project(id: 123) {
  id
  name
  riskLevel
  locations {
    id
    name
  }
}
```

### Get site conditions and their hazards for a specific day

``` graphql
query siteConditions(projectLocationId: 123, date: "2022-01-01") {
  id
  name
  riskLevel
  hazards {
    id
    name
  }
}
```

### Get a project and its tasks and their hazards and controls for a location on a day

``` graphql
query project(id:123){
  id
  name
  locations(projectLocationId:456) {
    tasks(date: "2022-01-01") {
      name
      hazards {
        name
        controls {
          name
          status
        }
      }

    }
  }
}
```

# Mutations

N/A
