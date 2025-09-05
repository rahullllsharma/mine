import type { Either } from "fp-ts/lib/Either";
import type { Errors } from "io-ts";

import * as t from "io-ts-types";
import { render, screen } from "@testing-library/react";
import { initFormField, updateFormField } from "@/utils/formField";

import { ErrorMessage } from "./ErrorMessage";

describe(ErrorMessage.name, () => {
  const decodeStringInput: (input: string) => Either<Errors, t.NonEmptyString> =
    t.withMessage(t.NonEmptyString, () => "This field is required").decode;
  const createField = (raw = "") => {
    return initFormField(decodeStringInput)(raw);
  };

  it("renders correctly", () => {
    let field = createField();
    field = updateFormField(decodeStringInput)("");
    const { asFragment } = render(<ErrorMessage field={field} />);

    expect(screen.getByText("This field is required")).toBeInTheDocument();
    expect(asFragment()).toMatchSnapshot();
  });
});
