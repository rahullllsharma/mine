import type { NextApiRequest, NextApiResponse } from "next";
import type { AuthUser } from "@/types/auth/AuthUser";
import type { TenantEntity } from "@/types/tenant/TenantEntities";

declare global {
  type UrbintNextApiHandler<T = any> = (
    req: NextApiRequest & {
      locals: {
        user: AuthUser & { entities: TenantEntity[] };
        connection: {
          protocol: "http" | "https";
          origin: string;
          isSecure: boolean;
        };
      };
    },
    res: NextApiResponse<T>
  ) => unknown | Promise<unknown>;

  type AuthMiddlewareHandler = (
    callback: UrbintNextApiHandler
  ) => UrbintNextApiHandler;
}
