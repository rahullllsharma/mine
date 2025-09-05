import { fireEvent, screen } from "@testing-library/react";
import { formRender } from "@/utils/dev/jest";
import CrewMembers from "./CrewMembers";

const emptyMembers = {
  nWelders: "",
  nSafetyProf: "",
  nFlaggers: "",
  nLaborers: "",
  nOperators: "",
  nOtherCrew: "",
};

const members = {
  nWelders: 1,
  nSafetyProf: 2,
  nFlaggers: 3,
  nLaborers: 4,
  nOperators: 5,
  nOtherCrew: 6,
};

describe(CrewMembers.name, () => {
  describe("when the page renders without default crew members", () => {
    beforeEach(() => {
      formRender(<CrewMembers />, {
        crew: {
          ...emptyMembers,
        },
      });
    });

    it("should have empty crew inputs", () => {
      const { asFragment } = formRender(<CrewMembers />);
      expect(asFragment()).toMatchSnapshot();
    });

    describe("when an input changes", () => {
      it("should change the crew value when the value inserted is a number", () => {
        const inputElement = screen.getByRole("spinbutton", {
          name: /welders/i,
        });
        fireEvent.change(inputElement, { target: { value: 55 } });
        expect(inputElement).toHaveValue(55);
      });

      it("shouldn't change the crew value when the value inserted is a string", () => {
        const inputElement = screen.getByRole("spinbutton", {
          name: /welders/i,
        });
        fireEvent.change(inputElement, { target: { value: "abc" } });
        expect(inputElement).toHaveTextContent("");
      });

      it("should update the total of crew members", () => {
        const value = 2;
        const inputElements = screen.getAllByRole("spinbutton");
        inputElements.forEach(textBox =>
          fireEvent.change(textBox, { target: { value } })
        );
        const totalElement = screen.getByRole("textbox");
        const expectedValue = inputElements.length * value;
        expect(totalElement).toHaveValue(`${expectedValue}`);
      });

      describe("when field value is cleared", () => {
        it("should clear the input", () => {
          const inputElements = screen.getByRole("spinbutton", {
            name: /welders/i,
          });
          fireEvent.change(inputElements, { target: { value: "" } });
          expect(inputElements).not.toHaveValue();
        });
      });
    });
  });

  describe("when the page renders with default crew members", () => {
    it("should have inputs filled with the default values", () => {
      const { asFragment } = formRender(<CrewMembers />, {
        crew: {
          ...members,
        },
      });
      expect(asFragment()).toMatchSnapshot();
    });

    it("should update the total of crew members", () => {
      formRender(<CrewMembers />, { crew: { ...members } });
      const totalElement = screen.getByRole("textbox");
      expect(totalElement).toHaveValue("21");
    });
  });
});
