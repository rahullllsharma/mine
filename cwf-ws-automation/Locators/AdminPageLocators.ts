export const AdminPageLocators = {
  VerticalNav_btnInsights: {
    mobile:
      "//div[@role='tablist' and @aria-orientation='vertical']//button[.//span[contains(text(),'Insights')]]",
    desktop:
      "//div[@role='tablist' and @aria-orientation='vertical']//button[.//span[contains(text(),'Insights')]]",
  },
  VerticalNav_btnInsights_highlighted: {
    mobile:
      "//div[@role='tablist' and @aria-orientation='vertical']//button[.//div[contains(@class,'border-neutral-shade-100')]][.//span[contains(text(),'Insights')]]",
    desktop:
      "//div[@role='tablist' and @aria-orientation='vertical']//button[.//div[contains(@class,'border-neutral-shade-100')]][.//span[contains(text(),'Insights')]]",
  },
  InsightsTab_btnAddInsights: {
    mobile:
      "//button[contains(@class,'text-center truncate')][.//span[contains(text(),'Add Insights')]]",
    desktop:
      "//button[contains(@class,'text-center truncate')][.//span[contains(text(),'Add Insights')]]",
  },
  InsightsTab_addInsightsPopUp: {
    mobile: "//div[@class='flex flex-col gap-4']",
    desktop: "//div[@class='flex flex-col gap-4']",
  },
  InsightsTab_mandatoryFieldNameErr: {
    mobile: "//div[@id='name-err']",
    desktop: "//div[@id='name-err']",
  },
  InsightsTab_mandatoryFieldURLErr: {
    mobile: "//div[@id='url-err']",
    desktop: "//div[@id='url-err']",
  },
  InsightsTab_addInsightsPopUp_txtReportName: {
    mobile: "//input[@id='name']",
    desktop: "//input[@id='name']",
  },
  InsightsTab_addInsightsPopUp_txtReportURL: {
    mobile: "//input[@id='url']",
    desktop: "//input[@id='url']",
  },
  InsightsTab_addInsightsPopUp_txtReportDescription: {
    mobile: "//textarea[@id='description']",
    desktop: "//textarea[@id='description']",
  },
  InsightsTab_addInsightsPopUp_checkboxVisibility: {
    mobile: "//label//input[@id='visibility']",
    desktop: "//label//input[@id='visibility']",
  },
  InsightsTab_addInsightsPopUp_btnCancel: {
    mobile:
      "//button[contains(@class,'text-center truncate')][.//span[contains(text(),'Cancel')]]",
    desktop:
      "//button[contains(@class,'text-center truncate')][.//span[contains(text(),'Cancel')]]",
  },
  InsightsTab_addInsightsPopUp_btnAddReport: {
    mobile:
      "//button[contains(@class,'text-center truncate')][.//span[contains(text(),'Add Report')]]",
    desktop:
      "//button[contains(@class,'text-center truncate')][.//span[contains(text(),'Add Report')]]",
  },
  InsightsTab_tableBody: {
    mobile: "//div[@data-testid='table-body']",
    desktop: "//div[@data-testid='table-body']",
  },
  InsightsTab_tableRow: {
    mobile: "(//div[contains(@class,'_tr') and @role='row'])[2]",
    desktop: "(//div[contains(@class,'_tr') and @role='row'])[2]",
  },
  InsightsTab_reportNameCell: {
    mobile: "//div[@role='cell'][1]",
    desktop: "//div[@role='cell'][1]",
  },
  InsightsTab_reportURLCell: {
    mobile: "//div[@role='cell'][2]",
    desktop: "//div[@role='cell'][2]",
  },
  InsightsTab_createdOnCell: {
    mobile: "//div[@role='cell'][3]",
    desktop: "//div[@role='cell'][3]",
  },
  InsightsTab_visibilityCell: {
    mobile: "//div[@role='cell'][4]",
    desktop: "//div[@role='cell'][4]",
  },
  InsightsTab_actionThreeDotsButton: {
    mobile: "//div[@role='row'][1]//div[@role='cell'][last()]//button[@type='button']",
    desktop: "//div[@role='row'][1]//div[@role='cell'][last()]//button[@type='button']",
  },
  InsightsTab_recentInsights_menuItem_editButton: {
    mobile:
      "(//button[contains(@class,'text-center truncate')])[.//span[contains(text(),'Edit')]]",
    desktop:
      "(//button[contains(@class,'text-center truncate')])[.//span[contains(text(),'Edit')]]",
  },
  InsightsTab_recentInsights_menuItem_deleteButton: {
    mobile:
      "(//button[contains(@class,'text-center truncate')])[.//span[contains(text(),'Delete')]]",
    desktop:
      "(//button[contains(@class,'text-center truncate')])[.//span[contains(text(),'Delete')]]",
  },
  InsightsTab_editInsightsPopUp_btnSaveReport: {
    mobile:
      "//button[contains(@class,'text-center truncate')][.//span[contains(text(),'Save Report')]]",
    desktop:
      "//button[contains(@class,'text-center truncate')][.//span[contains(text(),'Save Report')]]",
  },
  InsightsTab_deleteConfirmationPopUp: {
    mobile:
      "//span[contains(@class,'inline-block h-screen')]/following-sibling::div[1]",
    desktop:
      "//span[contains(@class,'inline-block h-screen')]/following-sibling::div[1]",
  },
  InsightsTab_deleteConfirmationPopUp_title: {
    mobile: "//h6[normalize-space(text())='Delete Insight']",
    desktop: "//h6[normalize-space(text())='Delete Insight']",
  },
  InsightsTab_deleteConfirmationPopUp_btnCancel: {
    mobile:
      "//button[contains(@class,'text-center truncate')][.//span[(text()='Cancel')]]",
    desktop:
      "//button[contains(@class,'text-center truncate')][.//span[(text()='Cancel')]]",
  },
  InsightsTab_deleteConfirmationPopUp_btnDeleteReport: {
    mobile:
      "//button[contains(@class,'text-center truncate')][.//span[(text()='Delete Report')]]",
    desktop:
      "//button[contains(@class,'text-center truncate')][.//span[(text()='Delete Report')]]",
  },
  InsightsTab_rowWithInsightName: (InsightName: string) => ({
    mobile: `(//div[contains(@class,'_tr') and @role='row'])[.//span[text()='${InsightName}']]`,
    desktop: `(//div[contains(@class,'_tr') and @role='row'])[.//span[text()='${InsightName}']]`,
  }),
};
