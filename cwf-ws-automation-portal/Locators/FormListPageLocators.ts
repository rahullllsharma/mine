export const FormListPageLocators = {
  FormsListPage_lblHeading: {
    mobile: "//h4[normalize-space(text())='Forms List']",
    desktop: "//h4[normalize-space(text())='Forms List']",
  },
  FormsListPage_lblSearchFormsList: {
    mobile: "(//input[@placeholder='Search forms list'])[1]",
    desktop: "(//input[@placeholder='Search forms list'])[1]",
  },
  FormsListPage_lblFilters: {
    mobile: "(//button[contains(@class,'text-center truncate')]//div)[1]",
    desktop: "(//button[contains(@class,'text-center truncate')]//div)[1]",
  },
  FormsListPage_btnAddForm: {
    mobile:
      "//button[contains(@class,'text-center truncate')][.//span[contains(text(),'Add Form')]]",
    desktop:
      "//button[contains(@class,'text-center truncate')][.//span[contains(text(),'Add Form')]]",
  },
  FormsListPage_lblEBOInAddFormBtn: {
    mobile: "//p[normalize-space(text())='Energy Based Observation']",
    desktop: "//p[normalize-space(text())='Energy Based Observation']",
  },
  FormsListPage_lblJSBInAddFormBtn: {
    mobile: "//p[normalize-space(text())='Job Safety Briefing']",
    desktop: "//p[normalize-space(text())='Job Safety Briefing']",
  },
  FormsListPage_btnJSBSaveAndContinue: {
    mobile: "//footer[contains(@class,'flex flex-col')]//button[1]",
    desktop: "//footer[contains(@class,'flex flex-col')]//button[1]",
  },
  FormsListPage_btnJobSafetyBriefing: {
    mobile:
      "(//li[@role='menuitem']//button)[.//p[text()='Job Safety Briefing']]",
    desktop:
      "(//li[@role='menuitem']//button)[.//p[text()='Job Safety Briefing']]",
  },
  FormsListPage_btnEnergyBasedObservation: {
    mobile:
      "(//li[@role='menuitem']//button)[.//p[text()='Energy Based Observation']]",
    desktop:
      "(//li[@role='menuitem']//button)[.//p[text()='Energy Based Observation']]",
  },
  FormsListPage_JSB_btnGoBackToAllFormsBtn: {
    mobile: "//span[normalize-space(text())='All Forms List']",
    desktop: "//span[normalize-space(text())='All Forms List']",
  },
  FormsListPage_JSB_lblHeadingJSB: {
    mobile: "//h4[normalize-space(text())='Job Safety Briefing']",
    desktop: "//h4[normalize-space(text())='Job Safety Briefing']",
  },
  FormsListPage_JSB_lblFormJSB: {
    mobile: "(//button[contains(@class,'inline-block p-4')])[1]",
    desktop: "(//button[contains(@class,'inline-block p-4')])[1]",
  },
  FormsListPage_JSB_lblHistoryJSB: {
    mobile: "(//button[contains(@class,'inline-block p-4')])[2]",
    desktop: "(//button[contains(@class,'inline-block p-4')])[2]",
  },
  FormsListPage_JSB_NavJobInfo: {
    mobile: "(//span[contains(@class,'ml-2 text-base')])[1]",
    desktop: "(//span[contains(@class,'ml-2 text-base')])[1]",
  },
  FormsListPage_JSB_NavMedAndEmer: {
    mobile: "(//span[contains(@class,'ml-2 text-base')])[2]",
    desktop: "(//span[contains(@class,'ml-2 text-base')])[2]",
  },
  FormsListPage_JSB_NavTaskAndCriRisk: {
    mobile: "(//span[contains(@class,'ml-2 text-base')])[3]",
    desktop: "(//span[contains(@class,'ml-2 text-base')])[3]",
  },
  FormsListPage_JSB_NavEnergySrcCtrls: {
    mobile: "(//span[contains(@class,'ml-2 text-base')])[4]",
    desktop: "(//span[contains(@class,'ml-2 text-base')])[4]",
  },
  FormsListPage_JSB_NavWorkProc: {
    mobile: "(//span[contains(@class,'ml-2 text-base')])[5]",
    desktop: "(//span[contains(@class,'ml-2 text-base')])[5]",
  },
  FormsListPage_JSB_NavSiteConditions: {
    mobile: "(//span[contains(@class,'ml-2 text-base')])[6]",
    desktop: "(//span[contains(@class,'ml-2 text-base')])[6]",
  },
  FormsListPage_JSB_NavCtrlAsses: {
    mobile: "(//span[contains(@class,'ml-2 text-base')])[7]",
    desktop: "(//span[contains(@class,'ml-2 text-base')])[7]",
  },
  FormsListPage_JSB_NavAttachments: {
    mobile: "(//span[contains(@class,'ml-2 text-base')])[8]",
    desktop: "(//span[contains(@class,'ml-2 text-base')])[8]",
  },
  FormsListPage_JSB_NavGD: {
    mobile: "(//span[contains(@class,'ml-2 text-base')])[9]",
    desktop: "(//span[contains(@class,'ml-2 text-base')])[9]",
  },
  FormsListPage_JSB_NavCrewSignOff: {
    mobile: "(//span[contains(@class,'ml-2 text-base')])[10]",
    desktop: "(//span[contains(@class,'ml-2 text-base')])[10]",
  },
  JSB_sectionRightSide: {
    mobile: "//section[contains(@class,'flex-1 w-full')]",
    desktop: "//section[contains(@class,'flex-1 w-full')]",
  },
  JSB_JobInfo_workAddressReqCheck: {
    mobile: "(//span[contains(@class,'text-sm mt-1')])[1]",
    desktop: "(//span[contains(@class,'text-sm mt-1')])[1]",
  },
  JSB_JobInfo_operatingHQReqCheck: {
    mobile: "(//span[contains(@class,'text-sm mt-1')])[2]",
    desktop: "(//span[contains(@class,'text-sm mt-1')])[2]",
  },
  JSB_JobInfo_lblGeneralInfo: {
    mobile: "//h2[normalize-space(text())='General Information']",
    desktop: "//h2[normalize-space(text())='General Information']",
  },
  JSB_JobInfo_GenInfo_lblBriefingDate: {
    mobile: "(//label[contains(@class,'block text-tiny')])[1]",
    desktop: "(//label[contains(@class,'block text-tiny')])[1]",
  },
  JSB_JobInfo_GenInfo_lblBriefingDatePrompt: {
    mobile:
      "//span[normalize-space(text())='Please select a date between yesterday and two weeks in the future.']",
    desktop:
      "//span[normalize-space(text())='Please select a date between yesterday and two weeks in the future.']",
  },
  JSB_JobInfo_GenInfo_lblBriefingTime: {
    mobile: "(//label[contains(@class,'block text-tiny')])[2]",
    desktop: "(//label[contains(@class,'block text-tiny')])[2]",
  },
  JSB_JobInfo_GenInfo_lblGPSCo: {
    mobile: "//h2[normalize-space(text())='GPS Coordinates']",
    desktop: "//h2[normalize-space(text())='GPS Coordinates']",
  },
  JSB_JobInfo_GenInfo_lblDateSelector: {
    mobile: "//input[contains(@class,'flex-auto rounded-md')]",
    desktop: "//input[contains(@class,'flex-auto rounded-md')]",
  },
  JSB_JobInfo_GenInfo_lblDatePickerBox: {
    mobile: "react-datepicker__month-container",
    desktop: "react-datepicker__month-container",
  },
  JSB_JobInfo_GenInfo_btnNextMonthDatePicker: {
    mobile:
      "//button[@class='react-datepicker__navigation react-datepicker__navigation--next']",
    desktop:
      "//button[@class='react-datepicker__navigation react-datepicker__navigation--next']",
  },
  JSB_JobInfo_GenInfo_btnDynamicDateInDatePickerBox: {
    mobile:
      "//div[contains(@class, 'react-datepicker__day react-datepicker__day--",
    desktop:
      "//div[contains(@class, 'react-datepicker__day react-datepicker__day--",
  },
  JSB_JobInfo_GenInfo_btnTimeSelector: {
    mobile: "(//input[contains(@class,'flex-auto appearance-none')])[1]",
    desktop: "(//input[contains(@class,'flex-auto appearance-none')])[1]",
  },
  JSB_JobInfo_GPSCo_lblLatitude: {
    mobile: "//label[normalize-space(text())='Current Latitude']",
    desktop: "//label[normalize-space(text())='Current Latitude']",
  },
  JSB_JobInfo_GPSCo_lblLongitude: {
    mobile: "//label[normalize-space(text())='Current Longitude']",
    desktop: "//label[normalize-space(text())='Current Longitude']",
  },
  FormsListPage_JSB_txtCurrentLatitude: {
    mobile: "(//input[@type='number'])[1]",
    desktop: "(//input[@type='number'])[1]",
  },
  FormsListPage_JSB_txtCurrentLongitude: {
    mobile: "(//input[@type='number'])[2]",
    desktop: "(//input[@type='number'])[2]",
  },
  JSB_JobInfo_GenInfo_btnUseCurrentLoc: {
    mobile: "(//button[contains(@class,'text-center truncate')]//div)[1]",
    desktop: "(//button[contains(@class,'text-center truncate')]//div)[1]",
  },
  JSB_JobInfo_WorkLoc_lblWorkLocation: {
    mobile: "//h2[normalize-space(text())='Work Location']",
    desktop: "//h2[normalize-space(text())='Work Location']",
  },
  JSB_JobInfo_WorkLoc_lblAddressPrompt: {
    mobile:
      "//label[normalize-space(text())='Please list included addresses and scope of work *']",
    desktop:
      "//label[normalize-space(text())='Please list included addresses and scope of work *']",
  },
  JSB_JobInfo_WorkLoc_txtBoxAddress: {
    mobile: "//textarea[contains(@class,'flex-auto rounded-md')]",
    desktop: "//textarea[contains(@class,'flex-auto rounded-md')]",
  },
  JSB_JobInfo_WorkLoc_lblOperatingHQ: {
    mobile: "//span[normalize-space(text())='Operating HQ *']",
    desktop: "//span[normalize-space(text())='Operating HQ *']",
  },
  JSB_btnSelectOperatingHQ: {
    mobile: "//div[contains(@class,'flex flex-grow')]//div[1]",
    desktop: "//div[contains(@class,'flex flex-grow')]//div[1]",
  },
  JSB_JobInfo_WorkLoc_dropdownMenuOperatingHQ: {
    mobile: "//div[@class='relative']//ul[1]",
    desktop: "//div[@class='relative']//ul[1]",
  },
  JSB_JobInfo_WorkLoc_dropdownMenuOperatingHQList: {
    mobile: "//div[@class='relative']//ul[1]//li",
    desktop: "//div[@class='relative']//ul[1]//li",
  },
  FormsListPage_JSB_selectOperatingHQFirstOption: {
    mobile: "(//span[@class='truncate max-w-md'])[1]",
    desktop: "(//span[@class='truncate max-w-md'])[1]",
  },
  JSB_JobInfo_WorkLoc_OptionCobdenOperatingHQ: {
    mobile: "//span[normalize-space(text())='Cobden']",
    desktop: "//span[normalize-space(text())='Cobden']",
  },
  JSB_btnNavMedAndEmer: {
    mobile: "(//button[contains(@class,'p-3 bg-neutral-shade-3')])[2]",
    desktop: "(//button[contains(@class,'p-3 bg-neutral-shade-3')])[2]",
  },
  FormsListPage_JSB_txtEmergencyContact1_Name: {
    mobile: "(//input[contains(@class,'flex-auto appearance-none')])[1]",
    desktop: "(//input[contains(@class,'flex-auto appearance-none')])[1]",
  },
  FormsListPage_JSB_txtEmergencyContact1_PhoneNumber: {
    mobile:
      "//*[@id='page-layout']/div/section/div/fieldset[1]/div/div[2]/div/input",
    desktop:
      "//*[@id='page-layout']/div/section/div/fieldset[1]/div/div[2]/div/input",
  },
  FormsListPage_JSB_txtEmergencyContact2_Name: {
    mobile: "(//input[contains(@class,'flex-auto appearance-none')])[2]",
    desktop: "(//input[contains(@class,'flex-auto appearance-none')])[2]",
  },
  FormsListPage_JSB_txtEmergencyContact2_PhoneNumber: {
    mobile:
      "//*[@id='page-layout']/div/section/div/fieldset[1]/div/div[4]/div/input",
    desktop:
      "//*[@id='page-layout']/div/section/div/fieldset[1]/div/div[4]/div/input",
  },
  FormsListPage_JSB_selectAEDLocation: {
    mobile: "(//div[contains(@class,'flex flex-grow')])[2]",
    desktop: "(//div[contains(@class,'flex flex-grow')])[2]",
  },
  FormsListPage_JSB_selectAEDLocationCabOfTruck: {
    mobile: "//li[@aria-hidden='true']//span[contains(text(),'Cab of truck')]",
    desktop: "//li[@aria-hidden='true']//span[contains(text(),'Cab of truck')]",
  },
  FormsListPage_JSB_selectAEDLocationTruckDriverSideComp: {
    mobile:
      "//li[@aria-hidden='true']//span[contains(text(),'Truck driver side compartment')]",
    desktop:
      "//li[@aria-hidden='true']//span[contains(text(),'Truck driver side compartment')]",
  },
  FormsListPage_JSB_selectAEDLocationOther: {
    mobile: "(//li[@aria-hidden='true']//span)[3]",
    desktop: "(//li[@aria-hidden='true']//span)[3]",
  },
  JSB_MedAndEmer_lblEmergencyContacts: {
    mobile: "//h2[normalize-space(text())='Emergency Contacts']",
    desktop: "//h2[normalize-space(text())='Emergency Contacts']",
  },
  JSB_MedAndEmer_lblEmerContact1: {
    mobile:
      "//label[normalize-space(text())='Emergency Contact 1 (e.g. Supervisor) *']",
    desktop:
      "//label[normalize-space(text())='Emergency Contact 1 (e.g. Supervisor) *']",
  },
  JSB_MedAndEmer_lblEmerContact1PhoneNum: {
    mobile:
      "//label[normalize-space(text())='Emergency Contact 1 Phone Number *']",
    desktop:
      "//label[normalize-space(text())='Emergency Contact 1 Phone Number *']",
  },
  JSB_MedAndEmer_lblEmerContact2: {
    mobile:
      "//label[normalize-space(text())='Emergency Contact 2 (e.g. Safety Supervisor) *']",
    desktop:
      "//label[normalize-space(text())='Emergency Contact 2 (e.g. Safety Supervisor) *']",
  },
  JSB_MedAndEmer_lblEmerContact2PhoneNum: {
    mobile:
      "//label[normalize-space(text())='Emergency Contact 2 Phone Number *']",
    desktop:
      "//label[normalize-space(text())='Emergency Contact 2 Phone Number *']",
  },
  JSB_DynamicReqCheckSpan: {
    mobile: "(//span[contains(@class,'text-sm mt-1')])",
    desktop: "(//span[contains(@class,'text-sm mt-1')])",
  },
  JSB_MedAndEmer_lblNearestMedFacility: {
    mobile: "//h2[normalize-space(text())='Nearest Medical Facility *']",
    desktop: "//h2[normalize-space(text())='Nearest Medical Facility *']",
  },
  JSB_MedAndEmer_lblSelectedMedFacility: {
    mobile: "//span[normalize-space(text())='Selected Medical Facility']",
    desktop: "//span[normalize-space(text())='Selected Medical Facility']",
  },
  JSB_MedAndEmer_lblMedicalDevices: {
    mobile:
      "(//h2[contains(@class,'text-section-heading font-section-heading')])[3]",
    desktop:
      "(//h2[contains(@class,'text-section-heading font-section-heading')])[3]",
  },
  JSB_MedAndEmer_lblAEDLocation: {
    mobile: "(//span[contains(@class,'text-sm text-brand-gray-70')])[2]",
    desktop: "(//span[contains(@class,'text-sm text-brand-gray-70')])[2]",
  },
  JSB_MedAndEmer_SelectedOptionInNearestMedFacility: {
    mobile: "//span[@class='truncate']//span[1]",
    desktop: "//span[@class='truncate']//span[1]",
  },
  JSB_MedAndEmer_SelectedOptionOtherInNearestMedFacility: {
    mobile: "(//span[@class='truncate max-w-md'])[1]",
    desktop: "(//span[@class='truncate max-w-md'])[1]",
  },
  JSB_MedAndEmer_selectNearestMedFacility: {
    mobile: "(//div[contains(@class,'flex flex-1')])[2]",
    desktop: "(//div[contains(@class,'flex flex-1')])[2]",
  },
  JSB_MedAndEmer_selectNearestMedFacilityFirstOption: {
    mobile: "//li[normalize-space(text())='Select nearest medical facility']",
    desktop: "//li[normalize-space(text())='Select nearest medical facility']",
  },
  JSB_MedAndEmer_selectNearestMedFacilityOtherOption: {
    mobile: "//li[contains(.,'Other')]",
    desktop: "//li[contains(.,'Other')]",
  },
  JSB_MedAndEmer_lblCustomNearestMedicalFacility: {
    mobile:
      "//label[normalize-space(text())='Please specify the nearest medical facility *']",
    desktop:
      "//label[normalize-space(text())='Please specify the nearest medical facility *']",
  },
  JSB_MedAndEmer_reqCheckNearestMedFacility: {
    mobile:
      "//label[text()='Please specify the nearest medical facility *']/following-sibling::span",
    desktop:
      "//label[text()='Please specify the nearest medical facility *']/following-sibling::span",
  },
  JSB_MedAndEmer_txtCustomNearestMedFacility: {
    mobile: "(//input[contains(@class,'flex-auto appearance-none')])[3]",
    desktop: "(//input[contains(@class,'flex-auto appearance-none')])[3]",
  },
  JSB_MedAndEmer_txtOtherAEDLocation: {
    mobile:
      "//label[normalize-space(text())='Other AED Location *']/following::input",
    desktop:
      "//label[normalize-space(text())='Other AED Location *']/following::input",
  },
  JSB_TasksAndCriRisks_lblHeading: {
    mobile:
      "(//h2[contains(@class,'text-section-heading font-section-heading')])[1]",
    desktop:
      "(//h2[contains(@class,'text-section-heading font-section-heading')])[1]",
  },
  JSB_TasksAndCriRisks_lblAddActivityBtn: {
    mobile: "(//span[@class='mx-1 truncate'])[1]",
    desktop: "(//span[@class='mx-1 truncate'])[1]",
  },
  JSB_TasksAndCriRisks_lblNoActivityPrompt: {
    mobile: "//p[normalize-space(text())='You currently have no Activities']",
    desktop: "//p[normalize-space(text())='You currently have no Activities']",
  },
  JSB_TasksAndCriRisks_lblNoActivitySubPrompt: {
    mobile:
      "//p[normalize-space(text())='Please click the button above to select the Activities you will be working on today']",
    desktop:
      "//p[normalize-space(text())='Please click the button above to select the Activities you will be working on today']",
  },
  JSB_TasksAndCriRisks_lblHeadCriRiskAreas: {
    mobile:
      "(//h2[contains(@class,'text-section-heading font-section-heading')])[2]",
    desktop:
      "(//h2[contains(@class,'text-section-heading font-section-heading')])[2]",
  },
  JSB_TasksAndCriRisks_lblReqCheckNoActivity: {
    mobile: "//div[contains(@class,'font-semibold text-system-error-40')]",
    desktop: "//div[contains(@class,'font-semibold text-system-error-40')]",
  },
  JSB_TasksAndCriRisks_lblLinkCriRiskAreaDocs: {
    mobile:
      "//span[normalize-space(text())='View Critical Risk Area documentation']",
    desktop:
      "//span[normalize-space(text())='View Critical Risk Area documentation']",
  },
  JSB_TasksCriRisks_lblCRAArcFlash: {
    mobile: "//span[normalize-space(text())='Arc Flash']",
    desktop: "//span[normalize-space(text())='Arc Flash']",
  },
  JSB_TasksCriRisks_lblCRAHoistedLoads: {
    mobile: "//span[normalize-space(text())='Hoisted Loads']",
    desktop: "//span[normalize-space(text())='Hoisted Loads']",
  },
  JSB_TasksCriRisks_lblCRAFallOrFallArrest: {
    mobile: "//span[normalize-space(text())='Fall or Fall Arrest']",
    desktop: "//span[normalize-space(text())='Fall or Fall Arrest']",
  },
  JSB_TasksCriRisks_lblCRALineOfFire: {
    mobile: "//span[normalize-space(text())='Line of Fire']",
    desktop: "//span[normalize-space(text())='Line of Fire']",
  },
  JSB_TasksCriRisks_lblCRAExposureToEnergy: {
    mobile: "//span[normalize-space(text())='Exposure to Energy']",
    desktop: "//span[normalize-space(text())='Exposure to Energy']",
  },
  JSB_TasksCriRisks_lblCRACollisionLossOfControl: {
    mobile: "//span[normalize-space(text())='Collision Loss of Control']",
    desktop: "//span[normalize-space(text())='Collision Loss of Control']",
  },
  JSB_TasksCriRisks_lblCRAEncOrConfinedSpace: {
    mobile: "//span[normalize-space(text())='Enclosed or Confined Space']",
    desktop: "//span[normalize-space(text())='Enclosed or Confined Space']",
  },
  JSB_TasksCriRisks_lblCRAMobileEquipment: {
    mobile: "//span[normalize-space(text())='Mobile Equipment']",
    desktop: "//span[normalize-space(text())='Mobile Equipment']",
  },
  JSB_TasksCriRisks_lblCRAFireOrExplosion: {
    mobile: "//span[normalize-space(text())='Fire or Explosion']",
    desktop: "//span[normalize-space(text())='Fire or Explosion']",
  },
  JSB_TasksCriRisks_lblCRATrenchingOrExcavation: {
    mobile: "//span[normalize-space(text())='Trenching or Excavation']",
    desktop: "//span[normalize-space(text())='Trenching or Excavation']",
  },
  JSB_TasksAndCriRisks_btnLinkToCriRiskAreaDocs: {
    mobile:
      "//h2[contains(@class,'text-section-heading font-section-heading')]/following-sibling::a[1]",
    desktop:
      "//h2[contains(@class,'text-section-heading font-section-heading')]/following-sibling::a[1]",
  },
  JSB_TasksAndCriRisks_toggleCRAArcFlash: {
    mobile: "(//input[@type='checkbox'])[1]",
    desktop: "(//input[@type='checkbox'])[1]",
  },
  JSB_TasksAndCriRisks_btnAddActivity: {
    mobile: "(//button[contains(@class,'text-center truncate')]//div)[1]",
    desktop: "(//button[contains(@class,'text-center truncate')]//div)[1]",
  },
  JSB_TasksAndCriRisks_popUpAddActivity: {
    mobile: "(//div[contains(@class,'fixed z-10')]//div)[1]",
    desktop: "(//div[contains(@class,'fixed z-10')]//div)[1]",
  },
  JSB_TasksAndCriRisks_lblPopUpAddActivityHeading: {
    mobile:
      "(//h2[contains(@class,'text-section-heading font-section-heading')])[3]",
    desktop:
      "(//h2[contains(@class,'text-section-heading font-section-heading')])[3]",
  },
  JSB_TasksAndCriRisks_lblNextInAddActivityPopUp: {
    mobile: "//span[normalize-space(text())='Next']",
    desktop: "//span[normalize-space(text())='Next']",
  },
  JSB_TasksAndCriRisks_lblCancelInAddActivityPopUp: {
    mobile: "//span[normalize-space(text())='Cancel']",
    desktop: "//span[normalize-space(text())='Cancel']",
  },
  JSB_TasksAndCriRisks_popUpAddActivitySearchBox: {
    mobile: "//input[contains(@class,'p-2 flex-auto')]",
    desktop: "//input[contains(@class,'p-2 flex-auto')]",
  },
  JSB_TasksAndCriRisks_btnNextInAddActivityPopUp: {
    mobile: "(//button[contains(@class,'text-center truncate')])[3]",
    desktop: "(//button[contains(@class,'text-center truncate')])[3]",
  },
  JSB_TasksAndCriRisks_btnCancelInAddActivityPopUp: {
    mobile: "(//button[contains(@class,'text-center truncate')])[2]",
    desktop: "(//button[contains(@class,'text-center truncate')])[2]",
  },
  JSB_TasksAndCriRisks_divTasksInAddActivityPopUp: {
    mobile: "(//div[contains(@class,'overflow-y-scroll flex')])",
    desktop: "(//div[contains(@class,'overflow-y-scroll flex')])",
  },
  JSB_TasksAndCriRisks_btnsTaskInAddActivityPopUp: {
    mobile: "(//div[contains(@class,'overflow-y-scroll flex')]//button)",
    desktop: "(//div[contains(@class,'overflow-y-scroll flex')]//button)",
  },
  JSB_TasksAndCriRisks_divSubTasksInAddActivityPopUp: {
    mobile: "(//div[contains(@id,'headlessui-disclosure-panel')]//div)[1]",
    desktop: "(//div[contains(@id,'headlessui-disclosure-panel')]//div)[1]",
  },
  JSB_TasksAndCriRisks_btnTaskInAddActivityPopUp: {
    mobile: "button[id^='headlessui-disclosure-button']",
    desktop: "button[id^='headlessui-disclosure-button']",
  },
  JSB_TasksAndCriRisks_btnSubTaskInAddActivityPopUp: {
    mobile: "div.flex.flex-row.items-center.gap-2",
    desktop: "div.flex.flex-row.items-center.gap-2",
  },
  JSB_TasksAndCriRisks_promptNoMatchFoundInAddActivityPopUp: {
    mobile: "//div[normalize-space(text())='No match found']",
    desktop: "//div[normalize-space(text())='No match found']",
  },
  JSB_TasksAndCriRisks_lblActivityNameInAddActivityPopUp: {
    mobile: "//label[contains(@class,'block text-tiny')]",
    desktop: "//label[contains(@class,'block text-tiny')]",
  },
  JSB_TasksAndCriRisks_txtActivityNameInAddActivityPopUp: {
    mobile: "//input[contains(@class,'flex-auto appearance-none')]",
    desktop: "//input[contains(@class,'flex-auto appearance-none')]",
  },
  JSB_TasksAndCriRisks_lblAddActivityInActivityNamePopUp: {
    mobile: "(//span[@class='mx-1 truncate'])[3]",
    desktop: "(//span[@class='mx-1 truncate'])[3]",
  },
  JSB_TasksAndCriRisks_btnAddActivityInActivityNamePopUp: {
    mobile: "(//button[contains(@class,'text-center truncate')])[3]",
    desktop: "(//button[contains(@class,'text-center truncate')])[3]",
  },
  JSB_btnNavTasksAndCriRisks: {
    mobile: "(//button[contains(@class,'p-3 bg-neutral-shade-3')])[3]",
    desktop: "(//button[contains(@class,'p-3 bg-neutral-shade-3')])[3]",
  },
  JSB_TasksAndCriRisks_btnAddActivityInAddActivityModal: {
    mobile: "//span[normalize-space(text())='Add Activity']",
    desktop: "//span[normalize-space(text())='Add Activity']",
  },
  JSB_btnNavEnergySrcCtrl: {
    mobile: "(//button[contains(@class,'p-3 bg-neutral-shade-3')])[4]",
    desktop: "(//button[contains(@class,'p-3 bg-neutral-shade-3')])[4]",
  },
  JSB_EnergySrcCtrl_lblArcFlashCategory: {
    mobile: "(//span[contains(@class,'text-sm text-brand-gray-70')])[1]",
    desktop: "(//span[contains(@class,'text-sm text-brand-gray-70')])[1]",
  },
  JSB_EnergySrcCtrl_lblPrimaryVoltage: {
    mobile: "(//span[contains(@class,'text-sm text-brand-gray-70')])[2]",
    desktop: "(//span[contains(@class,'text-sm text-brand-gray-70')])[2]",
  },
  JSB_EnergySrcCtrl_lblSecondaryVoltage: {
    mobile: "(//span[contains(@class,'text-sm text-brand-gray-70')])[3]",
    desktop: "(//span[contains(@class,'text-sm text-brand-gray-70')])[3]",
  },
  JSB_EnergySrcCtrl_lblTransmissionVoltage: {
    mobile: "(//span[contains(@class,'text-sm text-brand-gray-70')])[4]",
    desktop: "(//span[contains(@class,'text-sm text-brand-gray-70')])[4]",
  },
  JSB_EnergySrcCtrl_lblClearancePoints: {
    mobile: "//div[@class='w-full']//label",
    desktop: "//div[@class='w-full']//label",
  },
  JSB_EnergySrcCtrl_inputArcFlashCategory: {
    mobile:
      "(//div[@class='Select_select__6MkEx Select_selectPlaceholder__9_t4P'])[1]",
    desktop:
      "(//div[@class='Select_select__6MkEx Select_selectPlaceholder__9_t4P'])[1]",
  },
  JSB_EnergySrcCtrl_DropdownDivArcFlashCategory: {
    mobile: "//ul[contains(@class,'bg-white')]",
    desktop: "//ul[contains(@class,'bg-white')]",
  },
  JSB_EnergySrcCtrl_DropdownListItemsArcFlashCategory: {
    mobile: "(//ul[contains(@class,'bg-white')]//li)",
    desktop: "(//ul[contains(@class,'bg-white')]//li)",
  },
  JSB_EnergySrcCtrl_crossButtonFirstSelectedValuesInDropdown: {
    mobile: "(//i[contains(@class,'ci-off_outline_close self-center')])[1]",
    desktop: "(//i[contains(@class,'ci-off_outline_close self-center')])[1]",
  },
  JSB_EnergySrcCtrl_SelectedValuesInArcFlash: {
    mobile: "(//div[contains(@class,'flex flex-wrap')])[1]",
    desktop: "(//div[contains(@class,'flex flex-wrap')])[1]",
  },
  JSB_EnergySrcCtrl_SelectedValuesInPrimaryVoltage: {
    mobile: "(//div[contains(@class,'flex flex-wrap')])[2]",
    desktop: "(//div[contains(@class,'flex flex-wrap')])[2]",
  },
  JSB_EnergySrcCtrl_SelectedValuesInSecondaryVoltage: {
    mobile: "(//div[contains(@class,'flex flex-wrap')])[3]",
    desktop: "(//div[contains(@class,'flex flex-wrap')])[3]",
  },
  JSB_EnergySrcCtrl_SelectedValuesInTransmissionVoltage: {
    mobile: "(//div[contains(@class,'flex flex-wrap')])[4]",
    desktop: "(//div[contains(@class,'flex flex-wrap')])[4]",
  },
  JSB_EnergySrcCtrl_inputPrimaryVoltage: {
    mobile:
      "(//div[@class='MultiSelect_select__LKolc MultiSelect_selectPlaceholder__DavYQ'])[1]",
    desktop:
      "(//div[@class='MultiSelect_select__LKolc MultiSelect_selectPlaceholder__DavYQ'])[1]",
  },
  JSB_EnergySrcCtrl_inputClearancePoints: {
    mobile: "//input[contains(@class,'p-2 flex-auto')]",
    desktop: "//input[contains(@class,'p-2 flex-auto')]",
  },
  JSB_EnergySrcCtrl_lblEWPHeading: {
    mobile:
      "(//h2[contains(@class,'text-section-heading font-section-heading')])[1]",
    desktop:
      "(//h2[contains(@class,'text-section-heading font-section-heading')])[1]",
  },
  JSB_EnergySrcCtrl_divAdditionalEWP: {
    mobile: "(//div[@class=' px-4 md:px-0']//div)[3]",
    desktop: "(//div[@class=' px-4 md:px-0']//div)[3]",
  },
  JSB_EnergySrcCtrl_lblAddAdditionalEWP: {
    mobile: "(//span[@class='mx-1 truncate'])[1]",
    desktop: "(//span[@class='mx-1 truncate'])[1]",
  },
  JSB_EnergySrcCtrl_btnAddAdditionalEWP: {
    mobile: "(//button[contains(@class,'text-center truncate')])[1]",
    desktop: "(//button[contains(@class,'text-center truncate')])[1]",
  },
  JSB_EnergySrcCtrl_btnDeleteMostRecentEWP: {
    mobile: "(//i[@class='ci-trash_empty'])[1]",
    desktop: "(//i[@class='ci-trash_empty'])[1]",
  },
  JSB_EnergySrcCtrl_lblEWPInput: {
    mobile: "(//label[contains(@class,'block text-tiny')])[2]",
    desktop: "(//label[contains(@class,'block text-tiny')])[2]",
  },
  JSB_EnergySrcCtrl_EWP_lblTimeIssued: {
    mobile: "(//label[contains(@class,'block text-tiny')])[3]",
    desktop: "(//label[contains(@class,'block text-tiny')])[3]",
  },
  JSB_EnergySrcCtrl_EWP_lblTimeCompleted: {
    mobile: "(//label[contains(@class,'block text-tiny')])[4]",
    desktop: "(//label[contains(@class,'block text-tiny')])[4]",
  },
  JSB_EnergySrcCtrl_EWP_lblProcedure: {
    mobile: "(//label[contains(@class,'block text-tiny')])[5]",
    desktop: "(//label[contains(@class,'block text-tiny')])[5]",
  },
  JSB_EnergySrcCtrl_EWP_lblIssuedBy: {
    mobile: "(//label[contains(@class,'block text-tiny')])[6]",
    desktop: "(//label[contains(@class,'block text-tiny')])[6]",
  },
  JSB_EnergySrcCtrl_EWP_lblReceivedBy: {
    mobile: "(//label[contains(@class,'block text-tiny')])[7]",
    desktop: "(//label[contains(@class,'block text-tiny')])[7]",
  },
  JSB_EnergySrcCtrl_lblReferencePointsHeading: {
    mobile:
      "(//h2[contains(@class,'text-section-heading font-section-heading')])[2]",
    desktop:
      "(//h2[contains(@class,'text-section-heading font-section-heading')])[2]",
  },
  JSB_EnergySrcCtrl_ReferencePoints_lblRefPoint1: {
    mobile: "//label[normalize-space(text())='Reference Point 1 *']",
    desktop: "//label[normalize-space(text())='Reference Point 1 *']",
  },
  JSB_EnergySrcCtrl_ReferencePoints_lblRefPoint2: {
    mobile: "//label[normalize-space(text())='Reference Point 2 *']",
    desktop: "//label[normalize-space(text())='Reference Point 2 *']",
  },
  JSB_EnergySrcCtrl_lblCircuitBreakersHeading: {
    mobile:
      "(//h2[contains(@class,'text-section-heading font-section-heading')])[3]",
    desktop:
      "(//h2[contains(@class,'text-section-heading font-section-heading')])[3]",
  },
  JSB_EnergySrcCtrl_CircuitBreakers_lblCtBreaker: {
    mobile: "//label[normalize-space(text())='Circuit Breaker #']",
    desktop: "//label[normalize-space(text())='Circuit Breaker #']",
  },
  JSB_EnergySrcCtrl_CircuitBreakers_lblSwitch: {
    mobile: "//label[normalize-space(text())='Switch #']",
    desktop: "//label[normalize-space(text())='Switch #']",
  },
  JSB_EnergySrcCtrl_CircuitBreakers_lblTransformer: {
    mobile: "//label[normalize-space(text())='Transformer # *']",
    desktop: "//label[normalize-space(text())='Transformer # *']",
  },
  JSB_EnergySrcCtrl_CircuitBreakers_lblAddAdditionalCtBreaker: {
    mobile: "(//span[@class='mx-1 truncate'])[2]",
    desktop: "(//span[@class='mx-1 truncate'])[2]",
  },
  JSB_EnergySrcCtrl_txtEWP: {
    mobile: "(//input[contains(@class,'flex-auto appearance-none')])[1]",
    desktop: "(//input[contains(@class,'flex-auto appearance-none')])[1]",
  },
  JSB_EnergySrcCtrl_EWP_txtTimeIssued: {
    mobile: "(//input[contains(@class,'flex-auto appearance-none')])[2]",
    desktop: "(//input[contains(@class,'flex-auto appearance-none')])[2]",
  },
  JSB_EnergySrcCtrl_EWP_txtTimeCompleted: {
    mobile: "(//input[contains(@class,'flex-auto appearance-none')])[3]",
    desktop: "(//input[contains(@class,'flex-auto appearance-none')])[3]",
  },
  JSB_EnergySrcCtrl_EWP_txtProcedure: {
    mobile: "(//input[contains(@class,'flex-auto appearance-none')])[4]",
    desktop: "(//input[contains(@class,'flex-auto appearance-none')])[4]",
  },
  JSB_EnergySrcCtrl_EWP_txtIssuedBy: {
    mobile: "(//input[contains(@class,'flex-auto appearance-none')])[5]",
    desktop: "(//input[contains(@class,'flex-auto appearance-none')])[5]",
  },
  JSB_EnergySrcCtrl_EWP_txtReceivedBy: {
    mobile: "(//input[contains(@class,'flex-auto appearance-none')])[6]",
    desktop: "(//input[contains(@class,'flex-auto appearance-none')])[6]",
  },
  JSB_EnergySrcCtrl_EWP_txtRefPoint1: {
    mobile:
      "(//label[normalize-space(text())='Reference Point 1 *']/following::input)[1]",
    desktop:
      "(//label[normalize-space(text())='Reference Point 1 *']/following::input)[1]",
  },
  JSB_EnergySrcCtrl_EWP_txtRefPoint2: {
    mobile:
      "(//label[normalize-space(text())='Reference Point 2 *']/following::input)[1]",
    desktop:
      "(//label[normalize-space(text())='Reference Point 2 *']/following::input)[1]",
  },
  JSB_EnergySrcCtrl_EWP_txtCircuitBreaker: {
    mobile: "(//input[contains(@class,'p-2 flex-auto')])[2]",
    desktop: "(//input[contains(@class,'p-2 flex-auto')])[2]",
  },
  JSB_EnergySrcCtrl_EWP_txtSwitch: {
    mobile: "(//input[contains(@class,'p-2 flex-auto')])[3]",
    desktop: "(//input[contains(@class,'p-2 flex-auto')])[3]",
  },
  JSB_EnergySrcCtrl_EWP_txtTransformer: {
    mobile:
      "//label[normalize-space(text())='Transformer # *']/following::input",
    desktop:
      "//label[normalize-space(text())='Transformer # *']/following::input",
  },
  JSB_EnergySrcCtrl_EWP_ReqChecks: {
    mobile: "(//span[contains(@class,'text-sm mt-1')])",
    desktop: "(//span[contains(@class,'text-sm mt-1')])",
  },
  JSB_btnNavWorkProcedures: {
    mobile: "(//button[contains(@class,'p-3 bg-neutral-shade-3')])[5]",
    desktop: "(//button[contains(@class,'p-3 bg-neutral-shade-3')])[5]",
  },
  JSB_WorkProcedures_lblWorkProcedures: {
    mobile:
      "//h2[contains(@class,'text-section-heading font-section-heading')]",
    desktop:
      "//h2[contains(@class,'text-section-heading font-section-heading')]",
  },
  JSB_WorkProcedures_lblDistriBulletins: {
    mobile: "(//p[contains(@class,'text-caption-text font-caption-text')])[1]",
    desktop: "(//p[contains(@class,'text-caption-text font-caption-text')])[1]",
  },
  JSB_WorkProcedures_lblDistriBulletinsReqCheck: {
    mobile: "//p[contains(@class,'text-body-text font-body-text')]",
    desktop: "//p[contains(@class,'text-body-text font-body-text')]",
  },
  JSB_WorkProcedures_lbl4RulesOfCoverUp: {
    mobile:
      "(//span[contains(@class,'text-action-label font-action-label')])[1]",
    desktop:
      "(//span[contains(@class,'text-action-label font-action-label')])[1]",
  },
  JSB_WorkProcedures_lblMAD: {
    mobile:
      "(//span[contains(@class,'text-action-label font-action-label')])[2]",
    desktop:
      "(//span[contains(@class,'text-action-label font-action-label')])[2]",
  },
  JSB_WorkProcedures_lblSDOPSwitchProcedures: {
    mobile:
      "(//span[contains(@class,'text-action-label font-action-label')])[3]",
    desktop:
      "(//span[contains(@class,'text-action-label font-action-label')])[3]",
  },
  JSB_WorkProcedures_lblTOC: {
    mobile:
      "(//span[contains(@class,'text-action-label font-action-label')])[4]",
    desktop:
      "(//span[contains(@class,'text-action-label font-action-label')])[4]",
  },
  JSB_WorkProcedures_lblStepTouchPotential: {
    mobile:
      "(//span[contains(@class,'text-action-label font-action-label')])[5]",
    desktop:
      "(//span[contains(@class,'text-action-label font-action-label')])[5]",
  },
  JSB_WorkProcedures_lblWorkPracticesHyperlink: {
    mobile: "//span[normalize-space(text())='Best Work Practices']",
    desktop: "//span[normalize-space(text())='Best Work Practices']",
  },
  JSB_WorkProcedures_lblDistriBulletinsHyperlink: {
    mobile: "(//span[@class='truncate'])[3]",
    desktop: "(//span[@class='truncate'])[3]",
  },
  JSB_WorkProcedures_lblOtherWorkOrSpecialPre: {
    mobile: "(//p[contains(@class,'text-caption-text font-caption-text')])[2]",
    desktop: "(//p[contains(@class,'text-caption-text font-caption-text')])[2]",
  },
  JSB_WorkProcedures_inputDistributionBulletins: {
    mobile: "//input[@class='w-full outline-none']",
    desktop: "//input[@class='w-full outline-none']",
  },
  JSB_WorkProcedures_selectedValuesInDistriBullet: {
    mobile: "(//div[contains(@class,'flex flex-wrap')])[2]",
    desktop: "(//div[contains(@class,'flex flex-wrap')])[2]",
  },
  JSB_WorkProcedures_selectedValuesInMAD: {
    mobile: "(//div[contains(@class,'flex flex-wrap')])[3]",
    desktop: "(//div[contains(@class,'flex flex-wrap')])[3]",
  },
  JSB_WorkProcedures_input4RulesOfCoverUp: {
    mobile: "(//input[@class='flex-shrink-0 Checkbox_root__Lr2rF'])[1]",
    desktop: "(//input[@class='flex-shrink-0 Checkbox_root__Lr2rF'])[1]",
  },
  JSB_WorkProcedures_link4RulesAddDoc: {
    mobile: "(//a[contains(@class,'font-medium text-brand-urbint-50')])[3]",
    desktop: "(//a[contains(@class,'font-medium text-brand-urbint-50')])[3]",
  },
  JSB_WorkProcedures_inputMinApproachDist: {
    mobile:
      "//div[contains(@class,'Select_select__6MkEx Select_selectPlaceholder__9_t4P')]",
    desktop:
      "//div[contains(@class,'Select_select__6MkEx Select_selectPlaceholder__9_t4P')]",
  },
  JSB_WorkProcedures_divPopUpMAD: {
    mobile: "(//div[contains(@class,'fixed z-10')]//div)[1]",
    desktop: "(//div[contains(@class,'fixed z-10')]//div)[1]",
  },
  JSB_WorkProcedures_headingPopUpMAD: {
    mobile:
      "(//h2[contains(@class,'text-section-heading font-section-heading')])[2]",
    desktop:
      "(//h2[contains(@class,'text-section-heading font-section-heading')])[2]",
  },
  JSB_WorkProcedures_imgPopUpMAD: {
    mobile:
      "//img[@srcset='/_next/image?url=%2F_next%2Fstatic%2Fmedia%2Fmad.a7526566.png&w=1920&q=75 1x, /_next/image?url=%2F_next%2Fstatic%2Fmedia%2Fmad.a7526566.png&w=3840&q=75 2x']",
    desktop:
      "//img[@srcset='/_next/image?url=%2F_next%2Fstatic%2Fmedia%2Fmad.a7526566.png&w=1920&q=75 1x, /_next/image?url=%2F_next%2Fstatic%2Fmedia%2Fmad.a7526566.png&w=3840&q=75 2x']",
  },
  JSB_WorkProcedures_closePopUpBtnMAD: {
    mobile:
      "//button[contains(@class,'text-xl text-neutral-shade-75')]//i[contains(@class,'ci-close_big')]",
    desktop:
      "//button[contains(@class,'text-xl text-neutral-shade-75')]//i[contains(@class,'ci-close_big')]",
  },
  JSB_WorkProcedures_lblReqCheck: {
    mobile: "//p[contains(@class,'text-body-text font-body-text')]",
    desktop: "//p[contains(@class,'text-body-text font-body-text')]",
  },
  JSB_WorkProcedures_linkMAD: {
    mobile: "(//div[@class='flex flex-col']/following-sibling::a)[1]",
    desktop: "(//div[@class='flex flex-col']/following-sibling::a)[1]",
  },
  JSB_WorkProcedures_checkBoxMAD: {
    mobile: "(//input[@class='flex-shrink-0 Checkbox_root__Lr2rF'])[2]",
    desktop: "(//input[@class='flex-shrink-0 Checkbox_root__Lr2rF'])[2]",
  },
  JSB_WorkProcedures_lblMinApproachDist: {
    mobile: "//span[normalize-space(text())='Minimum Approach Distance *']",
    desktop: "//span[normalize-space(text())='Minimum Approach Distance *']",
  },
  JSB_WorkProcedures_checkBoxSDOP: {
    mobile: "(//input[@class='flex-shrink-0 Checkbox_root__Lr2rF'])[3]",
    desktop: "(//input[@class='flex-shrink-0 Checkbox_root__Lr2rF'])[3]",
  },
  JSB_WorkProcedures_checkBoxTOC: {
    mobile: "(//input[@class='flex-shrink-0 Checkbox_root__Lr2rF'])[4]",
    desktop: "(//input[@class='flex-shrink-0 Checkbox_root__Lr2rF'])[4]",
  },
  JSB_WorkProcedures_checkBoxStepOrTouchPotential: {
    mobile: "(//input[@class='flex-shrink-0 Checkbox_root__Lr2rF'])[5]",
    desktop: "(//input[@class='flex-shrink-0 Checkbox_root__Lr2rF'])[5]",
  },
  JSB_WorkProcedures_linkSwitchingProcedures: {
    mobile: "(//div[@class='flex flex-col']/following-sibling::a)[2]",
    desktop: "(//div[@class='flex flex-col']/following-sibling::a)[2]",
  },
  JSB_WorkProcedures_linkTOCRequestForm: {
    mobile: "(//div[@class='flex flex-col']/following-sibling::a)[3]",
    desktop: "(//div[@class='flex flex-col']/following-sibling::a)[3]",
  },
  JSB_WorkProcedures_OtherWorkProceduresFieldBox: {
    mobile: "//textarea[contains(@class,'w-full h-24')]",
    desktop: "//textarea[contains(@class,'w-full h-24')]",
  },
  JSB_btnNavSiteConditions: {
    mobile: "(//button[contains(@class,'p-3 bg-neutral-shade-3')])[6]",
    desktop: "(//button[contains(@class,'p-3 bg-neutral-shade-3')])[6]",
  },
  JSB_SiteConditions_lblAddSiteCondnHeading: {
    mobile:
      "//h2[contains(@class,'text-section-heading font-section-heading')]",
    desktop:
      "//h2[contains(@class,'text-section-heading font-section-heading')]",
  },
  JSB_SiteConditions_lblHelpTextSubHeading: {
    mobile: "//p[contains(@class,'text-caption-text font-caption-text')]",
    desktop: "//p[contains(@class,'text-caption-text font-caption-text')]",
  },
  JSB_SiteConditions_lblAddSiteCondnBtn: {
    mobile: "(//span[@class='mx-1 truncate'])[1]",
    desktop: "(//span[@class='mx-1 truncate'])[1]",
  },
  JSB_SiteConditions_lblAllSiteCondnCheckBox: {
    mobile: "(//label[@class='cursor-pointer w-full'])[1]",
    desktop: "(//label[@class='cursor-pointer w-full'])[1]",
  },
  JSB_SiteConditions_checkBoxAllSiteCondn: {
    mobile: "(//input[@class='flex-shrink-0 Checkbox_root__Lr2rF'])[1]",
    desktop: "(//input[@class='flex-shrink-0 Checkbox_root__Lr2rF'])[1]",
  },
  JSB_SiteConditions_checkBoxes: {
    mobile: "div.flex.w-full input[type='checkbox']",
    desktop: "div.flex.w-full input[type='checkbox']",
  },
  JSB_SiteConditions_btnAddSiteCondn: {
    mobile: "(//button[contains(@class,'text-center truncate')]//div)[1]",
    desktop: "(//button[contains(@class,'text-center truncate')]//div)[1]",
  },
  JSB_SiteConditions_popUpAddSiteCondn: {
    mobile: "(//div[contains(@class,'flex flex-col')])[3]",
    desktop: "(//div[contains(@class,'flex flex-col')])[3]",
  },
  JSB_SiteConditions_plusSignAddSiteCondnBtn: {
    mobile: "(//div[contains(@class,'flex items-center')]//i)[2]",
    desktop: "(//div[contains(@class,'flex items-center')]//i)[2]",
  },
  JSB_SiteConditions_lblHeadingPopUpAddSiteCondn: {
    mobile:
      "(//h2[contains(@class,'text-section-heading font-section-heading')])[2]",
    desktop:
      "(//h2[contains(@class,'text-section-heading font-section-heading')])[2]",
  },
  JSB_SiteConditions_lblPopUpApplicableSiteCondn: {
    mobile: "(//label[@class='text-md'])[1]",
    desktop: "(//label[@class='text-md'])[1]",
  },
  JSB_SiteConditions_lblPopUpOtherSideCondn: {
    mobile: "(//label[@class='text-md'])[2]",
    desktop: "(//label[@class='text-md'])[2]",
  },
  JSB_SiteConditions_lblPopUpCancelBtn: {
    mobile: "(//span[@class='mx-1 truncate'])[2]",
    desktop: "(//span[@class='mx-1 truncate'])[2]",
  },
  JSB_SiteConditions_lblPopUpAddBtn: {
    mobile: "(//span[@class='mx-1 truncate'])[3]",
    desktop: "(//span[@class='mx-1 truncate'])[3]",
  },
  JSB_SiteConditions_btnClosePopUp: {
    mobile: "(//button[contains(@class,'text-xl text-neutral-shade-75')])[2]",
    desktop: "(//button[contains(@class,'text-xl text-neutral-shade-75')])[2]",
  },
  JSB_SiteConditions_btnAddPopUp: {
    mobile: "(//button[contains(@class,'text-center truncate')])[3]",
    desktop: "(//button[contains(@class,'text-center truncate')])[3]",
  },
  JSB_SiteConditions_checkboxesPopUpApplicableSiteCondns: {
    mobile:
      "//div[contains(@class,'items-center')][.//label[text()='Applicable site conditions']]/following-sibling::div[not(contains(@class,'items-center'))][following::div[contains(@class,'items-center')][.//label[text()='Other site conditions']]]//input[@type='checkbox']",
    desktop:
      "//div[contains(@class,'items-center')][.//label[text()='Applicable site conditions']]/following-sibling::div[not(contains(@class,'items-center'))][following::div[contains(@class,'items-center')][.//label[text()='Other site conditions']]]//input[@type='checkbox']",
  },
  JSB_SiteConditions_checkboxesPopUpOtherSiteCondns: {
    mobile:
      "//div[contains(@class,'items-center')][.//label[text()='Other site conditions']]/following-sibling::div[not(contains(@class,'items-center'))]//input[@type='checkbox']",
    desktop:
      "//div[contains(@class,'items-center')][.//label[text()='Other site conditions']]/following-sibling::div[not(contains(@class,'items-center'))]//input[@type='checkbox']",
  },
  JSB_SiteConditions_checkboxesPopUpSectionHeaders: {
    mobile:
      "//div[contains(@class,'flex-1 overflow-auto')]//div//div[contains(@class,'items-center')]",
    desktop:
      "//div[contains(@class,'flex-1 overflow-auto')]//div//div[contains(@class,'items-center')]",
  },
  JSB_SiteConditions_lblCountApplicableSiteCondns: {
    mobile: "(//label[@class='text-sm font-semibold'])[1]",
    desktop: "(//label[@class='text-sm font-semibold'])[1]",
  },
  JSB_btnNavCtrlsAssessment: {
    mobile: "(//button[contains(@class,'p-3 bg-neutral-shade-3')])[7]",
    desktop: "(//button[contains(@class,'p-3 bg-neutral-shade-3')])[7]",
  },
  JSB_ControlAssessment_availableHeadingsOnTheScreen: {
    mobile:
      "(//h2[contains(@class,'text-section-heading font-section-heading')])",
    desktop:
      "(//h2[contains(@class,'text-section-heading font-section-heading')])",
  },
  JSB_ControlAssessment_CheckboxesOnTheScreen: {
    mobile: "(//input[@class='flex-shrink-0 Checkbox_root__Lr2rF'])[1]",
    desktop: "(//input[@class='flex-shrink-0 Checkbox_root__Lr2rF'])[1]",
  },
  JSB_ControlAssessment_autoSelectedRecommendedControls: {
    mobile: "(//div[contains(@class,'flex flex-wrap')])[1]//span",
    desktop: "(//div[contains(@class,'flex flex-wrap')])[1]//span",
  },
  JSB_ControlAssessment_emptySelectedRecommendedControls: {
    mobile: "(//div[contains(@class,'flex flex-1') and ./span[contains(.,'Select an option')]])",
    desktop: "(//div[contains(@class,'flex flex-1') and ./span[contains(.,'Select an option')]])",
  },
  JSB_ControlAssessment_inputOtherControlsDropdown: {
    mobile: "(//input[@class='w-full outline-none'])[1]",
    desktop: "(//input[@class='w-full outline-none'])[1]",
  },
  JSB_ControlAssessment_dropdownOtherControls: {
    mobile: "//ul[contains(@class,'bg-white max-h-36')]",
    desktop: "//ul[contains(@class,'bg-white max-h-36')]",
  },
  JSB_ControlAssessment_selectedOptionsInOtherControls: {
    mobile: "(//div[contains(@class,'flex flex-wrap')])[1]//span",
    desktop: "(//div[contains(@class,'flex flex-wrap')])[1]//span",
  },
  JSB_ControlAssessment_lblAdditionalInfo: {
    mobile: "//h2[normalize-space(text())='Additional Information']",
    desktop: "//h2[normalize-space(text())='Additional Information']",
  },
  JSB_ControlAssessment_txtAdditionalInfo: {
    mobile: "//textarea[contains(@class,'w-full h-24 p-2 border-solid')]",
    desktop: "//textarea[contains(@class,'w-full h-24 p-2 border-solid')]",
  },
  JSB_Attachments_lblPhotos: {
    mobile:
      "(//h2[contains(@class,'text-section-heading font-section-heading')])[1]",
    desktop:
      "(//h2[contains(@class,'text-section-heading font-section-heading')])[1]",
  },
  JSB_Attachments_lblAddPhotosBtn: {
    mobile: "(//label[contains(@class,'px-2.5 py-2')])[1]//span",
    desktop: "(//label[contains(@class,'px-2.5 py-2')])[1]//span",
  },
  JSB_Attachments_lblPhotosExtensions: {
    mobile:
      "//p[normalize-space(text())='APNG, AVIF, GIF, HEIC, JPG, JPEG, PNG, SVG, WEBP']",
    desktop:
      "//p[normalize-space(text())='APNG, AVIF, GIF, HEIC, JPG, JPEG, PNG, SVG, WEBP']",
  },
  JSB_Attachments_lblPhotosSize: {
    mobile: "(//div[contains(@class,'text-xs font-normal')]//p)[2]",
    desktop: "(//div[contains(@class,'text-xs font-normal')]//p)[2]",
  },
  JSB_Attachments_lblNoPhotosUploaded: {
    mobile: "(//span[@class='font-normal text-base'])[1]",
    desktop: "(//span[@class='font-normal text-base'])[1]",
  },
  JSB_Attachments_lblDocuments: {
    mobile:
      "(//h2[contains(@class,'text-section-heading font-section-heading')])[2]",
    desktop:
      "(//h2[contains(@class,'text-section-heading font-section-heading')])[2]",
  },
  JSB_Attachments_lblAddDocumentsBtn: {
    mobile: "(//label[contains(@class,'px-2.5 py-2')])[2]",
    desktop: "(//label[contains(@class,'px-2.5 py-2')])[2]",
  },
  JSB_Attachments_lblDocumentsExtensions: {
    mobile:
      "//p[normalize-space(text())='PDF, DOC, DOCX, XLS, XLSX, PPT, PPTX']",
    desktop:
      "//p[normalize-space(text())='PDF, DOC, DOCX, XLS, XLSX, PPT, PPTX']",
  },
  JSB_Attachments_lblDocumentsSize: {
    mobile: "(//div[contains(@class,'text-xs font-normal')]//p)[4]",
    desktop: "(//div[contains(@class,'text-xs font-normal')]//p)[4]",
  },
  JSB_Attachments_lblNoDocumentsUploaded: {
    mobile: "(//span[@class='font-normal text-base'])[2]",
    desktop: "(//span[@class='font-normal text-base'])[2]",
  },
  JSB_btnNavAttachments: {
    mobile: "(//button[contains(@class,'p-3 bg-neutral-shade-3')])[8]",
    desktop: "(//button[contains(@class,'p-3 bg-neutral-shade-3')])[8]",
  },
  JSB_btnNavJSBSummary: {
    mobile: "(//button[contains(@class,'p-3 bg-neutral-shade-3')])[9]",
    desktop: "(//button[contains(@class,'p-3 bg-neutral-shade-3')])[9]",
  },
  JSB_Attachments_uploadedImages: {
    mobile: "//img[contains(@class,'absolute inset-0')]",
    desktop: "//img[contains(@class,'absolute inset-0')]",
  },
  JSB_Attachments_uploadedImgDeleteBtn: {
    mobile: "(//i[contains(@class,'ci-off_outline_close absolute')])[1]",
    desktop: "(//i[contains(@class,'ci-off_outline_close absolute')])[1]",
  },
  JSB_Attachments_uploadedDocuments: {
    mobile: "//div[@data-testid='document-item']",
    desktop: "//div[@data-testid='document-item']",
  },
  JSB_Attachments_recentlyUploadedDocName: {
    mobile: "(//p[contains(@class,'text-sm font-semibold')])[1]",
    desktop: "(//p[contains(@class,'text-sm font-semibold')])[1]",
  },
  JSB_Attachments_recentlyUploadedDocMenuBtn: {
    mobile: "(//div[@class='relative z-30'])[1]",
    desktop: "(//div[@class='relative z-30'])[2]",
  },
  JSB_Attachments_menuDownloadBtn: {
    mobile: "(//button[contains(@class,'flex flex-1')])[1]",
    desktop: "(//button[contains(@class,'flex flex-1')])[1]",
  },
  JSB_Attachments_menuEditBtn: {
    mobile: "(//button[contains(@class,'flex flex-1')])[2]",
    desktop: "(//button[contains(@class,'flex flex-1')])[2]",
  },
  JSB_Attachments_menuDeleteBtn: {
    mobile: "(//button[contains(@class,'flex flex-1')])[3]",
    desktop: "(//button[contains(@class,'flex flex-1')])[3]",
  },
  JSB_Attachments_lblMaxFileSizePrompt: {
    mobile:
      "//p[normalize-space(text()) = 'Maximum file size exceeds. (10MB)']",
    desktop:
      "//p[normalize-space(text()) = 'Maximum file size exceeds. (10MB)']",
  },
  JSB_Attachments_editDocPopUp: {
    mobile: "(//div[contains(@class,'min-h-screen flex')]//div)[2]",
    desktop: "(//div[contains(@class,'min-h-screen flex')]//div)[2]",
  },
  JSB_Attachments_editDocPopUpHeading: {
    mobile:
      "(//h2[contains(@class,'text-section-heading font-section-heading')])[2]",
    desktop:
      "(//h2[contains(@class,'text-section-heading font-section-heading')])[2]",
  },
  JSB_Attachments_txtEditDocPopUpNewName: {
    mobile: "//input[contains(@class,'flex-auto rounded-md')]",
    desktop: "//input[contains(@class,'flex-auto rounded-md')]",
  },
  JSB_Attachments_btnEditDocPopUpType: {
    mobile: "(//button[contains(@class,'w-full px-2')])[2]",
    desktop: "(//button[contains(@class,'w-full px-2')])[2]",
  },
  JSB_Attachments_lblEditDocPopUpCurrentName: {
    mobile: "(//p[@class='text-base text-neutral-shade-100'])[1]",
    desktop: "(//p[@class='text-base text-neutral-shade-100'])[1]",
  },
  JSB_Attachments_lblEditDocPopUpDateTime: {
    mobile: "(//p[@class='text-base text-neutral-shade-100'])[2]",
    desktop: "(//p[@class='text-base text-neutral-shade-100'])[2]",
  },
  JSB_Attachments_btnEditDocPopUpCancel: {
    mobile: "(//button[contains(@class,'text-center truncate')])[2]",
    desktop: "(//button[contains(@class,'text-center truncate')])[2]",
  },
  JSB_Attachments_btnEditDocPopUpSave: {
    mobile: "(//button[contains(@class,'text-center truncate')])[3]",
    desktop: "(//button[contains(@class,'text-center truncate')])[3]",
  },
  JSB_Summary_lblSummaryHeading: {
    mobile:
      "(//h2[contains(@class,'text-section-heading font-section-heading')])[1]",
    desktop:
      "(//h2[contains(@class,'text-section-heading font-section-heading')])[1]",
  },
  JSB_Summary_lblSubHeading: {
    mobile: "(//p[contains(@class,'text-body-text font-body-text')])[1]",
    desktop: "(//p[contains(@class,'text-body-text font-body-text')])[1]",
  },
  JSB_Summary_QRCodeScanner: {
    mobile: "//div[contains(@class,'w-32 flex-grow')]/div",
    desktop: "//div[contains(@class,'w-32 flex-grow')]/div",
  },
  JSB_Summary_mainDivWithSummary: {
    mobile: "(//div[contains(@class,'p-2 sm:p-4')])[1]",
    desktop: "(//div[contains(@class,'p-2 sm:p-4')])[1]",
  },
  JSB_btnNavSignOff: {
    mobile: "(//button[contains(@class,'p-3 bg-neutral-shade-3')])[10]",
    desktop: "(//button[contains(@class,'p-3 bg-neutral-shade-3')])[10]",
  },
  JSB_SignOff_lblHeading: {
    mobile:
      "//h2[contains(@class,'text-section-heading font-section-heading')]",
    desktop:
      "//h2[contains(@class,'text-section-heading font-section-heading')]",
  },
  JSB_SignOff_lblAddNameBtn: {
    mobile: "(//span[@class='mx-1 truncate'])[1]",
    desktop: "(//span[@class='mx-1 truncate'])[1]",
  },
  JSB_SignOff_btnAddName: {
    mobile: "(//button[contains(@class,'text-center truncate')])[1]",
    desktop: "(//button[contains(@class,'text-center truncate')])[1]",
  },
  JSB_SignOff_lblName: {
    mobile: "//label[contains(@class,'block text-tiny')]",
    desktop: "//label[contains(@class,'block text-tiny')]",
  },
  JSB_SignOff_btnNameSelection: {
    mobile:
      "(//div[contains(@class,'flex flex-col')]/following-sibling::div)[3]",
    desktop:
      "(//div[contains(@class,'flex flex-col')]/following-sibling::div)[3]",
  },
  JSB_SignOff_popUpDivNameSelection: {
    mobile: "(//div[contains(@class,'min-h-screen flex')]//div)[2]",
    desktop: "(//div[contains(@class,'min-h-screen flex')]//div)[2]",
  },
  JSB_SignOff_txtInputSearchPopUpNameSelection: {
    mobile: "//input[contains(@class,'p-2 flex-auto')]",
    desktop: "//input[contains(@class,'p-2 flex-auto')]",
  },
  JSB_SignOff_btnOtherNamePopUpNameSelection: {
    mobile: "//span[normalize-space(text())='Other (name not listed)']",
    desktop: "//span[normalize-space(text())='Other (name not listed)']",
  },
  JSB_SignOff_lblReqCheckPromptForOtherName: {
    mobile: "//span[contains(@class,'text-sm mt-1')]",
    desktop: "//span[contains(@class,'text-sm mt-1')]",
  },
  JSB_SignOff_lblOtherNameInput: {
    mobile: "(//label[contains(@class,'block text-tiny')])[2]",
    desktop: "(//label[contains(@class,'block text-tiny')])[2]",
  },
  JSB_SignOff_txtInputOtherName: {
    mobile: "//input[contains(@class,'flex-auto appearance-none')]",
    desktop: "//input[contains(@class,'flex-auto appearance-none')]",
  },
  JSB_SignOff_divSignatureNameBoxDivs: {
    mobile: "(//*[@id='page-layout']/div/section/div/div[2]/div)",
    desktop: "(//*[@id='page-layout']/div/section/div/div[2]/div)",
  },
  JSB_SignOff_deleteSignatureNameBoxDiv: {
    mobile: "(//i[contains(@class,'ci-trash_empty border-[1px]')])",
    desktop: "(//i[contains(@class,'ci-trash_empty border-[1px]')])",
  },
  JSB_SignOff_lblSignForOtherNameBtn: {
    mobile: "(//span[@class='mx-1 truncate'])[2]",
    desktop: "(//span[@class='mx-1 truncate'])[2]",
  },
  JSB_SignOff_btnSignForOtherName: {
    mobile: "(//button[contains(@class,'text-center truncate')])[2]",
    desktop: "(//button[contains(@class,'text-center truncate')])[2]",
  },
  JSB_SignOff_lblReqCheckPromptForSignForOtherName: {
    mobile: "//p[contains(@class,'text-body-text font-body-text')]",
    desktop: "//p[contains(@class,'text-body-text font-body-text')]",
  },
  JSB_SignOff_divSignatureCanvas: {
    mobile: "(//div[contains(@class,'fixed z-10')]//div)[1]",
    desktop: "(//div[contains(@class,'fixed z-10')]//div)[1]",
  },
  JSB_SignOff_lblSignatureCanvasHeading: {
    mobile:
      "(//h2[contains(@class,'text-section-heading font-section-heading')])[2]",
    desktop:
      "(//h2[contains(@class,'text-section-heading font-section-heading')])[2]",
  },
  JSB_SignOff_lblSignatureCanvasSubHeading: {
    mobile: "(//label[contains(@class,'block text-tiny')])[3]",
    desktop: "(//label[contains(@class,'block text-tiny')])[3]",
  },
  JSB_SignOff_canvasSignature: {
    mobile: "//canvas[@class='border border-gray-400']",
    desktop: "//canvas[@class='border border-gray-400']",
  },
  JSB_SignOff_btnSignOffInCanvas: {
    mobile:
      "//button[contains(@class,'text-center truncate')]/following-sibling::button[1]",
    desktop:
      "//button[contains(@class,'text-center truncate')]/following-sibling::button[1]",
  },
  JSB_SignOff_btnCancelInCanvas: {
    mobile: "(//button[contains(@class,'text-center truncate')])[3]",
    desktop: "(//button[contains(@class,'text-center truncate')])[3]",
  },
  JSB_SignOff_imgSignature: {
    mobile: "//img[@class='max-w-full max-h-28']",
    desktop: "//img[@class='max-w-full max-h-28']",
  },
  JSB_SignOff_btnDeleteSignature: {
    mobile: "(//button[contains(@class,'text-xl text-neutral-shade-75')])[2]",
    desktop: "(//button[contains(@class,'text-xl text-neutral-shade-75')])[2]",
  },
  JSB_CompleteForm_lblHeading: {
    mobile: "//header[@class='flex-1']//h6",
    desktop: "//header[@class='flex-1']//h6",
  },
  JSB_CompleteForm_lblSubHeading: {
    mobile: "//div[contains(@class,'flex flex-col')]//p",
    desktop: "//div[contains(@class,'flex flex-col')]//p",
  },
  JSB_CompleteForm_lblCompleteFormBtn: {
    mobile: "(//span[@class='mx-1 truncate'])[3]",
    desktop: "(//span[@class='mx-1 truncate'])[3]",
  },
  JSB_CompleteForm_btnCompleteForm: {
    mobile: "(//button[contains(@class,'text-center truncate')])[3]",
    desktop: "(//button[contains(@class,'text-center truncate')])[3]",
  },
  FormsListPage_EBO_lblHeadingEBO: {
    mobile: "//h4[normalize-space(text())='Energy Based Observation']",
    desktop: "//h4[normalize-space(text())='Energy Based Observation']",
  },
  FormsListPage_EBO_NavObservationDetails: {
    mobile:
      "//button[contains(@class,'p-3 bg-neutral-shade-3')  and .//span[text()='Observation Details']]",
    desktop:
      "//button[contains(@class,'p-3 bg-neutral-shade-3')  and .//span[text()='Observation Details']]",
  },
  FormListPage_EBO_NavObservationDetailsReqCheckError: {
    mobile:
      "//button[contains(@class, 'bg-system-error-10')]/span[text()='Observation Details']",
    desktop:
      "//button[contains(@class, 'bg-system-error-10')]/span[text()='Observation Details']",
  },
  FormsListPage_EBO_NavHighEnergyTasks: {
    mobile:
      "//button[contains(@class,'p-3 bg-neutral-shade-3')  and .//span[text()='High Energy Tasks']]",
    desktop:
      "//button[contains(@class,'p-3 bg-neutral-shade-3')  and .//span[text()='High Energy Tasks']]",
  },
  FormListPage_EBO_NavHighEnergyTasksReqCheckError: {
    mobile:
      "//button[contains(@class, 'bg-system-error-10')]/span[text()='High Energy Tasks']",
    desktop:
      "//button[contains(@class, 'bg-system-error-10')]/span[text()='High Energy Tasks']",
  },
  FormsListPage_EBO_NavAdditionalInfo: {
    mobile:
      "//button[contains(@class,'p-3 bg-neutral-shade-3')  and .//span[text()='Additional Information']]",
    desktop:
      "//button[contains(@class,'p-3 bg-neutral-shade-3')  and .//span[text()='Additional Information']]",
  },
  FormListPage_EBO_NavAdditionalInfoReqCheckError: {
    mobile:
      "//button[contains(@class, 'bg-system-error-10')]/span[text()='Additional Information']",
    desktop:
      "//button[contains(@class, 'bg-system-error-10')]/span[text()='Additional Information']",
  },
  FormsListPage_EBO_NavHistoricalIncidents: {
    mobile:
      "//button[contains(@class,'p-3 bg-neutral-shade-3')  and .//span[text()='Historical Incidents']]",
    desktop:
      "//button[contains(@class,'p-3 bg-neutral-shade-3')  and .//span[text()='Historical Incidents']]",
  },
  FormListPage_EBO_NavHistoricalIncidentsReqCheckError: {
    mobile:
      "//button[contains(@class, 'bg-system-error-10')]/span[text()='Historical Incidents']",
    desktop:
      "//button[contains(@class, 'bg-system-error-10')]/span[text()='Historical Incidents']",
  },
  FormsListPage_EBO_NavPhotos: {
    mobile:
      "//button[contains(@class,'p-3 bg-neutral-shade-3')  and .//span[text()='Photos']]",
    desktop:
      "//button[contains(@class,'p-3 bg-neutral-shade-3')  and .//span[text()='Photos']]",
  },
  FormListPage_EBO_NavPhotosReqCheckError: {
    mobile:
      "//button[contains(@class, 'bg-system-error-10')]/span[text()='Photos']",
    desktop:
      "//button[contains(@class, 'bg-system-error-10')]/span[text()='Photos']",
  },
  FormsListPage_EBO_NavSummary: {
    mobile:
      "//button[contains(@class,'p-3 bg-neutral-shade-3')  and .//span[text()='Summary']]",
    desktop:
      "//button[contains(@class,'p-3 bg-neutral-shade-3')  and .//span[text()='Summary']]",
  },
  FormListPage_EBO_NavSummaryReqCheckError: {
    mobile:
      "//button[contains(@class, 'bg-system-error-10')]/span[text()='Summary']",
    desktop:
      "//button[contains(@class, 'bg-system-error-10')]/span[text()='Summary']",
  },
  FormsListPage_EBO_NavPersonnel: {
    mobile:
      "//button[contains(@class,'p-3 bg-neutral-shade-3')  and .//span[text()='Personnel']]",
    desktop:
      "//button[contains(@class,'p-3 bg-neutral-shade-3')  and .//span[text()='Personnel']]",
  },
  FormListPage_EBO_NavPersonnelReqCheckError: {
    mobile:
      "//button[contains(@class, 'bg-system-error-10')]/span[text()='Personnel']",
    desktop:
      "//button[contains(@class, 'bg-system-error-10')]/span[text()='Personnel']",
  },
  EBO_ObservationDetails_HECA_Rules_lblHeading: {
    mobile: "//header//span[contains(.,'HECA Rules')]",
    desktop: "//header//span[contains(.,'HECA Rules')]",
  },
  EBO_ObservationDetails_HECA_Rules_rightArrow: {
    mobile:
      "//div[contains(@class,'text-left text-base text-neutral-shade-100')]//i[contains(@class,'ci-chevron_big_right')]",
    desktop:
      "//div[contains(@class,'text-left text-base text-neutral-shade-100')]//i[contains(@class,'ci-chevron_big_right')]",
  },
  EBO_ObservationDetails_HECA_Rules_downArrow: {
    mobile:
      "//div[contains(@class,'text-left text-base text-neutral-shade-100')]//i[contains(@class,'ci-chevron_big_down')]",
    desktop:
      "//div[contains(@class,'text-left text-base text-neutral-shade-100')]//i[contains(@class,'ci-chevron_big_down')]",
  },
  EBO_ObservationDetails_HECA_Rules_expandedSection: {
    mobile: "//div[@class='p-4']//div[@class='px-8'][.//ol[1]]",
    desktop: "//div[@class='p-4']//div[@class='px-8'][.//ol[1]]",
  },
  EBO_ObservationDetails_lblJobDetails: {
    mobile: "//h2[normalize-space(text())='Job Details']",
    desktop: "//h2[normalize-space(text())='Job Details']",
  },
  EBO_ObservationDetails_OpCoObservedError: {
    mobile:
      "(//div[@role='select' and contains(@class, 'Select_selectError__')])[1]",
    desktop:
      "(//div[@role='select' and contains(@class, 'Select_selectError__')])[1]",
  },
  EBO_ObservationDetails_DepartmentObservedError: {
    mobile:
      "(//div[@role='select' and contains(@class, 'Select_selectError__')])[2]",
    desktop:
      "(//div[@role='select' and contains(@class, 'Select_selectError__')])[2]",
  },
  EBO_ObservationDetails_WorkTypeError: {
    mobile:
      "(//div[@role='select' and contains(@class, 'Select_selectError__')])[3]",
    desktop:
      "(//div[@role='select' and contains(@class, 'Select_selectError__')])[3]",
  },
  EBO_ObservationDetails_dateSelector: {
    mobile:
      "//label[contains(text(), 'Observation Date')]/following-sibling::div//input[@type='date']",
    desktop:
      "//label[contains(text(), 'Observation Date')]/following-sibling::div//input[@type='date']",
  },
  EBO_ObservationDetails_timeSelector: {
    mobile:
      "//label[contains(text(), 'Observation Time')]/following-sibling::div//input[@type='time']",
    desktop:
      "//label[contains(text(), 'Observation Time')]/following-sibling::div//input[@type='time']",
  },
  EBO_ObservationDetails_InputWONumber: {
    mobile: "//label[text()='WO Number']/following-sibling::div//input",
    desktop: "//label[text()='WO Number']/following-sibling::div//input",
  },
  EBO_ObservationDetails_lblWorkLocation: {
    mobile: "//h2[normalize-space(text())='Work Location *']",
    desktop: "//h2[normalize-space(text())='Work Location *']",
  },
  EBO_ObservationDetails_LocationError: {
    mobile:
      "//div[contains(@class, 'border-system-error-40')]//input[@placeholder='Search Location']",
    desktop:
      "//div[contains(@class, 'border-system-error-40')]//input[@placeholder='Search Location']",
  },
  EBO_ObservationDetails_LocationInput: {
    mobile: "//label[text()='Location']/following-sibling::div//input",
    desktop: "//label[text()='Location']/following-sibling::div//input",
  },
  EBO_ObservationDetails_LatError: {
    mobile:
      "//label[text()='Current Latitude']/following-sibling::div[contains(@class, 'border-system-error-40')]",
    desktop:
      "//label[text()='Current Latitude']/following-sibling::div[contains(@class, 'border-system-error-40')]",
  },
  EBO_ObservationDetails_LatInput: {
    mobile: "//label[text()='Current Latitude']/following-sibling::div//input",
    desktop: "//label[text()='Current Latitude']/following-sibling::div//input",
  },
  EBO_ObservationDetails_LongError: {
    mobile:
      "//label[text()='Current Longitude']/following-sibling::div[contains(@class, 'border-system-error-40')]",
    desktop:
      "//label[text()='Current Longitude']/following-sibling::div[contains(@class, 'border-system-error-40')]",
  },
  EBO_ObservationDetails_LongInput: {
    mobile: "//label[text()='Current Longitude']/following-sibling::div//input",
    desktop:
      "//label[text()='Current Longitude']/following-sibling::div//input",
  },
  FormListPage_EBO_DateSelector_ErrorToast: {
    mobile:
      "//div//button[.//p[contains(text(),'The observation date must be before or equal to today')]]",
    desktop:
      "//div//button[.//p[contains(text(),'The observation date must be before or equal to today')]]",
  },
  EBO_ObservationDetails_OpCoObservedDropdown: {
    mobile:
      "//span[text()='OpCo Observed *']/following-sibling::div//div[contains(@class,'Select_select__') and @role='select']",
    desktop:
      "//span[text()='OpCo Observed *']/following-sibling::div//div[contains(@class,'Select_select__') and @role='select']",
  },
  EBO_ObservationDetails_OpCoObservedDropdownOptions: {
    mobile:
      "//ul[contains(@class,'bg-white')]//li[contains(@class,'SelectOption')]",
    desktop:
      "//ul[contains(@class,'bg-white')]//li[contains(@class,'SelectOption')]",
  },
  EBO_ObservationDetails_OpCoObservedDropdownOptions_BGE: {
    mobile: "//ul//li[@aria-hidden='true']//span[text()='BGE']",
    desktop: "//ul//li[@aria-hidden='true']//span[text()='BGE']",
  },
  EBO_ObservationDetails_DepartmentObservedDropdown: {
    mobile:
      "//span[text()='Department Observed *']/following-sibling::div//div[contains(@class,'Select_select__') and @role='select']",
    desktop:
      "//span[text()='Department Observed *']/following-sibling::div//div[contains(@class,'Select_select__') and @role='select']",
  },
  EBO_ObservationDetails_DepartmentObservedOptions_BSC: {
    mobile: "//ul//li[@aria-hidden='true']//span[text()='BSC - BSC']",
    desktop: "//ul//li[@aria-hidden='true']//span[text()='BSC - BSC']",
  },
  EBO_ObservationDetails_WorkTypeDropdown: {
    mobile:
      "//span[text()='Work type *']/following-sibling::div[contains(@class,'MultiSelect_select__') and @role='select']",
    desktop:
      "//span[text()='Work type *']/following-sibling::div[contains(@class,'MultiSelect_select__') and @role='select']",
  },
  EBO_HET_AddedActivityTitleLbl: {
    mobile: "//span[@class='font-semibold text-neutral-shade-75']",
    desktop: "//span[@class='font-semibold text-neutral-shade-75']",
  },
  EBO_HET_AddedActivitySubTaskTitleLbl: {
    mobile: "//span[contains(@class,'text-base text-neutral-shade-100')]",
    desktop: "//span[contains(@class,'text-base text-neutral-shade-100')]",
  },
  FormListPage_EBO_NavDynamicLocator: (pageName: string) => ({
    mobile: `//button[contains(@class,'p-3 bg-neutral-shade-3')  and .//span[text()='${pageName}']]`,
    desktop: `//button[contains(@class,'p-3 bg-neutral-shade-3')  and .//span[text()='${pageName}']]`,
  }),
  EBO_SubPage_TitleLbl: (activityName: string) => ({
    mobile: `//span[contains(@class,'font-semibold text-xl') and contains(text(),'${activityName}')]`,
    desktop: `//span[contains(@class,'font-semibold text-xl') and contains(text(),'${activityName}')]`,
  }),
  EBO_SubPage_SubTaskTitleLbl: {
    mobile: "//span[contains(@class,'text-base text-neutral-shade-100')]",
    desktop: "//span[contains(@class,'text-base text-neutral-shade-100')]",
  },
  EBO_SubPage_HighEnergyHazardObservedComponents: {
    mobile: "(//div[contains(@class,'shadow-10 rounded-lg')])",
    desktop: "(//div[contains(@class,'shadow-10 rounded-lg')])",
  },
  EBO_SubPage_FirstHazardObservedComponentTitle: {
    mobile:
      "(//div[contains(@class,'shadow-10 rounded-lg')])[1]//span[contains(@class,'text-white font-semibold')]",
    desktop:
      "(//div[contains(@class,'shadow-10 rounded-lg')])[1]//span[contains(@class,'text-white font-semibold')]",
  },
  EBO_SubPage_FirstHazardObservedComponentToggleLabel: {
    mobile:
      "(//div[contains(@class,'shadow-10 rounded-lg')])[1]//span[contains(@class,'text-neutral-shade-100 text-sm font-semibold antialiased')]",
    desktop:
      "(//div[contains(@class,'shadow-10 rounded-lg')])[1]//span[contains(@class,'text-neutral-shade-100 text-sm font-semibold antialiased')]",
  },
  EBO_SubPage_FirstHazardObservedComponentInputToggle: {
    mobile:
      "(//div[contains(@class,'shadow-10 rounded-lg')])[1]//button[contains(.,'Toggle')]",
    desktop:
      "(//div[contains(@class,'shadow-10 rounded-lg')])[1]//button[contains(.,'Toggle')]",
  },
  EBO_RecommendedHighEnergyHazards_PopUp_SubTitle: {
    mobile: "//div[contains(@class,'flex flex-row')]/following-sibling::p[1]",
    desktop: "//div[contains(@class,'flex flex-row')]/following-sibling::p[1]",
  },
  EBO_RecommendedHighEnergyHazards_PopUp_HazardDescriptionInput: {
    mobile:
      "(//textarea[@placeholder='Detailed description of the Hazard'])[1]",
    desktop:
      "(//textarea[@placeholder='Detailed description of the Hazard'])[1]",
  },
  EBO_RecommendedHighEnergyHazards_PopUp_DirectControlsYes: {
    mobile:
      "(//button[contains(@class,'text-center truncate') and .//span[contains(text(),'Yes')]])[1]",
    desktop:
      "(//button[contains(@class,'text-center truncate') and .//span[contains(text(),'Yes')]])[1]",
  },
  EBO_RecommendedHighEnergyHazards_PopUp_DirectControlsNo: {
    mobile:
      "(//button[contains(@class,'text-center truncate') and .//span[contains(text(),'No')]])[1]",
    desktop:
      "(//button[contains(@class,'text-center truncate') and .//span[contains(text(),'No')]])[1]",
  },
  EBO_RecommendedHighEnergyHazards_PopUp_DropdownDirectControls: {
    mobile:
      "//label[text()='Direct Controls']/following-sibling::div//div[contains(@class,'MultiSelect_select__') and @role='select']",
    desktop:
      "//label[text()='Direct Controls']/following-sibling::div//div[contains(@class,'MultiSelect_select__') and @role='select']",
  },
  EBO_RecommendedHighEnergyHazards_PopUp_DropdownDirectControlsOptions: {
    mobile:
      "(//ul[contains(@class,'bg-white')]//li[contains(@class,'SelectOption')])",
    desktop:
      "(//ul[contains(@class,'bg-white')]//li[contains(@class,'SelectOption')])",
  },
  EBO_RecommendedHighEnergyHazards_PopUp_DirectControlDescriptionInput: {
    mobile:
      "(//textarea[@placeholder='Detailed description of the control'])[1]",
    desktop:
      "(//textarea[@placeholder='Detailed description of the control'])[1]",
  },
  EBO_RecommendedHighEnergyHazards_PopUp_ConfirmBtn: {
    mobile:
      "//button[contains(@class,'text-center truncate') and .//span[contains(text(),'Confirm updates')]]",
    desktop:
      "//button[contains(@class,'text-center truncate') and .//span[contains(text(),'Confirm updates')]]",
  },
  EBO_AdditionalInfo_TitleLbl: {
    mobile:
      "//h2[contains(@class,'text-section-heading font-section-heading')]",
    desktop:
      "//h2[contains(@class,'text-section-heading font-section-heading')]",
  },
  EBO_AdditionalInfo_CommentsInputTxtBox: {
    mobile: "//label[text()='Comments']/following-sibling::textarea",
    desktop: "//label[text()='Comments']/following-sibling::textarea",
  },
  EBO_HistoricalIncidents_TitleLbl: {
    mobile: "//h2[normalize-space(text())='Historical Incidents']",
    desktop: "//h2[normalize-space(text())='Historical Incidents']",
  },
  EBO_Summary_TitleLbl: {
    mobile: "//h2[normalize-space(text())='Energy-Based Observation Summary']",
    desktop: "//h2[normalize-space(text())='Energy-Based Observation Summary']",
  },
  EBO_Personnel_Title_Lbl: {
    mobile: "//h2[normalize-space(text())='Personnel']",
    desktop: "//h2[normalize-space(text())='Personnel']",
  },
  EBO_Personnel_CrewMembers_Title_Lbl: {
    mobile:
      "//span[contains(@class,'text-sm text-brand-gray-70') and contains(text(),'Crew Members *')]",
    desktop:
      "//span[contains(@class,'text-sm text-brand-gray-70') and contains(text(),'Crew Members *')]",
  },
  EBO_Personnel_ObserverName_Title_Lbl: {
    mobile:
      "//label[contains(@class,'block text-tiny') and contains(text(),'Observer Name')]",
    desktop:
      "//label[contains(@class,'block text-tiny') and contains(text(),'Observer Name')]",
  },
  EBO_Personnel_ObserverName_Value_Lbl: {
    mobile: "//label[text()='Observer Name']/following-sibling::span",
    desktop: "//label[text()='Observer Name']/following-sibling::span",
  },
  EBO_Personnel_CrewMembers_Dropdown: {
    mobile: "//span[text()='Crew Members *']/following-sibling::div[contains(@class,'MultiSelect_select__') and @role='select']",
    desktop: "//span[text()='Crew Members *']/following-sibling::div[contains(@class,'MultiSelect_select__') and @role='select']",
  },
  EBO_Personnel_CrewMembers_Dropdown_Error: {
    mobile: "(//div[@role='select' and contains(@class, 'Select_selectError__')])[1]",
    desktop: "(//div[@role='select' and contains(@class, 'Select_selectError__')])[1]",
  },
  EBO_Personnel_CrewMembers_DropdownOptions: {
    mobile: "(//ul[contains(@class,'bg-white')]//li[contains(@class,'SelectOption')])",
    desktop: "(//ul[contains(@class,'bg-white')]//li[contains(@class,'SelectOption')])",
  },
};
