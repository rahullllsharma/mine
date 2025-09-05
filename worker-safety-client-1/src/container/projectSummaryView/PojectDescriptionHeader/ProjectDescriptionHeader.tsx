import { Disclosure } from "@headlessui/react";
import classnames from "classnames";
import { Icon } from "@urbint/silica";
import ProjectDescriptionContent from "./ProjectDescriptionContent";

export type ProjectDescriptionHeaderProps = {
  description?: string;
  maxCharacters?: number;
};

const ProjectDescriptionHeader = ({
  description = "",
  maxCharacters = 100,
}: ProjectDescriptionHeaderProps) => {
  description = description ?? "";
  const breakTag =
    description.indexOf("<br>") < 0
      ? description.indexOf("\n") < 0
        ? "<br>"
        : "\n"
      : "<br>";
  const firstLine = description ? description.trim().split(breakTag)[0] : "";
  const truncatedTitle =
    firstLine.length > maxCharacters
      ? `${firstLine.substring(0, maxCharacters)}...`
      : firstLine;
  const totalLines = description ? description.split(breakTag).length : 0;
  const showFullDescription =
    totalLines > 1 || firstLine.length > maxCharacters;

  return (
    <Disclosure>
      {({ open }) => (
        <div className="flex">
          <ProjectDescriptionContent
            description={description}
            showFullDescription={open && showFullDescription}
            truncatedTitle={truncatedTitle}
          />
          <Disclosure.Button className="flex">
            {showFullDescription && (
              <Icon
                name="chevron_big_up"
                className={classnames(
                  "text-[1.375rem] leading-0",
                  "transform transition ease-in-out duration-200",
                  {
                    "rotate-0": open,
                    "rotate-180": !open,
                  }
                )}
              />
            )}
          </Disclosure.Button>
        </div>
      )}
    </Disclosure>
  );
};

export { ProjectDescriptionHeader };
