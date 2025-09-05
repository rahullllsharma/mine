import type { NavBarTabOptions } from "@/components/navbarWorkerSafety/NavBarWorkerSafety";
import { useRouter } from "next/router";
import { signOut, useSession } from "next-auth/react";
import axios from "axios";
import PageLayout from "@/components/layout/pageLayout/PageLayout";
import ButtonPrimary from "@/components/shared/button/primary/ButtonPrimary";
import UrbintLogo from "@/components/shared/urbintLogo/UrbintLogo";
import { useTenantFeatures } from "@/hooks/useTenantFeatures";
import { useTenantStore } from "@/store/tenant/useTenantStore.store";
import packageJson from "../../../package.json";

export default function Menu() {
  const router = useRouter();
  const { data: session } = useSession({ required: true });
  const { tenant, getAllEntities } = useTenantStore();
  const { displayTemplatesList, displayTemplateFormsList } = useTenantFeatures(
    tenant.name
  );

  const { templateForm } = getAllEntities();

  const logoutUser = async () => {
    if (session)
      await axios
        .get("/api/auth/logout")
        .then(() => signOut({ redirect: true }))
        .catch(console.error);
  };

  const getTabOptions = (): NavBarTabOptions[] => {
    return [
      ...(displayTemplatesList
        ? [
            {
              name: "Templates",
              route: "/templates",
            },
          ]
        : []),
      ...(displayTemplateFormsList
        ? [
            {
              name: `${templateForm?.labelPlural}`,
              route: "/template-forms",
            },
          ]
        : []),
    ];
  };

  return (
    <PageLayout
      sectionPadding="none"
      className="max-h-screen px-4 flex flex-col justify-between pt-8 pb-20"
    >
      <section className="flex flex-col gap-2">
        <div className="mb-4 flex items-center gap-2">
          <UrbintLogo className="text-brand-urbint-100 w-7 h-7 text-2xl" />
          <span className="text-sm text-brand-urbint-100">Worker Safety</span>
        </div>

        <div className="flex flex-col gap-2">
          {getTabOptions().map(option => (
            <ButtonPrimary
              key={option.route}
              label={option.name}
              onClick={() => router.push(option.route)}
            />
          ))}
        </div>
      </section>

      <section className="flex flex-col items-center gap-3">
        <span className="text-brand-urbint-100 text-sm">
          Version: {packageJson.version}
        </span>
        <ButtonPrimary label="Logout" className="w-full" onClick={logoutUser} />
      </section>
    </PageLayout>
  );
}
