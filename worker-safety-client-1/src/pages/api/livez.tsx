import type { NextApiRequest, NextApiResponse } from "next";

type LivezResponse = {
  status: string;
};

const livez = function (
  req: NextApiRequest,
  res: NextApiResponse<LivezResponse>
): void {
  res.status(200).json({ status: "OK" });
};

export default livez;
