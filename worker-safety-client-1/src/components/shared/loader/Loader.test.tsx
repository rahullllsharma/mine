import { render } from "@testing-library/react";
import Loader from "./Loader";

describe(Loader.name, () => {
  it("renders", () => {
    const { asFragment } = render(<Loader />);
    expect(asFragment()).toMatchSnapshot();
  });
});
