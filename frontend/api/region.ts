import type { VercelRequest, VercelResponse } from "@vercel/node";

export default function handler(
  req: VercelRequest,
  res: VercelResponse
) {
  const region = req.headers["x-vercel-ip-country-region"];

  res.status(200).json({
    region: typeof region === "string" ? region : null,
  });
}