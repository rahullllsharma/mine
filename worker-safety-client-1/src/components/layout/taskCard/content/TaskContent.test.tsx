import { render, screen } from "@testing-library/react";
import TaskContent from "./TaskContent";

describe("TaskContent", () => {
  describe("when task don't contain hazards", () => {
    it("should not render a hazard card", () => {
      render(<TaskContent hazards={[]} />);
      const hazardCardElements = screen.queryAllByTestId("hazardCard");
      expect(hazardCardElements).toHaveLength(0);
    });
  });

  describe("when task contain hazards", () => {
    const hazards = [
      {
        id: "1",
        name: "hazard 123",
        isApplicable: true,
        controls: [
          {
            id: "1",
            name: "control name",
            isApplicable: true,
          },
          {
            id: "2",
            name: "control name 2",
            isApplicable: true,
          },
        ],
      },
      {
        id: "2",
        name: "hazard 123",
        isApplicable: true,
        controls: [
          {
            id: "1",
            name: "control name",
            isApplicable: true,
          },
          {
            id: "2",
            name: "control name 2",
            isApplicable: true,
          },
        ],
      },
    ];

    it("should render a list of hazards and controls", () => {
      const { asFragment } = render(<TaskContent hazards={hazards} />);
      expect(asFragment()).toMatchSnapshot();
    });

    it(`should render ${hazards.length} total hazard card(s)`, () => {
      render(<TaskContent hazards={hazards} />);
      const hazardCardElements = screen.getAllByTestId("hazardCard");
      expect(hazardCardElements).toHaveLength(hazards.length);
    });

    describe("when there is no controls", () => {
      it("should not render a control card", () => {
        const hazardsWithoutControls = [
          {
            id: "1",
            name: "hazard 123",
            isApplicable: true,
            controls: [],
          },
        ];
        render(<TaskContent hazards={hazardsWithoutControls} />);
        const controlCardElements = screen.queryAllByTestId("controlCard");
        expect(controlCardElements).toHaveLength(0);
      });
    });

    describe("when we have a set of controls", () => {
      it(`should render ${hazards[0].controls.length} control cards`, () => {
        const hazard = hazards[0];
        render(<TaskContent hazards={[hazard]} />);
        const controlCardElements = screen.queryAllByTestId("controlCard");
        expect(controlCardElements).toHaveLength(hazard.controls.length);
      });
    });
  });
});
