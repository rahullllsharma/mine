import type { FormField } from "@/utils/formField";
import type { Either } from "fp-ts/lib/Either";
import type { Errors } from "io-ts";
import type { NonEmptyString } from "io-ts-types";
import { render, screen } from "@testing-library/react";
import * as t from "io-ts-types";

import { initFormField, updateFormField } from "@/utils/formField";
import { Input } from "./Input";

describe(Input.name, () => {
  let model: { name: FormField<Errors, string, NonEmptyString> };
  const decodeNameInput: (input: string) => Either<Errors, t.NonEmptyString> =
    t.withMessage(t.NonEmptyString, () => "Please provide a value").decode;

  beforeEach(() => {
    model = {
      name: initFormField(decodeNameInput)(""),
    };
  });

  it("renders correctly", () => {
    const { asFragment } = render(
      <Input
        type="text"
        label="Name:"
        field={model.name}
        onChange={jest.fn()}
      />
    );

    expect(screen.getByText("Name:")).toBeInTheDocument();
    expect(asFragment()).toMatchSnapshot();
  });

  it("renders error message", () => {
    model.name = updateFormField(decodeNameInput)("");
    const { asFragment } = render(
      <Input
        type="text"
        label="Name:"
        field={model.name}
        onChange={jest.fn()}
      />
    );

    expect(asFragment()).toMatchSnapshot();
  });
});
