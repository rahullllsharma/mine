import { screen, render } from "@testing-library/react";
import React from "react";
import NextLink from "next/link";
import Link from "./Link";

describe(Link.name, () => {
  it("should be rendered correctly", () => {
    const { asFragment } = render(<Link label="Button link" />);
    expect(asFragment()).toMatchSnapshot();
  });

  it("should display an icon", () => {
    const { asFragment } = render(
      <Link label="Back to projects" iconLeft="chevron_big_left" />
    );
    expect(asFragment()).toMatchSnapshot();
  });

  it("should get the correct value in the Anchor Element's href attribute", () => {
    const route = "/home";
    render(
      <NextLink href={route} passHref>
        <Link label="home" />
      </NextLink>
    );
    expect(screen.getByRole("link")).toHaveAttribute("href", route);
  });
});
