import type {
  ActivePageObjType,
  ActivitiesAndTasksFormType,
  CWFLocationType,
  CWFNearestHospitalType,
  CWFSiteConditionsType,
  FormComponentPayloadType,
  FormElement,
  HazardsAndControlsFormType,
  PersonnelComponentType,
} from "@/components/templatesComponents/customisedForm.types";
import { BodyText } from "@urbint/silica";
import { ErrorBoundary } from "react-error-boundary";
import parse from "html-react-parser";
import FormSection from "@/components/templatesComponents/CreateTemplateLayout/PreviewComponent/FormRenderer/FormComponents/Section/FormSection";
import {
  CWFItemType,
  UserFormModeTypes,
} from "@/components/templatesComponents/customisedForm.types";
import FieldRenderer from "@/components/templatesComponents/PreviewComponents";
import ImageGallery from "../AttachmentComponents/Photos/ImageGallery";
import PhotoForm from "../AttachmentComponents/Photos/PhotoUploaderForm";
import CWFHazardsAndControls from "../HazardAndControlsComponents/CWFHazardsAndControls";
import CWFActivitiesAndTask from "../ActivitiesAndTaskComponents/CWFActivitiesAndTask";
import CWFSiteConditions from "../SiteConditionsComponent/CWFSiteConditions";
import LocationInSummary from "../LocationComponent/LocationInSummary";
import { RenderNearestHospitalInSummary } from "../NearestHospitalComponents/RenderNearestHospitalInSummary";
import { RenderPersonnelComponentInSummary } from "../PersonnelComponent/RenderPersonnelComponentInSummary";
import { convertToPhotoUploadItem } from "../AttachmentComponents/Photos/utils";

const filterChildInstances = (
  parentElement: FormElement,
  element: FormElement
) => {
  return (
    parentElement.contents?.filter(
      parentElementContent =>
        parentElementContent.type === CWFItemType.Section &&
        parentElementContent.properties.child_instance &&
        parentElementContent.order === element.order
    ) || []
  );
};

const getRepeatableSectionTitle = (
  element: FormElement,
  parentElement: FormElement
) => {
  let title = element.properties.title ?? "Section";

  if (element.properties.is_repeatable && parentElement) {
    const childInstances = filterChildInstances(parentElement, element);

    if (childInstances.length > 0) {
      title += ` (${childInstances.length})`;
    }
  }

  if (element.properties.child_instance && parentElement) {
    const siblingInstances = filterChildInstances(parentElement, element);

    const instanceIndex = siblingInstances.findIndex(
      inst => inst.id === element.id
    );
    if (instanceIndex !== -1) {
      title += ` (${instanceIndex + 1}/${siblingInstances.length})`;
    }
  }

  return title;
};

export const renderElementInSummary = (
  element: FormElement,
  activePageDetails: ActivePageObjType,
  parentElement: FormElement
): JSX.Element | string | undefined => {
  const content = (() => {
    switch (element.type) {
      case CWFItemType.Section:
        return (
          !element.properties.is_repeatable && (
            <div className="rounded-md">
              <BodyText className="text-[20px] font-semibold">
                {getRepeatableSectionTitle(element, parentElement)}
              </BodyText>
              <FormSection
                id={element.id}
                type={element.type}
                order={element.order}
                item={element}
                activePageDetails={activePageDetails}
                previousContent={null}
                nextContent={null}
                properties={element.properties}
                contents={element.contents}
                mode={UserFormModeTypes.PREVIEW}
                activeWidgetDetails={null}
                inSummary={true}
              />
            </div>
          )
        );
      case CWFItemType.Choice:
      case CWFItemType.Dropdown:
      case CWFItemType.Contractor:
      case CWFItemType.Region:
      case CWFItemType.InputPhoneNumber:
      case CWFItemType.YesOrNo:
      case CWFItemType.InputText:
      case CWFItemType.Slide:
      case CWFItemType.InputDateTime:
      case CWFItemType.ReportDate:
      case CWFItemType.InputNumber:
      case CWFItemType.InputLocation:
      case CWFItemType.InputEmail:
      case CWFItemType.Checkbox:
        return (
          <FieldRenderer
            content={element}
            order={element.order}
            activePageDetails={activePageDetails}
            mode={UserFormModeTypes.PREVIEW}
            inSummary={true}
          />
        );
      case CWFItemType.RichTextEditor:
        return (
          <div className="list-disc">{parse(element.properties.data)}</div>
        );
      case CWFItemType.Attachment:
        return element.properties.attachment_type === "photo" &&
          element.properties.user_value.length > 0 ? (
          <ImageGallery
            photos={convertToPhotoUploadItem(element.properties.user_value)}
            title={element.properties.title}
            inSummary={true}
          />
        ) : (
          <PhotoForm
            section={null}
            activePageDetails={activePageDetails}
            mode={UserFormModeTypes.PREVIEW}
            item={element as FormComponentPayloadType}
            inSummary={true}
          />
        );
      case CWFItemType.HazardsAndControls:
        return (
          <ErrorBoundary FallbackComponent={() => null}>
            <CWFHazardsAndControls
              section={null}
              activePageDetails={activePageDetails}
              mode={UserFormModeTypes.PREVIEW}
              item={element as HazardsAndControlsFormType}
              inSummary={true}
            />
          </ErrorBoundary>
        );
      case CWFItemType.ActivitiesAndTasks:
        return (
          <CWFActivitiesAndTask
            section={null}
            activePageDetails={activePageDetails}
            mode={UserFormModeTypes.PREVIEW}
            item={element as ActivitiesAndTasksFormType}
            inSummary={true}
          />
        );
      case CWFItemType.SiteConditions:
        return (
          <CWFSiteConditions
            item={element as CWFSiteConditionsType}
            section={null}
            activePageDetails={activePageDetails}
            mode={UserFormModeTypes.PREVIEW}
            inSummary={true}
          />
        );
      case CWFItemType.Location:
        return (
          <LocationInSummary
            item={element as CWFLocationType}
            type={element.type}
          />
        );
      case CWFItemType.NearestHospital:
        return (
          <RenderNearestHospitalInSummary
            item={element as CWFNearestHospitalType}
          />
        );
      case CWFItemType.PersonnelComponent:
        return (
          <RenderPersonnelComponentInSummary
            item={element as PersonnelComponentType}
          />
        );
      case CWFItemType.Summary:
        return "";
    }
  })();

  if (!content) return undefined;
  return <div>{content}</div>;
};
