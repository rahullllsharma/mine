import type { ProjectFiltersPayload } from "./ProjectFilters";
import { fireEvent, render, screen } from "@testing-library/react";
import { getDate } from "@/utils/date/helper";
import { mockTenantStore } from "@/utils/dev/jest";
import { getTimeFrame } from "../utils";
import ProjectFilters from "./ProjectFilters";

const projects = [
  {
    id: "7114445f-966a-42e2-aa3b-0e4d5365075d",
    name: "5th Street Main Relocation",
    number: "123",
    locations: [
      {
        id: "1",
        name: "Location 1",
      },
      {
        id: "2",
        name: "Location 2",
      },
    ],
  },
  {
    id: "7114445f-966a-42e2-aa3b-0e4d53650751a",
    name: "N. Washington Street Bridge",
    number: "123",
    locations: [
      {
        id: "3",
        name: "Location 3",
      },
      {
        id: "4",
        name: "Location 4",
      },
    ],
  },
];

const mockOnChange = jest.fn();
const [startDate, endDate] = getTimeFrame(-14);

describe(ProjectFilters.name, () => {
  mockTenantStore();
  describe("when it renders", () => {
    it('should call "onChange"', () => {
      render(<ProjectFilters projects={projects} onChange={mockOnChange} />);
      const payload: ProjectFiltersPayload = {
        projectId: projects[0].id,
        locationIds: [],
        startDate,
        endDate,
      };
      expect(mockOnChange).toHaveBeenCalledWith(payload);
    });
  });

  describe("when a project is selected", () => {
    it('should call "onChange" with the updated payload', () => {
      render(<ProjectFilters projects={projects} onChange={mockOnChange} />);
      const inputElement = screen.getAllByRole("combobox");
      fireEvent.keyDown(inputElement[0], {
        key: "ArrowDown",
        code: "ArrowDown",
      });
      fireEvent.click(screen.getByText(projects[1].name));
      const payload: ProjectFiltersPayload = {
        projectId: projects[1].id,
        locationIds: [],
        startDate,
        endDate,
      };
      expect(mockOnChange).toHaveBeenCalledWith(payload);
    });
  });

  describe("when a locations is selected", () => {
    it('should call "onChange" with the updated payload', () => {
      render(<ProjectFilters projects={projects} onChange={mockOnChange} />);
      const inputElement = screen.getAllByRole("combobox");
      fireEvent.keyDown(inputElement[1], {
        key: "ArrowDown",
        code: "ArrowDown",
      });
      fireEvent.click(screen.getByText(projects[0].locations[0].name));
      const payload: ProjectFiltersPayload = {
        projectId: projects[0].id,
        locationIds: [projects[0].locations[0].id],
        startDate,
        endDate,
      };
      expect(mockOnChange).toHaveBeenCalledWith(payload);
    });
  });

  describe("when a time frame is selected", () => {
    it('should call "onChange" with the updated payload', () => {
      render(<ProjectFilters projects={projects} onChange={mockOnChange} />);
      const inputElement = screen.getAllByRole("combobox");
      fireEvent.keyDown(inputElement[2], {
        key: "ArrowDown",
        code: "ArrowDown",
      });
      fireEvent.click(screen.getByText("Previous 90 days"));
      const payload: ProjectFiltersPayload = {
        projectId: projects[0].id,
        locationIds: [],
        startDate: getDate(new Date(), -90, { includeToday: true }),
        endDate,
      };
      expect(mockOnChange).toHaveBeenCalledWith(payload);
    });
  });
});
