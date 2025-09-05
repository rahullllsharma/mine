import type { Hazard } from "@/types/project/Hazard";
import type { Control } from "@/types/project/Control";
import { fireEvent, screen } from "@testing-library/react";
import { formRender, mockTenantStore, openSelectMenu } from "@/utils/dev/jest";
import SiteConditionDetailsForm from "./SiteConditionDetailsForm";

const siteCondition = {
  id: "1",
  name: "SiteCondition 1",
  isManuallyAdded: true,
  hazards: [
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
      name: "hazard 567",
      isApplicable: true,
      controls: [
        {
          id: "12",
          name: "control name",
          isApplicable: true,
        },
        {
          id: "22",
          name: "control name 2",
          isApplicable: true,
        },
      ],
    },
  ],
  incidents: [],
  createdBy: {
    id: "0",
    name: "Homer",
  },
};

const controlsLibrary: Control[] = [
  { id: "custom-control-1", name: "Control 1", isApplicable: true },
  { id: "custom-control-2", name: "Control 2", isApplicable: true },
  { id: "custom-control-3", name: "Control 3", isApplicable: true },
  { id: "custom-control-4", name: "Control 4", isApplicable: true },
];

const hazardsLibrary: Hazard[] = [
  { id: "custom-hazard-1", name: "Hazard 1", isApplicable: true, controls: [] },
];

describe(SiteConditionDetailsForm.name, () => {
  mockTenantStore();
  describe("when the form is shown", () => {
    it("header should exist", () => {
      formRender(
        <SiteConditionDetailsForm
          siteCondition={siteCondition}
          hazardsLibrary={hazardsLibrary}
          controlsLibrary={controlsLibrary}
        />
      );
      const siteConditionHeader = screen.getByTestId("siteCondition-header");

      expect(siteConditionHeader).toBeInTheDocument();
    });

    describe("when we have hazards that can be manually added", () => {
      beforeEach(() => {
        formRender(
          <SiteConditionDetailsForm
            siteCondition={siteCondition}
            hazardsLibrary={hazardsLibrary}
            controlsLibrary={controlsLibrary}
          />
        );
      });

      it("should render the button 'Add a hazard'", () => {
        screen.getByRole("button", {
          name: /add a hazard/i,
        });
      });

      describe("when 'Add a hazard' button is clicked", () => {
        it("should render a select to pick a hazard from library", () => {
          fireEvent.click(
            screen.getByRole("button", {
              name: /add a hazard/i,
            })
          );
          screen.getByRole("button", {
            name: /select a hazard/i,
          });
        });

        describe("when a hazard is selected from list", () => {
          it("select the hazard", () => {
            fireEvent.click(
              screen.getByRole("button", {
                name: /add a hazard/i,
              })
            );

            openSelectMenu("button", /select a hazard/i);

            fireEvent.click(
              screen.getByRole("option", { name: hazardsLibrary[0].name })
            );
            screen.getByRole("button", {
              name: hazardsLibrary[0].name,
            });
          });

          describe("when we don't have more hazards that can be added", () => {
            it("should have 'Add a hazard' button disabled and have an explanatory title", () => {
              fireEvent.click(
                screen.getByRole("button", {
                  name: /add a hazard/i,
                })
              );

              openSelectMenu("button", /select a hazard/i);

              fireEvent.click(
                screen.getByRole("option", { name: hazardsLibrary[0].name })
              );

              const buttonElement = screen.getByRole("button", {
                name: /add a hazard/i,
              });

              expect(buttonElement).toBeDisabled();
            });
          });

          describe("when we remove a manually added hazard", () => {
            it("should remove the hazard from the list of hazards", () => {
              fireEvent.click(
                screen.getByRole("button", {
                  name: /add a hazard/i,
                })
              );

              openSelectMenu("button", /select a hazard/i);

              fireEvent.click(
                screen.getByRole("option", { name: hazardsLibrary[0].name })
              );

              screen.getByRole("button", {
                name: hazardsLibrary[0].name,
              });

              fireEvent.click(screen.getByRole("button", { name: /remove/i }));

              expect(
                screen.queryByRole("button", {
                  name: hazardsLibrary[0].name,
                })
              ).not.toBeInTheDocument();
            });
          });
        });
      });
    });

    describe("when we don't have hazards", () => {
      it("should not render the button 'Add a hazard'", () => {
        formRender(
          <SiteConditionDetailsForm
            siteCondition={siteCondition}
            hazardsLibrary={[]}
            controlsLibrary={controlsLibrary}
          />
        );
        expect(
          screen.queryByRole("button", { name: /add a hazard/i })
        ).not.toBeInTheDocument();
      });
    });
  });
});
