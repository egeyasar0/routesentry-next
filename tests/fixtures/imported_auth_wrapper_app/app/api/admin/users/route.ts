import { requireAdmin as guard } from "@/authz"

export async function GET() {
  await guard()
  return Response.json([])
}

