import type { MenuItemProps } from "@/components/shared/dropdown/Dropdown";
import type { UserPermission } from "@/types/auth/AuthUser";
import type { IconName } from "@urbint/silica";
import { useContext, useEffect, useState } from "react";
import { BodyText, Icon, SectionHeading } from "@urbint/silica";
import cloneDeep from "lodash/cloneDeep";
import router from "next/router";
import axiosRest from "@/api/customFlowApi";
import ToastContext from "@/components/shared/toast/context/ToastContext";
import CWFShare from "@/components/dynamicForm/ShareComponent/CWFShare";
import { Dialog } from "@/components/forms/Basic/Dialog";
import { isFormDeletable, isFormReopenable, isCopyAndRebriefAllowed } from "@/components/forms/Utils";
import ButtonDanger from "@/components/shared/button/danger/ButtonDanger";
import ButtonIcon from "@/components/shared/button/icon/ButtonIcon";
import ButtonSecondary from "@/components/shared/button/secondary/ButtonSecondary";
import Dropdown from "@/components/shared/dropdown/Dropdown";
import Modal from "@/components/shared/modal/Modal";
import CustomisedFromStateContext from "@/context/CustomisedDataContext/CustomisedFormStateContext";
import useCWFFormState from "@/hooks/useCWFFormState";
import useRestMutation from "@/hooks/useRestMutation";
import { useAuthStore } from "@/store/auth/useAuthStore.store";
import { CF_REDUCER_CONSTANTS } from "@/utils/customisedFormUtils/customisedForm.constants";
import { HTTP_STATUS_CODES } from "@/components/templatesComponents/error.utils";
import {
  type FormType,
  type UserFormMode,
  type WorkPackageData,
  FormStatus,
  UserFormModeTypes,
  CWFItemType,
} from "../../customisedForm.types";
import style from "../formPreview.module.scss";

type FormHeadingProps = {
  workPackageData?: WorkPackageData;
  formObject: FormType;
  setMode?: (mode: UserFormMode) => void;
};

const FormHeading = ({
  workPackageData: _workPackageData,
  formObject,
  setMode,
  
}: FormHeadingProps) => {
  const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false);
  const toastCtx = useContext(ToastContext);
  const [isEditAllowed, setIsEditAllowed] = useState(false);
  const [isDownloading, setIsDownloading] = useState(false); 
  const [openShareModal, setOpenShareModal] = useState(false);
  const [formStatus, setFormStatus] = useState(formObject.properties.status);
  const { setCWFFormStateDirty } = useCWFFormState();
  const heading = formObject.properties.title;
  const {
    me: { id: userId, permissions: userPermissions },
  } = useAuthStore();
  const isOwn = formObject?.created_by?.id === userId;

  const { project, location, startDate } = router.query;
  const { state, dispatch } = useContext(CustomisedFromStateContext)!;

  const { mutate: reopenForm } = useRestMutation<any>({
    endpoint: `/forms/${formObject.id}/reopen`,
    method: "put",
    axiosInstance: axiosRest,
    dtoFn: dataForm => dataForm,
    mutationOptions: {
      onSuccess: () => {
        setMode && setMode(UserFormModeTypes.EDIT);
        setFormStatus("in_progress");
        dispatch({
          type: CF_REDUCER_CONSTANTS.CHANGE_INITIAL_STATE,
          payload: {
            ...state.form,
            properties: {
              ...state.form.properties,
              status: "in_progress",
            },
          },
        });
      },
    },
  });

  const redirectionAfterDelete = () => {
    if (project) {
      router.replace(
        `/projects/${project}?location=${location}&startDate=${startDate}`
      );
    } else {
      router.replace("/template-forms");
    }
  };

  const { mutate: deleteForm } = useRestMutation<any>({
    endpoint: `/forms/${formObject.id}`,
    method: "delete",
    axiosInstance: axiosRest,
    dtoFn: dataForm => dataForm,
    mutationOptions: {
      onSuccess: () => {
        redirectionAfterDelete();
      },
    },
  });

  const { mutate: downloadPDF } = useRestMutation<any>({
    endpoint: `/pdf_download/forms/${formObject.id}?timezone=${encodeURIComponent(Intl.DateTimeFormat().resolvedOptions().timeZone)}`,
    method: "get",
    axiosInstance: axiosRest,
    axiosConfig: {
      responseType: "blob",
    },
    mutationOptions: {
      onSuccess: async (response: any) => {
        setIsDownloading(false); 

        const blob = new Blob([response.data], { type: "application/pdf" });
        const disposition = response.headers?.["content-disposition"];
        let filename = `form-${Date.now()}.pdf`;
        if (disposition) {
          const match = disposition.match(/filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/);
          if (match && match[1]) {
            filename = match[1].replace(/['"]/g, "");
          }
        }
        const url = window.URL.createObjectURL(blob);
        const link = document.createElement("a");
        link.href = url;
        link.setAttribute("download", filename);
        document.body.appendChild(link);
        link.click();
        link.remove();
        window.URL.revokeObjectURL(url);
      },
      onError: (error) => {
        setIsDownloading(false); 
        if(error?.response?.status === HTTP_STATUS_CODES.CONFLICT) {
          toastCtx?.pushToast("error", "You cannot download the PDF while the form is in Edit mode. Please save or cancel your changes first");
        }
      },
    },
  });

  const { mutate: createCopy } = useRestMutation<any>({
    endpoint: "/forms/",
    method: "post",
    axiosInstance: axiosRest,
    dtoFn: dataForm => dataForm,
    mutationOptions: {
      onSuccess: (response: any) => {
        const form = response.data;
        if (form) {
          router.push(`/template-forms/view?formId=${form.id}`)
        }
      },
    },
  });

  const resetSelectedData = (items: any[]) => {
    items.forEach(item => {
      if (item.type === CWFItemType.PersonnelComponent) {
        item.properties.attributes = [];
        item.properties.user_attachments = null;
        item.properties.user_comments = null;
        item.properties.user_value = [];
      }
      else if (item.type === CWFItemType.ReportDate) {
        item.properties.user_value = null;
      }
      if (item.contents && Array.isArray(item.contents)) {
        resetSelectedData(item.contents);
      }
    });
  };

  const handleCopyandRebriefClick = (type: string) => {
    const data = cloneDeep(state.form);
    data.contents.forEach(page => {
      page.properties.page_update_status = "default";
      if (page.contents && Array.isArray(page.contents)) {
        resetSelectedData(page.contents);
      }
    });
    const apiData = {
      contents: [...data.contents],
      properties: {
        ...data.properties,
        status: FormStatus.InProgress,
        report_start_date: null,
      },
      metadata: {
        ...data.metadata,
        copy_and_rebrief: {
          ...data.metadata?.copy_and_rebrief,
          ...(type === 'copy' ? { copy_linked_form_id: data.id } : { rebrief_linked_form_id: data.id }),
        }
      },
      template_id: data.template_id,
      component_data: {
        ...data.component_data,
      }
    };
    createCopy(apiData);
  }

  const handleDeleteCWF = () => {
    setIsDeleteDialogOpen(true);
    deleteForm({});
  };
  const handleReopenCWF = () => {
    reopenForm({});
  };

  const onDeleteDialogOpen = () => {
    setIsDeleteDialogOpen(true);
  };

  const handleDownloadPDF = () => {
    setIsDownloading(true);
    downloadPDF({});
  };

  const onDeleteDialogClose = () => {
    setIsDeleteDialogOpen(false);
  };

  const getMenuItems = (): MenuItemProps[] => [
    ...(formObject?.edit_expiry_days === 0
      ? [
          {
            label: "Edit",
            icon: "edit" as IconName,
            onClick: handleReopenCWF,
          },
        ]
      : []),
    {
      label: "Rebrief",
      icon: "group",
      onClick: () => handleCopyandRebriefClick('rebrief'),
      infoText: "For job scope or condition changes"
    },
    {
      label: "Make a copy",
      icon: "copy",
      onClick: () => handleCopyandRebriefClick('copy'),
    },
    ...(formStatus === FormStatus.Completed
      ? [
          {
            label: isDownloading ? "Downloading..." : "Download PDF",
            icon: isDownloading ? ("spinner" as IconName) : ("download" as IconName),
            onClick: handleDownloadPDF,
            disabled: isDownloading, 
          },
        ]
      : []),
    {
      label: "Delete",
      icon: "trash_empty",
      onClick: onDeleteDialogOpen,
    },
  ];

  const filterActionsMenuItems = (status: string): MenuItemProps[] => {
    if (!status) {
      return [];
    }
    let menuItems = getMenuItems();
    const { is_copy_enabled, is_rebrief_enabled } = state.form.metadata?.copy_and_rebrief ?? {};
    const formNotReopenable = !isFormReopenable(isOwn, status, userPermissions);
    const copyAllowed = isCopyAndRebriefAllowed(isOwn, userPermissions, is_copy_enabled);
    const rebriefAllowed = isCopyAndRebriefAllowed(isOwn, userPermissions, is_rebrief_enabled);

    if (status === "in_progress" || formNotReopenable) {
      menuItems = menuItems.filter(
        (item: MenuItemProps) => item.label !== "Edit"
      );
    }
    if (!copyAllowed) {
      menuItems = menuItems.filter(
        (item: MenuItemProps) => item.label !== "Make a copy"
      );
    }
    if (!rebriefAllowed || (status === FormStatus.Completed && new Date(formObject?.edit_expiry_time ?? 0).getTime() <
    new Date().getTime())) {
      menuItems = menuItems.filter(
        (item: MenuItemProps) => item.label !== "Rebrief"
      );
    }
    const formNotDeletable = !isFormDeletable(isOwn, status, userPermissions);
    if (formNotDeletable) {
      menuItems = menuItems.filter(
        (item: MenuItemProps) => item.label !== "Delete"
      );
    }
    return menuItems;
  };

  const renderDropdownMenu = () => {
    const filteredMenuItems = filterActionsMenuItems(formStatus);
    return (
      !router.pathname.includes("/templates/create") &&
      filteredMenuItems.length > 0
    );
  };

  useEffect(() => {
    if (state.isFormDirty && isDeleteDialogOpen) {
      setCWFFormStateDirty(false);
    }
  }, [isDeleteDialogOpen, state.isFormDirty, setCWFFormStateDirty]);

  useEffect(() => {
    setFormStatus(formObject.properties.status);
  }, [formObject.properties.status]);

  useEffect(() => {
    const isEdit =
      new Date(formObject?.edit_expiry_time ?? 0).getTime() >
        new Date().getTime() ||
      userPermissions.includes("ALLOW_EDITS_AFTER_EDIT_PERIOD" as UserPermission);
    setIsEditAllowed(isEdit);
    if (
      formStatus === FormStatus.Completed &&
      isEditAllowed &&
      formObject?.edit_expiry_days != 0
    ) {
      setMode && setMode(UserFormModeTypes.EDIT);
    }
  }, [isEditAllowed]);

  return (
    <>
      {isDeleteDialogOpen && (
        <Dialog
          size="flex"
          header={<DialogHeader onClose={onDeleteDialogClose} />}
          footer={
            <div className="flex flex-col gap-2">
              <div className="flex flex-row justify-end gap-2">
                <ButtonSecondary label="Cancel" onClick={onDeleteDialogClose} />
                <ButtonDanger label="Delete" onClick={handleDeleteCWF} />
              </div>
            </div>
          }
        >
          <BodyText>
            Deleting this form will remove all the associated details as well as
            remove it from any future report
          </BodyText>
        </Dialog>
      )}
      {openShareModal && (
        <Modal
          title=""
          isOpen={openShareModal}
          closeModal={() => setOpenShareModal(false)}
        >
          <div className="flex justify-center mb-2">
            <CWFShare formId={state.form.id}/>
          </div>
        </Modal>
      )}
      <div className={style.formPreviewHeading}>
        <div>
          <h1 className={style.formPreviewHeading__headingPreview}>
            {heading}
          </h1>
        </div>
        <div className="flex">
          {state.form.template_id && (
            <button className="mr-4" onClick={() => setOpenShareModal(true)}>
              <Icon name="share" className="text-neutral-shade-75"/>
            </button>
          )}
          {renderDropdownMenu() && (
            <Dropdown
              className="z-10"
              menuItems={[filterActionsMenuItems(formStatus)]}
            >
              <ButtonIcon iconName="hamburger" />
            </Dropdown>
          )}
        </div>
      </div>
    </>
  );
};

function DialogHeader({ onClose }: { onClose: () => void }): JSX.Element {
  return (
    <div className="flex flex-row justify-between">
      <SectionHeading className="text-xl font-semibold">
        Are you sure you want to do this?
      </SectionHeading>
      <ButtonIcon iconName="close_big" onClick={onClose} />
    </div>
  );
}

export default FormHeading;
