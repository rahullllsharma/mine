import type { MultiStepFormStateItem } from "./state/reducer";
import { render, screen, within } from "@testing-library/react";
import MultiStepForm from "./MultiStepForm";

jest.mock("@/hooks/useLeavePageConfirm");

jest.mock("next/router", () => ({
  useRouter: jest.fn(() => ({
    asPath: "path/to/page",
    push: jest.fn(),
  })),
}));

describe(MultiStepForm.name, () => {
  let cacheHistoryState: History;

  beforeEach(() => {
    cacheHistoryState = window.history;

    Object.defineProperty(window, "history", {
      value: {
        replaceState: jest.fn(),
        state: {
          as: "pathname",
        },
      },
      writable: true,
    });

    window.HTMLElement.prototype.scrollTo = jest.fn();
  });

  afterEach(() => {
    Object.defineProperties(
      window.history,
      cacheHistoryState as unknown as PropertyDescriptorMap
    );
  });

  it("should render the multi form properly", async () => {
    const steps = [
      {
        id: "step",
        name: "Step",
        path: "#step",
        // eslint-disable-next-line react/display-name
        Component: () => <p>Hello Step</p>,
      },
    ] as unknown as MultiStepFormStateItem[];

    const { asFragment } = render(<MultiStepForm steps={steps} />);
    await screen.findByText(/hello step/i);

    // Navigation(s)
    const nav = screen.getByTestId("multi-step-navigation");
    // non-mobile navigation
    within(nav).getByRole("tablist");
    // mobile only navigation
    within(nav).getByTestId("select");

    // Save button
    screen.getByRole("button", {
      name: /save and continue/i,
    });

    expect(asFragment()).toMatchSnapshot();
  });
});
