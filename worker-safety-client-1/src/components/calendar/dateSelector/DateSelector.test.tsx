import { render, screen } from "@testing-library/react";
import DateSelector from "./DateSelector";

const mockTodayClick = jest.fn();
const mockPreviousDateClick = jest.fn();
const mockNextDateClick = jest.fn();
const mockAddEventListener = jest.fn();

const build = (props = {}) =>
  Object.defineProperty(window, "matchMedia", {
    writable: true,
    value: jest.fn().mockImplementation(query => ({
      matches: true,
      media: query,
      onchange: null,
      addListener: jest.fn(), // Deprecated
      removeListener: jest.fn(), // Deprecated
      addEventListener: mockAddEventListener,
      removeEventListener: jest.fn(),
      dispatchEvent: jest.fn(),
      ...props,
    })),
  });

describe(DateSelector.name, () => {
  build();
  describe("when component renders", () => {
    it("should render with the today button and a date", () => {
      const { asFragment } = render(
        <DateSelector
          date="2022-01-12"
          onTodayClicked={mockTodayClick}
          onPreviousDateClicked={mockPreviousDateClick}
          onNextDateClicked={mockNextDateClick}
        />
      );
      expect(asFragment()).toMatchSnapshot();
    });

    it("should render the date with month in long format", () => {
      render(
        <DateSelector
          date="2022-01-12"
          onTodayClicked={mockTodayClick}
          onPreviousDateClicked={mockPreviousDateClick}
          onNextDateClicked={mockNextDateClick}
        />
      );
      screen.getByText(/january 12, 2022/i);
    });

    it("should render the date with month in short format", () => {
      mockAddEventListener.mockImplementation(() => {
        matches: false;
      });

      build({
        matches: false,
      });

      render(
        <DateSelector
          date="2022-01-12"
          onTodayClicked={mockTodayClick}
          onPreviousDateClicked={mockPreviousDateClick}
          onNextDateClicked={mockNextDateClick}
        />
      );

      screen.getAllByText(/jan 12, 2022/i);
    });

    afterEach(() => {
      jest.clearAllMocks();
    });
  });
});
