export default function handler(req, res) {
  if (!session) return res.status(401).end();
  return res.status(200).json({ ok: true });
}

