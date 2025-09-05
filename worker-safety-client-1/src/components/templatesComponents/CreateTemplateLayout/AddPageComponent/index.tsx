import type { MenuItemProps } from "@/components/shared/dropdown/Dropdown";
import type {
  ActivePageObjType,
  DeletePageDetails,
  ModeTypePageSection,
  PageType,
} from "../../customisedForm.types";
import cloneDeep from "lodash/cloneDeep";
import { useContext, useEffect, useState } from "react";
import ButtonIcon from "@/components/shared/button/icon/ButtonIcon";
import Dropdown from "@/components/shared/dropdown/Dropdown";
import ToastContext from "@/components/shared/toast/context/ToastContext";
import CustomisedFromStateContext from "@/context/CustomisedDataContext/CustomisedFormStateContext";
import { CF_REDUCER_CONSTANTS } from "@/utils/customisedFormUtils/customisedForm.constants";
import { CWFItemType } from "../../customisedForm.types";
import SvgButton from "../../ButtonComponents/SvgButton/SvgButton";
import style from "../createTemplateStyle.module.scss";
import AddPageForm from "./AddPageForm";
import DeletePageAction from "./DeletePageAction";
import DeletePageConfirmationModal from "./DeletePageConfirmationModal";
import DragPageAction from "./DragPageAction";
import EditPageAction from "./EditPageAction";
import MockPageListComponent from "./MockPageListComponent";
import PageListComponent from "./PageList";

type AddPageComponentProps = {
  newPageTitle: string;
  setNewPageTitle: (item: string) => void;
  activePageDetails: ActivePageObjType;
  setActivePageDetails: (item: ActivePageObjType) => void;
  subPageTitle: string;
  setSubPageTitle: (item: string) => void;
  parentPage: string;
  setParentPage: (item: string) => void;
  mode: ModeTypePageSection;
  setMode: (item: ModeTypePageSection) => void;
};

const AddPageComponent = ({
  newPageTitle,
  setNewPageTitle,
  activePageDetails,
  setActivePageDetails,
  subPageTitle,
  setSubPageTitle,
  parentPage,
  setParentPage,
  mode,
  setMode,
}: AddPageComponentProps) => {
  const [deletePageDetails, setDeletePageDetails] = useState<
    DeletePageDetails[]
  >([]);
  const [deletePageReset, setDeletePageReset] = useState(false);
  const { state, dispatch } = useContext(CustomisedFromStateContext)!;

  const [deletePageModalOpen, setDeletePageModalOpen] = useState(false);

  const toastCtx = useContext(ToastContext);

  const [pageEditDetails, setPageEditDetails] = useState(
    cloneDeep(state.form.contents)
  );

  const [mockPageContents, setMockPageContents] = useState<PageType[]>([]);

  useEffect(() => {
    if (state) {
      setMockPageContents(cloneDeep(state.form.contents));
    }
    console.log(pageEditDetails);
  }, [state]);

  function findPageOrSubpage(
    contents: PageType[],
    id: string
  ): PageType | undefined {
    for (const page of contents) {
      if (page.id === id) {
        return page;
      }
      if (page.contents && page.contents.length > 0) {
        const found = findPageOrSubpage(page.contents, id);
        if (found) return found;
      }
    }
    return undefined;
  }

  const disableEditSave = !findPageOrSubpage(
    mockPageContents,
    activePageDetails?.id ?? ""
  )?.properties.title?.trim();

  const items: MenuItemProps[] = [
    {
      label: "Add Page",
      onClick: () => {
        setMode("addPage");
      },
    },

    {
      label: "Add Sub Page",
      onClick: () => {
        setMode("addSubPage");
      },
    },
  ];

  const onClickDeletePageAction = (action: string) => {
    if (action === "delete") {
      setDeletePageModalOpen(true);
    } else if (action === "deleteCancel") {
      resetDeletePages();
    }
  };
  const resetDeletePages = () => {
    setDeletePageDetails([]);
    setMode("default");
    setDeletePageModalOpen(false);
    setDeletePageReset(true);
    setActivePageDetails(null);
  };

  const checkAndSetMetadata = (pagedetails: any) => {
    if (!pagedetails?.contents) return;
    const typesToCheck = [
      CWFItemType.HazardsAndControls,
      CWFItemType.ActivitiesAndTasks,
      CWFItemType.Summary,
      CWFItemType.SiteConditions,
      CWFItemType.Location,
      CWFItemType.NearestHospital,
      CWFItemType.Region,
      CWFItemType.Contractor,
      CWFItemType.ReportDate,
    ];
    const results: any = {};

    function searchForTypes(contents: any): void {
      if (!contents || !Array.isArray(contents)) return;

      for (const item of contents) {
        if (typesToCheck.includes(item.type)) {
          results[item.type] = true;
        }

        if (item.contents && Array.isArray(item.contents)) {
          searchForTypes(item.contents);
        }
      }
    }
    searchForTypes(pagedetails.contents);

    const updatedMetadata = {
      ...state.form.metadata,
    };

    if (results[CWFItemType.HazardsAndControls]) {
      updatedMetadata.is_hazards_and_controls_included = false;
    }

    if (results[CWFItemType.ActivitiesAndTasks]) {
      updatedMetadata.is_activities_and_tasks_included = false;
    }

    if (results[CWFItemType.Summary]) {
      updatedMetadata.is_summary_included = false;
    }

    if (results[CWFItemType.SiteConditions]) {
      updatedMetadata.is_site_conditions_included = false;
    }

    if (results[CWFItemType.Location]) {
      updatedMetadata.is_location_included = false;
    }

    if (results[CWFItemType.NearestHospital]) {
      updatedMetadata.is_nearest_hospital_included = false;
    }

    if (results[CWFItemType.Region]) {
      updatedMetadata.is_region_included = false;
    }

    if (results[CWFItemType.Contractor]) {
      updatedMetadata.is_contractor_included = false;
    }

    if (results[CWFItemType.ReportDate]) {
      updatedMetadata.is_report_date_included = false;
    }

    dispatch({
      type: CF_REDUCER_CONSTANTS.CHANGE_INITIAL_STATE,
      payload: {
        ...state.form,
        metadata: updatedMetadata,
      },
    });
  };

  const countAndDecrementWidgetItems = (pageDetails: any) => {
    if (!pageDetails?.contents) return;

    let widgetItemsCount = 0;

    function countWidgetItemsRecursively(contents: any): void {
      if (!contents || !Array.isArray(contents)) return;

      for (const item of contents) {
        // Check if the current item is marked for widget inclusion
        if (item.properties?.include_in_widget) {
          widgetItemsCount++;
        }

        // Recursively check nested contents (for sections within sections)
        if (item.contents && Array.isArray(item.contents)) {
          countWidgetItemsRecursively(item.contents);
        }
      }
    }

    countWidgetItemsRecursively(pageDetails.contents);

    // Decrement widget count if there are items to remove
    if (widgetItemsCount > 0) {
      const currentWidgetCount = state.form.settings?.widgets_added || 0;
      const newWidgetCount = Math.max(currentWidgetCount - widgetItemsCount, 0);

      dispatch({
        type: CF_REDUCER_CONSTANTS.UPDATE_WIDGET_SETTINGS,
        payload: {
          widgets_added: newWidgetCount,
        },
      });
    }
  };

  const onConfirmOfDeletePage = () => {
    const activePage =
      activePageDetails?.type === CWFItemType.Page
        ? state.form.contents.find(page => page.id === activePageDetails?.id)
        : state.form.contents
            .find(page => page.id === activePageDetails?.parentId)
            ?.contents.find(subPage => subPage.id === activePageDetails?.id);

    if (activePage) {
      checkAndSetMetadata(activePage);
      // Count and decrement widget items before deletion
      countAndDecrementWidgetItems(activePage);
    }

    dispatch({
      type: CF_REDUCER_CONSTANTS.BULK_DELETE_PAGE,
      payload: deletePageDetails,
    });
    toastCtx?.pushToast(
      "success",
      "Page deleted. Make sure to tap Save button to keep your changes intact"
    );

    resetDeletePages();
  };

  const onPageDragAction = (action: string) => {
    if (action === "dragPageSave") {
      dispatch({
        type: CF_REDUCER_CONSTANTS.PAGE_DRAG,
        payload: mockPageContents,
      });
      toastCtx?.pushToast(
        "success",
        "Page reordered. Make sure to tap Save/Update button to keep your changes intact"
      );
    }
    setMode("default");
  };

  const onEditPageAction = (action: "EDIT_PAGE_SAVE" | "EDIT_PAGE_CANCEL") => {
    if (action === "EDIT_PAGE_CANCEL") {
      setMockPageContents(cloneDeep(state.form.contents));
    } else {
      dispatch({
        type: CF_REDUCER_CONSTANTS.PAGE_TITLE_EDIT,
        payload: mockPageContents,
      });
      toastCtx?.pushToast(
        "success",
        "Page Names Edited. Make sure to tap Save/Update button to keep your changes intact"
      );
    }

    setMode("default");
  };

  const onClickOfDrag = () => {
    setMockPageContents(cloneDeep(state.form.contents));
    setMode("dragPage");
  };

  const renderTopPanel = () => {
    switch (mode) {
      case "addPage":
        return (
          <AddPageForm
            setMode={setMode}
            newPageTitle={newPageTitle}
            setNewPageTitle={setNewPageTitle}
            label="Add Page"
            mode={mode}
            setActivePageDetails={setActivePageDetails}
            parentPage={parentPage}
            setParentPage={setParentPage}
          />
        );
      case "addSubPage":
        return (
          <AddPageForm
            setMode={setMode}
            newPageTitle={subPageTitle}
            setNewPageTitle={setSubPageTitle}
            label="Add Sub Page"
            mode={mode}
            setActivePageDetails={setActivePageDetails}
            parentPage={parentPage}
            setParentPage={setParentPage}
          />
        );
      case "deletePage":
        return (
          <DeletePageAction
            deletePageDetails={deletePageDetails}
            onPageDeleteAction={action => onClickDeletePageAction(action)}
          />
        );
      case "editPage":
        return (
          <EditPageAction
            onPageEditAction={action => {
              onEditPageAction(action);
            }}
            isSaveDisabled={disableEditSave}
          />
        );

      case "dragPage":
        return <DragPageAction onPageDragAction={onPageDragAction} />;

      case "editPage":
        return <EditPageAction onPageEditAction={onEditPageAction} />;
      default:
        return (
          <>
            <div className={style.addPageComponentParent__dropDownSection}>
              <Dropdown
                icon="plus_square"
                menuItems={activePageDetails === null ? [[items[0]]] : [items]}
              />
            </div>

            {state.form.contents.length > 0 && activePageDetails && (
              <ButtonIcon
                className="text-md"
                iconName="edit"
                onClick={() => setMode("editPage")}
              />
            )}

            {state.form.contents.length > 0 && (
              <>
                <SvgButton
                  className="text-md"
                  svgPath={"/assets/CWF/page_arrange.svg"}
                  onClick={onClickOfDrag}
                />

                <ButtonIcon
                  className="text-md"
                  iconName="trash_empty"
                  onClick={() => setMode("deletePage")}
                />
              </>
            )}
          </>
        );
    }
  };

  return (
    <div className={style.addPageComponentParent}>
      <div className={style.addPageComponentParent__ctaPanel}>
        {renderTopPanel()}
      </div>

      <div className={style.addPageComponentParent__pageList}>
        {mode === "editPage" || mode === "dragPage" ? (
          <MockPageListComponent
            mode={mode}
            activePageDetails={activePageDetails}
            setActivePageDetails={setActivePageDetails}
            setParentPage={setParentPage}
            onPageEdit={setPageEditDetails}
            mockPageContents={mockPageContents}
            setMockPageContents={setMockPageContents}
          />
        ) : (
          <PageListComponent
            mode={mode}
            newPageTitle={newPageTitle}
            setNewPageTitle={setNewPageTitle}
            activePageDetails={activePageDetails}
            setActivePageDetails={setActivePageDetails}
            subPageTitle={subPageTitle}
            setSubPageTitle={setSubPageTitle}
            setParentPage={setParentPage}
            deletePageDetails={deletePageDetails}
            onDeletePageDetailsUpdate={setDeletePageDetails}
            deletePageReset={deletePageReset}
            OnDeletePageReset={setDeletePageReset}
          />
        )}
      </div>

      <DeletePageConfirmationModal
        deletePageModalOpen={deletePageModalOpen}
        setDeletePageModalOpen={setDeletePageModalOpen}
        onConfirmOfDeletePage={onConfirmOfDeletePage}
      />
    </div>
  );
};

export default AddPageComponent;
