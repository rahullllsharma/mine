import type { NextApiRequest, NextApiResponse } from "next";
import type { NextAuthOptions } from "next-auth";

import NextAuth from "next-auth";

import { getNextConfig } from "@/utils/auth";

export default async function NextAuthComp(
  req: NextApiRequest,
  res: NextApiResponse
) {
  const nextConfig: NextAuthOptions = await getNextConfig(req);
  return await NextAuth(req, res, nextConfig);
}
