import type { SectionItem } from "./ProjectPrintSection";
import { render, screen } from "@testing-library/react";
import ProjectPrintSection from "./ProjectPrintSection";

describe(ProjectPrintSection.name, () => {
  describe("when it renders", () => {
    it('should have a section header that matches the "header" prop', () => {
      render(<ProjectPrintSection header="Section title" items={[]} />);
      screen.getByText("Section title");
    });

    describe("when it renders a list of items", () => {
      const items: SectionItem[] = [
        {
          title: "Project name",
          description: "North Grand St. Bridge",
        },
        {
          title: "Project number",
          description: "12345678",
        },
      ];
      beforeEach(() => {
        render(<ProjectPrintSection header="Section title" items={items} />);
      });

      it.each(items)(`should show the items`, ({ title, description }) => {
        screen.getByText(title);
        screen.getByText(description as string);
      });
    });
  });

  describe("when an item doesn't have a description", () => {
    const items: SectionItem[] = [
      {
        title: "Project name",
      },
    ];
    it('should render a "-" character', () => {
      render(<ProjectPrintSection header="Section title" items={items} />);
      screen.getByText("-");
    });
  });

  describe("when an item has a description with an empty array", () => {
    const items: SectionItem[] = [
      {
        title: "Project name",
        description: [],
      },
    ];
    it('should render a "-" character', () => {
      render(<ProjectPrintSection header="Section title" items={items} />);
      screen.getByText("-");
    });
  });

  describe("when an item has a description multiple elements", () => {
    const description = ["123", "456", "789"];
    const items: SectionItem[] = [
      {
        title: "Project name",
        description,
      },
    ];
    it("should render the items of the array separated by a comma", () => {
      render(<ProjectPrintSection header="Section title" items={items} />);
      screen.getByText(description.join(", "));
    });
  });
});
