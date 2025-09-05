import type { ComponentMeta, ComponentStory } from "@storybook/react";
import type { UploadConfigs } from "../Upload";
import { useForm } from "react-hook-form";

import FileUploadPolicies from "@/graphql/queries/fileUploadPolicies.gql";
import { WrapperForm } from "@/utils/dev/storybook";
import UploadDocuments from "./UploadDocuments";

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
  title: "Components/Upload/Documents",
  component: UploadDocuments,
  argTypes: { fieldArrayName: { control: false } },
  parameters: appoloUploadMockParameters,
} as ComponentMeta<typeof UploadDocuments>;

const Template: ComponentStory<typeof UploadDocuments> = args => {
  const methods = useForm({
    defaultValues: {
      documents: [],
    },
  });

  return (
    <WrapperForm methods={methods}>
      <UploadDocuments {...args} />
    </WrapperForm>
  );
};

const configs: UploadConfigs = {
  title: "Documents",
  buttonLabel: "Add documents",
  buttonIcon: "file_blank_outline",
  allowedFormats: ".pdf,.doc,.docx,.xls,.xlsx,.ppt,.pptx",
};

const configsAllowOnlyOneFile: UploadConfigs = {
  ...configs,
  allowMultiple: false,
};

export const Playground = Template.bind({});
Playground.args = {
  configs,
  fieldArrayName: "attachments.documents",
};

export const SingleFile = Template.bind({});
SingleFile.args = {
  configs: configsAllowOnlyOneFile,
  fieldArrayName: "attachments.documents",
};
