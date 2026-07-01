import { cookies } from "next/headers"

export async function GET() {
  const session = cookies().get("session")
  const auth = cookies().get('auth')
  if (!session && !auth) {
    return Response.json({ error: "unauthorized" }, { status: 401 })
  }
  return Response.json([])
}
