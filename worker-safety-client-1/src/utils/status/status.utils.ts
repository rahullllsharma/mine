const statusTextColorMap: Record<string, string> = {
  in_progress: "text-neutral-shade-100",
  complete: "text-white",
  completed: "text-white",
  pending_post_job_brief: "text-white",
  pending_sign_off: "text-white",
};

const statusBackgroundColorMap: Record<string, string> = {
  complete: "bg-badges-blue",
  in_progress: "bg-gray-100",
  completed: "bg-brand-urbint-40",
  pending_post_job_brief: "bg-badges-purple",
  pending_sign_off: "bg-badges-green-neon",
};

const getDefaultTextColorByStatusLevel = (status: string): string =>
  statusTextColorMap[status?.toLowerCase()] || "text-white";

const getBackgroundColorByStatusLevel = (status: string): string =>
  statusBackgroundColorMap[status?.toLowerCase()] || "bg-gray-100";

export { getDefaultTextColorByStatusLevel, getBackgroundColorByStatusLevel };
