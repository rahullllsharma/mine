import type {
  PageHeaderAction,
  PageHeaderActionTooltip,
} from "./components/headerActions/HeaderActions";
import { fireEvent, render, screen } from "@testing-library/react";
import PageHeader from "./PageHeader";

describe(PageHeader.name, () => {
  it("should be rendered correctly", () => {
    const { asFragment } = render(
      <PageHeader linkText="some label" linkRoute="route" />
    );
    expect(asFragment()).toMatchSnapshot();
  });

  it("should display the link text and page title", () => {
    const linkLabel = "go back";
    const pageTitle = "tasks page";

    render(
      <PageHeader
        linkText={linkLabel}
        linkRoute="route"
        pageTitle={pageTitle}
      />
    );
    screen.getByText(linkLabel);
    screen.getByText(pageTitle);
  });

  describe("when a tooltip is passed in the header props", () => {
    beforeEach(() => {
      const headerTooltip: PageHeaderActionTooltip = {
        type: "tooltip",
        title: "tooltip hover",
      };

      render(<PageHeader actions={headerTooltip} />);
    });

    it("should display a icon non-interactive", () => {
      screen.getByRole("tooltip", { hidden: true });
    });

    it("when hovered, it should display the message", () => {
      fireEvent.mouseOver(screen.getByRole("tooltip", { hidden: true }));
      expect(screen.getByText("tooltip hover")).toBeInTheDocument();
    });
  });

  describe("when a single header action is passed in the header props", () => {
    it("should display the clickable icon", () => {
      const headerAction: PageHeaderAction = {
        icon: "settings_filled",
        title: "settings",
        onClick: jest.fn(),
      };

      render(<PageHeader actions={headerAction} />);
      screen.getByRole("button", { name: /settings/i });
    });
  });

  describe("when an header actions array with a single element is passed in the header props", () => {
    it("should display the clickable icon", () => {
      const headerAction: PageHeaderAction = {
        icon: "settings_filled",
        title: "settings",
        onClick: jest.fn(),
      };

      render(<PageHeader actions={[headerAction]} />);
      screen.getByRole("button", { name: /settings/i });
    });
  });

  describe("when an header actions array with multiple elements is passed in the header props", () => {
    it("should display a dropdown menu", () => {
      const headerActions: PageHeaderAction[] = [
        {
          icon: "settings_filled",
          title: "settings",
          onClick: jest.fn(),
        },
        {
          icon: "trash_empty",
          title: "delete",
          onClick: jest.fn(),
        },
      ];

      render(<PageHeader actions={headerActions} />);
      screen.getAllByTestId("dropdown");
    });
  });
});
