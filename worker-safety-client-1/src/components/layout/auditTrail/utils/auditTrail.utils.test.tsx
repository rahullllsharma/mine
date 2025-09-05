import type { AuditEvent } from "@/types/auditTrail/AuditEvent";
import { render } from "@testing-library/react";
import { AuditObjectType } from "@/types/auditTrail/AuditObjectType";
import { AuditActionType } from "@/types/auditTrail/AuditActionType";
import { getAuditTrailLabels } from "@/locales/messages";
import AuditTrail from "../AuditTrail";
import {
  getAuditCardContent,
  getDIRCardContent,
  getProjectStatusKey,
} from "./auditTrail.utils";

const auditTestEventList: AuditEvent[] = [
  {
    transactionId: "1",
    timestamp: "2022-04-06T11:14:37.742549+00:00",
    actor: { id: "1", name: "Montgomery Burns" },
    actionType: AuditActionType.UPDATED,
    objectType: AuditObjectType.TASK,
    objectDetails: {
      id: "001",
      name: "Loading/Unloading",
      location: {
        id: "001",
        name: "Main street 543",
      },
    },
    auditKey: "task_status",
    diffValues: {
      oldValue: "not_started",
      newValue: "in_progress",
    },
  },
  {
    transactionId: "2",
    timestamp: "2022-04-06T11:14:37.742549+00:00",
    actor: { id: "1", name: "Barney Gumble" },
    actionType: AuditActionType.CREATED,
    objectType: AuditObjectType.TASK,
    objectDetails: {
      id: "002",
      name: "Above the ground welding",
      location: {
        id: "002",
        name: "Second street 2",
      },
    },
    auditKey: "task",
  },
  {
    transactionId: "3",
    timestamp: "Oct 21, 2022 8:56am EST",
    actor: { id: "1", name: "Seymour Skinner" },
    actionType: AuditActionType.DELETED,
    objectType: AuditObjectType.SITE_CONDITION,
    objectDetails: {
      id: "003",
      name: "Cellular coverage",
      location: {
        id: "003",
        name: "Third Street",
      },
    },
    auditKey: "siteCondition",
  },
  {
    transactionId: "4",
    timestamp: "Oct 21, 2022 8:56am EST",
    actor: { id: "1", name: "Seymour Skinner" },
    actionType: AuditActionType.UPDATED,
    objectType: AuditObjectType.PROJECT,
    objectDetails: {
      id: "003",
      name: "Cellular coverage",
      location: {
        id: "003",
        name: "Third Street",
      },
    },
    auditKey: "project_additionalSupervisorIds",
    diffValues: {
      type: "List",
      removed: ["Lisa", "Marge", "Dr. Nick"],
    },
  },
  {
    transactionId: "6",
    timestamp: "2022-01-21T10:43:37.742549+00:00",
    actor: { id: "1", name: "Monty Burns" },
    actionType: AuditActionType.UPDATED,
    objectType: AuditObjectType.DAILY_REPORT,
    objectDetails: {
      id: "003",
      name: "report",
    },
    auditKey: "dailyReport_status",
    diffValues: {
      type: "String",
      oldValue: "in_progress",
      newValue: "complete",
    },
  },
  {
    transactionId: "6",
    timestamp: "2022-02-08T12:36:37.742549+00:00",
    actor: { id: "1", name: "Barney Gumble" },
    actionType: AuditActionType.CREATED,
    objectType: AuditObjectType.DAILY_REPORT,
    objectDetails: {
      id: "003",
      name: "report",
    },
    auditKey: "dailyReport",
  },
  {
    transactionId: "7",
    timestamp: "Oct 21, 2022 8:56am EST",
    actor: { id: "1", name: "Seymour Skinner" },
    actionType: AuditActionType.UPDATED,
    objectType: AuditObjectType.PROJECT,
    objectDetails: {
      id: "003",
      name: "Cellular coverage",
    },
    auditKey: "project_status",
    diffValues: {
      type: "String",
      oldValue: "active",
      newValue: "pending",
    },
  },
];

jest.mock("@/locales/messages", () => {
  return {
    __esModule: true,
    getAuditTrailLabels: () => ({
      in_progress: "In Progress",
      not_started: "Not Started",
      task_status: "Status",
      project: "Work Package",
      project_additionalSupervisorIds: "Additional Assigned Persons",
      daily_report: "Daily Inspection Report",
    }),
  };
});
const labels = getAuditTrailLabels();

describe(AuditTrail.name, () => {
  describe('when a "create" audit event is passed as an argument', () => {
    const event = auditTestEventList.find(
      ({ actionType }) => actionType === AuditActionType.CREATED
    ) as AuditEvent;
    const expectedOutput = `Added a ${labels[event.objectType]}: ${
      event.objectDetails.name
    }`;

    it("should contain the description of the task creation details", () => {
      const { asFragment } = render(getAuditCardContent(auditTestEventList[1]));
      expect(asFragment()).toHaveTextContent(expectedOutput);
    });
  });

  describe('when a "delete" audit event is passed as an argument', () => {
    const event = auditTestEventList.find(
      ({ actionType }) => actionType === AuditActionType.DELETED
    ) as AuditEvent;
    const expectedOutput = `Deleted a ${labels[event.objectType]}: ${
      event.objectDetails.name
    }`;

    it("should create a react node that contains the description of the task deletion details", () => {
      const { asFragment } = render(getAuditCardContent(auditTestEventList[2]));
      expect(asFragment()).toHaveTextContent(expectedOutput);
    });
  });

  describe('when an "update" audit event is passed as an argument', () => {
    const event = auditTestEventList.find(
      ({ actionType }) => actionType === AuditActionType.UPDATED
    ) as AuditEvent;
    const expectedOutput = `Updated the ${
      labels[event.auditKey as string]
    } in the ${labels[event.objectType]}: ${event.objectDetails.name} from ${
      labels[event.diffValues?.oldValue as string]
    }${labels[event.diffValues?.newValue as string]}`;

    it("should create a react node that contains the description of the task update details", () => {
      const { asFragment } = render(getAuditCardContent(auditTestEventList[0]));
      expect(asFragment()).toHaveTextContent(expectedOutput);
    });
  });

  describe('when an "update" event regarding a multi selection field is passed as an argument', () => {
    const event = auditTestEventList.find(
      ({ actionType, diffValues }) =>
        actionType === AuditActionType.UPDATED && diffValues?.type === "List"
    ) as AuditEvent;

    const expectedOutput = `Deleted ${
      labels[event.auditKey as string]
    } in the ${
      labels[event.objectType.toLowerCase()]
    }: ${event.diffValues?.removed?.join(", ")}`;

    it("should create a react node that contains the description of the added/removed items of the corresponding list", () => {
      const { asFragment } = render(getAuditCardContent(auditTestEventList[3]));
      expect(asFragment()).toHaveTextContent(expectedOutput);
    });
  });

  describe('when an "update" event regarding a DIR complete status is passed as an argument', () => {
    const expectedOutput = "Completed a Daily Inspection Report";

    it("should create a react node that describes a Daily Inspection Report as completed", () => {
      const { asFragment } = render(getDIRCardContent(auditTestEventList[4]));
      expect(asFragment()).toHaveTextContent(expectedOutput);
    });
  });

  describe('when a "create" event for a DIR is passed as an argument', () => {
    const event = auditTestEventList.find(
      ({ objectType, actionType }) =>
        actionType === AuditActionType.CREATED &&
        objectType === AuditObjectType.DAILY_REPORT
    ) as AuditEvent;

    const expectedOutput = `Added a ${labels[event.objectType.toLowerCase()]}`;

    it("should contain the description of a created Daily Inspection Report", () => {
      const { asFragment } = render(getAuditCardContent(auditTestEventList[5]));
      expect(asFragment()).toHaveTextContent(expectedOutput);
    });
  });

  describe("when the event refers to a Status update in a Work Package", () => {
    const event = auditTestEventList.find(
      ({ objectType, actionType, auditKey }) =>
        actionType === AuditActionType.UPDATED &&
        objectType === AuditObjectType.PROJECT &&
        auditKey === "project_status"
    ) as AuditEvent;

    it('should add the "project_status" prefix to the key', () => {
      const expectedOutput = `${event.auditKey}_${event.diffValues?.oldValue}`;
      expect(
        getProjectStatusKey(
          event.objectType,
          event.auditKey as string,
          event.diffValues?.oldValue as string
        )
      ).toEqual(expectedOutput);
    });
  });
});
