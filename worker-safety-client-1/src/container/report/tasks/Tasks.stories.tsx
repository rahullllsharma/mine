import type { ComponentMeta, ComponentStory } from "@storybook/react";
import type { TasksProps } from "./Tasks";
import { action } from "@storybook/addon-actions";
import { DevTool } from "@hookform/devtools";
import { useForm } from "react-hook-form";
import { useProjects } from "@/hooks/useProjects";
import ButtonPrimary from "@/components/shared/button/primary/ButtonPrimary";
import { transformTasksToListTasks } from "@/utils/task";
import { WrapperForm } from "@/utils/dev/storybook";
import Tasks from "./Tasks";

type StoryProps = TasksProps & { withSubmit?: boolean };

// eslint-disable-next-line react-hooks/rules-of-hooks
const { tasks } = useProjects()[0].locations[0];

export default {
  title: "Container/Report/Tasks",
  component: Tasks,
  argTypes: {
    withSubmit: { control: "boolean" },
  },
} as ComponentMeta<typeof Tasks>;

const Template: ComponentStory<typeof Tasks> = (args: StoryProps) => {
  // eslint-disable-next-line @typescript-eslint/ban-ts-comment
  // @ts-ignore
  const listTasks = transformTasksToListTasks(args?.tasks || []);
  const methods = useForm({});

  const onSubmitHandler = (
    formData: Record<string, Record<string, unknown>>
  ) => {
    // eslint-disable-next-line @typescript-eslint/no-shadow
    const { tasks } = formData;

    // after updating the form, we may need to update the original tasks
    // with the current changes. eg,
    const updatedTaskSelection = listTasks.map(({ id, name }) => {
      return {
        id,
        name,
        isSelected: !!tasks[id],
      };
    });

    return action("on submit")({
      formData: tasks,
      updatedTasks: updatedTaskSelection,
    });
  };

  return (
    <WrapperForm methods={methods}>
      <form onSubmit={methods.handleSubmit(onSubmitHandler)}>
        <Tasks {...args} tasks={listTasks} />
        {args.withSubmit && <ButtonPrimary type="submit" label="Button" />}
      </form>
      <DevTool control={methods.control} />
    </WrapperForm>
  );
};

export const Default = Template.bind({});
Default.args = {
  // eslint-disable-next-line @typescript-eslint/ban-ts-comment
  // @ts-ignore
  tasks,
};
Default.decorators = [
  Story => (
    <div className="overflow-y-scroll h-screen p-1">
      <div className="my-4 text-sm text-brand-urbint-60 bg-brand-gray-10 p-2 border-l-2">
        Since we don`t include state in the <code>Tasks</code> component, it`s
        up to the parent to pass down the props including a `tasks` and
        `setTasks` as props.
        <p className="mt-2">
          To make it easy (and saner), don`t forget to augment the `tasks` array
          with the `isSelected` option.
        </p>
        <p className="mt-2">
          Use the <code>transformTasksToListTasks(tasks)</code> to help out
        </p>
      </div>
      <Story />
    </div>
  ),
];

export const Readonly = Template.bind({});
Readonly.args = {
  // eslint-disable-next-line @typescript-eslint/ban-ts-comment
  // @ts-ignore
  tasks,
  isCompleted: true,
};

export const WithEmptyState = Template.bind({});
WithEmptyState.args = {};
