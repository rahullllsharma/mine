import type { ComponentProps } from "react";
import { fireEvent, render, screen } from "@testing-library/react";
import { FormProvider, useForm } from "react-hook-form";
import { mockTenantStore } from "@/utils/dev/jest";
import HazardCardContent from "./HazardCardContent";

const userInitials = "JD";
const hazardId = "123";
const controlName = "control-name";
const hazardControls = [
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
];

const controlsLibrary = [
  {
    id: "1",
    name: "control-library-1",
  },
  {
    id: "2",
    name: "control-library-2",
  },
];

describe(HazardCardContent.name, () => {
  beforeAll(mockTenantStore);

  describe("when registering the form provider", () => {
    const mockOnSubmit = jest.fn();

    const TestWrapper = (
      params:
        | Pick<ComponentProps<typeof HazardCardContent>, "controlFormPrefix">
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
            <HazardCardContent
              {...params}
              hazardId={hazardId}
              hazardControls={hazardControls}
              controlsLibrary={controlsLibrary}
              userInitials={userInitials}
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
});
