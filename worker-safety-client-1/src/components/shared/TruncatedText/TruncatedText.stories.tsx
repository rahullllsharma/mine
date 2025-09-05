import type { ComponentMeta, ComponentStory } from "@storybook/react";
import { TruncatedText } from "./TruncatedText";

export default {
  title: "Components/TruncatedText",
  component: TruncatedText,
} as ComponentMeta<typeof TruncatedText>;

export const Playground: ComponentStory<typeof TruncatedText> = args => (
  <TruncatedText {...args} />
);

Playground.args = {
  text: "Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
  maxCharacters: 20,
  showEllipsis: true,
};
