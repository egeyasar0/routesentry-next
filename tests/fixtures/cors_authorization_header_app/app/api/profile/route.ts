export async function POST() {
  const headers = { "Access-Control-Allow-Headers": "Content-Type, Authorization" }
  return Response.json({ ok: true }, { headers })
}

