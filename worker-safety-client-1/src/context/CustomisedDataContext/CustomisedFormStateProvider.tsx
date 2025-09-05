/* eslint-disable @typescript-eslint/no-explicit-any */
import type {
  CommonAction,
  FormBuilderModeProps,
  FormComponentPayloadType,
  FormElementsType,
  FormType,
  PageType,
  PersonnelPage,
  Task,
} from "@/components/templatesComponents/customisedForm.types";
import type { ReactNode } from "react";
import { EventEmitter } from "fbemitter";
import { isEmpty } from "lodash-es";
import React, { useReducer } from "react";
import { v4 as uuidv4 } from "uuid";
import { CF_REDUCER_CONSTANTS } from "@/utils/customisedFormUtils/customisedForm.constants";
import {
  CWFItemType,
  UserFormModeTypes,
} from "@/components/templatesComponents/customisedForm.types";
import CustomisedFromStateContext from "./CustomisedFormStateContext";
import {
  updatePageContents,
  updatePages,
} from "./helpers/customisedFormStateProviderhelpers";

interface CommonState {
  form: FormType;
  formBuilderMode: FormBuilderModeProps;
  isFormDirty: boolean;
  apiData: FormType | null;
  isFormIsValid: boolean;
}
const isPersonnelComponent = (node: PageType): node is PersonnelPage =>
  node.type === "personnel_component" ||
  node.type === CWFItemType.PersonnelComponent;

export const walkAndPatch = (
  nodes: PageType[],
  mutator: (node: PageType) => PageType
): PageType[] =>
  nodes.map(original => {
    const withChildren =
      Array.isArray(original.contents) && original.contents.length
        ? {
            ...original,
            contents: walkAndPatch(original.contents as PageType[], mutator),
          }
        : { ...original };
    return mutator(withChildren);
  });
const initialState: CommonState = {
  form: {
    id: uuidv4(),
    isDisabled: false,
    type: "template",
    settings: {
      availability: {
        adhoc: {
          selected: true,
        },
        work_package: {
          selected: false,
        },
      },
      edit_expiry_days: 0,
      maximum_widgets: 15,
      widgets_added: 0,
      copy_and_rebrief: {
        is_copy_enabled: false,
        is_rebrief_enabled: false,
      },
    },
    properties: {
      title: "",
      status: "",
      description: "",
    },
    contents: [],
    component_data: {
      activities_tasks: [],
      hazards_controls: {
        manually_added_hazards: [],
        tasks: [],
        site_conditions: [],
      },
    },
  },
  formBuilderMode: UserFormModeTypes.BUILD,
  isFormDirty: false,
  apiData: null,
  isFormIsValid: true,
};

// Helper functions for updating nested content
const updateContentById = (
  contents: any[],
  id: string,
  updater: (content: any) => any
) => contents.map(content => (content.id === id ? updater(content) : content));

const updateSubpageContent = (
  page: any,
  subpageId: string,
  updater: (subpage: any) => any
) => ({
  ...page,
  contents: page.contents.map((content: any) =>
    content.type === CWFItemType.SubPage && content.id === subpageId
      ? updater(content)
      : content
  ),
});

const addItemWithOrder = (contents: any[], newItem: any) => {
  const newOrder = isEmpty(contents)
    ? 1
    : !newItem.properties.title
    ? newItem.order
    : contents[contents.length - 1].order + 1;
  return [
    ...contents,
    {
      ...newItem,
      order: newOrder,
    },
  ];
};

// Main reducer
const commonReducer = (
  state: CommonState,
  action: CommonAction
): CommonState => {
  switch (action.type) {
    case CF_REDUCER_CONSTANTS.CHANGE_INITIAL_STATE:
      const shouldPreserveComponentData =
        state.form.component_data &&
        ((state.form.component_data?.activities_tasks?.length ?? 0) > 0 ||
          (state.form.component_data?.hazards_controls?.manually_added_hazards
            ?.length ?? 0) > 0 ||
          (state.form.component_data?.hazards_controls?.tasks?.length ?? 0) >
            0 ||
          (state.form.component_data?.hazards_controls?.site_conditions
            ?.length ?? 0) > 0);

      return {
        ...state,
        form: {
          ...action.payload,
          component_data: shouldPreserveComponentData
            ? state.form.component_data
            : action.payload.component_data,
        },
        apiData: state.apiData === null ? { ...action.payload } : state.apiData,
      };

    case CF_REDUCER_CONSTANTS.RESET_PAGE: {
      const pageId = action.payload;
      if (!state.apiData) return state;

      // Find the original page data from apiData
      const originalPage = state.apiData.contents.find(
        page => page.id === pageId
      );
      if (!originalPage) return state;

      // Update the form with the original page data
      return {
        ...state,
        form: {
          ...state.form,
          contents: state.form.contents.map(page =>
            page.id === pageId ? { ...originalPage } : page
          ),
        },
      };
    }

    case CF_REDUCER_CONSTANTS.ADD_PAGE:
      return {
        ...state,
        form: {
          ...state.form,
          contents: [...state.form.contents, action.payload],
        },
      };
    case CF_REDUCER_CONSTANTS.BUTTON_DISABLE_STATUS_CHANGE:
      return {
        ...state,
        form: {
          ...state.form,
          isDisabled: action.payload,
        },
      };

    case CF_REDUCER_CONSTANTS.DELETE_PAGE:
      return {
        ...state,
        form: {
          ...state.form,
          contents: state.form.contents.filter(
            page => page.id !== action.payload.id
          ),
        },
      };

    case CF_REDUCER_CONSTANTS.DELETE_SUBPAGE: {
      const { parentPage, id } = action.payload;
      return {
        ...state,
        form: {
          ...state.form,
          contents: state.form.contents.map(page => ({
            ...page,
            contents:
              page.id === parentPage
                ? page.contents.filter(subPage => subPage.id !== id)
                : page.contents,
          })),
        },
      };
    }

    case CF_REDUCER_CONSTANTS.ADD_SUBPAGE: {
      const { parentPage, subpageDetails } = action.payload;
      return {
        ...state,
        form: {
          ...state.form,
          contents: updateContentById(
            state.form.contents,
            parentPage,
            page => ({
              ...page,
              contents: [...page.contents, subpageDetails],
            })
          ),
        },
      };
    }

    case CF_REDUCER_CONSTANTS.ADD_SECTION: {
      const { parentData, sectionData } = action.payload;
      if (!parentData) return state;

      if (parentData.type === CWFItemType.Page) {
        return {
          ...state,
          form: {
            ...state.form,
            contents: updateContentById(
              state.form.contents,
              parentData.id,
              page => ({
                ...page,
                contents: [...page.contents, sectionData],
              })
            ),
          },
        };
      }

      return {
        ...state,
        form: {
          ...state.form,
          contents: updateContentById(
            state.form.contents,
            parentData.parentId,
            page =>
              updateSubpageContent(page, parentData.id, subpage => ({
                ...subpage,
                contents: addItemWithOrder(subpage.contents, sectionData),
              }))
          ),
        },
      };
    }

    case CF_REDUCER_CONSTANTS.EDIT_SECTION_FIELD: {
      const { sectionId, updatedProperties } = action.payload;

      const updatedContents = state.form.contents.map((page: any) => {
        const updatedPageContents = page.contents.map((content: any) => {
          if (
            content.id === sectionId &&
            content.type === CWFItemType.Section
          ) {
            return {
              ...content,
              properties: {
                ...content.properties,
                ...updatedProperties,
              },
            };
          }
          if (content.type === CWFItemType.SubPage) {
            const updateSubPageContent = content.contents.map(
              (subContent: any) => {
                if (
                  subContent.id === sectionId &&
                  subContent.type === CWFItemType.Section
                ) {
                  return {
                    ...subContent,
                    properties: {
                      ...subContent.properties,
                      ...updatedProperties,
                    },
                  };
                }
                return subContent;
              }
            );
            return {
              ...content,
              contents: updateSubPageContent,
            };
          }
          return content;
        });

        return {
          ...page,
          contents: updatedPageContents,
        };
      });

      return {
        ...state,
        form: {
          ...state.form,
          contents: updatedContents,
        },
      };
    }

    case CF_REDUCER_CONSTANTS.ADD_SECTION_FIELD: {
      const { parentData, section, fieldData } = action.payload;
      if (!parentData || !section) return state;

      const addFieldToSection = (content: any) =>
        content.type === CWFItemType.Section && content.id === section.id
          ? {
              ...content,
              contents: addItemWithOrder(content.contents, fieldData),
            }
          : content;

      if (parentData.type === CWFItemType.Page) {
        return {
          ...state,
          form: {
            ...state.form,
            contents: updateContentById(
              state.form.contents,
              parentData.id,
              page => ({
                ...page,
                contents: page.contents.map(addFieldToSection),
              })
            ),
          },
        };
      }

      return {
        ...state,
        form: {
          ...state.form,
          contents: updateContentById(
            state.form.contents,
            parentData.parentId,
            page =>
              updateSubpageContent(page, parentData.id, subpage => ({
                ...subpage,
                contents: subpage.contents.map(addFieldToSection),
              }))
          ),
        },
      };
    }

    case CF_REDUCER_CONSTANTS.ADD_FIELD: {
      const { parentData, fieldData } = action.payload;
      if (!parentData) return state;

      if (parentData.type === CWFItemType.Page) {
        return {
          ...state,
          form: {
            ...state.form,
            contents: updateContentById(
              state.form.contents,
              parentData.id,
              page => ({
                ...page,
                contents: addItemWithOrder(page.contents, fieldData),
              })
            ),
          },
        };
      }

      return {
        ...state,
        form: {
          ...state.form,
          contents: updateContentById(
            state.form.contents,
            parentData.parentId,
            page =>
              updateSubpageContent(page, parentData.id, subpage => ({
                ...subpage,
                contents: addItemWithOrder(subpage.contents, fieldData),
              }))
          ),
        },
      };
    }

    case CF_REDUCER_CONSTANTS.ADD_COMPONENTS: {
      const { parentData, fieldData } = action.payload;
      if (!parentData) return state;
      if (parentData.type === CWFItemType.Page) {
        return {
          ...state,
          form: {
            ...state.form,
            contents: updateContentById(
              state.form.contents,
              parentData.id,
              page => ({
                ...page,
                contents: addItemWithOrder(page.contents, fieldData),
              })
            ),
          },
        };
      } else {
        return {
          ...state,
          form: {
            ...state.form,
            contents: updateContentById(
              state.form.contents,
              parentData.parentId,
              page =>
                updateSubpageContent(page, parentData.id, subpage => ({
                  ...subpage,
                  contents: addItemWithOrder(subpage.contents, fieldData),
                }))
            ),
          },
        };
      }
    }

    case CF_REDUCER_CONSTANTS.ATTACHMENTS_VALUE_CHANGE: {
      const { parentData, section, fieldData } = action.payload;
      if (!parentData) return state;

      const updateContents = (pageItem: PageType) => {
        return pageItem.contents.map(
          (content: PageType | FormElementsType | FormComponentPayloadType) => {
            if (
              section &&
              content.type === CWFItemType.Section &&
              content.id === section.id
            ) {
              return {
                ...content,
                contents: content.contents.map(sectionContent =>
                  sectionContent.id === fieldData.id
                    ? fieldData
                    : sectionContent
                ),
              };
            }
            return content.id === fieldData.id ? fieldData : content;
          }
        );
      };

      if (parentData.type === CWFItemType.Page) {
        return {
          ...state,
          form: {
            ...state.form,
            contents: updateContentById(
              state.form.contents,
              parentData.id,
              page => ({
                ...page,
                contents: updateContents(page),
              })
            ),
          },
        };
      } else {
        return {
          ...state,
          form: {
            ...state.form,
            contents: updateContentById(
              state.form.contents,
              parentData.parentId,
              page =>
                updateSubpageContent(page, parentData.id, subpage => ({
                  ...subpage,
                  contents: updateContents(subpage),
                }))
            ),
          },
        };
      }
    }

    case CF_REDUCER_CONSTANTS.DELETE_FIELD: {
      const { parentData, section, fieldData } = action.payload;
      if (!parentData) return state;

      const filterByOrder = (content: any) => content.order !== fieldData.order;

      const updateSectionContents = (content: any) =>
        content.type === CWFItemType.Section && content.id === section?.id
          ? { ...content, contents: content.contents.filter(filterByOrder) }
          : content;

      if (parentData.type === CWFItemType.Page) {
        return {
          ...state,
          form: {
            ...state.form,
            contents: updateContentById(
              state.form.contents,
              parentData.id,
              page => ({
                ...page,
                contents: section
                  ? page.contents.map(updateSectionContents)
                  : page.contents.filter(filterByOrder),
              })
            ),
            settings: {
              ...state.form.settings,
            },
          },
        };
      }

      return {
        ...state,
        form: {
          ...state.form,
          contents: updateContentById(
            state.form.contents,
            parentData.parentId,
            page =>
              updateSubpageContent(page, parentData.id, subpage => ({
                ...subpage,
                contents: section
                  ? subpage.contents.map(updateSectionContents)
                  : subpage.contents.filter(filterByOrder),
              }))
          ),
          settings: {
            ...state.form.settings,
          },
        },
      };
    }
    case CF_REDUCER_CONSTANTS.EDIT_FIELD: {
      const { parentData, section, fieldData, newOrder } = action.payload;

      return {
        ...state,
        form: {
          ...state.form,
          contents: state.form.contents.map(page => {
            // If we're not on the correct page, return unchanged
            if (
              page.id !==
              (parentData.type === CWFItemType.Page
                ? parentData.id
                : parentData.parentId)
            ) {
              return page;
            }

            // Handle page-level updates
            if (parentData.type === CWFItemType.Page) {
              return {
                ...page,
                contents: section
                  ? page.contents.map(content =>
                      content.type === CWFItemType.Section &&
                      content.id === section.id
                        ? updateSectionContents(content, fieldData, newOrder)
                        : content
                    )
                  : page.contents.map(content =>
                      content.order === fieldData.order
                        ? updateField(content, fieldData, newOrder)
                        : content
                    ),
              };
            }

            // Handle subpage-level updates
            return {
              ...page,
              contents: page.contents.map(content => {
                if (
                  content.type !== CWFItemType.SubPage ||
                  content.id !== parentData.id
                ) {
                  return content;
                }

                if (!section) {
                  return {
                    ...content,
                    contents: content.contents.map((c: any) =>
                      c.order === fieldData.order
                        ? updateField(c, fieldData, newOrder)
                        : c
                    ),
                  };
                }

                return {
                  ...content,
                  contents: content.contents.map((subContent: any) =>
                    subContent.type === CWFItemType.Section &&
                    subContent.id === section.id
                      ? updateSectionContents(subContent, fieldData, newOrder)
                      : subContent
                  ),
                };
              }),
            };
          }),
        },
      };
    }

    case CF_REDUCER_CONSTANTS.SWITCH_CONTENT_ORDERS: {
      const { parent, updatedContents } = action.payload;
      return {
        ...state,
        form: {
          ...state.form,
          contents: updateContentById(state.form.contents, parent.id, page => ({
            ...page,
            contents: page.contents.map((content: any) => {
              const updatedContent = updatedContents.find(
                uc => uc.id === content.id
              );
              return updatedContent || content;
            }),
          })),
        },
      };
    }

    case CF_REDUCER_CONSTANTS.FORM_NAME_CHANGE:
      return {
        ...state,
        form: {
          ...state.form,
          properties: {
            ...state.form.properties,
            title: action.payload,
          },
        },
      };
    case CF_REDUCER_CONSTANTS.FIELD_VALUE_CHANGE:
    case CF_REDUCER_CONSTANTS.ADD_FIELD_COMMENT:
    case CF_REDUCER_CONSTANTS.ADD_FIELD_ATTACHMENTS: {
      const { parentData, section, fieldData } = action.payload;
      if (!parentData) {
        return state;
      }
      return {
        ...state,
        form: {
          ...state.form,
          contents:
            parentData.type === CWFItemType.Page
              ? state.form.contents.map(page =>
                  updatePageContents(
                    page,
                    parentData,
                    section,
                    fieldData,
                    action.type
                  )
                )
              : state.form.contents.map(page =>
                  updatePages(page, parentData, section, fieldData, action.type)
                ),
        },
      };
    }
    case CF_REDUCER_CONSTANTS.ACTIVITIES_VALUE_CHANGE:
      return {
        ...state,
        form: {
          ...state.form,
          component_data: {
            ...state.form.component_data,
            activities_tasks: action.payload,
          },
        },
      };
    case CF_REDUCER_CONSTANTS.ENERGY_HAZARDS_VALUE_CHANGE:
      return {
        ...state,
        form: {
          ...state.form,
          component_data: {
            ...state.form.component_data,
            hazards_controls: {
              ...(state.form.component_data?.hazards_controls || {}),
              manually_added_hazards: action.payload,
            },
          },
        },
      };

    case CF_REDUCER_CONSTANTS.SET_TASKS_HAZARD_DATA:
      return {
        ...state,
        form: {
          ...state.form,
          component_data: {
            ...state.form.component_data,
            hazards_controls: {
              ...state.form.component_data?.hazards_controls,
              tasks: action.payload.map((task: Task) => ({
                ...task,
                hazards: task?.hazards?.map(hazard => ({
                  ...hazard,
                  noControlsImplemented: hazard.noControlsImplemented ?? false,
                  controls: hazard.controls?.map(control => ({ ...control })),
                  taskApplicabilityLevels: hazard.taskApplicabilityLevels?.map(
                    level => ({ ...level })
                  ),
                })),
              })),
            },
          },
        },
      };

    case CF_REDUCER_CONSTANTS.SET_SITE_CONDITIONS_HAZARD_DATA:
      return {
        ...state,
        form: {
          ...state.form,
          component_data: {
            ...state.form.component_data,
            hazards_controls: {
              ...state.form.component_data?.hazards_controls,
              site_conditions: action.payload.map(hazard => ({
                ...hazard,
                noControlsImplemented: hazard.noControlsImplemented ?? false,
                controls: hazard.controls?.map(control => ({
                  ...control,
                  selected: control.selected === true,
                })),
                taskApplicabilityLevels: hazard.taskApplicabilityLevels?.map(
                  level => ({ ...level })
                ),
              })),
            },
          },
        },
      };

    case CF_REDUCER_CONSTANTS.CHANGE_BUILDER_MODE:
      return {
        ...state,
        formBuilderMode: action.payload,
      };

    case CF_REDUCER_CONSTANTS.DELETE_SECTION: {
      const { parentId, subPageId, pageContents } = action.payload;
      return {
        ...state,
        form: {
          ...state.form,
          contents: updateContentById(state.form.contents, parentId, page => ({
            ...page,
            contents: subPageId
              ? page.contents.map((content: any) =>
                  content.type === CWFItemType.SubPage &&
                  content.id === subPageId
                    ? { ...content, contents: pageContents }
                    : content
                )
              : pageContents,
          })),
          settings: {
            ...state.form.settings,
          },
        },
      };
    }

    case CF_REDUCER_CONSTANTS.BULK_DELETE_PAGE: {
      const deletePageDetails = action.payload;

      // Remove parent pages marked for deletion
      const remainingPages = state.form.contents.filter(
        page =>
          !deletePageDetails.some(
            item => item.id === page.id && item.deleteParentPage
          )
      );

      // Update remaining pages - remove marked subpages
      const updatedContents = remainingPages.map(page => {
        const pageDetails = deletePageDetails.find(item => item.id === page.id);
        if (!pageDetails) return page;

        return {
          ...page,
          contents: page.contents.filter(
            item => !pageDetails.subPages.includes(item.id)
          ),
        };
      });

      return {
        ...state,
        form: {
          ...state.form,
          contents: updatedContents,
          settings: {
            ...state.form.settings,
          },
        },
      };
    }

    case CF_REDUCER_CONSTANTS.PAGE_DRAG:
    case CF_REDUCER_CONSTANTS.PAGE_TITLE_EDIT:
    case CF_REDUCER_CONSTANTS.PAGE_STATUS_CHANGE:
    case CF_REDUCER_CONSTANTS.PAGE_SUMMARY_VISIBILITY_TOGGLE:
    case CF_REDUCER_CONSTANTS.SUBPAGE_SUMMARY_VISIBILITY_TOGGLE:
      return {
        ...state,
        form: {
          ...state.form,
          contents: [...action.payload],
          settings: {
            ...state.form.settings,
          },
        },
      };
    case CF_REDUCER_CONSTANTS.CHANGE_WORK_PACKAGE_DATA:
      return {
        ...state,
        form: {
          ...state.form,
          work_package_data: action.payload,
        },
      };
    case CF_REDUCER_CONSTANTS.SET_FORM_STATE:
      return {
        ...state,
        isFormDirty: action.payload,
      };
    case CF_REDUCER_CONSTANTS.SITE_CONDITIONS_VALUE_CHANGE:
      return {
        ...state,
        form: {
          ...state.form,
          component_data: {
            ...state.form.component_data,
            site_conditions: action.payload,
          },
        },
      };

    case CF_REDUCER_CONSTANTS.LOCATION_VALUE_CHANGE:
      return {
        ...state,
        form: {
          ...state.form,
          component_data: {
            ...state.form.component_data,
            location_data: action.payload,
          },
        },
      };

    case CF_REDUCER_CONSTANTS.NEAREST_HOSPITAL_VALUE_CHANGE:
      return {
        ...state,
        form: {
          ...state.form,
          component_data: {
            ...state.form.component_data,
            nearest_hospital: action.payload,
          },
        },
      };

    case CF_REDUCER_CONSTANTS.PERSONNEL_COMPONENT_ADD_DATA: {
      const {
        componentId,
        rowId,
        name,
        signature,
        attrIds,
        employeeNumber,
        jobTitle,
        type,
        displayName,
        email,
        departmentName,
        managerId,
        managerEmail,
        managerName,
      } = action.payload;

      const rowObj = {
        crew_details: {
          name,
          signature,
          job_title: jobTitle ?? "",
          employee_number: employeeNumber ?? "",
          external_id: rowId,
          display_name: displayName,
          type: type,
          email: email,
          primary: null,
          department: departmentName,
          manager_id: managerId,
          company_name: "",
          manager_name: managerName,
          manager_email: managerEmail,
        },
        selected_attribute_ids: attrIds,
      };

      const contents = walkAndPatch(state.form.contents, node => {
        if (node.id === componentId && isPersonnelComponent(node)) {
          const current = node.properties.user_value ?? [];
          const idx = current.findIndex(
            r => r.crew_details.external_id === rowId
          );

          const next =
            idx === -1
              ? [...current, rowObj]
              : current.map((r, n) => (n === idx ? rowObj : r));

          return {
            ...node,
            properties: { ...node.properties, user_value: next },
          };
        }
        return node;
      });

      return { ...state, form: { ...state.form, contents } };
    }
    case CF_REDUCER_CONSTANTS.PERSONNEL_COMPONENT_REMOVE_DATA: {
      const { componentId, rowId } = action.payload;

      const removeRow = (node: any) => {
        if (node.id === componentId && node.type === "personnel_component") {
          return {
            ...node,
            properties: {
              ...node.properties,
              user_value: (node.properties.user_value ?? []).filter(
                (row: any) => row.crew_details.external_id !== rowId
              ),
            },
          };
        }
        return node;
      };

      return {
        ...state,
        form: {
          ...state.form,
          contents: walkAndPatch(state.form.contents, removeRow),
        },
      };
    }
    case CF_REDUCER_CONSTANTS.SET_FORM_VALIDITY:
      return {
        ...state,
        isFormIsValid: action.payload,
      };
    case CF_REDUCER_CONSTANTS.UPDATE_METADATA:
      return {
        ...state,
        form: {
          ...state.form,
          metadata: action.payload,
        },
      };
    case CF_REDUCER_CONSTANTS.UPDATE_HISTORICAL_INCIDENT: {
      const { componentId, incident } = action.payload;

      const updateHistoricalIncident = (node: any): any => {
        // Check if this is a Summary component with the matching ID
        if (node.type === "summary" && node.id === componentId) {
          return {
            ...node,
            properties: {
              ...node.properties,
              historical_incident: {
                ...node.properties.historical_incident,
                incident,
              },
            },
          };
        }

        // Recursively search through contents
        if (Array.isArray(node.contents) && node.contents.length > 0) {
          return {
            ...node,
            contents: node.contents.map(updateHistoricalIncident),
          };
        }

        return node;
      };

      return {
        ...state,
        form: {
          ...state.form,
          contents: state.form.contents.map(updateHistoricalIncident),
        },
      };
    }
    case CF_REDUCER_CONSTANTS.UPDATE_WIDGET_SETTINGS:
      return {
        ...state,
        form: {
          ...state.form,
          settings: {
            ...state.form.settings,
            ...action.payload,
          },
        },
      };
    default:
      return state;
  }
};

interface CustomisedFormStateProviderProps {
  children: ReactNode;
}

const CustomisedFormStateProvider: React.FC<CustomisedFormStateProviderProps> =
  ({ children }) => {
    const [state, dispatch] = useReducer(commonReducer, initialState);
    return (
      <CustomisedFromStateContext.Provider value={{ state, dispatch }}>
        {children}
      </CustomisedFromStateContext.Provider>
    );
  };

// Helper function to update field properties
const updateField = (content: any, fieldData: any, newOrder?: any) => ({
  ...content,
  ...(newOrder && { order: newOrder }),
  properties: fieldData.properties,
});

// Helper function to update section contents
const updateSectionContents = (
  section: any,
  fieldData: any,
  newOrder?: any
) => ({
  ...section,
  contents: section.contents.map((c: any) =>
    c.order === fieldData.order ? updateField(c, fieldData, newOrder) : c
  ),
});

/**
 * An event emitter object to send around event that cannot be syncronously captured
 * Example: when save and continue button is pressed, to need to save the value of datetime fields on that page
 *
 * Since save and continue button has no knowledge of current page and its fields, it will emit an event
 * and the datetime component will listen to that event and save its value
 */
export const formEventEmitter = new EventEmitter();

export const FORM_EVENTS = {
  SAVE_AND_CONTINUE: "SAVE_AND_CONTINUE",
  SHOW_ATTR_ERRORS: "SHOW_ATTR_ERRORS",
  SHOW_CREW_ERRORS: "SHOW_CREW_ERRORS",
};

export default CustomisedFormStateProvider;
