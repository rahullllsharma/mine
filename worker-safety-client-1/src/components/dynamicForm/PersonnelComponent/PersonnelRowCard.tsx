/* PersonelRowCard.tsx – complete file */
import type { FileInputsCWF } from "@/types/natgrid/jobsafetyBriefing";
import type { Props } from "@/components/templatesComponents/customisedForm.types";
import { BodyText, Icon } from "@urbint/silica";
import { useCallback, useContext, useState, useEffect } from "react";
import cx from "classnames";
import { UserFormModeTypes } from "@/components/templatesComponents/customisedForm.types";
import Labeled from "@/components/forms/Basic/Labeled";
import CustomisedFromStateContext from "@/context/CustomisedDataContext/CustomisedFormStateContext";
import { CF_REDUCER_CONSTANTS } from "@/utils/customisedFormUtils/customisedForm.constants";
import Checkbox from "@/components/shared/checkbox/Checkbox";
import Tooltip from "@/components/shared/tooltip/Tooltip";
import {
  formEventEmitter,
  FORM_EVENTS,
} from "@/context/CustomisedDataContext/CustomisedFormStateProvider";
import SignatureField from "./SignatureField";

export default function PersonelRowCard({
  person,
  item,
  mode,
  onRequestDelete,
  onSignatureUpdate,
  onToggleAttr,
  singleAttrMap,
}: Props) {
  const isPreviewMode = mode === UserFormModeTypes.PREVIEW;
  const [showAttrErrors, setShowAttrErrors] = useState(false);

  useEffect(() => {
    const sub = formEventEmitter.addListener(FORM_EVENTS.SHOW_ATTR_ERRORS, () =>
      setShowAttrErrors(true)
    );
    return () => sub.remove();
  }, []);
  const { dispatch } = useContext(CustomisedFromStateContext)!;
  const handleSignatureSave = useCallback(
    (fileMeta: FileInputsCWF) => {
      dispatch({
        type: CF_REDUCER_CONSTANTS.PERSONNEL_COMPONENT_ADD_DATA,
        payload: {
          componentId: item.id,
          rowId: person.id,
          name: person.name,
          signature: fileMeta,
          employeeNumber: person.employeeNumber ?? "",
          jobTitle: person.jobTitle ?? "",
          attrIds: person.attrIds ?? [],
          type: person.type ?? "",
          displayName: person.displayName ?? "",
          email: person.email ?? "",
          departmentName: person.departmentName ?? "",
          managerId: person.managerId ?? "",
          managerEmail: person.managerEmail ?? "",
          managerName: person.managerName ?? "",
        },
      });
      onSignatureUpdate(fileMeta);
    },
    [dispatch, item.id, person, onSignatureUpdate]
  );

  const attrs = item.properties.attributes ?? [];
  const isAttrMissing = (attr: typeof attrs[number]): boolean => {
    if (!showAttrErrors || !attr.is_required_for_form_completion) return false;
    const checkedSomewhere =
      attr.applies_to_user_value === "single_name"
        ? Boolean(singleAttrMap[attr.attribute_id])
        : (item.properties.user_value ?? []).some((row: any) =>
            (row.selected_attribute_ids ?? []).includes(attr.attribute_id)
          );

    return !checkedSomewhere;
  };

  const renderAttr = (attr: typeof attrs[number]) => {
    const single = attr.applies_to_user_value === "single_name";
    const checked = single
      ? singleAttrMap[attr.attribute_id] === person.id
      : !!person.attrIds?.includes(attr.attribute_id);
    const disabled =
      single &&
      !!singleAttrMap[attr.attribute_id] &&
      singleAttrMap[attr.attribute_id] !== person.id;
    const showErr = isAttrMissing(attr);
    const helper = `${attr.attribute_name} is required. Select it for ${
      single ? "one person." : "one or more people."
    }`;

    return (
      <div key={attr.attribute_id} className="flex flex-col gap-[2px] text-sm">
        <div className="flex items-center gap-2">
          <label
            className={cx(
              "flex items-center gap-2",
              disabled && !checked
                ? "opacity-50 cursor-not-allowed"
                : "cursor-pointer"
            )}
          >
            <Checkbox
              className="h-4 w-4 accent-brand-urbint-40"
              disabled={disabled || isPreviewMode}
              checked={checked}
              onChange={() => !isPreviewMode && onToggleAttr(attr.attribute_id)}
              hasError={showErr}
            />
            {attr.attribute_name}
          </label>
          {single && (
            <Tooltip
              title="This attribute can only be selected for one person."
              className="max-w-xl"
              position="right"
            >
              <Icon
                name="info_circle"
                className="w-4 h-4 text-neutral-60 cursor-pointer"
                aria-label="single-name attribute info"
              />
            </Tooltip>
          )}
        </div>

        {showErr && (
          <span className="text-xs text-red-600 leading-tight">{helper}</span>
        )}
      </div>
    );
  };
  return (
    <div className="mt-4 rounded-lg border border-neutral-200 bg-gray-100 p-4">
      <div className="flex items-center gap-3">
        <div className="flex-1 min-w-[240px]">
          <Labeled label="Name *">
            <div className="h-10 border border-gray-300 rounded-md mb-2 px-3 py-2 bg-white flex items-center justify-between">
              {person.name}
              {person.jobTitle ? ` (${person.jobTitle})` : ""}

              {person.employeeNumber && (
                <BodyText className="text-sm">{person.employeeNumber}</BodyText>
              )}
            </div>
          </Labeled>
        </div>
        {!isPreviewMode && (
          <Icon
            name="trash_empty"
            className={`border rounded-md border-brand-gray-40 mt-4 w-10 h-10 flex items-center justify-center ${
              isPreviewMode ? "opacity-50 cursor-not-allowed" : "cursor-pointer"
            }`}
            onClick={() => !isPreviewMode && onRequestDelete()}
          />
        )}
      </div>
      {attrs.length > 0 && (
        <div className="mt-3 flex flex-col gap-1 mb-2">
          {attrs.map(renderAttr)}
        </div>
      )}
      <SignatureField
        displayName={person.name}
        initialFile={person.signature as FileInputsCWF}
        onSignature={handleSignatureSave}
        disabled={isPreviewMode}
      />
    </div>
  );
}
