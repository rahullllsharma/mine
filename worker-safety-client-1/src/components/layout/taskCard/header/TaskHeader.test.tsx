import { fireEvent, render, screen } from "@testing-library/react";
import { noop } from "lodash-es";
import { RiskLevel } from "@/components/riskBadge/RiskLevel";
import TaskHeader from "./TaskHeader";

const headerTextValue = "Above Ground Welding";
const subHeaderTextValue = "sub Above Ground Welding";

describe("TaskHeader", () => {
  it("should render a label", () => {
    render(
      <TaskHeader
        icon="chevron_big_down"
        headerText="Above Ground Welding"
        onClick={noop}
      />
    );
    const labelElement = screen.getByText("Above Ground Welding");
    expect(labelElement).toBeInTheDocument();
  });

  describe("when contain sub-header", () => {
    it("should render the sub-header text", () => {
      render(
        <TaskHeader
          icon="chevron_big_down"
          headerText={headerTextValue}
          subHeaderText={subHeaderTextValue}
          onClick={noop}
        />
      );
      const labelElement = screen.getByText("sub Above Ground Welding");
      expect(labelElement).toBeInTheDocument();
    });

    it("should render the header and sub-header text", () => {
      render(
        <TaskHeader
          icon="chevron_big_down"
          headerText={headerTextValue}
          subHeaderText={subHeaderTextValue}
          onClick={noop}
        />
      );
      const headerText = screen.getByText(headerTextValue);
      const subHeaderText = screen.getByText(subHeaderTextValue);
      expect(headerText).toBeInTheDocument();
      expect(subHeaderText).toBeInTheDocument();
    });

    it("should render an icon with header and sub-header text", () => {
      const { asFragment } = render(
        <TaskHeader
          icon="chevron_big_down"
          headerText={headerTextValue}
          subHeaderText={subHeaderTextValue}
          onClick={noop}
        />
      );
      expect(asFragment()).toMatchSnapshot();
    });
  });

  describe("when clickable region is clicked", () => {
    it("should call 'onClickableRegion'", () => {
      const clickableRegionHandler = jest.fn();
      render(
        <TaskHeader
          icon="chevron_big_down"
          headerText="Above Ground Welding"
          onClick={clickableRegionHandler}
        />
      );
      const button = screen.getByRole("button");
      fireEvent.click(button);
      expect(clickableRegionHandler).toHaveBeenCalled();
    });
  });

  describe("when a riskLevel is passed", () => {
    it("should render a risk badge", () => {
      const { asFragment } = render(
        <TaskHeader
          riskLevel={RiskLevel.HIGH}
          icon="chevron_big_down"
          headerText="Above Ground Welding"
          onClick={noop}
        />
      );
      const riskBadge = screen.getByRole("note");
      expect(riskBadge).toBeInTheDocument();
      expect(asFragment()).toMatchSnapshot();
    });
  });

  describe("when we want to show the summary count", () => {
    it("should render two badges", () => {
      const { asFragment } = render(
        <TaskHeader
          icon="chevron_big_down"
          headerText="Above Ground Welding"
          onClick={noop}
          showSummaryCount
        />
      );
      const badges = screen.getAllByRole("note");
      expect(badges).toHaveLength(2);
      expect(asFragment()).toMatchSnapshot();
    });

    it("should render the badge count of hazards", () => {
      render(
        <TaskHeader
          icon="chevron_big_down"
          headerText="Above Ground Welding"
          onClick={noop}
          showSummaryCount
          totalControls={0}
          totalHazards={1}
        />
      );
      const badge = screen.getByText("1H");
      expect(badge).toBeInTheDocument();
    });

    it("should render the badge count of controls", () => {
      render(
        <TaskHeader
          icon="chevron_big_down"
          headerText="Above Ground Welding"
          onClick={noop}
          showSummaryCount
          totalControls={1}
          totalHazards={0}
        />
      );
      const badge = screen.getByText("1C");
      expect(badge).toBeInTheDocument();
    });
  });

  describe("when menu button is rendered", () => {
    const menuButtonHandler = jest.fn();
    const clickableRegionHandler = jest.fn();
    const headerText = "Above Ground Welding";
    beforeEach(() => {
      render(
        <TaskHeader
          icon="chevron_big_down"
          menuIcon="edit"
          headerText={headerText}
          onClick={clickableRegionHandler}
          onMenuClicked={menuButtonHandler}
        />
      );
    });

    it("should render two buttons", () => {
      screen.getByRole("button", { name: headerText });
      screen.getByRole("button", { name: /menu button/i });
    });

    describe("when menu button is clicked", () => {
      it("should call 'onMenuClicked'", () => {
        const buttonElements = screen.getAllByRole("button");
        fireEvent.click(buttonElements[1]);
        expect(menuButtonHandler).toHaveBeenCalled();
      });
    });
  });
});
