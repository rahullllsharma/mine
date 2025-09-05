import React from "react";
import CustomisedFormStateProvider from "@/context/CustomisedDataContext/CustomisedFormStateProvider";
import CreateTemplateHome from "@/components/templatesComponents/CreateTemplateHome";

const CreateTemplate = () => {
  return (
    <CustomisedFormStateProvider>
      <CreateTemplateHome />
    </CustomisedFormStateProvider>
  );
};

export default CreateTemplate;