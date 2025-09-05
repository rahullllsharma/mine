import type { AuditEvent } from "@/types/auditTrail/AuditEvent";
import { render, screen } from "@testing-library/react";
import { AuditObjectType } from "@/types/auditTrail/AuditObjectType";
import { AuditActionType } from "@/types/auditTrail/AuditActionType";
import { mockTenantStore } from "@/utils/dev/jest";
import AuditTrail from "../AuditTrail";

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
    auditKey: "task_endDate",
    diffValues: {
      oldValue: "24/06/2022",
      newValue: "21/07/2022",
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
];

describe(AuditTrail.name, () => {
  mockTenantStore();
  it("should display as many cards as the events passed in the auditEventsList array", () => {
    render(<AuditTrail auditEventsList={auditTestEventList} />);
    const cards = screen.queryAllByTestId("audit-card");
    expect(cards).toHaveLength(auditTestEventList.length);
  });

  it("shouldn't display any cards when an empty array is passed to the component", () => {
    render(<AuditTrail auditEventsList={[]} />);
    const cards = screen.queryAllByTestId("audit-card");
    expect(cards).toHaveLength(0);
  });
});
