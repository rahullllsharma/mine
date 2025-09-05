import type { IncomingMessage } from "http";
import type { NextApiRequest, NextApiResponse } from "next";
import type { AxiosError } from "axios";
import axios from "axios";
import { getServerSession } from "next-auth";
import { getKeycloakCfg, getNextConfig } from "@/utils/auth";
import { config } from "@/config";

const LogoutComponent = async (req: NextApiRequest, res: NextApiResponse) => {
  const { host } = (req as IncomingMessage).headers;
  const { hostname } = new URL(
    `${config.appEnv === "development" ? "http" : "https"}://${host}`
  );
  const keycloakCfg = await getKeycloakCfg({ hostname });
  // Add the id_token_hint to the query string
  const params = new URLSearchParams();
  const nextConfig = await getNextConfig(req);
  const session = await getServerSession(req, res, nextConfig);
  const idToken = session?.idToken as string;
  params.append("id_token_hint", idToken);
  const path = `${config.keycloakUrl}/realms/${
    keycloakCfg.realm
  }/protocol/openid-connect/logout?${params.toString()}`;
  try {
    const { status, statusText } = await axios.get(path);

    console.log("Completed post-logout handshake", status, statusText);
    res.status(status).json(null);
  } catch (e: any) {
    console.error(
      "Unable to perform post-logout handshake",
      (e as AxiosError)?.code ?? e
    );
    res.status(500).json(null);
  }
};

export default LogoutComponent;
