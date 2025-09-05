import type { ComponentMeta, ComponentStory } from "@storybook/react";
import React from "react";

import FieldDatePicker from "./FieldDatePicker";

export default {
  title: "Silica/Field/FieldDatePicker",
  component: FieldDatePicker,
  argTypes: { onChange: { action: "clicked" } },
} as ComponentMeta<typeof FieldDatePicker>;

const Template: ComponentStory<typeof FieldDatePicker> = args => (
  <FieldDatePicker {...args} />
);

export const Playground = Template.bind({});
Playground.args = {
  label: "Work Start Date",
  required: true,
};

const currentDate = new Date().toISOString().substring(0, 10);

export const Readonly = Template.bind({});
Readonly.args = {
  label: "Work Start Date",
  required: true,
  defaultValue: currentDate,
  readOnly: true,
};

export const WithADefaultValue: ComponentStory<typeof FieldDatePicker> =
  args => (
    <div>
      <p>
        With <code>defaultValue</code>, it will pass the initial date for the
        input <b>however</b> the element is still <b>uncontrolled</b>
      </p>
      <p>
        meaning that the <code>parent</code> needs to keep track of the changes
        mande using the <code>`onChange`</code> method
      </p>
      <br />
      <FieldDatePicker {...args} />
    </div>
  );
WithADefaultValue.args = {
  label: "Work Start Date",
  required: true,
  defaultValue: currentDate,
};

export const WithValue: ComponentStory<typeof FieldDatePicker> = args => {
  const [value, setValue] = React.useState(currentDate);
  const onChangeHandler = (date?: string) => {
    date && setValue(date);
  };

  return (
    <div>
      <p>
        Using <code>value</code> means that the component is now
        <b>controlled</b> by the parent component.
      </p>
      <p>
        Now the responsibility of updating the component and keep it in sync is
        from the parent (use React DevTools to check the state updates)
      </p>
      <br />
      <p>current date: {value}</p>
      <FieldDatePicker
        {...args}
        defaultValue={currentDate}
        value={value}
        onChange={onChangeHandler}
      />
    </div>
  );
};
WithValue.args = {
  label: "Work Start Date",
  required: true,
  defaultValue: currentDate,
};
