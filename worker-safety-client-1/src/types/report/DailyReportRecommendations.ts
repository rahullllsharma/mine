type DailyReportRecommendations = {
  dailyReport: {
    crew: {
      foremanName: string;
      constructionCompany: string;
    } | null;
    safetyAndCompliance: {
      phaCompletion: string;
      sopNumber: string;
      sopType: string;
      stepsCalledIn: string;
    } | null;
  };
};

export type { DailyReportRecommendations };
