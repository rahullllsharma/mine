import type { AuditEvent } from "@/types/auditTrail/AuditEvent";
import type { ComponentMeta, ComponentStory } from "@storybook/react";
import { AuditObjectType } from "@/types/auditTrail/AuditObjectType";
import { AuditActionType } from "@/types/auditTrail/AuditActionType";
import AuditTrail from "./AuditTrail";

const auditTestEventList: AuditEvent[] = [
  {
    transactionId: "1",
    timestamp: "2022-04-06T11:14:37.742549+00:00",
    actor: { id: "1", name: "Montgomery Burns", role: "administrator" },
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
    auditKey: "task_endDate",
    diffValues: {
      oldValue: "24/06/2022",
      newValue: "21/07/2022",
    },
  },
  {
    transactionId: "2",
    timestamp: "2022-04-06T11:14:37.742549+00:00",
    actor: { id: "1", name: "Barney Gumble", role: "supervisor" },
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
    timestamp: "2022-04-06T11:14:37.742549+00:00",
    actor: { id: "1", name: "Seymour Skinner", role: "administrator" },
    actionType: AuditActionType.DELETED,
    objectType: AuditObjectType.TASK,
    objectDetails: {
      id: "003",
      name: "Loading/Unloading",
      location: {
        id: "003",
        name: "Third Street",
      },
    },
    auditKey: "task",
  },
  {
    transactionId: "3",
    timestamp: "2022-04-06T11:14:37.742549+00:00",
    actor: { id: "1", name: "Seymour Skinner", role: "administrator" },
    actionType: AuditActionType.UPDATED,
    objectType: AuditObjectType.PROJECT,
    objectDetails: {
      id: "003",
      name: "Loading/Unloading",
      location: {
        id: "003",
        name: "Third Street",
      },
    },
    auditKey: "project_additionalSupervisorIds",
    diffValues: {
      type: "List",
      added: ["Paul", "Lewis"],
    },
  },
  {
    transactionId: "3",
    timestamp: "2022-04-06T11:14:37.742549+00:00",
    actor: { id: "1", name: "Seymour Skinner", role: "viewer" },
    actionType: AuditActionType.UPDATED,
    objectType: AuditObjectType.PROJECT,
    objectDetails: {
      id: "003",
      name: "Loading/Unloading",
      location: {
        id: "003",
        name: "Third Street",
      },
    },
    auditKey: "project_managerId",
    diffValues: {
      oldValue: "Stewie",
      newValue: "Brian Griffin",
    },
  },
  {
    transactionId: "6",
    timestamp: "2022-01-21T10:43:37.742549+00:00",
    actor: { id: "1", name: "Monty Burns", role: "supervisor" },
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
    actor: { id: "1", name: "Barney Gumble", role: "manager" },
    actionType: AuditActionType.CREATED,
    objectType: AuditObjectType.DAILY_REPORT,
    objectDetails: {
      id: "003",
      name: "report",
    },
    auditKey: "dailyReport",
  },
];

export default {
  title: "Layout/AuditTrail/AuditTrail",
  component: AuditTrail,
} as ComponentMeta<typeof AuditTrail>;

const Template: ComponentStory<typeof AuditTrail> = args => (
  <AuditTrail {...args} />
);

export const Playground = Template.bind({});
Playground.args = {
  auditEventsList: auditTestEventList,
};
