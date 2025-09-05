import type { GraphQLClient } from "graphql-request";
import type { TaskEither } from "fp-ts/lib/TaskEither";
import type { Option } from "fp-ts/lib/Option";
import type {
  Ebo,
  EboId,
  Hazard,
  Incident,
  LibraryTaskId,
  SavedEboInfo,
  CrewMember,
} from "../codecs";
import type {
  EnergyBasedObservationInput,
  HazardsLibraryQueryVariables,
  QueryTenantLinkedHazardsLibraryArgs,
  Sdk,
} from "../generated/types";
import type { ApiError } from "../api";
import * as O from "fp-ts/lib/Option";
import * as t from "io-ts";
import { constUndefined, identity, pipe } from "fp-ts/function";
import { makeRequest } from "../api";
import { getSdk } from "../generated/types";
import {
  eboCodec,
  hazardResultCodec,
  incidentDataCodec,
  savedEboInfoCodec,
  crewMemberCodec,
  hazardApplicabilityLevelsCodec,
  hazardControlCodec,
} from "../codecs";

const eboDataCodec = t.type({
  energyBasedObservation: eboCodec,
});

const saveEboResultCodec = t.type({
  saveEnergyBasedObservation: savedEboInfoCodec,
});

const completeEboResultCodec = t.type({
  completeEnergyBasedObservation: savedEboInfoCodec,
});

const reopenEboResultCodec = t.type({
  reopenEnergyBasedObservation: savedEboInfoCodec,
});

export const getEbo =
  (sdk: Sdk) =>
  (id: EboId): TaskEither<ApiError, Ebo> =>
    makeRequest(
      sdk.Ebo,
      { id },
      eboDataCodec.decode,
      res => res.energyBasedObservation
    );

export const saveEbo =
  (sdk: Sdk) =>
  (id: Option<EboId>) =>
  (input: EnergyBasedObservationInput): TaskEither<ApiError, SavedEboInfo> =>
    makeRequest(
      sdk.SaveEbo,
      {
        energyBasedObservationInput: input,
        id: pipe(id, O.getOrElseW(constUndefined)),
      },
      saveEboResultCodec.decode,
      res => res.saveEnergyBasedObservation
    );

export const completeEbo =
  (sdk: Sdk) =>
  (id: EboId) =>
  (input: EnergyBasedObservationInput): TaskEither<ApiError, SavedEboInfo> =>
    makeRequest(
      sdk.CompleteEbo,
      { id, energyBasedObservationInput: input },
      completeEboResultCodec.decode,
      res => res.completeEnergyBasedObservation
    );

export const reopenEbo =
  (sdk: Sdk) =>
  (id: EboId): TaskEither<ApiError, SavedEboInfo> =>
    makeRequest(
      sdk.ReopenEbo,
      { id },
      reopenEboResultCodec.decode,
      res => res.reopenEnergyBasedObservation
    );

export const deleteEbo =
  (sdk: Sdk) =>
  (id: EboId): TaskEither<ApiError, boolean> =>
    makeRequest(
      sdk.DeleteEbo,
      { id },
      res => t.success(res.deleteEnergyBasedObservation),
      identity
    );

export const getHazardsLibrary =
  (sdk: Sdk) =>
  (query: HazardsLibraryQueryVariables): TaskEither<ApiError, Hazard[]> =>
    makeRequest(
      sdk.HazardsLibrary,
      query,
      hazardResultCodec.decode,
      res => res.hazardsLibrary
    );

const linkedLibraryHazardCodec = t.type({
  id: t.string,
  name: t.string,
  isApplicable: t.boolean,
  energyLevel: t.union([t.string, t.null]),
  energyType: t.union([t.string, t.null]),
  imageUrl: t.string,
  taskApplicabilityLevels: t.union([
    t.array(hazardApplicabilityLevelsCodec),
    t.undefined,
  ]),
  controls: t.array(hazardControlCodec),
});

const linkedLibraryHazardResultCodec = t.type({
  tenantLinkedHazardsLibrary: t.array(linkedLibraryHazardCodec),
});

export const getTenantLinkedHazardsLibrary =
  (sdk: Sdk) =>
  (
    query: QueryTenantLinkedHazardsLibraryArgs
  ): TaskEither<ApiError, Hazard[]> =>
    makeRequest(
      sdk.TenantLinkedHazardsLibrary,
      query,
      linkedLibraryHazardResultCodec.decode,
      res => {
        return res.tenantLinkedHazardsLibrary.map(hazard => {
          return {
            id: hazard.id as any,
            name: hazard.name,
            isApplicable: hazard.isApplicable,
            controls: hazard.controls,
            energyType: O.fromNullable(hazard.energyType as any),
            energyLevel: O.fromNullable(hazard.energyLevel as any),
            taskApplicabilityLevels: hazard.taskApplicabilityLevels || [],
            imageUrl: O.some(hazard.imageUrl),
            archivedAt: O.none,
          };
        });
      }
    );

export const getHistoricalIncidents =
  (sdk: Sdk) =>
  (id: LibraryTaskId): TaskEither<ApiError, Incident[]> =>
    makeRequest(
      sdk.HistoricalIncidents,
      { libraryTaskId: id },
      incidentDataCodec.decode,
      res => res.historicalIncidents
    );

// TODO: upon backend change sdk.CrewLeaders endpoint and its return object type will also change
export const getCrewMembers = (sdk: Sdk): TaskEither<ApiError, CrewMember[]> =>
  makeRequest(
    sdk.CrewLeaders,
    undefined,
    t.type({ crewLeaders: t.array(crewMemberCodec) }).decode,
    res => res.crewLeaders
  );

export interface EboApi {
  getEbo: (id: EboId) => TaskEither<ApiError, Ebo>;
  saveEbo: (
    id: Option<EboId>
  ) => (
    input: EnergyBasedObservationInput
  ) => TaskEither<ApiError, SavedEboInfo>;
  reopenEbo: (id: EboId) => TaskEither<ApiError, SavedEboInfo>;
  completeEbo: (
    id: EboId
  ) => (
    input: EnergyBasedObservationInput
  ) => TaskEither<ApiError, SavedEboInfo>;
  deleteEbo: (id: EboId) => TaskEither<ApiError, boolean>;
  getHistoricalIncidents: (
    id: LibraryTaskId
  ) => TaskEither<ApiError, Incident[]>;
  getTenantLinkedHazardsLibrary: (
    query: QueryTenantLinkedHazardsLibraryArgs
  ) => TaskEither<ApiError, Hazard[]>;
  getCrewMembers: TaskEither<ApiError, CrewMember[]>;
}

export const eboApi = (c: GraphQLClient) => ({
  getEbo: getEbo(getSdk(c)),
  saveEbo: saveEbo(getSdk(c)),
  completeEbo: completeEbo(getSdk(c)),
  reopenEbo: reopenEbo(getSdk(c)),
  deleteEbo: deleteEbo(getSdk(c)),
  getHistoricalIncidents: getHistoricalIncidents(getSdk(c)),
  getTenantLinkedHazardsLibrary: getTenantLinkedHazardsLibrary(getSdk(c)),
  getCrewMembers: getCrewMembers(getSdk(c)),
});
