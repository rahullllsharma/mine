export const WorkPackagePageLocators = {
  WorkOrderOrProjectNameInput: {
    mobile: "//input[contains(@id,'name')]",
    desktop: "//input[contains(@id,'name')]",
  },
  ProjectNumberOrKeyInput: {
    mobile: "//input[contains(@id,'externalKey')]",
    desktop: "//input[contains(@id,'externalKey')]",
  },
  ProjectTypeDropdown: {
    mobile: "(//button[contains(@class,'w-full px-2')])[1]",
    desktop: "(//button[contains(@class,'w-full px-2')])[1]",
  },
  WorkTypesDropdown: {
    mobile: "//label[contains(text(),'Work Types')]/following-sibling::div//div[contains(@role,'button') and contains(@class,'w-full')]",
    desktop: "//label[contains(text(),'Work Types')]/following-sibling::div//div[contains(@role,'button') and contains(@class,'w-full')]",
  },
  AssetTypeDropdown: {
    mobile: "(//button[contains(@class,'w-full px-2')])[2]",
    desktop: "(//button[contains(@class,'w-full px-2')])[2]",
  },
  StatusDropdown: {
    mobile: "(//button[contains(@class,'w-full px-2')])[3]",
    desktop: "(//button[contains(@class,'w-full px-2')])[3]",
  },
  ProjectZipCodeInput: {
    mobile: "//input[contains(@class,'p-2') and @placeholder='Ex. 10010']",
    desktop: "//input[contains(@class,'p-2') and @placeholder='Ex. 10010']",
  },
  StartDateInput: {
    mobile:
      "//input[contains(@class,'p-2') and @type='date' and @name='startDate']",
    desktop:
      "//input[contains(@class,'p-2') and @type='date' and @name='startDate']",
  },
  EndDateInput: {
    mobile:
      "//input[contains(@class,'p-2') and @type='date' and @name='endDate']",
    desktop:
      "//input[contains(@class,'p-2') and @type='date' and @name='endDate']",
  },
  AreaOrDivisionDropdown: {
    mobile: "(//button[contains(@class,'w-full px-2')])[4]",
    desktop: "(//button[contains(@class,'w-full px-2')])[4]",
  },
  AreaOrDivisionOption: {
    mobile: "(//ul[contains(@class,'absolute z-10')]//li)[1]",
    desktop: "(//ul[contains(@class,'absolute z-10')]//li)[1]",
  },
  OperatingHQorRegionDropdown: {
    mobile: "(//button[contains(@class,'w-full px-2')])[5]",
    desktop: "(//button[contains(@class,'w-full px-2')])[5]",
  },
  OperatingHQorRegionOption: {
    mobile: "(//ul[contains(@class,'absolute z-10')]//li)[1]",
    desktop: "(//ul[contains(@class,'absolute z-10')]//li)[1]",
  },
  DescriptionTextarea: {
    mobile:
      "//textarea[contains(@class,'px-2') and contains(@placeholder,'Add')]",
    desktop:
      "//textarea[contains(@class,'px-2') and contains(@placeholder,'Add')]",
  },
  EngineerNameInput: {
    mobile: "//input[contains(@class,'p-2') and @placeholder='Engineer name']",
    desktop: "//input[contains(@class,'p-2') and @placeholder='Engineer name']",
  },
  ContractReferenceNumberInput: {
    mobile: "//input[contains(@class,'p-2') and @placeholder='Ex. ABC-1234']",
    desktop: "//input[contains(@class,'p-2') and @placeholder='Ex. ABC-1234']",
  },
  ContractNameInput: {
    mobile: "//input[contains(@id,'contractName')]",
    desktop: "//input[contains(@id,'contractName')]",
  },
  ContractorDropdown: {
    mobile:
      "//div[@data-testid='work-package-contractor']//div[contains(@class,'css-0') and @role='button']",
    desktop:
      "//div[@data-testid='work-package-contractor']//div[contains(@class,'css-0') and @role='button']",
  },
  ContractorOption: {
    mobile: "(//div[@role='option'])[2]",
    desktop: "(//div[@role='option'])[2]",
  },
  LocationNameInput: {
    mobile:
      "(//input[contains(@class,'p-2') and contains(@id,'locationName')])[1]",
    desktop:
      "(//input[contains(@class,'p-2') and contains(@id,'locationName')])[1]",
  },
  LocationLatInput: {
    mobile:
      "(//input[contains(@class,'p-2') and contains(@id,'locationLat')])[1]",
    desktop:
      "(//input[contains(@class,'p-2') and contains(@id,'locationLat')])[1]",
  },
  LocationLongInput: {
    mobile:
      "(//input[contains(@class,'p-2') and contains(@id,'locationLong')])[1]",
    desktop:
      "(//input[contains(@class,'p-2') and contains(@id,'locationLong')])[1]",
  },
  LocationPrimarySupervisorDropdown: {
    mobile:
      "(//div[@data-testid='location-primary-assigned-person'])[1]//div[contains(@class,'css-0') and @role='button']",
    desktop:
      "(//div[@data-testid='location-primary-assigned-person'])[1]//div[contains(@class,'css-0') and @role='button']",
  },
  LocationPrimarySupervisorOption: {
    mobile: "(//div[@role='option'])[1]",
    desktop: "(//div[@role='option'])[1]",
  },
  LocationAdditionalSupervisorDropdown: {
    mobile:
      "(//div[@data-testid='location-additional-assigned-person'])[1]//div[contains(@class,'css-0') and @role='button']",
    desktop:
      "(//div[@data-testid='location-additional-assigned-person'])[1]//div[contains(@class,'css-0') and @role='button']",
  },
  LocationAdditionalSupervisorOption: {
    mobile: "(//div[@role='option'])[1]",
    desktop: "(//div[@role='option'])[1]",
  },
  AddLocationButton: {
    mobile: "//button[@data-testid='add-location-button']",
    desktop: "//button[@data-testid='add-location-button']",
  },
  ProjectManagerDropdown: {
    mobile:
      "//div[@data-testid='work-package-manager']//div[contains(@class,'css-0') and @role='button']",
    desktop:
      "//div[@data-testid='work-package-manager']//div[contains(@class,'css-0') and @role='button']",
  },
  ProjectManagerOption: {
    mobile: "(//div[@role='option'])[2]",
    desktop: "(//div[@role='option'])[2]",
  },
  PrimarySupervisorDropdown: {
    mobile:
      "//div[@data-testid='work-package-assigned-person']//div[contains(@class,'css-0') and @role='button']",
    desktop:
      "//div[@data-testid='work-package-assigned-person']//div[contains(@class,'css-0') and @role='button']",
  },
  PrimarySupervisorOption: {
    mobile: "(//div[@role='option'])[2]",
    desktop: "(//div[@role='option'])[2]",
  },
  AdditionalSupervisorDropdown: {
    mobile:
      "//div[@data-testid='work-package-additional-assigned-person']//div[contains(@class,'css-0') and @role='button']",
    desktop:
      "//div[@data-testid='work-package-additional-assigned-person']//div[contains(@class,'css-0') and @role='button']",
  },
  AdditionalSupervisorOption: {
    mobile: "(//div[@role='option'])[2]",
    desktop: "(//div[@role='option'])[2]",
  },
  RemoveAdditionalSupervisorButton: {
    mobile:
      "//button[contains(@class,'text-base') and .//span[contains(text(),'Remove')]]",
    desktop:
      "//button[contains(@class,'text-base') and .//span[contains(text(),'Remove')]]",
  },
  SaveButton: {
    mobile:
      "//button[contains(@class,'text-white') and .//span[contains(text(),'Save')]]",
    desktop:
      "//button[contains(@class,'text-white') and .//span[contains(text(),'Save')]]",
  },
  SettingsButton: {
    mobile: "//button[@title='settings']",
    desktop: "//button[@title='settings']",
  },
  DeleteButtonIcon: {
    mobile:
      "//button[contains(@class,'text-xl text-neutral-shade-75')]//i[contains(@class,'ci-trash_empty')]",
    desktop:
      "//button[contains(@class,'text-xl text-neutral-shade-75')]//i[contains(@class,'ci-trash_empty')]",
  },
  DeleteProjectPopup: {
    mobile: "(//div[contains(@class,'min-h-screen flex')]//div)[2]",
    desktop: "(//div[contains(@class,'min-h-screen flex')]//div)[2]",
  },
  DeleteProjectButton: {
    mobile: "(//button[contains(@class,'text-center truncate')])[3]",
    desktop: "(//button[contains(@class,'text-center truncate')])[3]",
  },
  AddWorkPackageButton: {
    mobile: "[data-testid='add-work-package-button']",
    desktop: "[data-testid='add-work-package-button']",
  },
  WorkPackageSearchInput: {
    mobile: "(//input[@data-testid='work-package-search'])[2]",
    desktop: "(//input[@data-testid='work-package-search'])[1]",
  },
  WorkPackageResultRow: {
    mobile: "(//button[@class='flex-1 p-6 text-left'])[1]",
    desktop: "(//div[@role='cell']//a)[1]",
  },
  NoProjectsMessage: {
    mobile: "//p[contains(text(),'There are no')]",
    desktop: "//p[contains(text(),'There are no')]",
  },
  ActiveTab: {
    mobile: "//span[normalize-space()='Active']",
    desktop: "//span[normalize-space()='Active']",
  },
  PendingTab: {
    mobile: "//span[normalize-space()='Pending']",
    desktop: "//span[normalize-space()='Pending']",
  },
  CompletedTab: {
    mobile: "//span[normalize-space()='Completed']",
    desktop: "//span[normalize-space()='Completed']",
  },
  HistoryTabButton: {
    mobile: "//button[@class='bg-neutral-shade-3' and contains(., 'History')]",
    desktop: "//button[@class='bg-neutral-shade-3' and contains(., 'History')]",
  },
  HistoryHeader: {
    mobile: "//h6[normalize-space()='History']",
    desktop: "//h6[normalize-space()='History']",
  },
  ToastMessage: {
    mobile: "//*[contains(text(),'saved') or contains(text(),'Saved')]",
    desktop: "//*[contains(text(),'saved') or contains(text(),'Saved')]",
  },
  HistoryDateTimeEntry: Object.assign(
    (dateTime: string) => ({
      mobile: `(//span[normalize-space(text())='${dateTime}'])[1]`,
      desktop: `(//span[normalize-space(text())='${dateTime}'])[1]`,
    }),
    {
      flexible: (date: string, time: string) => ({
        mobile: `(//span[contains(normalize-space(.), '${time}') and contains(normalize-space(.), 'GMT+5:30')])[1]`,
        desktop: `(//span[contains(normalize-space(.), '${time}') and contains(normalize-space(.), 'GMT+5:30')])[1]`,
      }),
    }
  ),
  AddMenuButton: {
    mobile:
      "//button[contains(.,'Add Form')]/following-sibling::div[@data-testid='dropdown']/button",
    desktop:
      "//button[contains(.,'Add Form')]/following-sibling::div[@data-testid='dropdown']/button",
  },
  ActivityTypeButton: (type: string) => ({
    mobile: `//button[contains(@role,'button') and contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '${type.toLowerCase()}')]`,
    desktop: `//button[contains(@role,'button') and contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '${type.toLowerCase()}')]`,
  }),
  SubActivityCheckbox: (name: string) => ({
    mobile: `//input[@type='checkbox' and contains(@aria-label, '${name}')]`,
    desktop: `//input[@type='checkbox' and contains(@aria-label, '${name}')]`,
  }),
  NextButton: {
    mobile: "//button[normalize-space()='Next']",
    desktop: "//button[normalize-space()='Next']",
  },
  AddActivityButton: {
    mobile: "//button[contains(.,'Add Activity')]",
    desktop: "//button[contains(.,'Add Activity')]",
  },
  ActivityEntryByName: (name: string) => ({
    mobile: `//*[text()='${name}']`,
    desktop: `//*[text()='${name}']`,
  }),
  ActivityThreeDotsMenu: (name: string) => ({
    mobile: `(//div[contains(@class, 'flex') and .//div[contains(text(), '${name}')]]//button[contains(@id, 'headlessui-menu-button')])[1]`,
    desktop: `(//div[contains(@class, 'flex') and .//div[contains(text(), '${name}')]]//button[contains(@id, 'headlessui-menu-button')])[1]`,
  }),
  EditActivityMenuItem: {
    mobile: "//button[contains(.,'Edit Activity')]",
    desktop: "//button[contains(.,'Edit Activity')]",
  },
  ActivityNameInput: {
    mobile: "//input[@name='activityName']",
    desktop: "//input[@name='activityName']",
  },
  SaveActivityButton: {
    mobile: "//button[contains(.,'Save Activity')]",
    desktop: "//button[contains(.,'Save Activity')]",
  },
  DeleteActivityMenuItem: {
    mobile: "//button[contains(.,'Delete Activity')]",
    desktop: "//button[contains(.,'Delete Activity')]",
  },
  ConfirmDeleteButton: {
    mobile: "(//div[contains(@class,'flex justify-end')]//button)[2]",
    desktop: "(//div[contains(@class,'flex justify-end')]//button)[2]",
  },
  SiteConditionMenuItem: {
    mobile: "(//button[contains(@class,'flex flex-1')]//p)[2]",
    desktop: "(//button[contains(@class,'flex flex-1')]//p)[2]",
  },
  SiteConditionDropdown: {
    mobile: "//div[@id='react-select-2-placeholder']/following-sibling::div[1]",
    desktop:
      "//div[@id='react-select-2-placeholder']/following-sibling::div[1]",
  },
  SiteConditionFirstOption: {
    mobile: "((//div[contains(@class,'absolute z-10')]//div)[1])//div[1]",
    desktop: "((//div[contains(@class,'absolute z-10')]//div)[1])//div[1]",
  },
  SiteConditionContinueButton: {
    mobile:
      "//button[contains(@class,'text-center truncate')]/following-sibling::button[1]",
    desktop:
      "//button[contains(@class,'text-center truncate')]/following-sibling::button[1]",
  },
  SiteConditionSwitch: {
    mobile: "(//button[@role='switch'])[1]",
    desktop: "(//button[@role='switch'])[1]",
  },
  AddSiteConditionButton: {
    mobile: "//button[contains(.,'Add Site Condition')]",
    desktop: "//button[contains(.,'Add Site Condition')]",
  },
  SiteConditionAddedMessage: {
    mobile: "//div[text()='Site Condition added']",
    desktop: "//div[text()='Site Condition added']",
  },
  SiteConditionListEntry: (name: string) => ({
    mobile: `//span[contains(@class,'text-action-label') and contains(text(),'${name}')]`,
    desktop: `//span[contains(@class,'text-action-label') and contains(text(),'${name}')]`,
  }),
  EditSiteConditionButton: (name: string) => ({
    mobile: `//div[contains(@class,'flex-1') and .//span[text()='${name}']]//button[./i[contains(@class,'ci-edit')]]`,
    desktop: `//div[contains(@class,'flex-1') and .//span[text()='${name}']]//button[./i[contains(@class,'ci-edit')]]`,
  }),
  AddHazardButton: {
    mobile: "//button[contains(.,'Add a hazard')]/div",
    desktop: "//button[contains(.,'Add a hazard')]/div",
  },
  RemoveHazardButton: {
    mobile: "(//button[contains(@class,'text-xl text-neutral-shade-75')])[2]",
    desktop: "(//button[contains(@class,'text-xl text-neutral-shade-75')])[2]",
  },
  HazardDropdown: {
    mobile: "(//div[@role='button' and contains(@class,'w-full pr-2')])[1]",
    desktop: "(//div[@role='button' and contains(@class,'w-full pr-2')])[1]",
  },
  ArrowDownButton: {
    mobile:
      "(//div[contains(@class, 'css-1wy0on6')]//i[contains(@class, 'ci-chevron_down')])[1]",
    desktop:
      "(//div[contains(@class, 'css-1wy0on6')]//i[contains(@class, 'ci-chevron_down')])[1]",
  },
  HazardOption: {
    mobile:
      "(//div[contains(@class, 'flex') and contains(@class, 'items-center') and contains(@class, 'p-3') and contains(@class, 'text-base') and contains(@class, 'cursor-pointer') and contains(@class, 'css-0')])[3]",
    desktop:
      "(//div[contains(@class, 'flex') and contains(@class, 'items-center') and contains(@class, 'p-3') and contains(@class, 'text-base') and contains(@class, 'cursor-pointer') and contains(@class, 'css-0')])[3]",
  },
  AddControlButton: {
    mobile:
      "(//button[.//i[contains(@class,'ci-plus')] and .//span[text()='Add a control']])[1]",
    desktop:
      "(//button[.//i[contains(@class,'ci-plus')] and .//span[text()='Add a control']])[1]",
  },
  ControlSelector: {
    mobile:
      "//div[@role='button'][.//div[contains(@id, 'react-select') and contains(@id, '-placeholder') and text()='Select a control']]",
    desktop:
      "//div[@role='button'][.//div[contains(@id, 'react-select') and contains(@id, '-placeholder') and text()='Select a control']]",
  },
  RemoveControlButton: {
    mobile: "(//button[contains(@class,'text-xl text-neutral-shade-75')])[3]",
    desktop: "(//button[contains(@class,'text-xl text-neutral-shade-75')])[3]",
  },
  ControlOption: {
    mobile: "(//div[@role='option'])[3]",
    desktop: "(//div[@role='option'])[3]",
  },
  SaveSiteConditionButton: {
    mobile: "//footer//button/div/span[text()='Save']",
    desktop: "//footer//button/div/span[text()='Save']",
  },
  SiteConditionSavedMessage: {
    mobile: "//div[text()='Site Condition saved']",
    desktop: "//div[text()='Site Condition saved']",
  },
  SummaryViewButton: {
    mobile: "//a[contains(@class,'font-medium text-brand-urbint-50')]",
    desktop: "//a[contains(@class,'font-medium text-brand-urbint-50')]",
  },
  ExpandSiteConditionButton: {
    mobile: "(//button[contains(@class,'flex justify-between')])[1]",
    desktop: "(//button[contains(@class,'flex justify-between')])[1]",
  },
  RemoveSiteConditionButton: {
    mobile:
      "((//button[contains(@class,'text-xl text-neutral-shade-75')])[1])//i",
    desktop:
      "((//button[contains(@class,'text-xl text-neutral-shade-75')])[1])//i",
  },
  DeleteSiteConditionConfirm: {
    mobile: "//button[contains(.,'Delete site condition')]",
    desktop: "//button[contains(.,'Delete site condition')]",
  },
  SiteConditionDeletedMessage: {
    mobile: "//div[text()='Site Condition deleted']",
    desktop: "//div[text()='Site Condition deleted']",
  },
};
