export const MapPageLocators = {
  Map_txtSearchInput: {
    mobile:
      "//input[contains(@class, 'flex-auto') and contains(@class, 'rounded-md') and @placeholder='Search locations']",
    desktop:
      "//input[contains(@class, 'flex-auto') and contains(@class, 'rounded-md') and @placeholder='Search locations']",
  },
  Map_CrossBtnSearchInput: {
    mobile: "//button[contains(@class,'text-xl text-neutral-shade-75')]//i[1]",
    desktop: "//button[contains(@class,'text-xl text-neutral-shade-75')]//i[1]",
  },
  Map_LocationAsideBar: {
    mobile:
      "//aside[contains(@class,'absolute inset-0')]",
    desktop:
      "//aside[contains(@class,'absolute inset-0')]",
  },
  Map_LocationCardsInSearchResultsAside: {
    mobile: "//li//div[@data-testid='location-card']",
    desktop: "//li//div[@data-testid='location-card']",
  },
  Map_FirstLocationCardInSearchResults: {
    mobile: "(//li//div[@data-testid='location-card'])[1]",
    desktop: "(//li//div[@data-testid='location-card'])[1]",
  },
  Map_NoWorkOrderFoundMsg_Lbl: {
    mobile:
      "(//div[contains(@class,'text-tiny p-8')]//p[1])[contains(text(),'There are no')]",
    desktop:
      "(//div[contains(@class,'text-tiny p-8')]//p[1])[contains(text(),'There are no')]",
  },
  Map_MapBoxCanvas: {
    mobile:
      "//div[contains(@class,'mapboxgl-canvas-container mapboxgl-interactive')]//canvas[1]",
    desktop:
      "//div[contains(@class,'mapboxgl-canvas-container mapboxgl-interactive')]//canvas[1]",
  },
  Map_MapBoxZoomInBtn: {
    mobile: "//button[@aria-label='Zoom in']",
    desktop: "//button[@aria-label='Zoom in']",
  },
  Map_MapBoxZoomOutBtn: {
    mobile: "//button[@aria-label='Zoom out']",
    desktop: "//button[@aria-label='Zoom out']",
  },
  Map_MapBoxFindMyLocationBtn: {
    mobile: "(//div[@class='mapboxgl-ctrl mapboxgl-ctrl-group']//button)[3]",
    desktop: "(//div[@class='mapboxgl-ctrl mapboxgl-ctrl-group']//button)[3]",
  },
  Map_MapBoxLocationRiskBox: {
    mobile: "//aside[contains(@class,'absolute inline-block')]",
    desktop: "//aside[contains(@class,'absolute inline-block')]",
  },
  Map_LocationRiskBox_HideUnhideBtn: {
    mobile: "//aside[contains(@class,'absolute inline-block')]//button[1]",
    desktop: "//aside[contains(@class,'absolute inline-block')]//button[1]",
  },
  Map_LocationRisks_Lbls: {
    mobile: "//ul[contains(@class,'flex flex-col')]//span//span//p",
    desktop: "//ul[contains(@class,'flex flex-col')]//span//span//p",
  },
  Map_ManageMapLayersBtn: {
    mobile: "(//div[@class='relative']//button[1])[1]",
    desktop: "(//div[@class='relative']//button[1])[1]",
  },
  Map_ManageMapLayers_Dropdown: {
    mobile: "//div[contains(@class,'absolute z-10')]",
    desktop: "//div[contains(@class,'absolute z-10')]",
  },
  Map_ManageMapLayers_ShowLegendBtn: {
    mobile: "(//div[@class='grid gap-y-2']//div//button)[1]",
    desktop: "(//div[@class='grid gap-y-2']//div//button)[1]",
  },
  Map_ManageMapLayers_ShowLegendLbl: {
    mobile: "(//div[@class='grid gap-y-2']//div//p)[1]",
    desktop: "(//div[@class='grid gap-y-2']//div//p)[1]",
  },
  Map_ManageMapLayers_ShowSatelliteBtn: {
    mobile: "(//div[@class='grid gap-y-2']//div//button)[2]",
    desktop: "(//div[@class='grid gap-y-2']//div//button)[2]",
  },
  Map_ManageMapLayers_ShowSatelliteLbl: {
    mobile: "(//div[@class='grid gap-y-2']//div//p)[2]",
    desktop: "(//div[@class='grid gap-y-2']//div//p)[2]",
  },
  Map_ResultsCountLbl: {
    mobile: "//span[contains(@class,'hidden md:block')]",
    desktop: "//span[contains(@class,'hidden md:block')]",
  },
  Map_FilterBtn: {
    mobile: "//span[contains(@class,'hidden md:block')]/following-sibling::button[1]",
    desktop: "//span[contains(@class,'hidden md:block')]/following-sibling::button[1]",
  },
  Map_SearchThisAreaBtn: {
    mobile: "//button[contains(@class,'bg-neutral-light-100 px-1')][contains(text(),'Search')]",
    desktop: "//button[contains(@class,'bg-neutral-light-100 px-1')][contains(text(),'Search')]",
  },
};
