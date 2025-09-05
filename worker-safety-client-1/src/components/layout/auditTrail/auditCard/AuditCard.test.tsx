import { render, screen } from "@testing-library/react";
import { getUserInitials } from "@/components/shared/avatar/utils";
import AuditCard from "./AuditCard";

const username = "Paulo Sousa";
const taskTimestamp = "Aug 24, 2022 8:56am EST";
const location = { id: "012", name: "Main Street" };
const cardContent = "Added a Task: Above the ground welding";

describe(AuditCard.name, () => {
  it("should render an avatar with initials, a name and a timestamp", () => {
    render(<AuditCard username={username} timestamp={taskTimestamp} />);
    screen.getByText(username);
    screen.getByText(getUserInitials(username));
    screen.getByText(taskTimestamp);
  });

  it('should render the Urbint Logo as avatar and "Urbint Administrator" as user, when the actors role is "administrator"', () => {
    render(
      <AuditCard
        username={username}
        userRole="administrator"
        timestamp={taskTimestamp}
      />
    );
    screen.getByText(/urbint administrator/i);
    screen.getByRole("img", { name: /urbint/i });
  });

  it("should render a location, when passed", () => {
    render(
      <AuditCard
        username={username}
        timestamp={taskTimestamp}
        location={location}
      />
    );
    screen.getByText(location.name);
  });

  it("should render the card content", () => {
    render(
      <AuditCard username={username} timestamp={taskTimestamp}>
        {cardContent}
      </AuditCard>
    );
    screen.getByText(cardContent);
  });
});
