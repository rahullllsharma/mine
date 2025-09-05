import create from "zustand";

// TODO: File to be removed completely when projectContractorId is fetched from project api
interface TemplateStore {
  projectContractorId?: string;
  projectRegionId?: string;
  setTemplateData: (data: Partial<TemplateStore>) => void;
}

const useTemplateStore = create<TemplateStore>(set => ({
  setTemplateData: set,
}));

export default useTemplateStore;
