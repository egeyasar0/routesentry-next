export default function handler(req, res) {
  if (req.method !== "POST") return res.status(405).end();
  db.orders.create(req.body);
  return res.status(200).json({ ok: true });
}

