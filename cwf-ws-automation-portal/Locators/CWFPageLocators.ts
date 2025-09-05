export const CWFPageLocators = {
  CWF_Template_SaveAndContinueBtn: {
    mobile: "//footer[contains(@class,'flex flex-col')]//button",
    desktop: "//footer[contains(@class,'flex flex-col')]//button",
  },
  CWF_Template_ReportDate: {
    mobile: "(//input[@placeholder='MM-DD-YYYY'])",
    desktop: "(//input[@placeholder='MM-DD-YYYY'])",
  },
  ReportDate_Time_UpdatePopup: {
    mobile: "header[class='flex-1']",
    desktop: "header[class='flex-1']",
  },
  ReportDate_Time_UpdateConfirm: {
    mobile: "//span[normalize-space()='Confirm']",
    desktop: "//span[normalize-space()='Confirm']",
  },
  ReportDate_TimeSection: {
    mobile: "div[class='h-full']",
    desktop: "div[class='h-full']",
  },
  CWF_Template_ReportDate_PickDate: {
    mobile: "//*[@aria-current='date']",
    desktop: "//*[@aria-current='date']",
  },
  CWF_Template_ReportDate_PickTime: {
    mobile: "//*[@aria-selected='true']/following-sibling::li[2]",
    desktop: "//*[@aria-selected='true']/following-sibling::li[2]",
  },
  CWF_Form_SuccessToast: {
    mobile: "//*[@class='text-neutral-light-100 text-base text-left']",
    desktop: "//*[@class='text-neutral-light-100 text-base text-left']",
  },
  inputPhoneNumber: {
    mobile: "(//input[@placeholder='(___) ___-____'])",
    desktop: "(//input[@placeholder='(___) ___-____'])",
  },
  numberComponentInput: {
    mobile: "(//input[@type='number'])",
    desktop: "(//input[@type='number'])",
  },
  // errorMsgNumberComponent:
  // {
  //   mobile: "//div[@class='previewComponents_numberInputBox__zdwdF previewComponents_errorTelephoneInput__cVncb']//ancestor::div//p[@class='text-red-500']",
  //   desktop: "//div[@class='previewComponents_numberInputBox__zdwdF previewComponents_errorTelephoneInput__cVncb']//ancestor::div//p[@class='text-red-500']"
  // },
  CWF_Template_TitleIsMandatoryLocator: (title: string) => ({
    mobile: `//label[normalize-space(text())="${title}*"]`,
    desktop: `//label[normalize-space(text())="${title}*"]`,
  }),
  CWF_Template_TitleIsNotMandatoryLocator: (title: string) => ({
    mobile: `//label[normalize-space(text())="${title}"]`,
    desktop: `//label[normalize-space(text())="${title}"]`,
  }),
  CWF_Template_isMandatoryErrorPrompt: {
    mobile: "(//p[contains(@class,'text-red-500')])",
    desktop: "(//p[contains(@class,'text-red-500')])",
  },
  CWF_Template_inputTextFieldDynamicOpeningLocator: {
    mobile: '//input[@placeholder="',
    desktop: '//input[@placeholder="',
  },
  CWF_Template_inputTextareaFieldDynamicOpeningLocator: {
    mobile: '//textarea[@placeholder="',
    desktop: '//textarea[@placeholder="',
  },
  CWF_Template_inputTextFieldDynamicClosingLocator: {
    mobile: '"]',
    desktop: '"]',
  },
  CWF_Template_inputTextAlphanumericInvalidInputErrorPrompt: {
    mobile:
      "(//p[normalize-space(text())='Alphabets and Numbers only allowed'])[1]",
    desktop:
      "(//p[normalize-space(text())='Alphabets and Numbers only allowed'])[1]",
  },
  CWF_Template_inputTextOnlyAlphaInvalidInputErrorPrompt: {
    mobile:
      "//p[normalize-space(text())='Alphabetic entries are only allowed']",
    desktop:
      "//p[normalize-space(text())='Alphabetic entries are only allowed']",
  },
  CWF_SavedForm_recentlySavedForm: {
    mobile: "(//div[contains(@class,'_td text-sm')]//a)[1]",
    desktop: "(//div[contains(@class,'_td text-sm')]//a)[1]",
  },
  CWF_SavedForm_recentlySavedFormStatus: {
    mobile: "(//span[contains(@class,'flex items-center')]//span)[1]",
    desktop: "(//span[contains(@class,'flex items-center')]//span)[1]",
  },
  Attachment_uploadPhotoBtnInput: {
    mobile: "(//span[normalize-space(text())='Add Photos']/following::input)",
    desktop: "(//span[normalize-space(text())='Add Photos']/following::input)",
  },
  Attachment_recentlyUploadedPhoto: {
    mobile: "(//img[contains(@class,'rounded')])",
    desktop: "(//img[contains(@class,'rounded')])",
  },
  Attachment_loaderAltImageUploadPhoto: {
    mobile: "//div[contains(@class,'inset-0 flex')]",
    desktop: "//div[contains(@class,'inset-0 flex')]",
  },
  Attachment_spinnerUploadPhoto: {
    mobile: "//i[contains(@class,'animate-spin absolute')]",
    desktop: "//i[contains(@class,'animate-spin absolute')]",
  },
  Attachment_uploadingTextWhilePhotoUpload: {
    mobile: "//p[normalize-space(text())='Uploading']",
    desktop: "//p[normalize-space(text())='Uploading']",
  },
  Attachment_cancelButtonWhilePhotoUpload: {
    mobile: "//button//span[normalize-space(text())='Cancel']",
    desktop: "//button//span[normalize-space(text())='Cancel']",
  },
  Attachment_deletedPhotoSuccessfullyPrompt: {
    mobile: "//p[@class='text-neutral-light-100 text-base text-left']",
    desktop: "//p[@class='text-neutral-light-100 text-base text-left']",
  },
  Attachment_descriptionTextAreaPhoto: {
    mobile: "(//textarea[@placeholder='Add a description'])",
    desktop: "(//textarea[@placeholder='Add a description'])",
  },
  Attachment_lblDescriptionTextArea: {
    mobile: "//label[contains(@class,'block text-tiny')]",
    desktop: "//label[contains(@class,'block text-tiny')]",
  },
  Attachment_deleteBtnRecentlyUploadedPhoto: {
    mobile: "//button[@aria-label='Delete photo']",
    desktop: "//button[@aria-label='Delete photo']",
  },
  Attachment_deletePopupBox: {
    mobile:
      "//span[contains(@class,'inline-block h-screen')]/following-sibling::div[1]",
    desktop:
      "//span[contains(@class,'inline-block h-screen')]/following-sibling::div[1]",
  },
  Attachment_popupBoxPhotoHeaderLbl: {
    mobile: "//h6[normalize-space(text())='Delete Photos']",
    desktop: "//h6[normalize-space(text())='Delete Photos']",
  },
  Attachment_popupBoxPhotoDescriptionLbl: {
    mobile: "(//div[contains(@class,'flex flex-col')]//p)[3]",
    desktop: "(//div[contains(@class,'flex flex-col')]//p)[3]",
  },
  Attachment_deletePhotoPopupDeleteBtn: {
    mobile:
      "//button[contains(@class,'text-center truncate')]/following-sibling::button[1]",
    desktop:
      "//button[contains(@class,'text-center truncate')]/following-sibling::button[1]",
  },
  Attachment_deletePhotoPopupCancelBtn: {
    mobile: "//footer[contains(@class,'mt-14 flex')]//button[1]",
    desktop: "//footer[contains(@class,'mt-14 flex')]//button[1]",
  },
  Attachment_documentUploadBtnInput: {
    mobile:
      "(//span[normalize-space(text())='Add Documents']/following::input)",
    desktop:
      "(//span[normalize-space(text())='Add Documents']/following::input)",
  },
  Attachment_recentlyUploadedDocument: {
    mobile: "(//div[@data-testid='document-item'])",
    desktop: "(//div[@data-testid='document-item'])",
  },
  Attachment_recentlyUploadedDocIcon: {
    mobile: "//i[@class='ci-file_blank_outline text-2xl']",
    desktop: "//i[@class='ci-file_blank_outline text-2xl']",
  },
  Attachment_recentlyUploadedDocName: {
    mobile:
      "//label[contains(@class,'text-component-label font-component-label')]",
    desktop:
      "//label[contains(@class,'text-component-label font-component-label')]",
  },
  Attachment_recentlyUploadedDocMenuBtn: {
    mobile: "//div[@class='relative z-100']//button",
    desktop: "//div[@class='relative z-100']//button",
  },
  Attachment_uploadedDocMenuBtnAfterDropdownActive: {
    mobile: "//button[@aria-expanded='true']",
    desktop: "//button[@aria-expanded='true']",
  },
  Attachment_recentlyUploadedDocDetailsLbl: {
    mobile: "(//p[contains(@class,'text-caption-text font-caption-text')])[3]",
    desktop: "(//p[contains(@class,'text-caption-text font-caption-text')])[3]",
  },
  Attachment_editDocMenuItem: {
    mobile: "(//button[contains(@class,'flex flex-1')])[1]",
    desktop: "(//button[contains(@class,'flex flex-1')])[1]",
  },
  Attachment_editDocPopupBox: {
    mobile: "(//div[contains(@class,'min-h-screen flex')]//div)[2]",
    desktop: "(//div[contains(@class,'min-h-screen flex')]//div)[2]",
  },
  Attachment_editDocPopupUpdateNameInput: {
    mobile: "//input[contains(@class,'flex-auto rounded-md')]",
    desktop: "//input[contains(@class,'flex-auto rounded-md')]",
  },
  Attachment_editDocPopupCurrentFilename: {
    mobile: "(//p[@class='text-base text-neutral-shade-100'])[1]",
    desktop: "(//p[@class='text-base text-neutral-shade-100'])[1]",
  },
  Attachment_editDocPopupCancelBtn: {
    mobile: "(//button[contains(@class,'text-center truncate')])[3]",
    desktop: "(//button[contains(@class,'text-center truncate')])[3]",
  },
  Attachment_editDocPopupAddBtn: {
    mobile:
      "//button[contains(@class,'text-center truncate')]/following-sibling::button[1]",
    desktop:
      "//button[contains(@class,'text-center truncate')]/following-sibling::button[1]",
  },
  Attachment_editDocPopupUploadDateTime: {
    mobile: "(//p[@class='text-base text-neutral-shade-100'])[2]",
    desktop: "(//p[@class='text-base text-neutral-shade-100'])[2]",
  },
  Attachment_downloadDocMenuItem: {
    mobile: "(//button[contains(@class,'flex flex-1')])[2]",
    desktop: "(//button[contains(@class,'flex flex-1')])[2]",
  },
  Attachment_deleteDocMenuItem: {
    mobile: "(//button[contains(@class,'flex flex-1')])[3]",
    desktop: "(//button[contains(@class,'flex flex-1')])[3]",
  },
  Attachment_popupDeleteDocHeadingLbl: {
    mobile: "//h6[normalize-space(text())='Delete Documents']",
    desktop: "//h6[normalize-space(text())='Delete Documents']",
  },
  Attachment_popupDeleteDocDescriptionLbl: {
    mobile:
      "//p[contains(.,'Are you sure you want to permanently delete this document? This action cannot be undone.')]",
    desktop:
      "//p[contains(.,'Are you sure you want to permanently delete this document? This action cannot be undone.')]",
  },
  CWF_TemplateForms_FiltersBtn: {
    mobile: "(//button[contains(@class,'text-center truncate')])[1]",
    desktop: "(//button[contains(@class,'text-center truncate')])[1]",
  },
  templateFormFilters_filterBtnText: {
    mobile: "//section[@id='page-layout']//h4/following-sibling::button//span",
    desktop: "//section[@id='page-layout']//h4/following-sibling::button//span",
  },
  templateFormFiltersHeader: {
    mobile:
      "//header[contains(@class,'flex items-center justify-between bg-brand-gray')]",
    desktop:
      "//header[contains(@class,'flex items-center justify-between bg-brand-gray')]",
  },
  templateFormFiltersClearAllBtn: {
    mobile: "(//div[contains(@class,'flex-1 px-3 overflow-y-auto')]/button)[1]",
    desktop:
      "(//div[contains(@class,'flex-1 px-3 overflow-y-auto')]/button)[1]",
  },
  templateFormFiltersFormName: {
    mobile: "(//div[contains(@class,'flex-1 px-3 overflow-y-auto')]/button)[2]",
    desktop:
      "(//div[contains(@class,'flex-1 px-3 overflow-y-auto')]/button)[2]",
  },
  templateFormFiltersStatus: {
    mobile: "(//div[contains(@class,'flex-1 px-3 overflow-y-auto')]/button)[3]",
    desktop:
      "(//div[contains(@class,'flex-1 px-3 overflow-y-auto')]/button)[3]",
  },
  templateFormFiltersCreatedBy: {
    mobile: "(//div[contains(@class,'flex-1 px-3 overflow-y-auto')]/button)[4]",
    desktop:
      "(//div[contains(@class,'flex-1 px-3 overflow-y-auto')]/button)[4]",
  },
  templateFormFiltersCreatedOn: {
    mobile: "(//div[contains(@class,'flex-1 px-3 overflow-y-auto')]/button)[5]",
    desktop:
      "(//div[contains(@class,'flex-1 px-3 overflow-y-auto')]/button)[5]",
  },
  templateFormFiltersUpdatedBy: {
    mobile: "(//div[contains(@class,'flex-1 px-3 overflow-y-auto')]/button)[6]",
    desktop:
      "(//div[contains(@class,'flex-1 px-3 overflow-y-auto')]/button)[6]",
  },
  templateFormFiltersUpdatedOn: {
    mobile: "(//div[contains(@class,'flex-1 px-3 overflow-y-auto')]/button)[7]",
    desktop:
      "(//div[contains(@class,'flex-1 px-3 overflow-y-auto')]/button)[7]",
  },
  templateFormFiltersCompletedOn: {
    mobile: "(//div[contains(@class,'flex-1 px-3 overflow-y-auto')]/button)[8]",
    desktop:
      "(//div[contains(@class,'flex-1 px-3 overflow-y-auto')]/button)[8]",
  },
  templateFormFiltersProjects: {
    mobile: "(//div[contains(@class,'flex-1 px-3 overflow-y-auto')]/button)[9]",
    desktop:
      "(//div[contains(@class,'flex-1 px-3 overflow-y-auto')]/button)[9]",
  },
  templateFormFiltersLocation: {
    mobile:
      "(//div[contains(@class,'flex-1 px-3 overflow-y-auto')]/button)[10]",
    desktop:
      "(//div[contains(@class,'flex-1 px-3 overflow-y-auto')]/button)[10]",
  },
  templateFormFiltersRegion: {
    mobile:
      "(//div[contains(@class,'flex-1 px-3 overflow-y-auto')]/button)[11]",
    desktop:
      "(//div[contains(@class,'flex-1 px-3 overflow-y-auto')]/button)[11]",
  },
  templateFormFiltersApplyBtn: {
    mobile: "//div[@class='flex justify-end gap-4 px-6 py-6']/button[2]",
    desktop: "//div[@class='flex justify-end gap-4 px-6 py-6']/button[2]",
  },
  templateFormFiltersNoDataFoundMsg: {
    mobile:
      "//div[@class='flex flex-col items-center w-full text-center px-6']/p[1]",
    desktop:
      "//div[@class='flex flex-col items-center w-full text-center px-6']/p[1]",
  },
  templateFormSearchInput: {
    mobile: "//input[@placeholder='Search Template Forms']",
    desktop: "//input[@placeholder='Search Template Forms']",
  },
  templateFormSearchResultSet: {
    mobile: "(//div[@class='w-full flex bg-white']//a/span)",
    desktop: "(//div[@class='w-full flex bg-white']//a/span)",
  },
  templateFormSearchResultStatus: {
    mobile: "(//div[@class='_tbody flex flex-col gap-2.5']//span/span)",
    desktop: "(//div[@class='_tbody flex flex-col gap-2.5']//span/span)",
  },
  filterFormNameInput: {
    mobile: "(//div[@class='p-3']//input)[1]",
    desktop: "(//div[@class='p-3']//input)[1]",
  },
  selectFilterFormName: {
    mobile:
      "//div[@class='flex items-center p-3 text-base cursor-pointer bg-brand-gray-10 css-0']",
    desktop:
      "//div[@class='flex items-center p-3 text-base cursor-pointer bg-brand-gray-10 css-0']",
  },
  filterCompletedOnFromDate: {
    mobile:
      "((//div[contains(@class,'flex-1 px-3 overflow-y-auto')]/button)[8]/following-sibling::div//input)[1]",
    desktop:
      "((//div[contains(@class,'flex-1 px-3 overflow-y-auto')]/button)[8]/following-sibling::div//input)[1]",
  },
  filterResultSetCompletedOn: {
    mobile:
      "//div[@class='_tr px-4 py-1 min-h-[3.5rem] bg-white  flex items-center']/div[5]",
    desktop:
      "//div[@class='_tr px-4 py-1 min-h-[3.5rem] bg-white  flex items-center']/div[5]",
  },
  templateFilterCompleteStatus: {
    mobile:
      "//div[contains(@class, 'flex items-center gap-2')]/input[@id='completed']",
    desktop:
      "//div[contains(@class, 'flex items-center gap-2')]/input[@id='completed']",
  },
  templateFilterFirstFormName: {
    mobile:
      "(//div[contains(@class,'_tbody flex flex-col gap-2.5')]//div[contains(@class,'_td text-sm pr-4 last:pr-0')]/a/span)[1]",
    desktop:
      "(//div[contains(@class,'_tbody flex flex-col gap-2.5')]//div[contains(@class,'_td text-sm pr-4 last:pr-0')]/a/span)[1]",
  },
  filterCompletedOnToDate: {
    mobile:
      "((//div[contains(@class,'flex-1 px-3 overflow-y-auto')]/button)[8]/following-sibling::div//input)[2]",
    desktop:
      "((//div[contains(@class,'flex-1 px-3 overflow-y-auto')]/button)[8]/following-sibling::div//input)[2]",
  },
  templateFilterCreatedOnFromDate: {
    mobile:
      "(//div[contains(@class,'flex flex-row text-base font-semibold text-neutral-shade-75 justify-between')]//button/following-sibling::div//input)[1]",
    desktop:
      "(//div[contains(@class,'flex flex-row text-base font-semibold text-neutral-shade-75 justify-between')]//button/following-sibling::div//input)[1]",
  },
  templateFilterCreatedOnToDate: {
    mobile:
      "(//div[contains(@class,'flex flex-row text-base font-semibold text-neutral-shade-75 justify-between')]//button/following-sibling::div//input)[2]",
    desktop:
      "(//div[contains(@class,'flex flex-row text-base font-semibold text-neutral-shade-75 justify-between')]//button/following-sibling::div//input)[2]",
  },
  templateFilterFirstCreatedOnDate: {
    mobile:
      "(//div[contains(@class,'_tr px-4 py-1 min-h-[3.5rem] bg-white  flex items-center')]/div[4])[1]",
    desktop:
      "(//div[contains(@class,'_tr px-4 py-1 min-h-[3.5rem] bg-white  flex items-center')]/div[4])[1]",
  },
  templateFormSearchResultCreatedOnDate: {
    mobile:
      "//div[@class='_tr px-4 py-1 min-h-[3.5rem] bg-white  flex items-center']/div[4]",
    desktop:
      "//div[@class='_tr px-4 py-1 min-h-[3.5rem] bg-white  flex items-center']/div[4]",
  },
  choiceComponentLocator: {
    mobile:
      "(//div[contains(@class,'previewComponents_choiceComponentParent__GZUn_ flex')])",
    desktop:
      "(//div[contains(@class,'previewComponents_choiceComponentParent__GZUn_ flex')])",
  },
  choiceComponentTitle: {
    mobile: "//label[contains(@class,'block md:text-sm')]",
    desktop: "//label[contains(@class,'block md:text-sm')]",
  },
  choicePrepopulatedSingleOptionLabelClassFirst: {
    mobile: " and contains(@class, 'flex')])[",
    desktop: " and contains(@class, 'flex')])[",
  },
  choicePrepopulatedSingleOptionLabelClassSecond: {
    mobile: "]//div[@role='radio' and contains(., '",
    desktop: "]//div[@role='radio' and contains(., '",
  },
  choicePrepopulatedSingleOptionLabelClosing: {
    mobile: "')]",
    desktop: "')]",
  },
  EnergyWheelComponentLocator: {
    mobile: `//div[contains(@class,'relative w-full')]`,
    desktop: `//div[contains(@class,'relative w-full')]`,
  },
  subtitleComponentLocator: {
    mobile: "(//p[contains(@class,'text-body-text font-body-text')])[1]",
    desktop: "(//p[contains(@class,'text-body-text font-body-text')])[1]",
  },
  hazardAndControlsMessageBox:{
    mobile:"(//p[contains(@class,'text-caption-text font-caption-text')])[1]",
    desktop:"(//p[contains(@class,'text-caption-text font-caption-text')])[1]"  
  },
  hazardAndControlsContentMessage:{
    mobile:"(//p[contains(@class,'text-caption-text font-caption-text')])[2]",
    desktop:"(//p[contains(@class,'text-caption-text font-caption-text')])[2]"
  },
  hazardsAndControlsAddButton:{
    mobile: "(//button[contains(@class,'text-center truncate') and .//span[contains(text(),'Add Hazards')]])[1]",
    desktop: "(//button[contains(@class,'text-center truncate') and .//span[contains(text(),'Add Hazards')]])[1]"
  },
  hazardsAndControlsAddButton2:{
    mobile: "(//button[contains(@class,'text-center truncate') and .//span[contains(text(),'Add Hazards')]])[1]",
    desktop: "(//button[contains(@class,'text-center truncate') and .//span[contains(text(),'Add Hazards')]])[1]"
  },
  manuallyAddedHazards:{
    mobile:"//span[contains(@class,'text-brand-urbint-40 font-semibold')]",
    desktop:"//span[contains(@class,'text-brand-urbint-40 font-semibold')]"
  },
  inputBoxForManuallyAddedHazards:{
    mobile:"//input[contains(@class,'p-2 flex-auto')]",
    desktop:"//input[contains(@class,'p-2 flex-auto')]"
  },
  addButtonForManuallyAddedHazards:{
    mobile:"(//button[contains(@class,'text-xl text-neutral-shade-75')])[3]",
    desktop:"(//button[contains(@class,'text-xl text-neutral-shade-75')])[3]"
  },
  addControlsButtonManuallyAddedHazards:{
    mobile:"(//div[contains(@class,'rounded-md pt-1')])[3]",
    desktop:"(//div[contains(@class,'rounded-md pt-1')])[3]"
  },
  deleteButtonForAddedHazards:{
    mobile:"(//i[contains(@class,'ci-trash_empty text-neutral-shade-58')])[3]",
    desktop:"(//i[contains(@class,'ci-trash_empty text-neutral-shade-58')])[3]"
  },
  checkDeleteModalForAddedHazards:{
    mobile:"//span[contains(@class,'inline-block h-screen')]/following-sibling::div[1]",
    desktop:"//span[contains(@class,'inline-block h-screen')]/following-sibling::div[1]"
  },
  confirmDeleteButtonForAddedHazards:{
    mobile:"//button[contains(@class,'text-center truncate')]/following-sibling::button[1]",
    desktop:"//button[contains(@class,'text-center truncate')]/following-sibling::button[1]"
  },
  deletionOfControlsCancelButton:{
    mobile:"(//i[contains(@class,'ci-close_small border-[1px]')])[2]",
    desktop:"(//i[contains(@class,'ci-close_small border-[1px]')])[2]"
  },
  hazardsAndControlsCancelButton:{
    mobile: "//button[@title='Close modal']//i[1]",
    desktop: "//button[@title='Close modal']//i[1]"
  },
  hazardsSelectionModal:{
    mobile:"(//div[contains(@class,'grid grid-cols-1')]//div)[5]",
    desktop:"(//div[contains(@class,'grid grid-cols-1')]//div)[5]"
  },
  addButtonHazardsAndControls:{
    mobile:"//button[contains(@class,'text-center truncate')]/following-sibling::button[1]",
    desktop:"//button[contains(@class,'text-center truncate')]/following-sibling::button[1]"
  },
  addControlsButton:{
    mobile:"(//div[@class='w-full mx-auto ']//div)[1]",
    desktop:"(//div[@class='w-full mx-auto ']//div)[1]"
  },
  controlsSelection:{
    mobile:"(//div[contains(@class,'px-1.5 py-2')])[1]",
    desktop:"(//div[contains(@class,'px-1.5 py-2')])[1]"
  },
  otherHazardsSelection:{
    mobile:"(//div[contains(@class,'max-h-[16.5vh] overflow-auto')]//div)[1]",
    desktop:"(//div[contains(@class,'max-h-[16.5vh] overflow-auto')]//div)[1]"
  },
  addOtherControlsButton:{
    mobile:"(//div[contains(@class,'rounded-md pt-1')])[2]",
    desktop:"(//div[contains(@class,'rounded-md pt-1')])[2]"
  },
  hazardCardColor: {
    mobile:"(//div[contains(@class,'p-2 flex')])",
    desktop:"(//div[contains(@class,'p-2 flex')])"
  },
  hazardCardHeader: {
    mobile:"//div[contains(@class,'p-2 flex')]//div[1]",
    desktop:"//div[contains(@class,'p-2 flex')]//div[1]"
  },
  emailInput: {
    mobile: "(//div[contains(@class,'relative flex')]//input)",
    desktop: "(//div[contains(@class,'relative flex')]//input)"
  },
  CWF_Template_EmailMandatoryDynamicTitle: (titleName: string) => ({
    mobile: `//label[normalize-space(text())="${titleName} *"]`,
    desktop: `//label[normalize-space(text())="${titleName} *"]`,
  }),

  CWF_Template_EmailNonMandatoryDynamicTitle: (titleName: string) => ({
    mobile: `//label[normalize-space(text())="${titleName}"]`,
    desktop: `//label[normalize-space(text())="${titleName}"]`,
  }),
  requiredFieldErrorToast: {
    mobile: "//div//button[.//p[contains(text(),'This field is required')]]",
    desktop: "//div//button[.//p[contains(text(),'This field is required')]]",
  },
  FinalCWFCompleteFormBtn: {
    mobile: "//div[@role='dialog' or contains(@class,'fixed inset-0')]//button[contains(@class,'text-center truncate') and .//span[contains(text(),'Complete Form')]]",
    desktop: "//div[@role='dialog' or contains(@class,'fixed inset-0')]//button[contains(@class,'text-center truncate') and .//span[contains(text(),'Complete Form')]]"
  }
};
