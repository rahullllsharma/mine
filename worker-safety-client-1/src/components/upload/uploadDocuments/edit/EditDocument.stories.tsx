import type { ComponentMeta, ComponentStory } from "@storybook/react";
import type { UploadItem } from "../../Upload";
import { nanoid } from "nanoid";
import { WrapperModal } from "@/utils/dev/storybook";
import EditDocument from "./EditDocument";

export default {
  title: "Components/Upload/Documents/Edit",
  component: EditDocument,
  argTypes: { onSave: { action: "onSave" }, onCancel: { action: "onCancel" } },
} as ComponentMeta<typeof EditDocument>;

const Template: ComponentStory<typeof EditDocument> = args => (
  <EditDocument {...args} />
);

const ModalTemplate: ComponentStory<typeof EditDocument> = args => (
  <WrapperModal title="Crew Member Info">
    <EditDocument {...args} />
  </WrapperModal>
);

const file: UploadItem = {
  id: nanoid(),
  name: "CrewMember.xls",
  displayName: "CrewMember.xls",
  size: "564 KB",
  date: "11/22/2021",
  time: "10:50PM",
  url: "",
  signedUrl: "",
};

const fileWithCategory: UploadItem = {
  ...file,
  category: "JHA",
};

export const Playground = Template.bind({});
Playground.args = {
  file,
};

export const PlaygroundWithFileCategory = Template.bind({});
PlaygroundWithFileCategory.args = {
  file: fileWithCategory,
};

export const WithModal = ModalTemplate.bind({});
WithModal.args = {
  file,
};

export const WithModalAndFileCategory = ModalTemplate.bind({});
WithModalAndFileCategory.args = {
  file: fileWithCategory,
};
