export const InsightsPageLocators = {
  InsightsPage_lblTitle: {
    mobile: "//h4[contains(text(),'Insights')]",
    desktop: "//h4[contains(text(),'Insights')]",
  },
  Sidebar: {
    mobile:
      "//div[contains(@class,'bg-white') and contains(@class,'rounded-xl') and contains(@class,'flex-col') and contains(@class,'gap-3')]",
    desktop:
      "//div[contains(@class,'bg-white') and contains(@class,'rounded-xl') and contains(@class,'flex-col') and contains(@class,'gap-3')]",
  },
  SelectedButton: {
    mobile:
      "//button[contains(@class,'border-2') and contains(@class,'border-black')]",
    desktop:
      "//button[contains(@class,'border-2') and contains(@class,'border-black')]",
  },
  MainSectionTitle: {
    mobile:
      "//h5[contains(@class,'text-center') and contains(@class,'font-medium')]",
    desktop:
      "//h5[contains(@class,'text-center') and contains(@class,'font-medium')]",
  },
  ExpandButton: {
    mobile: "//button//i[contains(@class,'ci-expand')]",
    desktop: "//button//i[contains(@class,'ci-expand')]",
  },
  RecentAddedInsight: {
    mobile: "(//button[contains(@class,'p-3 bg-neutral-shade-3')])[1]",
    desktop: "(//button[contains(@class,'p-3 bg-neutral-shade-3')])[1]",
  },
  RecentAddedInsightName: {
    mobile: "(//button[contains(@class,'p-3 bg-neutral-shade-3')])[1]//span",
    desktop: "(//button[contains(@class,'p-3 bg-neutral-shade-3')])[1]//span",
  },
  AddedInsightReportDiv: {
    mobile: "//section[@id='report-insight']",
    desktop: "//section[@id='report-insight']",
  },
  AddedInsightDetailsIFrame: {
    mobile:
      "//section[@id='report-insight']//iframe[contains(@src, 'powerbi.com/reportEmbed')]",
    desktop:
      "//section[@id='report-insight']//iframe[contains(@src, 'powerbi.com/reportEmbed')]",
  },
  InsightLocatorByName: (InsightName: string) => ({
    mobile: `(//button[contains(@class,'p-3 bg-neutral-shade-3')])[1][.//span[text()='${InsightName}']]`,
    desktop: `(//button[contains(@class,'p-3 bg-neutral-shade-3')])[1][.//span[text()='${InsightName}']]`,
  }),
};
