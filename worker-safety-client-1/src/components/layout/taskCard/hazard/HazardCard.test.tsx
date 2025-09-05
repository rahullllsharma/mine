import { render, screen } from "@testing-library/react";
import ControlCard from "../control/ControlCard";
import HazardCard from "./HazardCard";

describe("HazardCard", () => {
  it("should render a label", () => {
    render(<HazardCard header="Lorem ipsum" />);
    const labelElement = screen.getByText("Lorem ipsum");
    expect(labelElement).toBeInTheDocument();
  });

  it("should render a custom header with a button", () => {
    const header = (
      <div>
        <button>Lorem ipsum</button>
      </div>
    );
    render(<HazardCard header={header} />);
    const labelElement = screen.getByRole("button");
    expect(labelElement).toBeInTheDocument();
  });

  describe("when we have a set of controls", () => {
    it("should render 3 control cards", () => {
      render(
        <HazardCard header="Lorem ipsum">
          <ControlCard label="Situational Jobsite Awareness" />
          <ControlCard label="Trained and Qualified" />
          <ControlCard label="Erection of Proper Barricades and Warning Signs" />
        </HazardCard>
      );
      const controlCardElements = screen.getAllByTestId("controlCard");
      expect(controlCardElements).toHaveLength(3);
    });

    it("should render a list of controls", () => {
      const { asFragment } = render(
        <HazardCard header="Lorem ipsum">
          <ControlCard label="Situational Jobsite Awareness" />
          <ControlCard label="Trained and Qualified" />
          <ControlCard label="Erection of Proper Barricades and Warning Signs" />
        </HazardCard>
      );
      expect(asFragment()).toMatchSnapshot();
    });
  });
});
