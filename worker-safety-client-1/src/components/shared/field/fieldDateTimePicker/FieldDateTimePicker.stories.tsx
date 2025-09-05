import type { ComponentMeta, ComponentStory } from "@storybook/react";
import React from "react";

import FieldDateTimePicker from "./FieldDateTimePicker";

export default {
  title: "Silica/Field/FieldDateTimePicker",
  component: FieldDateTimePicker,
  argTypes: { onChange: { action: "selected" } },
} as ComponentMeta<typeof FieldDateTimePicker>;

const Template: ComponentStory<typeof FieldDateTimePicker> = args => (
  <FieldDateTimePicker {...args} />
);

export const Playground = Template.bind({});
Playground.args = {
  label: "Work Start Date and time",
  required: false,
  placeholder: "Placeholder for the input",
};

// https://developer.mozilla.org/en-US/docs/Web/HTML/Element/input/datetime-local#the_y10k_problem_often_client-side
// TODO: Find a way to properly validate YYYY-MM-DDThh:mm

const date = new Date("2022-01-11T21:58:59.708Z").toISOString();
const currentTime = date.substring(0, ((date.indexOf("T") | 0) + 6) | 0);

export const Readonly = Template.bind({});
Readonly.args = {
  label: "Work Start Date and time",
  required: true,
  defaultValue: currentTime,
  readOnly: true,
};

export const WithADefaultValue: ComponentStory<typeof FieldDateTimePicker> =
  args => (
    <div>
      <p>
        With <code>defaultValue</code>, it will pass the initial time for the
        input <b>however</b> the element is still <b>uncontrolled</b>
      </p>
      <p>
        meaning that the <code>parent</code> needs to keep track of the changes
        mande using the <code>`onChange`</code> method
      </p>
      <br />
      <FieldDateTimePicker
        {...args}
        value="2022-04-29T11:10"
        defaultValue="2022-04-29T10:10"
      />
    </div>
  );
WithADefaultValue.args = {
  label: "Work Start Date and time",
  required: true,
  defaultValue: currentTime,
};

export const WithValue: ComponentStory<typeof FieldDateTimePicker> = args => {
  const [value, setValue] = React.useState(currentTime);
  const onChangeHandler = (time?: string) => {
    time && setValue(time);
  };

  return (
    <div>
      <p>
        Using <code>value</code> means that the component is now{" "}
        <b>controlled</b> by the parent component.
      </p>
      <p>
        Now the responsibility of updating the component and keep it in sync is
        from the parent (use React DevTools to check the state being updated)
      </p>
      <br />
      <p>current time: {value}</p>
      <FieldDateTimePicker
        {...args}
        defaultValue={currentTime}
        value={value}
        onChange={onChangeHandler}
      />
    </div>
  );
};
WithValue.args = {
  label: "Work Start Date and time",
  required: true,
  defaultValue: currentTime,
};
