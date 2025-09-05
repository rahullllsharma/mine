import type { ComponentMeta, ComponentStory } from "@storybook/react";
import type { UploadConfigs } from "../Upload";
import { useForm } from "react-hook-form";

import FileUploadPolicies from "@/graphql/queries/fileUploadPolicies.gql";
import { WrapperForm } from "@/utils/dev/storybook";
import UploadPhotos from "./UploadPhotos";

const uploadPoliciesMock = {
  request: {
    query: FileUploadPolicies,
    variables: {
      count: 1,
    },
  },
  result: {
    data: {
      fileUploadPolicies: [
        {
          id: "",
          url: "",
          fields: "",
        },
      ],
    },
  },
};

const appoloUploadMockParameters = {
  apolloClient: {
    mocks: [uploadPoliciesMock],
  },
};

export default {
  title: "Components/Upload/Photos",
  component: UploadPhotos,
  argTypes: { fieldArrayName: { control: false } },
  parameters: appoloUploadMockParameters,
} as ComponentMeta<typeof UploadPhotos>;

const Template: ComponentStory<typeof UploadPhotos> = args => {
  const methods = useForm({
    defaultValues: {
      documents: [],
    },
  });

  return (
    <WrapperForm methods={methods}>
      <UploadPhotos {...args} />
    </WrapperForm>
  );
};

const configs: UploadConfigs = {
  title: "Photos",
  buttonLabel: "Add photos",
  buttonIcon: "image_alt",
  allowedFormats: "apng,.avif,.gif,.jpg,.jpeg,.png,.svg,.webp",
};

const configsAllowOnlyOneFile: UploadConfigs = {
  ...configs,
  allowMultiple: false,
};

export const Playground = Template.bind({});
Playground.args = {
  configs,
  fieldArrayName: "attachments.photos",
};

export const SingleFile = Template.bind({});
SingleFile.args = {
  configs: configsAllowOnlyOneFile,
  fieldArrayName: "attachments.photos",
};
