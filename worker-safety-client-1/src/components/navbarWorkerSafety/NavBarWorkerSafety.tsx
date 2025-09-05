import type { DropdownProps } from "../shared/dropdown/Dropdown";
import type { TabsOption } from "../shared/tabs/Tabs";
import router from "next/router";
import { signOut } from "next-auth/react";
import axios from "axios";
import InitialsAvatar from "@/components/shared/avatar/initials/InitialsAvatar";
import { useTenantFeatures } from "@/hooks/useTenantFeatures";
import { useAuthStore } from "@/store/auth/useAuthStore.store";
import { useTenantStore } from "@/store/tenant/useTenantStore.store";
import packageJson from "../../../package.json";
import BottomNavbar from "../shared/bottomNavbar/BottomNavbar";
import Dropdown from "../shared/dropdown/Dropdown";
import NavBar from "../shared/navbar/NavBar";
import TabsDark from "../shared/tabs/dark/TabsDark";
import TabsMenuLight from "../shared/tabs/menuLight/TabsMenuLight";
import styles from "./navBarWorkerSafety.module.scss";

export type NavBarTabOptions = TabsOption & { route: string };
export enum NavbarPlacement {
  TOP = "TOP",
  BOTTOM = "BOTTOM",
}

export const getTabOptions = (
  workPackageLabel: string,
  tabType: NavbarPlacement,
  displayLearnings: boolean | undefined,
  displayFormsList: boolean | undefined,
  displayWorkPackage: boolean | undefined,
  displayMap: boolean | undefined,
  displayPlannings: boolean | undefined,
  formsListLabel: string,
  templateFormLabel: string,
  displayInsights: boolean | undefined,
  displayTemplatesList: boolean | undefined,
  displayTemplateFormsList: boolean | undefined
): NavBarTabOptions[] => {
  if (tabType === NavbarPlacement.BOTTOM) {
    return [
      ...(displayWorkPackage
        ? [
            {
              name: workPackageLabel,
              route: "/projects",
              icon: "projects_list",
            } as NavBarTabOptions,
          ]
        : []),
      ...(displayMap
        ? [
            {
              name: "Map",
              route: "/map",
              icon: "map",
            } as NavBarTabOptions,
          ]
        : []),
      ...(displayFormsList
        ? [
            {
              name: formsListLabel,
              route: "/forms",
              icon: "projects_list",
            } as NavBarTabOptions,
          ]
        : []),
      {
        name: "Menu",
        route: "/menu",
        icon: "hamburger",
      },
    ];
  }

  return [
    ...(displayWorkPackage
      ? [
          {
            name: workPackageLabel,
            route: "/projects",
          },
        ]
      : []),
    ...(displayMap
      ? [
          {
            name: "Map",
            route: "/map",
          },
        ]
      : []),

    ...(displayFormsList
      ? [
          {
            name: formsListLabel,
            route: "/forms",
          },
        ]
      : []),
    ...(displayTemplateFormsList
      ? [
          {
            name: templateFormLabel,
            route: "/template-forms",
          },
        ]
      : []),
    ...(displayInsights
      ? [
          {
            name: "Insights",
            route: "/insights",
          },
        ]
      : []),
  ];
};

type TabsOptions = {
  options: NavBarTabOptions[];
  defaultIndex?: number;
  navbarPlacement?: NavbarPlacement;
};

const Tabs = ({
  options,
  navbarPlacement = NavbarPlacement.TOP,
}: TabsOptions): JSX.Element => {
  const tabSelectionHandler = (index: number) => {
    router.push(options[index].route);
  };

  let routeInOptionsIndex = options.findIndex(option =>
    router.pathname?.startsWith(option.route)
  );

  if (routeInOptionsIndex === -1) {
    if (
      router.pathname?.startsWith("/jsb") ||
      router.pathname?.startsWith("/ebo")
    ) {
      routeInOptionsIndex = options.findIndex(
        // We are re routing back to forms tab on clicking on any jsb,ebo
        option => option.route === "/forms"
      );
    } else {
      /**
       * NOTE:
       * This is a hack solution because Tabs component always has to select an option.
       * This condition adds an option to the options array that will never be present in the nav bar,
       * so when users land in a 404 page they can navigate in the application.
       */

      options.push({
        name: "placeholder tab",
        route: router.pathname,
        hidden: true,
      });
    }
  }

  if (navbarPlacement === NavbarPlacement.BOTTOM) {
    return (
      <TabsMenuLight
        options={options}
        selectedIndex={routeInOptionsIndex}
        onSelect={tabSelectionHandler}
      />
    );
  }

  return (
    <div className="hidden sm:block">
      <TabsDark
        options={options}
        selectedIndex={routeInOptionsIndex}
        onSelect={tabSelectionHandler}
      />
    </div>
  );
};

export default function NavBarWorkerSafety(): JSX.Element {
  const { tenant, getAllEntities } = useTenantStore();
  const { workPackage, formList, templateForm } = getAllEntities();
  const {
    displayLearnings,
    displayFormsList,
    displayWorkPackage,
    displayMap,
    displayPlannings,
    displayInsights,
    displayTemplatesList,
    displayTemplateFormsList,
  } = useTenantFeatures(tenant.name);

  const { me, isAdmin } = useAuthStore();

  const dropdownArgs: DropdownProps = {
    menuItems: [
      [
        {
          label: "Logout",
          onClick: async () => {
            await logout();
          },
        },
      ],
    ],
  };

  const options = getTabOptions(
    workPackage.labelPlural,
    NavbarPlacement.TOP,
    displayLearnings,
    displayFormsList,
    displayWorkPackage,
    displayMap,
    displayPlannings,
    formList?.labelPlural,
    templateForm?.labelPlural,
    displayInsights,
    displayTemplatesList,
    displayTemplateFormsList
  );

  if (
    displayTemplatesList &&
    me.permissions.includes("CONFIGURE_CUSTOM_TEMPLATES")
  ) {
    options.push({
      name: "Templates",
      route: "/templates",
    });
  }

  if (isAdmin()) {
    options.push({
      name: "Admin",
      route: "/admin/config",
    });

    dropdownArgs.menuItems = [
      ...dropdownArgs.menuItems,
      [
        {
          label: `Version: ${packageJson.version}`,
          disabled: true,
        },
      ],
    ];
  }

  const rightContent = (
    <Dropdown className="z-30" {...dropdownArgs}>
      <button>
        <InitialsAvatar name={me.initials ?? "NA"} />
      </button>
    </Dropdown>
  );

  const mobileAndTabletOptions = getTabOptions(
    workPackage.labelPlural,
    NavbarPlacement.BOTTOM,
    displayLearnings,
    displayFormsList,
    displayWorkPackage,
    displayMap,
    displayPlannings,
    formList?.labelPlural,
    templateForm?.labelPlural,
    displayInsights,
    displayTemplatesList,
    displayTemplateFormsList
  );

  return (
    <>
      <div className={styles.bottomNavBar}>
        <BottomNavbar
          content={
            <Tabs
              options={mobileAndTabletOptions}
              navbarPlacement={NavbarPlacement.BOTTOM}
            />
          }
        />
      </div>
      <div className={styles.topNavBar}>
        <NavBar
          title="Worker Safety"
          leftContent={<Tabs options={options} />}
          rightContent={rightContent}
        />
      </div>
    </>
  );
}

const logout = async (): Promise<void> => {
  try {
    await axios.get("/api/auth/logout").then(() => {
      signOut({ redirect: true, callbackUrl: window.location.href });
    });
  } catch (error) {
    // <show some notification to user asking to retry signout>
    console.error(error);
    throw error;
  }
};
