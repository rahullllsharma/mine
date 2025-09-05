import type { ComponentMeta, ComponentStory } from "@storybook/react";
import React from "react";

import FieldTimePicker from "./FieldTimePicker";

export default {
  title: "Silica/Field/FieldTimePicker",
  component: FieldTimePicker,
  argTypes: { onChange: { action: "selected" } },
} as ComponentMeta<typeof FieldTimePicker>;

const Template: ComponentStory<typeof FieldTimePicker> = args => (
  <FieldTimePicker {...args} />
);

export const Playground = Template.bind({});
Playground.args = {
  label: "Work Start Time",
  required: false,
  placeholder: "Placeholder for the input",
};

const currentTime = new Date("2022-01-11T21:58:59.708Z")
  .toISOString()
  .substring(11, 16);

export const Readonly = Template.bind({});
Readonly.args = {
  label: "Work Start Date",
  required: true,
  defaultValue: currentTime,
  readOnly: true,
};

export const WithADefaultValue: ComponentStory<typeof FieldTimePicker> =
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
      <FieldTimePicker {...args} />
    </div>
  );
WithADefaultValue.args = {
  label: "Work Start Date",
  required: true,
  defaultValue: currentTime,
};

export const WithValue: ComponentStory<typeof FieldTimePicker> = args => {
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
      <FieldTimePicker
        {...args}
        defaultValue={currentTime}
        value={value}
        onChange={onChangeHandler}
      />
    </div>
  );
};
WithValue.args = {
  label: "Work Start Date",
  required: true,
  defaultValue: currentTime,
};
