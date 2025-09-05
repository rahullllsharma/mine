import type { PropsWithClassName, RouterLink } from "@/types/Generic";

import type { ReactNode } from "react";
import type {
  PageHeaderAction,
  PageHeaderActionTooltip,
} from "./components/headerActions/HeaderActions";
import cx from "classnames";
import NextLink from "next/link";
import { capitalize } from "lodash-es";
import { FormViewTabStates } from "@/components/forms/Utils";
import Link from "@/components/shared/link/Link";

import { HeaderActions } from "./components/headerActions/HeaderActions";

type PageHeaderBaseProps = PropsWithClassName<{
  children?: ReactNode;
  pageTitle?: string;
  linkText?: string;
  linkRoute?: string | RouterLink;
  actions?: PageHeaderActionTooltip | PageHeaderAction | PageHeaderAction[];
  additionalInfo?: ReactNode;
  selectedTab?: FormViewTabStates;
  setSelectedTab?: (selectedTab: FormViewTabStates) => void;
}>;

type PageHeaderPropsWithLink = PageHeaderBaseProps & {
  linkText: string;
  linkRoute: string | RouterLink;
};

type PageHeaderPropsWithoutLink = PageHeaderBaseProps & {
  linkText?: never;
  linkRoute?: never;
};

type PageHeaderProps = PageHeaderPropsWithLink | PageHeaderPropsWithoutLink;

export default function PageHeader({
  className,
  children,
  pageTitle,
  linkText,
  linkRoute,
  actions,
  additionalInfo,
  setSelectedTab,
  selectedTab,
}: PageHeaderProps): JSX.Element {
  let actionsArray:
    | PageHeaderAction[]
    | [PageHeaderAction]
    | [PageHeaderActionTooltip] = [];

  if (actions) {
    actionsArray = Array.isArray(actions)
      ? actions
      : ([actions] as [PageHeaderAction] | [PageHeaderActionTooltip]);
  }

  const hasActions = actionsArray.length > 0;

  return (
    <header className={cx("shadow-5 py-2 px-6 bg-white relative", className)}>
      {linkRoute && linkText ? (
        <NextLink href={linkRoute} passHref>
          <Link label={linkText} iconLeft="chevron_big_left" className="mb-3" />
        </NextLink>
      ) : (
        <div className="h-5 mb-3" />
      )}
      <div className="flex items-center flex-wrap">
        <div className="flex w-full">
          {pageTitle ? (
            <h4 className="text-neutral-shade-100 mr-3">{pageTitle}</h4>
          ) : (
            children
          )}
          {hasActions && <HeaderActions actions={actionsArray} />}
        </div>
        {additionalInfo && <div className="mt-3 w-full">{additionalInfo}</div>}

        {selectedTab && setSelectedTab && (
          <div className="-mb-2 border-b border-gray-200 dark:border-gray-700 w-full">
            <ul
              className="flex flex-wrap -mb-px text-16px font-medium text-center w-full"
              id="default-tab"
              data-tabs-toggle="#tabs"
              role="tablist"
            >
              {Object.values(FormViewTabStates).map(tab => (
                <li className="me-2" role="presentation" key={tab}>
                  <button
                    className={cx("inline-block p-4 border-b-2 rounded-t-lg", {
                      ["border-brand-urbint-40"]: selectedTab === tab,
                      ["border-transparent hover:text-gray-600 hover:border-gray-300 dark:hover:text-gray-300"]:
                        selectedTab !== tab,
                    })}
                    id={`${tab}-tab`}
                    data-tabs-target={`#${tab}`}
                    type="button"
                    role="tab"
                    aria-controls={tab}
                    aria-selected={selectedTab === tab}
                    onClick={() => setSelectedTab(tab)}
                  >
                    {capitalize(tab)}
                  </button>
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </header>
  );
}

export type { PageHeaderProps };
