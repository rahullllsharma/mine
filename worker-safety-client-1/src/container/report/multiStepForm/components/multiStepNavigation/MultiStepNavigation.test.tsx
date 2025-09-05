import MultiStepNavigation from "./MultiStepNavigation";

jest.mock("next/router", () => ({
  useRouter: jest.fn(() => ({
    asPath: "path/to/page",
    push: jest.fn(),
  })),
}));

describe(MultiStepNavigation.name, () => {
  // reports -> reports#work-schedule
  it.todo("should include the current section hashbang on the first render");
  // reports#old-schedule -> reports#new-section
  it.todo("should shallow replace the hashbang when the current step changes");
  // reports#old-schedule -> reports/11f0bfce-44aa-4ee0-86d2-fb35775b6798#old-schedule"
  it.todo(
    "should shallow replace the hashbang when the current step and preserve the daily report id in the url"
  );
  // reports#state=... -> reports#work-schedule&state=989e3c06-adcd-4d43-87dd-324a0303d98d&state_session
  it.todo(
    "should replace the auth parameter that starts with a hashbang and keep it in the url"
  );
  it.todo(
    "should NOT shallow replace the hashbang when the current step didn't change"
  );
});
