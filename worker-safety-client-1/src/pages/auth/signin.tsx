import type { GetServerSidePropsContext, NextApiRequest } from "next";
import { signIn } from "next-auth/react";
import { getServerSession } from "next-auth/next";
import { useEffect, useRef } from "react";
import { getNextConfig } from "@/utils/auth";
import Loader from "@/components/shared/loader/Loader";

export default function SignIn({
  session,
  callbackUrl,
}: Readonly<Record<string, any>>) {
  const signingIn = useRef(false);
  useEffect(() => {
    if (signingIn.current) return;
    signingIn.current = true;
    signIn("keycloak", { callbackUrl });
  }, [session, callbackUrl]);

  return <Loader />;
}

export async function getServerSideProps(context: GetServerSidePropsContext) {
  const { query } = context;

  const authOptions = await getNextConfig(context.req as NextApiRequest);
  const session = await getServerSession(context.req, context.res, authOptions);

  return {
    props: {
      session: {
        ...session,
        user: { ...session?.user, image: session?.user?.image ?? null },
        error: session?.error ?? null,
      },
      callbackUrl: query.callbackUrl ?? "/",
    },
  };
}
