import { render } from "@testing-library/react";
import { AttributeOptionList } from "./AttributeOptionList";

describe(AttributeOptionList.name, () => {
  describe("when isVisible is passed as false", () => {
    it("should display only 'hide' icon", () => {
      const { asFragment } = render(
        <AttributeOptionList
          isVisible={false}
          isRequired={false}
          isFilterable={false}
        />
      );

      expect(asFragment()).toMatchSnapshot();
    });

    it("should display only 'hide' icon, even when isFilterable and isRequired are true", () => {
      const { asFragment } = render(
        <AttributeOptionList
          isVisible={false}
          isRequired={true}
          isFilterable={true}
        />
      );

      expect(asFragment()).toMatchSnapshot();
    });
  });

  describe("when isVisible is passed", () => {
    it("should display 'show' icon", () => {
      const { asFragment } = render(
        <AttributeOptionList
          isVisible={true}
          isRequired={false}
          isFilterable={false}
        />
      );

      expect(asFragment()).toMatchSnapshot();
    });

    it("should display 'required' icon when isRequired is true", () => {
      const { asFragment } = render(
        <AttributeOptionList
          isVisible={true}
          isRequired={true}
          isFilterable={false}
        />
      );

      expect(asFragment()).toMatchSnapshot();
    });

    it("should display 'filter' icon when isFilterable is true", () => {
      const { asFragment } = render(
        <AttributeOptionList
          isVisible={true}
          isRequired={false}
          isFilterable={true}
        />
      );

      expect(asFragment()).toMatchSnapshot();
    });

    it("should display all 3 icons when all props are true", () => {
      const { asFragment } = render(
        <AttributeOptionList
          isVisible={true}
          isRequired={true}
          isFilterable={true}
        />
      );

      expect(asFragment()).toMatchSnapshot();
    });
  });
});
