import type { NextApiRequest, NextApiResponse } from "next";

type ReadyResponse = {
  status: string;
};

const readyz = function (
  req: NextApiRequest,
  res: NextApiResponse<ReadyResponse>
): void {
  res.status(200).json({ status: "OK" });
};

export default readyz;
