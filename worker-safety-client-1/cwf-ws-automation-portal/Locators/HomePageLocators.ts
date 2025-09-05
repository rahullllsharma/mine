export const HomePageLocators = {
  HomePage_MainMenu_lblWorkerSafety: {
    mobile: "//div[@class='pl-2 text-sm font-semibold uppercase']",
    desktop: "//div[@class='pl-2 text-sm font-semibold uppercase']",
  },
  HomePage_MainMenu_lblWorkPackages: {
    mobile: "//span[normalize-space()='Work Packages']",
    desktop: "//span[normalize-space()='Work Packages']",
  },
  HomePage_MainMenu_lblMap: {
    mobile: "//span[normalize-space()='Map']",
    desktop: "//span[normalize-space()='Map']",
  },
  HomePage_MainMenu_btnMap: {
    mobile: "(//button[contains(@class,'min-w-0 z-10')])[2]",
    desktop:
      "(//button[contains(@id,'headlessui-tabs') and .//span[contains(text(),'Map')]])[2]",
  },
  HomePage_MainMenu_lblFormsList: {
    mobile: "//span[normalize-space()='Forms List']",
    desktop: "//span[normalize-space()='Forms List']",
  },
  HomePage_MainMenu_btnFormsList: {
    mobile: "(//button[contains(@id,'headlessui-tabs-tab')])[3]",
    desktop: "(//button[contains(@id,'headlessui-tabs-tab')])[7]",
  },
  HomePage_MainMenu_highlightedFormsListBtn: {
    mobile:
      "(//button[contains(@id,'headlessui-tabs-tab')])[3]/div[contains(@class, 'border-brand-urbint-40')]",
    desktop:
      "(//button[contains(@id,'headlessui-tabs-tab')])[7]/div[contains(@class, 'border-brand-urbint-40')]",
  },
  HomePage_MainMenu_lblTemplateForms: {
    mobile: "//span[normalize-space()='Template Forms']",
    desktop: "//span[normalize-space()='Template Forms']",
  },
  HomePage_MainMenu_btnTemplateForms: {
    mobile: "(//button[contains(@id,'headlessui-tabs-tab')])[8]",
    desktop: "(//button[contains(@id,'headlessui-tabs-tab')])[8]",
  },
  HomePage_MainMenu_lblInsights: {
    mobile: "//span[normalize-space()='Insights']",
    desktop: "//span[normalize-space()='Insights']",
  },
  HomePage_MainMenu_lblTemplates: {
    mobile: "//span[normalize-space()='Templates']",
    desktop: "//span[normalize-space()='Templates']",
  },
  HomePage_MainMenu_lblAdmin: {
    mobile: "//span[normalize-space()='Admin']",
    desktop: "//span[normalize-space()='Admin']",
  },
  HomePage_MainMenu_btnAdmin: {
    mobile:
      "//button[@role='tab']/div[contains(@class, 'border-b-2')]/span[text()='Admin']",
    desktop:
      "//button[@role='tab']/div[contains(@class, 'border-b-2')]/span[text()='Admin']",
  },
  HomePage_MainMenu_highlightedAdminBtn: {
    mobile:
      "//button[@role='tab']/div[contains(@class, 'border-brand-urbint-40')]/span[text()='Admin']",
    desktop:
      "//button[@role='tab']/div[contains(@class, 'border-brand-urbint-40')]/span[text()='Admin']",
  },
  HomePage_MainHeader_lblWorkPackages: {
    mobile: "//div[@class='flex flex-1']//h4[1]",
    desktop: "//div[@class='flex flex-1']//h4[1]",
  },
  HomePage_txtSearchWorkPackages: {
    mobile: "(//input[contains(@class,'flex-auto rounded-md')])[1]",
    desktop: "(//input[contains(@class,'flex-auto rounded-md')])[1]",
  },
  HomePage_btnAddWorkPackage: {
    mobile: "(//span[@class='mx-1 truncate'])[1]",
    desktop: "(//span[@class='mx-1 truncate'])[1]",
  },
  HomePage_btnActiveTab: {
    mobile: "//span[normalize-space()='Active']",
    desktop: "//span[normalize-space()='Active']",
  },
  HomePage_btnPendingTab: {
    mobile: "//span[normalize-space()='Pending']",
    desktop: "//span[normalize-space()='Pending']",
  },
  HomePage_btnCompletedTab: {
    mobile: "//span[normalize-space()='Completed']",
    desktop: "//span[normalize-space()='Completed']",
  },
  HomePage_btnFormsListTab: {
    mobile: "//span[normalize-space()='Forms List']",
    desktop: "//span[normalize-space()='Forms List']",
  },
  HomePage_lblTableHeaderProject: {
    mobile: "//div[normalize-space()='project']",
    desktop: "//div[normalize-space()='project']",
  },
  HomePage_lblTableHeaderTodaysRisk: {
    mobile: "//div[normalize-space()='Todays risk']",
    desktop: "//div[normalize-space()='Todays risk']",
  },
  HomePage_lblTableHeaderSupervisorRegion: {
    mobile: "//div[contains(text(),'Supervisor')]",
    desktop: "//div[contains(text(),'Supervisor')]",
  },
  HomePage_lblTableHeaderWorkPackageType: {
    mobile: "'//div[contains(text(),'Work Package Type')]')]",
    desktop: "'//div[contains(text(),'Work Package Type')]')]",
  },
  HomePage_lblTableHeaderDivision: {
    mobile: "//div[normalize-space()='Division']",
    desktop: "//div[normalize-space()='Division']",
  },
  HomePage_MainMenu_btnInsights: {
    mobile:
      "//button[@role='tab']/div[contains(@class, 'border-b-2')]/span[text()='Insights']",
    desktop:
      "//button[@role='tab']/div[contains(@class, 'border-b-2')]/span[text()='Insights']",
  },
  HomePage_MainMenu_highlightedInsightsBtn: {
    mobile:
      "//button[@role='tab']/div[contains(@class, 'border-brand-urbint-40')]/span[text()='Insights']",
    desktop:
      "//button[@role='tab']/div[contains(@class, 'border-brand-urbint-40')]/span[text()='Insights']",
  },
  HomePage_MainMenu_btnTabsAll: {
    mobile: "(//button[@role='tab']/div[contains(@class, 'box-border')])",
    desktop: "//button[@role='tab']/div[contains(@class, 'border-b-2')]",
  },
};
