import type { ActivityInputs } from "@/container/activity/addActivityModal/AddActivityModal";
import type { Control } from "@/types/project/Control";
import type { Hazard } from "@/types/project/Hazard";
import type { TaskHazardAggregator } from "@/types/project/HazardAggregator";
import type { TaskSelectionInputs } from "@/types/report/DailyReportInputs";
import type { SiteConditionData } from "@/types/siteCondition/SiteConditionData";
import type { SiteConditionInputs } from "@/types/siteCondition/SiteConditionInputs";
import type { LocationHazardControlSettings } from "@/types/task/TaskData";
import { RiskLevel } from "@/components/riskBadge/RiskLevel";
import { TaskStatus } from "@/types/task/TaskStatus";
import {
  applyLocationHazardControlSettings,
  buildSiteConditionData,
  excludeRecommendedControls,
  excludeRecommendedHazards,
  getFormHazards,
  getLocationHazardControlSettingChanges,
  isTaskComplete,
  transformTasksToListTasks,
} from "./task.utils";

describe("task helper", () => {
  describe("when getFormHazards is called", () => {
    describe("when we add a task", () => {
      const hazards = [
        {
          controls: [
            {
              id: "c0c5d686-b373-48f8-9275-299b4c88b17c",
              isApplicable: true,
              name: "Gloves",
              key: "c0c5d686-b373-48f8-9275-299b4c88b17c",
            },
            {
              id: "6f861d56-fe24-413d-89d1-3a3eed715e6c",
              isApplicable: true,
              name: "situational jobsite awareness",
              key: "6f861d56-fe24-413d-89d1-3a3eed715e6c",
            },
          ],
          id: "ec4c82da-0923-4040-b142-b693bf382d1a",
          isApplicable: true,
          name: "Pinch point",
          key: "ec4c82da-0923-4040-b142-b693bf382d1a",
        },
      ];
      const expectedFormHazards = {
        "ec4c82da-0923-4040-b142-b693bf382d1a": {
          controls: {
            "c0c5d686-b373-48f8-9275-299b4c88b17c": {
              libraryControlId: "c0c5d686-b373-48f8-9275-299b4c88b17c",
              isApplicable: true,
            },
            "6f861d56-fe24-413d-89d1-3a3eed715e6c": {
              libraryControlId: "6f861d56-fe24-413d-89d1-3a3eed715e6c",
              isApplicable: true,
            },
          },
          libraryHazardId: "ec4c82da-0923-4040-b142-b693bf382d1a",
          isApplicable: true,
        },
      };

      it("should format the hazards and controls for the form", () => {
        expect(getFormHazards(hazards)).toStrictEqual(expectedFormHazards);
      });
    });

    describe("when we edit a task", () => {
      const hazards = [
        {
          id: "c1ff365a-0fdb-43a4-8d41-9b3d8e25b3ef",
          isApplicable: true,
          name: "Caught in between bevel machine",
          libraryHazard: {
            id: "12da934f-0077-40cc-823d-10956ff8954a",
          },
          controls: [
            {
              name: "Situational jobsite awareness",
              isApplicable: true,
              id: "15d6a4d0-1a16-4055-94c2-d455c70eac73",
              libraryControl: {
                id: "7921b1cb-2b96-4e55-a67f-0f22af0e95cf",
              },
              key: "15d6a4d0-1a16-4055-94c2-d455c70eac73",
            },
          ],
          key: "c1ff365a-0fdb-43a4-8d41-9b3d8e25b3ef",
        },
      ];

      const expectedFormHazards = {
        "c1ff365a-0fdb-43a4-8d41-9b3d8e25b3ef": {
          controls: {
            "15d6a4d0-1a16-4055-94c2-d455c70eac73": {
              libraryControlId: "7921b1cb-2b96-4e55-a67f-0f22af0e95cf",
              isApplicable: true,
              id: "15d6a4d0-1a16-4055-94c2-d455c70eac73",
            },
          },
          libraryHazardId: "12da934f-0077-40cc-823d-10956ff8954a",
          isApplicable: true,
          id: "c1ff365a-0fdb-43a4-8d41-9b3d8e25b3ef",
        },
      };

      it("should format the hazards and controls for the form", () => {
        expect(getFormHazards(hazards)).toStrictEqual(expectedFormHazards);
      });
    });
  });

  // TODO: https://urbint.atlassian.net/browse/WSAPP-1268
  // Re-enable these tests ASAP
  // xdescribe("when buildTaskData is called", () => {
  //   const taskStatus = TaskStatus.NOT_STARTED;

  //   describe("when we add a task", () => {
  //     it("should return the task payload formatted for the mutation", () => {
  //       const addTaskInputs: TaskInputs = {
  //         startDate: "2022-01-21",
  //         endDate: "2022-01-22",
  //         libraryTaskId: "7a91aaf5-b54f-4586-ab38-66d0bb3b22bd",
  //         status: { id: taskStatus, name: taskStatus },
  //         hazards: {
  //           "ec4c82da-0923-4040-b142-b693bf382d1a": {
  //             libraryHazardId: "ec4c82da-0923-4040-b142-b693bf382d1a",
  //             isApplicable: true,
  //             controls: {
  //               "c0c5d686-b373-48f8-9275-299b4c88b17c": {
  //                 libraryControlId: "c0c5d686-b373-48f8-9275-299b4c88b17c",
  //                 isApplicable: false,
  //               },
  //               "6f861d56-fe24-413d-89d1-3a3eed715e6c": {
  //                 libraryControlId: "6f861d56-fe24-413d-89d1-3a3eed715e6c",
  //                 isApplicable: true,
  //               },
  //               "7921b1cb-2b96-4e55-a67f-0f22af0e95cf": {
  //                 libraryControlId: "7921b1cb-2b96-4e55-a67f-0f22af0e95cf",
  //                 isApplicable: true,
  //               },
  //               "c614eddc-4066-4771-b176-e69c67c6d4ac": {
  //                 libraryControlId: "c614eddc-4066-4771-b176-e69c67c6d4ac",
  //                 isApplicable: true,
  //               },
  //             },
  //           },
  //           "37731c12-55bf-4120-8c2c-57dcf0b8ecd2": {
  //             libraryHazardId: "37731c12-55bf-4120-8c2c-57dcf0b8ecd2",
  //             isApplicable: false,
  //             controls: {
  //               "7921b1cb-2b96-4e55-a67f-0f22af0e95cf": {
  //                 libraryControlId: "7921b1cb-2b96-4e55-a67f-0f22af0e95cf",
  //                 isApplicable: false,
  //               },
  //             },
  //           },
  //         },
  //       };

  //       const expectedTaskData: TaskData = {
  //         startDate: "2022-01-21",
  //         endDate: "2022-01-22",
  //         libraryTaskId: "7a91aaf5-b54f-4586-ab38-66d0bb3b22bd",
  //         status: taskStatus.toUpperCase(),
  //         hazards: [
  //           {
  //             libraryHazardId: "ec4c82da-0923-4040-b142-b693bf382d1a",
  //             isApplicable: true,
  //             controls: [
  //               {
  //                 libraryControlId: "c0c5d686-b373-48f8-9275-299b4c88b17c",
  //                 isApplicable: false,
  //               },
  //               {
  //                 libraryControlId: "6f861d56-fe24-413d-89d1-3a3eed715e6c",
  //                 isApplicable: true,
  //               },
  //               {
  //                 libraryControlId: "7921b1cb-2b96-4e55-a67f-0f22af0e95cf",
  //                 isApplicable: true,
  //               },
  //               {
  //                 libraryControlId: "c614eddc-4066-4771-b176-e69c67c6d4ac",
  //                 isApplicable: true,
  //               },
  //             ],
  //           },
  //           {
  //             libraryHazardId: "37731c12-55bf-4120-8c2c-57dcf0b8ecd2",
  //             isApplicable: false,
  //             controls: [
  //               {
  //                 libraryControlId: "7921b1cb-2b96-4e55-a67f-0f22af0e95cf",
  //                 isApplicable: false,
  //               },
  //             ],
  //           },
  //         ],
  //       };

  //       expect(buildTaskData(addTaskInputs)).toStrictEqual(expectedTaskData);
  //     });

  //     describe("when we have manually added control", () => {
  //       it("should return the task payload formatted for the mutation", () => {
  //         const addTaskInputsWithManualControl: TaskInputs = {
  //           startDate: "2022-01-21",
  //           endDate: "2022-01-22",
  //           libraryTaskId: "7a91aaf5-b54f-4586-ab38-66d0bb3b22bd",
  //           status: { id: taskStatus, name: taskStatus },
  //           hazards: {
  //             "ec4c82da-0923-4040-b142-b693bf382d1a": {
  //               libraryHazardId: "ec4c82da-0923-4040-b142-b693bf382d1a",
  //               isApplicable: true,
  //               controls: {
  //                 "c0c5d686-b373-48f8-9275-299b4c88b17c": {
  //                   libraryControlId: "c0c5d686-b373-48f8-9275-299b4c88b17c",
  //                   isApplicable: false,
  //                 },
  //                 "6f861d56-fe24-413d-89d1-3a3eed715e6c": {
  //                   libraryControlId: "6f861d56-fe24-413d-89d1-3a3eed715e6c",
  //                   isApplicable: true,
  //                 },
  //                 "7921b1cb-2b96-4e55-a67f-0f22af0e95cf": {
  //                   libraryControlId: "7921b1cb-2b96-4e55-a67f-0f22af0e95cf",
  //                   isApplicable: true,
  //                 },
  //                 "c614eddc-4066-4771-b176-e69c67c6d4ac": {
  //                   libraryControlId: "c614eddc-4066-4771-b176-e69c67c6d4ac",
  //                   isApplicable: true,
  //                 },
  //                 Wnodct4pOOahA1bWTMfC8: {
  //                   libraryControlId: "8aac579e-b59c-4252-8939-c799b7f9166d",
  //                   isApplicable: true,
  //                 },
  //               },
  //             },
  //             "37731c12-55bf-4120-8c2c-57dcf0b8ecd2": {
  //               libraryHazardId: "37731c12-55bf-4120-8c2c-57dcf0b8ecd2",
  //               isApplicable: false,
  //               controls: {
  //                 "7921b1cb-2b96-4e55-a67f-0f22af0e95cf": {
  //                   libraryControlId: "7921b1cb-2b96-4e55-a67f-0f22af0e95cf",
  //                   isApplicable: false,
  //                 },
  //               },
  //             },
  //           },
  //         };

  //         const expectedTaskData: TaskData = {
  //           startDate: "2022-01-21",
  //           endDate: "2022-01-22",
  //           libraryTaskId: "7a91aaf5-b54f-4586-ab38-66d0bb3b22bd",
  //           status: taskStatus.toUpperCase(),
  //           hazards: [
  //             {
  //               libraryHazardId: "ec4c82da-0923-4040-b142-b693bf382d1a",
  //               isApplicable: true,
  //               controls: [
  //                 {
  //                   libraryControlId: "c0c5d686-b373-48f8-9275-299b4c88b17c",
  //                   isApplicable: false,
  //                 },
  //                 {
  //                   libraryControlId: "6f861d56-fe24-413d-89d1-3a3eed715e6c",
  //                   isApplicable: true,
  //                 },
  //                 {
  //                   libraryControlId: "7921b1cb-2b96-4e55-a67f-0f22af0e95cf",
  //                   isApplicable: true,
  //                 },
  //                 {
  //                   libraryControlId: "c614eddc-4066-4771-b176-e69c67c6d4ac",
  //                   isApplicable: true,
  //                 },
  //                 {
  //                   libraryControlId: "8aac579e-b59c-4252-8939-c799b7f9166d",
  //                   isApplicable: true,
  //                 },
  //               ],
  //             },
  //             {
  //               libraryHazardId: "37731c12-55bf-4120-8c2c-57dcf0b8ecd2",
  //               isApplicable: false,
  //               controls: [
  //                 {
  //                   libraryControlId: "7921b1cb-2b96-4e55-a67f-0f22af0e95cf",
  //                   isApplicable: false,
  //                 },
  //               ],
  //             },
  //           ],
  //         };

  //         expect(buildTaskData(addTaskInputsWithManualControl)).toStrictEqual(
  //           expectedTaskData
  //         );
  //       });
  //     });

  //     describe("when we have manually added hazard", () => {
  //       it("should return the task payload formatted for the mutation", () => {
  //         const addTaskInputsWithManualHazard: TaskInputs = {
  //           startDate: "2022-01-21",
  //           endDate: "2022-01-22",
  //           libraryTaskId: "7a91aaf5-b54f-4586-ab38-66d0bb3b22bd",
  //           status: { id: taskStatus, name: taskStatus },
  //           hazards: {
  //             "ec4c82da-0923-4040-b142-b693bf382d1a": {
  //               libraryHazardId: "ec4c82da-0923-4040-b142-b693bf382d1a",
  //               isApplicable: true,
  //               controls: {
  //                 "c0c5d686-b373-48f8-9275-299b4c88b17c": {
  //                   libraryControlId: "c0c5d686-b373-48f8-9275-299b4c88b17c",
  //                   isApplicable: false,
  //                 },
  //                 "6f861d56-fe24-413d-89d1-3a3eed715e6c": {
  //                   libraryControlId: "6f861d56-fe24-413d-89d1-3a3eed715e6c",
  //                   isApplicable: true,
  //                 },
  //                 "7921b1cb-2b96-4e55-a67f-0f22af0e95cf": {
  //                   libraryControlId: "7921b1cb-2b96-4e55-a67f-0f22af0e95cf",
  //                   isApplicable: true,
  //                 },
  //                 "c614eddc-4066-4771-b176-e69c67c6d4ac": {
  //                   libraryControlId: "c614eddc-4066-4771-b176-e69c67c6d4ac",
  //                   isApplicable: true,
  //                 },
  //               },
  //             },
  //             "37731c12-55bf-4120-8c2c-57dcf0b8ecd2": {
  //               libraryHazardId: "37731c12-55bf-4120-8c2c-57dcf0b8ecd2",
  //               isApplicable: false,
  //               controls: {
  //                 "7921b1cb-2b96-4e55-a67f-0f22af0e95cf": {
  //                   libraryControlId: "7921b1cb-2b96-4e55-a67f-0f22af0e95cf",
  //                   isApplicable: false,
  //                 },
  //               },
  //             },
  //             "6o4RNEsAZ-ROzsm9aV6J4": {
  //               libraryHazardId: "b967e3e8-ca66-4039-91ee-688f33ac31d7",
  //               isApplicable: true,
  //             },
  //           },
  //         };

  //         const expectedTaskData: TaskData = {
  //           startDate: "2022-01-21",
  //           endDate: "2022-01-22",
  //           libraryTaskId: "7a91aaf5-b54f-4586-ab38-66d0bb3b22bd",
  //           status: taskStatus.toUpperCase(),
  //           hazards: [
  //             {
  //               libraryHazardId: "ec4c82da-0923-4040-b142-b693bf382d1a",
  //               isApplicable: true,
  //               controls: [
  //                 {
  //                   libraryControlId: "c0c5d686-b373-48f8-9275-299b4c88b17c",
  //                   isApplicable: false,
  //                 },
  //                 {
  //                   libraryControlId: "6f861d56-fe24-413d-89d1-3a3eed715e6c",
  //                   isApplicable: true,
  //                 },
  //                 {
  //                   libraryControlId: "7921b1cb-2b96-4e55-a67f-0f22af0e95cf",
  //                   isApplicable: true,
  //                 },
  //                 {
  //                   libraryControlId: "c614eddc-4066-4771-b176-e69c67c6d4ac",
  //                   isApplicable: true,
  //                 },
  //               ],
  //             },
  //             {
  //               libraryHazardId: "37731c12-55bf-4120-8c2c-57dcf0b8ecd2",
  //               isApplicable: false,
  //               controls: [
  //                 {
  //                   libraryControlId: "7921b1cb-2b96-4e55-a67f-0f22af0e95cf",
  //                   isApplicable: false,
  //                 },
  //               ],
  //             },
  //             {
  //               libraryHazardId: "b967e3e8-ca66-4039-91ee-688f33ac31d7",
  //               isApplicable: true,
  //               controls: [],
  //             },
  //           ],
  //         };

  //         expect(buildTaskData(addTaskInputsWithManualHazard)).toStrictEqual(
  //           expectedTaskData
  //         );
  //       });
  //     });
  //   });

  //   describe("when we edit a task", () => {
  //     it("should return the task payload formatted for the mutation", () => {
  //       const hazards = {
  //         "c1ff365a-0fdb-43a4-8d41-9b3d8e25b3ef": {
  //           libraryHazardId: "12da934f-0077-40cc-823d-10956ff8954a",
  //           isApplicable: true,
  //           controls: {
  //             "15d6a4d0-1a16-4055-94c2-d455c70eac73": {
  //               libraryControlId: "7921b1cb-2b96-4e55-a67f-0f22af0e95cf",
  //               isApplicable: true,
  //               id: "15d6a4d0-1a16-4055-94c2-d455c70eac73",
  //             },
  //           },
  //           id: "c1ff365a-0fdb-43a4-8d41-9b3d8e25b3ef",
  //         },
  //         "e64f5507-71b3-4103-afec-5aec95d945d9": {
  //           libraryHazardId: "d5f817c0-200a-4fc7-9738-65567b514c4c",
  //           isApplicable: true,
  //           controls: {
  //             "c294f6a5-1bb9-46e4-b10c-fe37e1d3d28a": {
  //               libraryControlId: "dfcdd14a-842f-498b-a5e9-3f7256848a1d",
  //               isApplicable: true,
  //               id: "c294f6a5-1bb9-46e4-b10c-fe37e1d3d28a",
  //             },
  //             "14f0cc61-fc2b-468e-85e9-a525271aab68": {
  //               libraryControlId: "775863d4-e06d-427c-8017-0cd33b8798d5",
  //               isApplicable: true,
  //               id: "14f0cc61-fc2b-468e-85e9-a525271aab68",
  //             },
  //             "911d6b72-7bf0-41a6-9a7a-fd1319606362": {
  //               libraryControlId: "05b74e20-5b9a-4e42-9c3f-ec6ce9cb2fe9",
  //               isApplicable: true,
  //               id: "911d6b72-7bf0-41a6-9a7a-fd1319606362",
  //             },
  //           },
  //           id: "e64f5507-71b3-4103-afec-5aec95d945d9",
  //         },
  //       };

  //       const expectTaskHazards: HazardData[] = [
  //         {
  //           id: "c1ff365a-0fdb-43a4-8d41-9b3d8e25b3ef",
  //           libraryHazardId: "12da934f-0077-40cc-823d-10956ff8954a",
  //           isApplicable: true,
  //           controls: [
  //             {
  //               libraryControlId: "7921b1cb-2b96-4e55-a67f-0f22af0e95cf",
  //               isApplicable: true,
  //               id: "15d6a4d0-1a16-4055-94c2-d455c70eac73",
  //             },
  //           ],
  //         },
  //         {
  //           libraryHazardId: "d5f817c0-200a-4fc7-9738-65567b514c4c",
  //           isApplicable: true,
  //           id: "e64f5507-71b3-4103-afec-5aec95d945d9",
  //           controls: [
  //             {
  //               libraryControlId: "dfcdd14a-842f-498b-a5e9-3f7256848a1d",
  //               isApplicable: true,
  //               id: "c294f6a5-1bb9-46e4-b10c-fe37e1d3d28a",
  //             },
  //             {
  //               libraryControlId: "775863d4-e06d-427c-8017-0cd33b8798d5",
  //               isApplicable: true,
  //               id: "14f0cc61-fc2b-468e-85e9-a525271aab68",
  //             },
  //             {
  //               libraryControlId: "05b74e20-5b9a-4e42-9c3f-ec6ce9cb2fe9",
  //               isApplicable: true,
  //               id: "911d6b72-7bf0-41a6-9a7a-fd1319606362",
  //             },
  //           ],
  //         },
  //       ];

  //       const task: TaskInputs = {
  //         startDate: "2022-01-21",
  //         endDate: "2022-01-22",
  //         libraryTaskId: "7a91aaf5-b54f-4586-ab38-66d0bb3b22bd",
  //         status: { id: taskStatus, name: taskStatus },
  //         hazards,
  //       };

  //       expect(buildTaskData(task)).toStrictEqual({
  //         ...task,
  //         status: taskStatus.toUpperCase(),
  //         hazards: expectTaskHazards,
  //       });
  //     });

  //     describe("when we have manually added control", () => {
  //       const hazards = {
  //         "c1ff365a-0fdb-43a4-8d41-9b3d8e25b3ef": {
  //           libraryHazardId: "12da934f-0077-40cc-823d-10956ff8954a",
  //           isApplicable: true,
  //           controls: {
  //             "15d6a4d0-1a16-4055-94c2-d455c70eac73": {
  //               libraryControlId: "7921b1cb-2b96-4e55-a67f-0f22af0e95cf",
  //               isApplicable: true,
  //               id: "15d6a4d0-1a16-4055-94c2-d455c70eac73",
  //             },
  //             PycM25pmf_WTjIqMYGro5: {
  //               libraryControlId: "8aac579e-b59c-4252-8939-c799b7f9166d",
  //               isApplicable: true,
  //             },
  //           },
  //           id: "c1ff365a-0fdb-43a4-8d41-9b3d8e25b3ef",
  //         },
  //         "e64f5507-71b3-4103-afec-5aec95d945d9": {
  //           libraryHazardId: "d5f817c0-200a-4fc7-9738-65567b514c4c",
  //           isApplicable: true,
  //           controls: {
  //             "c294f6a5-1bb9-46e4-b10c-fe37e1d3d28a": {
  //               libraryControlId: "dfcdd14a-842f-498b-a5e9-3f7256848a1d",
  //               isApplicable: true,
  //               id: "c294f6a5-1bb9-46e4-b10c-fe37e1d3d28a",
  //             },
  //             "14f0cc61-fc2b-468e-85e9-a525271aab68": {
  //               libraryControlId: "775863d4-e06d-427c-8017-0cd33b8798d5",
  //               isApplicable: true,
  //               id: "14f0cc61-fc2b-468e-85e9-a525271aab68",
  //             },
  //             "911d6b72-7bf0-41a6-9a7a-fd1319606362": {
  //               libraryControlId: "05b74e20-5b9a-4e42-9c3f-ec6ce9cb2fe9",
  //               isApplicable: true,
  //               id: "911d6b72-7bf0-41a6-9a7a-fd1319606362",
  //             },
  //           },
  //           id: "e64f5507-71b3-4103-afec-5aec95d945d9",
  //         },
  //       };

  //       const expectTaskHazards: HazardData[] = [
  //         {
  //           id: "c1ff365a-0fdb-43a4-8d41-9b3d8e25b3ef",
  //           libraryHazardId: "12da934f-0077-40cc-823d-10956ff8954a",
  //           isApplicable: true,
  //           controls: [
  //             {
  //               libraryControlId: "7921b1cb-2b96-4e55-a67f-0f22af0e95cf",
  //               isApplicable: true,
  //               id: "15d6a4d0-1a16-4055-94c2-d455c70eac73",
  //             },
  //             {
  //               libraryControlId: "8aac579e-b59c-4252-8939-c799b7f9166d",
  //               isApplicable: true,
  //             },
  //           ],
  //         },
  //         {
  //           libraryHazardId: "d5f817c0-200a-4fc7-9738-65567b514c4c",
  //           isApplicable: true,
  //           id: "e64f5507-71b3-4103-afec-5aec95d945d9",
  //           controls: [
  //             {
  //               libraryControlId: "dfcdd14a-842f-498b-a5e9-3f7256848a1d",
  //               isApplicable: true,
  //               id: "c294f6a5-1bb9-46e4-b10c-fe37e1d3d28a",
  //             },
  //             {
  //               libraryControlId: "775863d4-e06d-427c-8017-0cd33b8798d5",
  //               isApplicable: true,
  //               id: "14f0cc61-fc2b-468e-85e9-a525271aab68",
  //             },
  //             {
  //               libraryControlId: "05b74e20-5b9a-4e42-9c3f-ec6ce9cb2fe9",
  //               isApplicable: true,
  //               id: "911d6b72-7bf0-41a6-9a7a-fd1319606362",
  //             },
  //           ],
  //         },
  //       ];

  //       const task: TaskInputs = {
  //         startDate: "2022-01-21",
  //         endDate: "2022-01-22",
  //         libraryTaskId: "7a91aaf5-b54f-4586-ab38-66d0bb3b22bd",
  //         status: { id: taskStatus, name: taskStatus },
  //         hazards,
  //       };

  //       it("should return the task payload formatted for the mutation", () => {
  //         expect(buildTaskData(task)).toStrictEqual({
  //           ...task,
  //           status: taskStatus.toUpperCase(),
  //           hazards: expectTaskHazards,
  //         });
  //       });
  //     });

  //     describe("when we have manually added hazard", () => {
  //       const hazards = {
  //         "c1ff365a-0fdb-43a4-8d41-9b3d8e25b3ef": {
  //           libraryHazardId: "12da934f-0077-40cc-823d-10956ff8954a",
  //           isApplicable: true,
  //           controls: {
  //             "15d6a4d0-1a16-4055-94c2-d455c70eac73": {
  //               libraryControlId: "7921b1cb-2b96-4e55-a67f-0f22af0e95cf",
  //               isApplicable: true,
  //               id: "15d6a4d0-1a16-4055-94c2-d455c70eac73",
  //             },
  //             PycM25pmf_WTjIqMYGro5: {
  //               libraryControlId: "8aac579e-b59c-4252-8939-c799b7f9166d",
  //               isApplicable: true,
  //             },
  //           },
  //           id: "c1ff365a-0fdb-43a4-8d41-9b3d8e25b3ef",
  //         },
  //         "e64f5507-71b3-4103-afec-5aec95d945d9": {
  //           libraryHazardId: "d5f817c0-200a-4fc7-9738-65567b514c4c",
  //           isApplicable: true,
  //           controls: {
  //             "c294f6a5-1bb9-46e4-b10c-fe37e1d3d28a": {
  //               libraryControlId: "dfcdd14a-842f-498b-a5e9-3f7256848a1d",
  //               isApplicable: true,
  //               id: "c294f6a5-1bb9-46e4-b10c-fe37e1d3d28a",
  //             },
  //             "14f0cc61-fc2b-468e-85e9-a525271aab68": {
  //               libraryControlId: "775863d4-e06d-427c-8017-0cd33b8798d5",
  //               isApplicable: true,
  //               id: "14f0cc61-fc2b-468e-85e9-a525271aab68",
  //             },
  //             "911d6b72-7bf0-41a6-9a7a-fd1319606362": {
  //               libraryControlId: "05b74e20-5b9a-4e42-9c3f-ec6ce9cb2fe9",
  //               isApplicable: true,
  //               id: "911d6b72-7bf0-41a6-9a7a-fd1319606362",
  //             },
  //           },
  //           id: "e64f5507-71b3-4103-afec-5aec95d945d9",
  //         },
  //         "tu9a0gaY7-uzc7GbS858E": {
  //           libraryHazardId: "1625a8d4-3330-4a9a-8054-f29948dde211",
  //           isApplicable: true,
  //         },
  //       };

  //       const expectTaskHazards: HazardData[] = [
  //         {
  //           id: "c1ff365a-0fdb-43a4-8d41-9b3d8e25b3ef",
  //           libraryHazardId: "12da934f-0077-40cc-823d-10956ff8954a",
  //           isApplicable: true,
  //           controls: [
  //             {
  //               libraryControlId: "7921b1cb-2b96-4e55-a67f-0f22af0e95cf",
  //               isApplicable: true,
  //               id: "15d6a4d0-1a16-4055-94c2-d455c70eac73",
  //             },
  //             {
  //               libraryControlId: "8aac579e-b59c-4252-8939-c799b7f9166d",
  //               isApplicable: true,
  //             },
  //           ],
  //         },
  //         {
  //           libraryHazardId: "d5f817c0-200a-4fc7-9738-65567b514c4c",
  //           isApplicable: true,
  //           id: "e64f5507-71b3-4103-afec-5aec95d945d9",
  //           controls: [
  //             {
  //               libraryControlId: "dfcdd14a-842f-498b-a5e9-3f7256848a1d",
  //               isApplicable: true,
  //               id: "c294f6a5-1bb9-46e4-b10c-fe37e1d3d28a",
  //             },
  //             {
  //               libraryControlId: "775863d4-e06d-427c-8017-0cd33b8798d5",
  //               isApplicable: true,
  //               id: "14f0cc61-fc2b-468e-85e9-a525271aab68",
  //             },
  //             {
  //               libraryControlId: "05b74e20-5b9a-4e42-9c3f-ec6ce9cb2fe9",
  //               isApplicable: true,
  //               id: "911d6b72-7bf0-41a6-9a7a-fd1319606362",
  //             },
  //           ],
  //         },
  //         {
  //           libraryHazardId: "1625a8d4-3330-4a9a-8054-f29948dde211",
  //           isApplicable: true,
  //           controls: [],
  //         },
  //       ];

  //       const task: TaskInputs = {
  //         startDate: "2022-01-21",
  //         endDate: "2022-01-22",
  //         libraryTaskId: "7a91aaf5-b54f-4586-ab38-66d0bb3b22bd",
  //         status: { id: taskStatus, name: taskStatus },
  //         hazards,
  //       };

  //       it("should return the task payload formatted for the mutation", () => {
  //         expect(buildTaskData(task)).toStrictEqual({
  //           ...task,
  //           status: taskStatus.toUpperCase(),
  //           hazards: expectTaskHazards,
  //         });
  //       });
  //     });
  //   });

  //   describe("when we don't have hazards", () => {
  //     const addTaskInputs: TaskInputs = {
  //       startDate: "2022-01-21",
  //       endDate: "2022-01-22",
  //       libraryTaskId: "7a91aaf5-b54f-4586-ab38-66d0bb3b22bd",
  //       status: { id: taskStatus, name: taskStatus },
  //     };

  //     const expectedTaskData: TaskData = {
  //       startDate: "2022-01-21",
  //       endDate: "2022-01-22",
  //       libraryTaskId: "7a91aaf5-b54f-4586-ab38-66d0bb3b22bd",
  //       status: taskStatus.toUpperCase(),
  //       hazards: [],
  //     };

  //     describe("when is hazards is null", () => {
  //       it("should return the task payload formatted for the mutation without hazards", () => {
  //         expect(buildTaskData(addTaskInputs)).toStrictEqual(expectedTaskData);
  //       });
  //     });

  //     describe("when is hazards is empty", () => {
  //       it("should return the task payload formatted for the mutation without hazards", () => {
  //         expect(
  //           buildTaskData({ ...addTaskInputs, hazards: {} })
  //         ).toStrictEqual(expectedTaskData);
  //       });
  //     });
  //   });

  //   describe("when we don't have controls", () => {
  //     it("should return the task payload formatted for the mutation without controls", () => {
  //       const addTaskInputs: TaskInputs = {
  //         startDate: "2022-01-21",
  //         endDate: "2022-01-22",
  //         libraryTaskId: "7a91aaf5-b54f-4586-ab38-66d0bb3b22bd",
  //         status: { id: taskStatus, name: taskStatus },
  //         hazards: {
  //           "ec4c82da-0923-4040-b142-b693bf382d1a": {
  //             libraryHazardId: "ec4c82da-0923-4040-b142-b693bf382d1a",
  //             isApplicable: true,
  //           },
  //         },
  //       };

  //       const expectedTaskData: TaskData = {
  //         startDate: "2022-01-21",
  //         endDate: "2022-01-22",
  //         libraryTaskId: "7a91aaf5-b54f-4586-ab38-66d0bb3b22bd",
  //         status: taskStatus.toUpperCase(),
  //         hazards: [
  //           {
  //             libraryHazardId: "ec4c82da-0923-4040-b142-b693bf382d1a",
  //             isApplicable: true,
  //             controls: [],
  //           },
  //         ],
  //       };

  //       expect(buildTaskData(addTaskInputs)).toStrictEqual(expectedTaskData);
  //     });
  //   });
  // });

  describe("when buildSiteConditionData is called", () => {
    it("should return the task payload formatted for the mutation", () => {
      const addSiteConditionInputs: SiteConditionInputs = {
        librarySiteConditionId: "7a91aaf5-b54f-4586-ab38-66d0bb3b22bd",
        hazards: {
          "ec4c82da-0923-4040-b142-b693bf382d1a": {
            libraryHazardId: "ec4c82da-0923-4040-b142-b693bf382d1a",
            isApplicable: true,
            controls: {
              "c0c5d686-b373-48f8-9275-299b4c88b17c": {
                libraryControlId: "c0c5d686-b373-48f8-9275-299b4c88b17c",
                isApplicable: false,
              },
              "6f861d56-fe24-413d-89d1-3a3eed715e6c": {
                libraryControlId: "6f861d56-fe24-413d-89d1-3a3eed715e6c",
                isApplicable: true,
              },
              "7921b1cb-2b96-4e55-a67f-0f22af0e95cf": {
                libraryControlId: "7921b1cb-2b96-4e55-a67f-0f22af0e95cf",
                isApplicable: true,
              },
              "c614eddc-4066-4771-b176-e69c67c6d4ac": {
                libraryControlId: "c614eddc-4066-4771-b176-e69c67c6d4ac",
                isApplicable: true,
              },
            },
          },
          "37731c12-55bf-4120-8c2c-57dcf0b8ecd2": {
            libraryHazardId: "37731c12-55bf-4120-8c2c-57dcf0b8ecd2",
            isApplicable: false,
            controls: {
              "7921b1cb-2b96-4e55-a67f-0f22af0e95cf": {
                libraryControlId: "7921b1cb-2b96-4e55-a67f-0f22af0e95cf",
                isApplicable: false,
              },
            },
          },
        },
      };

      const expectedSiteConditionData: SiteConditionData = {
        librarySiteConditionId: "7a91aaf5-b54f-4586-ab38-66d0bb3b22bd",
        hazards: [
          {
            libraryHazardId: "ec4c82da-0923-4040-b142-b693bf382d1a",
            isApplicable: true,
            controls: [
              {
                libraryControlId: "c0c5d686-b373-48f8-9275-299b4c88b17c",
                isApplicable: false,
              },
              {
                libraryControlId: "6f861d56-fe24-413d-89d1-3a3eed715e6c",
                isApplicable: true,
              },
              {
                libraryControlId: "7921b1cb-2b96-4e55-a67f-0f22af0e95cf",
                isApplicable: true,
              },
              {
                libraryControlId: "c614eddc-4066-4771-b176-e69c67c6d4ac",
                isApplicable: true,
              },
            ],
          },
          {
            libraryHazardId: "37731c12-55bf-4120-8c2c-57dcf0b8ecd2",
            isApplicable: false,
            controls: [
              {
                libraryControlId: "7921b1cb-2b96-4e55-a67f-0f22af0e95cf",
                isApplicable: false,
              },
            ],
          },
        ],
      };

      expect(buildSiteConditionData(addSiteConditionInputs)).toStrictEqual(
        expectedSiteConditionData
      );
    });
  });

  describe("when excludeRecommendedControls is called", () => {
    const controlsLibrary = [
      {
        id: "7d1fccd0-5229-419b-b803-d32f721049c9",
        name: "Cutting goggles Wall for public safety",
        isApplicable: true,
      },
      {
        id: "8aac579e-b59c-4252-8939-c799b7f9166d",
        name: "Fire extinguisher",
        isApplicable: true,
      },
      {
        id: "b0ec7069-b7ed-4d62-ae12-25bfd471949e",
        name: "Welders gloves",
        isApplicable: true,
      },
      {
        id: "5d06c932-2434-4990-8609-45afc42f9864",
        name: "pipe holders",
        isApplicable: true,
      },
      {
        id: "0b2da794-4f9a-4ec2-adc6-ddd15342ca5e",
        name: "Cutting goggles",
        isApplicable: true,
      },
      {
        id: "c0c5d686-b373-48f8-9275-299b4c88b17c",
        name: "Gloves",
        isApplicable: true,
      },
      {
        id: "6f861d56-fe24-413d-89d1-3a3eed715e6c",
        name: "situational jobsite awareness",
        isApplicable: true,
      },
    ];

    const expectedControls = [
      {
        id: "7d1fccd0-5229-419b-b803-d32f721049c9",
        name: "Cutting goggles Wall for public safety",
        isApplicable: true,
      },
      {
        id: "8aac579e-b59c-4252-8939-c799b7f9166d",
        name: "Fire extinguisher",
        isApplicable: true,
      },
      {
        id: "b0ec7069-b7ed-4d62-ae12-25bfd471949e",
        name: "Welders gloves",
        isApplicable: true,
      },
      {
        id: "5d06c932-2434-4990-8609-45afc42f9864",
        name: "pipe holders",
        isApplicable: true,
      },
      {
        id: "0b2da794-4f9a-4ec2-adc6-ddd15342ca5e",
        name: "Cutting goggles",
        isApplicable: true,
      },
      {
        id: "c0c5d686-b373-48f8-9275-299b4c88b17c",
        name: "Gloves",
        isApplicable: true,
      },
    ];

    describe("when editing a task", () => {
      it("should return a collection of controls excluding the Urbint's recommended hazards controls", () => {
        const controls = [
          {
            id: "8aac579e-b59c-4252-8939-c799b7f9166d",
            name: "Fire extinguisher",
            isApplicable: true,
            createdBy: { id: "", name: "" },
            libraryControl: {
              id: "8aac579e-b59c-4252-8939-c799b7f9166d",
            },
          },
          {
            id: "6f861d56-fe24-413d-89d1-3a3eed715e6c",
            name: "situational jobsite awareness",
            isApplicable: true,
            libraryControl: {
              id: "6f861d56-fe24-413d-89d1-3a3eed715e6c",
            },
          },
        ];

        expect(excludeRecommendedControls(controlsLibrary, controls)).toEqual(
          expectedControls
        );
      });
    });
    describe("when adding a task", () => {
      it("should return a collection of controls excluding the Urbint's recommended hazards controls", () => {
        const controls = [
          {
            id: "6f861d56-fe24-413d-89d1-3a3eed715e6c",
            name: "situational jobsite awareness",
            isApplicable: true,
          },
        ];

        expect(excludeRecommendedControls(controlsLibrary, controls)).toEqual(
          expectedControls
        );
      });
    });

    describe("when hazards does not contain controls", () => {
      it("should return the entire list of controlsLibrary", () => {
        const controls: Control[] = [];

        expect(excludeRecommendedControls(controlsLibrary, controls)).toEqual(
          controlsLibrary
        );
      });
    });
  });

  describe("when excludeRecommendedHazards is called", () => {
    const hazardsLibrary = [
      {
        id: "1625a8d4-3330-4a9a-8054-f29948dde211",
        name: "Eye Flash",
        isApplicable: true,
        controls: [],
      },
      {
        id: "b967e3e8-ca66-4039-91ee-688f33ac31d7",
        name: "Fire",
        isApplicable: true,
        controls: [],
      },
      {
        id: "444fc4b3-3b98-4b08-abbe-dbb799903c4c",
        name: "Burns",
        isApplicable: true,
        controls: [],
      },
      {
        id: "179c69cf-2762-4b61-ad3b-36aee3ba9c69",
        name: "Flying hot debris",
        isApplicable: true,
        controls: [],
      },
      {
        id: "ec4c82da-0923-4040-b142-b693bf382d1a",
        name: "Pinch point",
        isApplicable: true,
        controls: [],
      },
      {
        id: "37731c12-55bf-4120-8c2c-57dcf0b8ecd2",
        name: "Struck by equipment and material",
        isApplicable: true,
        controls: [],
      },
      {
        id: "12da934f-0077-40cc-823d-10956ff8954a",
        name: "Caught in between bevel machine",
        isApplicable: true,
        controls: [],
      },
      {
        id: "d5f817c0-200a-4fc7-9738-65567b514c4c",
        name: "Flying debris",
        isApplicable: true,
        controls: [],
      },
    ];

    const expectedHazardsLibrary = [
      {
        id: "1625a8d4-3330-4a9a-8054-f29948dde211",
        name: "Eye Flash",
        isApplicable: true,
        controls: [],
      },
      {
        id: "444fc4b3-3b98-4b08-abbe-dbb799903c4c",
        name: "Burns",
        isApplicable: true,
        controls: [],
      },
      {
        id: "179c69cf-2762-4b61-ad3b-36aee3ba9c69",
        name: "Flying hot debris",
        isApplicable: true,
        controls: [],
      },
      {
        id: "ec4c82da-0923-4040-b142-b693bf382d1a",
        name: "Pinch point",
        isApplicable: true,
        controls: [],
      },
      {
        id: "37731c12-55bf-4120-8c2c-57dcf0b8ecd2",
        name: "Struck by equipment and material",
        isApplicable: true,
        controls: [],
      },
      {
        id: "12da934f-0077-40cc-823d-10956ff8954a",
        name: "Caught in between bevel machine",
        isApplicable: true,
        controls: [],
      },
      {
        id: "d5f817c0-200a-4fc7-9738-65567b514c4c",
        name: "Flying debris",
        isApplicable: true,
        controls: [],
      },
    ];

    describe("when editing a task", () => {
      it("should return a collection of hazards excluding the Urbint's recommended task hazards", () => {
        const hazards = [
          {
            id: "34da0018-e489-4d80-9c7c-1b0a2cb35b28",
            libraryHazard: {
              id: "1625a8d4-3330-4a9a-8054-f29948dde211",
            },
            isApplicable: true,
            name: "Eye Flash",
            createdBy: { id: "", name: "" },
            controls: [],
          },
          {
            id: "6504a943-567a-4e7d-a1ad-e5d7cbf652af",
            libraryHazard: {
              id: "b967e3e8-ca66-4039-91ee-688f33ac31d7",
            },
            isApplicable: true,
            name: "Fire",
            controls: [],
          },
          {
            id: "9b647503-5bd1-46b0-b8ef-1410c6271e58",
            libraryHazard: {
              id: "179c69cf-2762-4b61-ad3b-36aee3ba9c69",
            },
            isApplicable: true,
            name: "Flying hot debris",
            createdBy: { id: "", name: "" },
            controls: [],
          },
        ];

        expect(excludeRecommendedHazards(hazardsLibrary, hazards)).toEqual(
          expectedHazardsLibrary
        );
      });
    });

    describe("when adding a task", () => {
      it("should return a collection of hazards excluding the Urbint's recommended task hazards", () => {
        const hazards = [
          {
            id: "b967e3e8-ca66-4039-91ee-688f33ac31d7",
            isApplicable: true,
            name: "Fire",
            controls: [],
          },
        ];

        expect(excludeRecommendedHazards(hazardsLibrary, hazards)).toEqual(
          expectedHazardsLibrary
        );
      });
    });

    describe("when task does not contain hazards", () => {
      const hazards: Hazard[] = [];

      it("should return the entire list of hazardsLibrary", () => {
        expect(excludeRecommendedHazards(hazardsLibrary, hazards)).toEqual(
          hazardsLibrary
        );
      });
    });
  });

  describe("when transformTasksToListTasks is called", () => {
    it("should add a new property called `isSelected` and set it to true", () => {
      const arr = [{ id: 1 }, { id: 2 }];
      expect(
        transformTasksToListTasks(arr as unknown as TaskHazardAggregator[])
      ).toEqual([
        { id: 1, isSelected: false },
        { id: 2, isSelected: false },
      ]);
    });

    it("should mark the selected only the tasks exist in the selectedTasks param", () => {
      const arr = [{ id: "a" }, { id: "b" }, { id: "c" }, { id: "d" }];
      const selected = [{ id: "a" }, { id: "d" }];
      expect(
        transformTasksToListTasks(
          arr as unknown as TaskHazardAggregator[],
          selected as unknown as TaskSelectionInputs[]
        )
      ).toEqual([
        { id: "a", isSelected: true },
        { id: "b", isSelected: false },
        { id: "c", isSelected: false },
        { id: "d", isSelected: true },
      ]);
    });

    describe("when tasks is not defined", () => {
      it("should return empty array", () => {
        expect(transformTasksToListTasks()).toHaveLength(0);
      });
    });
  });

  describe("when isTaskComplete is called", () => {
    describe("when TaskStatus is not complete", () => {
      it("should return false", () => {
        expect(isTaskComplete(TaskStatus.NOT_STARTED)).toBeFalsy();
      });
    });
    describe("when TaskStatus is complete", () => {
      it("should return false", () => {
        expect(isTaskComplete(TaskStatus.COMPLETE)).toBeTruthy();
      });
    });
    describe("when TaskStatus is not defined", () => {
      it("should return false", () => {
        expect(isTaskComplete()).toBeFalsy();
      });
    });
  });

  describe("handle location hazard control settings", () => {
    const mockTask: TaskHazardAggregator = {
      id: "",
      name: "",
      incidents: [],
      riskLevel: RiskLevel.LOW,
      libraryTask: {
        id: "",
        name: "",
        category: "",
        hazards: [],
        activitiesGroups: [],
      },
      hazards: [
        {
          controls: [
            {
              id: "c0c5d686-b373-48f8-9275-299b4c88b17c",
              isApplicable: true,
              name: "Gloves",
            },
            {
              id: "6f861d56-fe24-413d-89d1-3a3eed715e6c",
              isApplicable: true,
              name: "situational jobsite awareness",
            },
          ],
          id: "ec4c82da-0923-4040-b142-b693bf382d1a",
          isApplicable: true,
          name: "Pinch point",
        },
        {
          id: "37731c12-55bf-4120-8c2c-57dcf0b8ecd2",
          name: "Struck by equipment and material",
          isApplicable: true,
          controls: [],
        },
      ],
    };

    const mockExistingLocationHazardSettings: LocationHazardControlSettings[] =
      [
        {
          id: "aa0d0e31-1537-43cd-bfba-77f3209b5951",
          libraryHazardId: "ec4c82da-0923-4040-b142-b693bf382d1a",
          libraryControlId: "6f861d56-fe24-413d-89d1-3a3eed715e6c",
          disabled: true,
        },
        {
          id: "7a92fda7-06c9-45b3-b5e9-e80d92171c5a",
          libraryHazardId: "37731c12-55bf-4120-8c2c-57dcf0b8ecd2",
          disabled: true,
        },
      ];
    describe("when applyLocationHazardControlSettings is called", () => {
      describe("when location has existing hazard/control settings", () => {
        it("should apply those settings to the hazard/control selection", () => {
          const taskWithLocationHazardSettingsApplied =
            applyLocationHazardControlSettings(
              mockTask,
              mockExistingLocationHazardSettings
            );

          const hazardWithSettingsApplied =
            taskWithLocationHazardSettingsApplied.hazards;

          const controlsWithSettingsApplied =
            hazardWithSettingsApplied[0].controls;

          expect(hazardWithSettingsApplied[0].isApplicable).toBe(true);
          expect(hazardWithSettingsApplied[1].isApplicable).toBe(false);

          expect(controlsWithSettingsApplied[0].isApplicable).toBe(true);
          expect(controlsWithSettingsApplied[1].isApplicable).toBe(false);
        });
      });
    });

    describe("when getLocationHazardControlSettingChanges is called", () => {
      const activityInput: ActivityInputs = {
        name: "Mock Activity",
        locationId: "23aaa56b-c684-4438-95c1-9a87436d2a2d",
        startDate: "2023-02-01",
        endDate: "2023-02-10",
        status: { id: "", name: "PENDING" },
        isCritical: false,
        criticalDescription: null,
        tasks: [
          {
            libraryTaskId: "",
            hazards: {
              "ec4c82da-0923-4040-b142-b693bf382d1a": {
                isApplicable: true,
                libraryHazardId: "ec4c82da-0923-4040-b142-b693bf382d1a",
                controls: {
                  "c0c5d686-b373-48f8-9275-299b4c88b17c": {
                    isApplicable: false,
                    libraryControlId: "c0c5d686-b373-48f8-9275-299b4c88b17c",
                  },
                  "6f861d56-fe24-413d-89d1-3a3eed715e6c": {
                    isApplicable: true,
                    libraryControlId: "6f861d56-fe24-413d-89d1-3a3eed715e6c",
                  },
                },
              },
              "37731c12-55bf-4120-8c2c-57dcf0b8ecd2": {
                isApplicable: true,
                libraryHazardId: "37731c12-55bf-4120-8c2c-57dcf0b8ecd2",
                controls: {},
              },
            },
          },
        ],
      };
      describe("when changes were made to recommended hazard/controls during add modal", () => {
        it("should collect the changes to the hazard/control selection", () => {
          const {
            newLocationHazardControlSettings,
            existingHazardControlSettingsToRemove,
          } = getLocationHazardControlSettingChanges(
            activityInput,
            mockExistingLocationHazardSettings
          );

          expect(existingHazardControlSettingsToRemove).toContainEqual(
            "aa0d0e31-1537-43cd-bfba-77f3209b5951"
          );
          expect(existingHazardControlSettingsToRemove).toContainEqual(
            "7a92fda7-06c9-45b3-b5e9-e80d92171c5a"
          );
          expect(newLocationHazardControlSettings).toContainEqual({
            libraryControlId: "c0c5d686-b373-48f8-9275-299b4c88b17c",
            libraryHazardId: "ec4c82da-0923-4040-b142-b693bf382d1a",
            locationId: "23aaa56b-c684-4438-95c1-9a87436d2a2d",
          });
        });
      });
    });
  });
});
