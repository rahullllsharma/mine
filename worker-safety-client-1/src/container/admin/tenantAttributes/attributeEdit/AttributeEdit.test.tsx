import { fireEvent, screen, act, waitFor } from "@testing-library/react";
import { formRender } from "@/utils/dev/jest";
import { AttributeEdit } from "./AttributeEdit";

describe(AttributeEdit.name, () => {
  const mockOnSubmit = jest.fn();
  const mockCancelCb = jest.fn();

  it("should render with prefilled label and label plural", () => {
    formRender(
      <AttributeEdit onSubmit={mockOnSubmit} onCancel={mockCancelCb} />,
      {
        label: "Singular",
        labelPlural: "Plural",
      }
    );

    screen.getByDisplayValue("Singular");
    screen.getByDisplayValue("Plural");
  });

  it("should show an error when label has less than 3 chars", async () => {
    formRender(
      <AttributeEdit onSubmit={mockOnSubmit} onCancel={mockCancelCb} />,
      {
        label: "Singular",
        labelPlural: "Plural",
      }
    );

    const inputElement = screen.getByDisplayValue("Singular");

    act(() => {
      fireEvent.change(inputElement, { target: { value: "Si" } });
      fireEvent.focusOut(inputElement);
      const buttonElement = screen.getByRole("button", { name: /Save/i });
      fireEvent.click(buttonElement);
    });

    await screen.findByText(
      "Attribute name should be longer than 3 characters."
    );
  });

  it("should show an error when label has less than 50 chars", async () => {
    formRender(
      <AttributeEdit onSubmit={mockOnSubmit} onCancel={mockCancelCb} />,
      {
        label: "Singular",
        labelPlural: "Plural",
      }
    );

    const inputElement = screen.getByDisplayValue("Singular");

    act(() => {
      fireEvent.change(inputElement, {
        target: {
          value: "123456789012345678901234567890123456789012345678901",
        },
      });
      fireEvent.focusOut(inputElement);
      const buttonElement = screen.getByRole("button", { name: /Save/i });
      fireEvent.click(buttonElement);
    });

    await screen.findByText(
      "Attribute name should be shorter than 50 characters."
    );
  });

  it("should call onSubmit callback when submitting", async () => {
    formRender(
      <AttributeEdit onSubmit={mockOnSubmit} onCancel={mockCancelCb} />,
      {
        label: "Singular",
        labelPlural: "Plural",
      }
    );

    act(() => {
      const buttonElement = screen.getByRole("button", { name: /Save/i });
      fireEvent.click(buttonElement);
    });
    await waitFor(() => {
      expect(mockOnSubmit).toHaveBeenCalledWith({
        label: "Singular",
        labelPlural: "Plural",
      });
    });
  });

  it("should call onCancel callback when clicking Cancel button", () => {
    formRender(
      <AttributeEdit onSubmit={mockOnSubmit} onCancel={mockCancelCb} />,
      {
        label: "Singular",
        labelPlural: "Plural",
      }
    );

    act(() => {
      const buttonElement = screen.getByRole("button", { name: /Cancel/i });
      fireEvent.click(buttonElement);
    });
    expect(mockCancelCb).toHaveBeenCalled();
  });
});
