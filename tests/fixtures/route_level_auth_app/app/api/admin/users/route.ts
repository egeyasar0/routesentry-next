import { auth } from "@/auth"

export async function GET() {
  const session = await auth()
  if (!session?.user) {
    return Response.json({ error: "unauthorized" }, { status: 401 })
  }
  return Response.json([{ id: 1 }])
}

