import { render, screen } from "@testing-library/react";
import PageLayout from "./PageLayout";

describe(PageLayout.name, () => {
  it("should render correctly including a header and footer when passed", () => {
    render(
      <PageLayout
        header={<header>header</header>}
        footer={<footer>footer</footer>}
      >
        <p>content</p>
      </PageLayout>
    );

    screen.getByRole("banner");
    screen.getByText(/content/i);
    screen.getByRole("contentinfo");
  });
});
