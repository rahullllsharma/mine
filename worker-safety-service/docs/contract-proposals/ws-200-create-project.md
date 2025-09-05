---
author: Aaron Trachtman
---

# Create Project

<https://urbint.atlassian.net/browse/WS-200>

# Types

## ProjectType

``` graphql
type ProjectType {
  id: ID
  name: String!
  riskLevel: RiskLevel
  startDate: Date!
  endDate: Date!
  locations(projectLocationId:ID): [ProjectLocation]

  # New field
  status: ProjectStatus
}
```

## ProjectLocationInput

``` graphql
input ProjectLocationInput {
  name: str!
  latitude: str!
  longitude: str!
}
```

## CreateProjectInput

``` graphql
input CreateProjectInput {
  name: str!
  startDate: Date!
  endDate: Date!
  status: ProjectStatus!
  locations: [ProjectLocationInput]
}
```

## ProjectStatus enum

``` graphql
enum ProjectStatus {
  PENDING
  ACTIVE
  COMPLETED
}
```

# Interfaces

N/A

# Queries

N/A

# Mutations

## Definition

``` graphql
type mutation {
  createProject(project: CreateProjectInput!): ProjectType
}
```

## Example Mutations

### Create Project and return its properties

``` graphql
mutation CreateProjectExample($project: CreateProjectInput!){
  createProject(project: $project){
    id
    name
    startDate
    endDate
    status
  }
}

{
  "project": {
    "name": "My fun example project",
    "startDate": "2021-12-06",
    "endDate": "2022-01-01",
    "status": "PENDING"
  }
}
```

### Create Project with locations

``` graphql
mutation CreateProjectWithLocations($project: CreateProjectInput!){
  createProject(project: $project){
    id
    name
    startDate
    endDate
    status
  }
}

{
  "project": {
    "name": "My fun example project",
    "startDate": "2021-12-06",
    "endDate": "2022-01-01",
    "status": "PENDING",
    "locations": [{
        "name": "the beginning",
        "latitude": "40.7831N",
        "logitude": "73.9712W"
      }]
  }
}
```
