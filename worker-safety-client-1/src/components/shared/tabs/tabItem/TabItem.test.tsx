import { render, screen } from "@testing-library/react";
import TabItem from "./TabItem";

describe(TabItem.name, () => {
  it('should render with a text element with the same value given by the "value" prop', () => {
    render(<TabItem value="Lorem ipsum" />);
    screen.getByText(/lorem ipsum/i);
  });

  it('should render with an icon if the "icon" prop is passed', () => {
    const { asFragment } = render(
      <TabItem value="Lorem ipsum" icon="settings_future" />
    );
    expect(asFragment()).toMatchSnapshot();
  });
});
