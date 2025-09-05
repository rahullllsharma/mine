import type { ComponentProps } from "react";
import { fireEvent, render, screen } from "@testing-library/react";
import { FormProvider, useForm } from "react-hook-form";
import { formRender, mockTenantStore, openSelectMenu } from "@/utils/dev/jest";
import TaskContentEdit from "./TaskContentEdit";

const mockOnSelectHazard = jest.fn();
const mockOnRemoveHazard = jest.fn();

const hazardName = "hazard 123";
const controlName = "control name";
const hazards = [
  {
    id: "1",
    key: "1",
    name: hazardName,
    isApplicable: true,
    controls: [
      {
        id: "1",
        key: "1",
        name: controlName,
        isApplicable: true,
      },
      {
        id: "2",
        key: "2",
        name: `${controlName} 2`,
        isApplicable: true,
      },
    ],
  },
  {
    id: "2",
    key: "2",
    name: hazardName,
    isApplicable: true,
    controls: [
      {
        id: "1",
        key: "1",
        name: controlName,
        isApplicable: true,
      },
      {
        id: "2",
        key: "2",
        name: `${controlName} 2`,
        isApplicable: true,
      },
    ],
  },
];

describe(TaskContentEdit.name, () => {
  mockTenantStore();
  describe("when task doesn't contain hazards", () => {
    it("should not render a hazard card", () => {
      formRender(
        <TaskContentEdit
          hazards={[]}
          controlsLibrary={[]}
          onRemoveHazard={mockOnRemoveHazard}
          onSelectHazard={mockOnSelectHazard}
        />
      );
      const hazardCardElements = screen.queryAllByTestId("hazardCard");
      expect(hazardCardElements).toHaveLength(0);
    });
  });

  describe("when task contain hazards", () => {
    describe("when registering the form provider", () => {
      const mockOnSubmit = jest.fn();

      const TestWrapper = (
        params:
          | Pick<ComponentProps<typeof TaskContentEdit>, "controlFormPrefix">
          | undefined = {}
      ) => {
        const methods = useForm({
          mode: "all",
        });

        return (
          <FormProvider {...methods}>
            <form
              onSubmit={methods.handleSubmit(mockOnSubmit)}
              data-testid="form"
            >
              <TaskContentEdit
                {...params}
                hazards={hazards}
                controlsLibrary={[]}
                onRemoveHazard={mockOnRemoveHazard}
                onSelectHazard={mockOnSelectHazard}
              />
            </form>
          </FormProvider>
        );
      };

      afterEach(() => {
        mockOnSubmit.mockReset();
      });

      it("should register each controller starting with the `hazard` prefix and include that in the form data", async () => {
        render(<TestWrapper />);

        fireEvent.submit(await screen.findByTestId("form"));

        expect(await screen.findByTestId("form")).toBeInTheDocument();
        // We don't care about the internal value, only the key in the formData
        expect(mockOnSubmit).toHaveBeenCalledWith(
          expect.objectContaining({
            hazards: expect.any(Array),
          }),
          expect.anything()
        );
      });

      it("should register each controller with the prefix passed and include that in the form data, in the proper position", async () => {
        const prefix = "hello";
        const position = 1;
        render(<TestWrapper controlFormPrefix={`${prefix}.${position}`} />);

        fireEvent.submit(await screen.findByTestId("form"));

        expect(await screen.findByTestId("form")).toBeInTheDocument();
        // We don't care about the internal values, only that the object was properly filled.
        expect(mockOnSubmit).toHaveBeenCalledWith(
          expect.objectContaining({
            // test that the prefix is the key for the FormData
            [prefix]: expect.arrayContaining(
              // test creates an array where the last element of that array contains the key = hazards
              new Array(position).fill(expect.anything()).concat(
                expect.objectContaining({
                  hazards: expect.anything(),
                })
              )
            ),
          }),
          expect.anything()
        );
      });
    });

    it(`should render ${hazards.length} hazard card`, () => {
      formRender(
        <TaskContentEdit
          hazards={hazards}
          controlsLibrary={[]}
          onRemoveHazard={mockOnRemoveHazard}
          onSelectHazard={mockOnSelectHazard}
        />
      );
      const hazardCardElements = screen.getAllByTestId("hazardCard");
      expect(hazardCardElements).toHaveLength(hazards.length);
    });

    describe("when hazard is applicable", () => {
      it("should render the switch checked", () => {
        const mockHazard = [
          { ...hazards[0], isApplicable: true, controls: [] },
        ];
        formRender(
          <TaskContentEdit
            hazards={mockHazard}
            controlsLibrary={[]}
            onRemoveHazard={mockOnRemoveHazard}
            onSelectHazard={mockOnSelectHazard}
          />
        );
        const buttonElements = screen.getAllByRole("switch", {
          name: new RegExp(hazardName, "i"),
        });
        expect(buttonElements[0]).toBeChecked();
      });
    });

    describe("when hazard is not applicable", () => {
      it("should render the switch unchecked", () => {
        const mockHazard = [
          { ...hazards[0], isApplicable: false, controls: [] },
        ];
        formRender(
          <TaskContentEdit
            hazards={mockHazard}
            controlsLibrary={[]}
            onRemoveHazard={mockOnRemoveHazard}
            onSelectHazard={mockOnSelectHazard}
          />
        );
        screen.getByRole("switch", {
          name: new RegExp(hazardName, "i"),
          checked: false,
        });
      });
    });

    describe("when there is no controls", () => {
      it("should not render a control card", () => {
        const mockHazard = [
          { ...hazards[0], isApplicable: true, controls: [] },
        ];
        formRender(
          <TaskContentEdit
            hazards={mockHazard}
            controlsLibrary={[]}
            onRemoveHazard={mockOnRemoveHazard}
            onSelectHazard={mockOnSelectHazard}
          />
        );
        const controlCardElements = screen.queryAllByTestId("controlCard");
        expect(controlCardElements).toHaveLength(0);
      });
    });

    describe("when we have a set of controls", () => {
      it(`should render ${hazards[0].controls.length} control cards`, () => {
        const hazard = hazards[0];
        formRender(
          <TaskContentEdit
            hazards={[hazard]}
            controlsLibrary={[]}
            onRemoveHazard={mockOnRemoveHazard}
            onSelectHazard={mockOnSelectHazard}
          />
        );
        const controlCardElements = screen.queryAllByTestId("controlCard");
        expect(controlCardElements).toHaveLength(hazard.controls.length);
      });

      it("should render a switch button for each control", () => {
        const mockHazard = [hazards[0]];
        formRender(
          <TaskContentEdit
            hazards={mockHazard}
            controlsLibrary={[]}
            onRemoveHazard={mockOnRemoveHazard}
            onSelectHazard={mockOnSelectHazard}
          />
        );
        const switchElements = screen.getAllByRole("switch");
        expect(switchElements).toHaveLength(
          mockHazard.length + mockHazard[0].controls.length
        );
      });

      describe("when control is applicable", () => {
        const mockHazard = [hazards[0]];
        it("should render the switch checked", () => {
          formRender(
            <TaskContentEdit
              hazards={mockHazard}
              controlsLibrary={[]}
              onRemoveHazard={mockOnRemoveHazard}
              onSelectHazard={mockOnSelectHazard}
            />
          );
          const buttonElements = screen.getAllByRole("switch", {
            name: new RegExp(controlName, "i"),
          });
          expect(buttonElements[0]).toBeChecked();
        });

        describe("when we toggle the control state", () => {
          it("should be set as not applicable", () => {
            formRender(
              <TaskContentEdit
                hazards={mockHazard}
                controlsLibrary={[]}
                onRemoveHazard={mockOnRemoveHazard}
                onSelectHazard={mockOnSelectHazard}
              />
            );

            const buttonElements = screen.getAllByRole("switch", {
              name: new RegExp(controlName, "i"),
            });
            fireEvent.click(buttonElements[0]);
            expect(buttonElements[0]).not.toBeChecked();
          });
        });
      });

      describe("when control is not applicable", () => {
        const name = "control name";
        const hazard = {
          id: "1",
          key: "1",
          name: "hazard 123",
          isApplicable: true,
          controls: [
            {
              id: "1",
              key: "1",
              name,
              isApplicable: false,
            },
          ],
        };
        it("should render the switch unchecked", () => {
          formRender(
            <TaskContentEdit
              hazards={[hazard]}
              controlsLibrary={[]}
              onRemoveHazard={mockOnRemoveHazard}
              onSelectHazard={mockOnSelectHazard}
            />
          );
          const buttonElement = screen.getByRole("switch", {
            name: new RegExp(name, "i"),
          });
          expect(buttonElement).not.toBeChecked();
        });

        describe("when we toggle the control state", () => {
          it("should be set as applicable", () => {
            formRender(
              <TaskContentEdit
                hazards={[hazard]}
                controlsLibrary={[]}
                onRemoveHazard={mockOnRemoveHazard}
                onSelectHazard={mockOnSelectHazard}
              />
            );

            const buttonElement = screen.getByRole("switch", {
              name: new RegExp(name, "i"),
            });
            fireEvent.click(buttonElement);
            expect(buttonElement).toBeChecked();
          });
        });
      });

      describe("when we toggle a hazard state", () => {
        it("should collapse the controls section", () => {
          formRender(
            <TaskContentEdit
              hazards={[hazards[0]]}
              controlsLibrary={[]}
              onRemoveHazard={mockOnRemoveHazard}
              onSelectHazard={mockOnSelectHazard}
            />
          );
          const buttonElements = screen.getAllByRole("switch", {
            name: new RegExp(hazardName, "i"),
          });
          fireEvent.click(buttonElements[0]);
          const controlCardElements = screen.queryAllByTitle("controlCard");
          expect(controlCardElements).toHaveLength(0);
        });
      });
    });

    describe("when we want to handle custom controls", () => {
      const controlsLibrary = [
        {
          id: "custom-control-1",
          name: "Control 1",
          isApplicable: true,
        },
        {
          id: "custom-control-2",
          name: "Control 2",
          isApplicable: true,
        },
        {
          id: "custom-control-3",
          name: "Control 3",
          isApplicable: true,
        },
        {
          id: "custom-control-4",
          name: "Control 4",
          isApplicable: true,
        },
      ];

      beforeEach(() => {
        formRender(
          <TaskContentEdit
            hazards={[hazards[0]]}
            controlsLibrary={controlsLibrary}
            onRemoveHazard={mockOnRemoveHazard}
            onSelectHazard={mockOnSelectHazard}
          />
        );
        fireEvent.click(
          screen.getByRole("button", {
            name: /add a control/i,
          })
        );
      });

      it('should add a custom control when we click the "Add a control" button', () => {
        const customControl = screen.getByTestId("ControlSelectCard");
        expect(customControl).toBeInTheDocument();
      });

      it('should disable the "Add a control" button when the amount of custom controls matches the length of the control library', () => {
        const buttonElement = screen.getByRole("button", {
          name: /add a control/i,
        });

        controlsLibrary.forEach(() => {
          fireEvent.click(buttonElement);
        });
        expect(buttonElement).toBeDisabled();
      });

      it('should remove a custom control when the "trash can" icon is clicked', () => {
        fireEvent.click(screen.getByRole("button", { name: /remove/i }));
        const customControl = screen.queryByTestId("ControlSelectCard");
        expect(customControl).toBeNull();
      });

      it("should update the custom control option", () => {
        openSelectMenu("button", /select a control/i);

        fireEvent.click(screen.getByText(controlsLibrary[2].name));

        const selectElement = screen.getByRole("button", {
          name: new RegExp(controlsLibrary[2].name, "i"),
        });

        expect(selectElement).toBeInTheDocument();
      });

      describe("when an option is selected", () => {
        beforeEach(() => {
          const selectOption = controlsLibrary[2].name;

          openSelectMenu("button", /select a control/i);

          fireEvent.click(screen.getByText(selectOption));
          fireEvent.click(
            screen.getByRole("button", {
              name: /add a control/i,
            })
          );

          openSelectMenu("button", /select a control/i);
        });
        it("should remove that option from the list of the next select", () => {
          const listItems = screen.getAllByRole("option");
          expect(
            listItems.some(
              option => option.textContent === controlsLibrary[2].name
            )
          ).toBe(false);
        });

        it("should add that option to the list if the previous one is deleted", () => {
          fireEvent.click(
            screen.getAllByRole("button", { name: /remove/i })[0]
          );
          const listItems = screen.getAllByRole("option");
          expect(listItems.map(option => option.textContent)).toEqual(
            controlsLibrary.map(option => option.name)
          );
        });
      });
    });

    describe("when no custom controls are available", () => {
      it('shouldn\'t render the "Add a control" button', () => {
        formRender(
          <TaskContentEdit
            hazards={[hazards[0]]}
            onRemoveHazard={mockOnRemoveHazard}
            onSelectHazard={mockOnSelectHazard}
          />
        );
        const buttonElement = screen.queryByRole("button", {
          name: /add a control/i,
        });
        expect(buttonElement).toBeNull();
      });
    });

    describe("when task status is complete", () => {
      beforeEach(() => {
        formRender(
          <TaskContentEdit
            hazards={hazards}
            controlsLibrary={[]}
            onRemoveHazard={mockOnRemoveHazard}
            onSelectHazard={mockOnSelectHazard}
            isDisabled
          />
        );
      });

      it("should have the hazard's switch button disabled", () => {
        const buttonElements = screen.getAllByRole("switch", {
          name: new RegExp(hazardName, "i"),
        });

        buttonElements.forEach(button => expect(button).toBeDisabled());
      });

      it("should have the controls's switch button disabled", () => {
        const buttonElements = screen.getAllByRole("switch", {
          name: new RegExp(controlName, "i"),
        });
        buttonElements.forEach(button => expect(button).toBeDisabled());
      });
    });
  });
});
