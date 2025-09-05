import { fireEvent, render, screen } from "@testing-library/react";
import {
  convertDateToString,
  getDate,
  getDayAndWeekdayFromDate,
  getFormattedDate,
} from "@/utils/date/helper";
import Calendar from "./Calendar";

Object.defineProperty(window, "matchMedia", {
  writable: true,
  value: jest.fn().mockImplementation(query => ({
    matches: true,
    media: query,
    onchange: null,
    addListener: jest.fn(), // Deprecated
    removeListener: jest.fn(), // Deprecated
    addEventListener: jest.fn(),
    removeEventListener: jest.fn(),
    dispatchEvent: jest.fn(),
  })),
});

const mockOnDateSelect = jest.fn();

jest.useFakeTimers();
jest.setSystemTime(new Date("2022-01-24").valueOf());

describe(Calendar.name, () => {
  describe("when it renders", () => {
    const startDate = "2022-01-01";
    const endDate = "2030-01-20";

    it("should have 7 calendar day buttons and two navigation buttons", () => {
      const { asFragment } = render(
        <Calendar
          startDate={startDate}
          endDate={endDate}
          onDateSelect={mockOnDateSelect}
          defaultDate={startDate}
        />
      );
      expect(asFragment()).toMatchSnapshot();
    });

    it("should have the current day as a default when the current day is within the project range", () => {
      const today = convertDateToString(new Date());

      render(
        <Calendar
          startDate={startDate}
          endDate={endDate}
          onDateSelect={mockOnDateSelect}
          defaultDate={today}
        />
      );

      const [day, weekday] = getDayAndWeekdayFromDate(today);
      const buttonElement = screen.getByRole("button", {
        name: `${day} ${weekday}`,
      });
      expect(buttonElement).toHaveAttribute("data-is-today");
    });

    it("should have the endDate as default when the current day is after the project end date", () => {
      const date = convertDateToString("2021-01-25");

      render(
        <Calendar
          startDate="2021-01-15"
          endDate="2021-01-25"
          onDateSelect={mockOnDateSelect}
          defaultDate={date}
        />
      );

      const [day, weekday] = getDayAndWeekdayFromDate(date);
      const buttonElement = screen.getByRole("button", {
        name: `${day} ${weekday}`,
      });
      expect(buttonElement).toHaveAttribute("data-is-selected");
    });

    it("should have the startDate as default when the current day is before the project start date", () => {
      const date = convertDateToString("2030-01-15");

      render(
        <Calendar
          startDate="2030-01-15"
          endDate="2030-01-25"
          onDateSelect={mockOnDateSelect}
          defaultDate={date}
        />
      );

      const [day, weekday] = getDayAndWeekdayFromDate(date);
      const buttonElement = screen.getByRole("button", {
        name: `${day} ${weekday}`,
      });
      expect(buttonElement).toHaveAttribute("data-is-selected");
    });
  });

  describe("when dealing with the today button", () => {
    it("should select the current day when it's clicked", () => {
      const today = convertDateToString(new Date());

      render(
        <Calendar
          startDate="2022-01-15"
          endDate="2030-01-25"
          onDateSelect={mockOnDateSelect}
          defaultDate={today}
        />
      );
      const nextDate = convertDateToString(getDate(new Date(), 1));
      const [nextDay, nextWeekday] = getDayAndWeekdayFromDate(nextDate);
      const buttonElement = screen.getByRole("button", {
        name: `${nextDay} ${nextWeekday}`,
      });
      fireEvent.click(buttonElement);
      fireEvent.click(screen.getByRole("button", { name: /today/i }));

      const [day, weekday] = getDayAndWeekdayFromDate(today);
      const todayElement = screen.getByRole("button", {
        name: `${day} ${weekday}`,
      });
      expect(todayElement).toHaveAttribute("data-is-today");
    });

    it("should select the current day when it's clicked and update the calendar range", () => {
      render(
        <Calendar
          startDate="2022-01-15"
          endDate="2030-01-25"
          onDateSelect={mockOnDateSelect}
          defaultDate="2022-01-15"
        />
      );
      fireEvent.click(
        screen.getByRole("button", {
          name: /last week/i,
        })
      );
      fireEvent.click(screen.getByRole("button", { name: /today/i }));
      const date = convertDateToString(new Date());
      const [day, weekday] = getDayAndWeekdayFromDate(date);
      const todayElement = screen.getByRole("button", {
        name: `${day} ${weekday}`,
      });
      expect(todayElement).toHaveAttribute("data-is-today");
    });

    it("should be disabled if the current day is outside the calendar dates", () => {
      render(
        <Calendar
          startDate="2021-01-15"
          endDate="2021-01-25"
          onDateSelect={mockOnDateSelect}
          defaultDate="2022-01-15"
        />
      );
      const buttonElement = screen.getByRole("button", { name: /today/i });
      expect(buttonElement).toBeDisabled();
    });
  });

  describe("when the calendar day buttons are pressed", () => {
    const startDate = "2022-01-15";
    const endDate = "2030-01-25";

    it("should switch to another active element when clicked", () => {
      const today = convertDateToString(getDate(new Date(), 1));

      render(
        <Calendar
          startDate={startDate}
          endDate={endDate}
          onDateSelect={mockOnDateSelect}
          defaultDate={today}
        />
      );

      const [day, weekday] = getDayAndWeekdayFromDate(today);
      const buttonElement = screen.getByRole("button", {
        name: `${day} ${weekday}`,
      });
      fireEvent.click(buttonElement);
      expect(buttonElement).toHaveAttribute("data-is-selected");
    });

    it("should remove the selected styling from the current day when another day is selected", () => {
      const today = convertDateToString(new Date());

      render(
        <Calendar
          startDate={startDate}
          endDate={endDate}
          onDateSelect={mockOnDateSelect}
          defaultDate={today}
        />
      );
      const date = convertDateToString(getDate(new Date(), 1));
      const [day, weekday] = getDayAndWeekdayFromDate(date);
      const buttonElement = screen.getByRole("button", {
        name: `${day} ${weekday}`,
      });
      fireEvent.click(buttonElement);

      const [todayDay, todayWeekday] = getDayAndWeekdayFromDate(today);
      const todayElement = screen.getByRole("button", {
        name: `${todayDay} ${todayWeekday}`,
      });

      expect(todayElement).not.toHaveAttribute("data-is-selected");
    });
  });

  describe("when the calendar navigation buttons are pressed", () => {
    describe('when "Last week" button is pressed', () => {
      const startDate = "2022-01-10";
      const endDate = "2022-01-20";

      beforeEach(() => {
        render(
          <Calendar
            startDate={startDate}
            endDate={endDate}
            onDateSelect={mockOnDateSelect}
            defaultDate={startDate}
          />
        );
      });

      it("should navigate to the previous week", () => {
        const buttonElement = screen.getByRole("button", {
          name: /last week/i,
        });
        fireEvent.click(buttonElement);

        const [d1, w1] = getDayAndWeekdayFromDate("2022-01-10");
        const [d2, w2] = getDayAndWeekdayFromDate("2022-01-13");

        screen.getByRole("button", { name: `${d1} ${w1}` });
        screen.getByRole("button", { name: `${d2} ${w2}` });
      });

      it("should disable the button when no more weeks are available", () => {
        const buttonElement = screen.getByRole("button", {
          name: /last week/i,
        });
        fireEvent.click(buttonElement);

        expect(buttonElement).toBeDisabled();
      });
    });

    describe('when "Next week" is pressed', () => {
      const startDate = "2030-01-15";
      const endDate = "2030-01-25";

      beforeEach(() => {
        render(
          <Calendar
            startDate={startDate}
            endDate={endDate}
            onDateSelect={mockOnDateSelect}
            defaultDate={startDate}
          />
        );
      });

      it("should navigate to the next week", () => {
        const buttonElement = screen.getByRole("button", {
          name: /next week/i,
        });
        fireEvent.click(buttonElement);

        const [d1, w1] = getDayAndWeekdayFromDate("2030-01-19");
        const [d2, w2] = getDayAndWeekdayFromDate("2030-01-25");

        screen.getByRole("button", { name: `${d1} ${w1}` });
        screen.getByRole("button", { name: `${d2} ${w2}` });
      });

      it("should disable the button when no more weeks are available", () => {
        const buttonElement = screen.getByRole("button", {
          name: /next week/i,
        });
        fireEvent.click(buttonElement);

        expect(buttonElement).toBeDisabled();
      });
    });

    describe("when on smaller screens", () => {
      const today = convertDateToString(new Date());
      const startDate = "2022-01-15";
      const endDate = "2030-01-25";

      beforeEach(() => {
        render(
          <Calendar
            startDate={startDate}
            endDate={endDate}
            onDateSelect={mockOnDateSelect}
            defaultDate={today}
          />
        );
      });
      it("should navigate to the previous day when the left arrow is pressed", () => {
        const buttonElements = screen.getAllByRole("button", {
          hidden: true,
          name: "",
        });
        fireEvent.click(buttonElements[0]);

        const date = getDate(new Date(), -1);
        screen.getByText(getFormattedDate(date, "long"));
      });

      it("should navigate to the next day when the right arrow is pressed", () => {
        const buttonElements = screen.getAllByRole("button", {
          hidden: true,
          name: "",
        });
        fireEvent.click(buttonElements[1]);

        const date = getDate(new Date(), 1);
        screen.getByText(getFormattedDate(date, "long"));
      });

      it("should update the date range when the left arrow is pressed and user reaches the previous week", () => {
        const buttonElements = screen.getAllByRole("button", { hidden: true });
        const hiddenButtons = buttonElements.filter(
          btn => btn.textContent === ""
        );

        for (let i = 0; i < 4; i++) {
          fireEvent.click(hiddenButtons[0]);
        }
        const firstDate = convertDateToString(getDate(new Date(), -10));
        const lastDate = convertDateToString(getDate(new Date(), -4));

        const [d1, w1] = getDayAndWeekdayFromDate(firstDate);
        const [d2, w2] = getDayAndWeekdayFromDate(lastDate);

        screen.getByRole("button", { name: `${d1} ${w1}` });
        screen.getByRole("button", { name: `${d2} ${w2}` });
      });

      it("should update the date range when the left arrow is pressed and user reaches the next week", () => {
        const buttonElements = screen.getAllByRole("button", { hidden: true });
        const hiddenButtons = buttonElements.filter(
          btn => btn.textContent === ""
        );

        for (let i = 0; i < 4; i++) {
          fireEvent.click(hiddenButtons[1]);
        }
        const firstDate = convertDateToString(getDate(new Date(), 4));
        const lastDate = convertDateToString(getDate(new Date(), 10));

        const [d1, w1] = getDayAndWeekdayFromDate(firstDate);
        const [d2, w2] = getDayAndWeekdayFromDate(lastDate);

        screen.getByRole("button", { name: `${d1} ${w1}` });
        screen.getByRole("button", { name: `${d2} ${w2}` });
      });
    });
  });
});
