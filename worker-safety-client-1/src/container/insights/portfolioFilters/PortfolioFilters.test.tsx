import type { PortfolioFiltersPayload } from "./PortfolioFilters";
import { fireEvent, render, screen } from "@testing-library/react";
import { projectStatusOptions } from "@/types/project/ProjectStatus";
import { getDate } from "@/utils/date/helper";
import { mockTenantStore } from "@/utils/dev/jest";
import { getTimeFrame } from "../utils";
import PortfolioFilters from "./PortfolioFilters";

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
  {
    id: "7114445f-966a-42e2-aa3b-0e4d53650751b",
    name: "22nd Street Main Intersection",
    number: "123",
    locations: [
      {
        id: "5",
        name: "Location 5",
      },
      {
        id: "6",
        name: "Location 6",
      },
    ],
  },
];

const regions = [
  {
    id: "8e255eb4-09f2-45aa-a6c8-79f2f45a5120",
    name: "DNY (Downstate New York)",
  },
  {
    id: "f99ddad3-a34b-4380-bff8-f0aa94acda23",
    name: "UNY (Upstate New York)",
  },
  {
    id: "61910ead-90d1-4afd-846c-e053fad35921",
    name: "NE (New England)",
  },
];

const divisions = [
  {
    id: "26188e20-01bc-4afe-80c1-2e9d0ad1a341",
    name: "Gas",
  },
  {
    id: "9f86e0d2-de57-43a7-bcda-53c18029708e",
    name: "Electric",
  },
];

const contractors = [
  {
    id: "383fbe30-2eef-441f-898e-b07f8c53bb68",
    name: "Kiewit Power",
  },
  {
    id: "841b37e4-f9ac-42a1-b273-ce0c7eed6678",
    name: "Kiewit Energy Group Inc. And Subsidiaries",
  },
];

const mockOnChange = jest.fn();
const [startDate, endDate] = getTimeFrame(-14);

describe(PortfolioFilters.name, () => {
  mockTenantStore();
  beforeEach(() => {
    render(
      <PortfolioFilters
        projects={projects}
        projectStatuses={projectStatusOptions()}
        regions={regions}
        divisions={divisions}
        contractors={contractors}
        onChange={mockOnChange}
      />
    );
  });

  describe("when it renders", () => {
    it('should call "onChange"', () => {
      const payload: PortfolioFiltersPayload = {
        projectIds: [],
        projectStatuses: [],
        startDate,
        endDate,
        regionIds: [],
        divisionIds: [],
        contractorIds: [],
      };
      expect(mockOnChange).toHaveBeenCalledWith(payload);
    });
  });

  describe("when a project is selected", () => {
    it('should call "onChange" with the updated payload', () => {
      const inputElements = screen.getAllByRole("combobox");
      fireEvent.keyDown(inputElements[0], {
        key: "ArrowDown",
        code: "ArrowDown",
      });
      fireEvent.click(screen.getByText(projects[1].name));
      const payload: PortfolioFiltersPayload = {
        projectIds: [projects[1].id],
        projectStatuses: [],
        startDate,
        endDate,
        regionIds: [],
        divisionIds: [],
        contractorIds: [],
      };
      expect(mockOnChange).toHaveBeenCalledWith(payload);
    });
  });

  describe("when a status is selected", () => {
    it('should call "onChange" with the updated payload', () => {
      const inputElements = screen.getAllByRole("combobox");
      fireEvent.keyDown(inputElements[1], {
        key: "ArrowDown",
        code: "ArrowDown",
      });
      fireEvent.click(screen.getByText(projectStatusOptions()[1].name));
      const payload: PortfolioFiltersPayload = {
        projectIds: [],
        projectStatuses: [projectStatusOptions()[1].id],
        startDate,
        endDate,
        regionIds: [],
        divisionIds: [],
        contractorIds: [],
      };
      expect(mockOnChange).toHaveBeenCalledWith(payload);
    });
  });

  describe("when a time frame is selected", () => {
    it('should call "onChange" with the updated payload', () => {
      const inputElement = screen.getAllByRole("combobox");
      fireEvent.keyDown(inputElement[2], {
        key: "ArrowDown",
        code: "ArrowDown",
      });
      fireEvent.click(screen.getByText("Previous 90 days"));
      const payload: PortfolioFiltersPayload = {
        projectIds: [],
        projectStatuses: [],
        startDate: getDate(new Date(), -90, { includeToday: true }),
        endDate,
        regionIds: [],
        divisionIds: [],
        contractorIds: [],
      };
      expect(mockOnChange).toHaveBeenCalledWith(payload);
    });
  });

  describe("when a region is selected", () => {
    it('should call "onChange" with the updated payload', () => {
      const inputElements = screen.getAllByRole("combobox");
      fireEvent.keyDown(inputElements[3], {
        key: "ArrowDown",
        code: "ArrowDown",
      });
      fireEvent.click(screen.getByText(regions[1].name));
      const payload: PortfolioFiltersPayload = {
        projectIds: [],
        projectStatuses: [],
        startDate,
        endDate,
        regionIds: [regions[1].id],
        divisionIds: [],
        contractorIds: [],
      };
      expect(mockOnChange).toHaveBeenCalledWith(payload);
    });
  });

  describe("when a division is selected", () => {
    it('should call "onChange" with the updated payload', () => {
      const inputElements = screen.getAllByRole("combobox");
      fireEvent.keyDown(inputElements[4], {
        key: "ArrowDown",
        code: "ArrowDown",
      });
      fireEvent.click(screen.getByText(divisions[1].name));
      const payload: PortfolioFiltersPayload = {
        projectIds: [],
        projectStatuses: [],
        startDate,
        endDate,
        regionIds: [],
        divisionIds: [divisions[1].id],
        contractorIds: [],
      };
      expect(mockOnChange).toHaveBeenCalledWith(payload);
    });
  });

  describe("when a contractor is selected", () => {
    it('should call "onChange" with the updated payload', () => {
      const inputElements = screen.getAllByRole("combobox");
      fireEvent.keyDown(inputElements[5], {
        key: "ArrowDown",
        code: "ArrowDown",
      });
      fireEvent.click(screen.getByText(contractors[1].name));
      const payload: PortfolioFiltersPayload = {
        projectIds: [],
        projectStatuses: [],
        startDate,
        endDate,
        regionIds: [],
        divisionIds: [],
        contractorIds: [contractors[1].id],
      };
      expect(mockOnChange).toHaveBeenCalledWith(payload);
    });
  });
});
