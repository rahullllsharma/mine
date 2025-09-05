export type ProjectDescriptionContentType = {
  description?: string;
  showFullDescription?: boolean;
  truncatedTitle?: string;
};

const ProjectDescriptionContent = function ({
  description = "",
  showFullDescription = false,
  truncatedTitle = "",
}) {
  return (
    <pre
      className="text-sm text-neutral-shade-58 text-left font-sans whitespace-pre-line max-h-60 overflow-y-auto w-full"
      dangerouslySetInnerHTML={{
        __html: showFullDescription
          ? description
            ? description.trim()
            : ""
          : truncatedTitle,
      }}
    ></pre>
  );
};

export default ProjectDescriptionContent;
