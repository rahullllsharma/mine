export type Insight = {
  id: string;
  name: string;
  url: string;
  created_at: string;
  visibility: boolean;
  description?: string;
};

export type InsightFormInputs = {
  name: string;
  url: string;
  description?: string;
  visibility: boolean;
};
