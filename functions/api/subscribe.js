// Cloudflare Pages Function mirroring src/pages/api/subscribe.ts (used on Vercel).
// Env vars (set in the Pages project): BENCHMARK_API_KEY, BENCHMARK_API_BASE_URL, BENCHMARK_LIST_ID.
const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

const json = (body, status = 200) =>
  new Response(JSON.stringify(body), {
    status,
    headers: { "Content-Type": "application/json", "Cache-Control": "no-store" },
  });

export async function onRequestPost({ request, env }) {
  let body = {};
  try {
    const type = request.headers.get("content-type") || "";
    body = type.includes("application/json")
      ? await request.json()
      : Object.fromEntries(await request.formData());
  } catch {
    return json({ message: "Please enter a valid email address." }, 400);
  }

  if (typeof body.company === "string" && body.company.trim()) return json({ ok: true });

  const email = typeof body.email === "string" ? body.email.trim().toLowerCase() : "";
  if (!emailPattern.test(email)) return json({ message: "Please enter a valid email address." }, 400);

  const apiKey = env.BENCHMARK_API_KEY;
  const apiBaseUrl = env.BENCHMARK_API_BASE_URL?.replace(/\/$/, "");
  const listId = env.BENCHMARK_LIST_ID;
  if (!apiKey || !apiBaseUrl || !listId) {
    return json({ message: "Newsletter signup is being configured. Please try again soon." }, 503);
  }

  try {
    const res = await fetch(`${apiBaseUrl}/api/contact`, {
      method: "POST",
      headers: { "X-API-Key": apiKey, "Content-Type": "application/json" },
      body: JSON.stringify({
        key: email,
        contactStructureId: "6aabad92bcc5301fb756f6f5",
        lists: [{ _id: listId, action: "add" }],
      }),
    });
    if (res.ok) return json({ ok: true, message: "Thanks — you’re on the list." });
    if ([400, 409, 422].includes(res.status)) {
      return json({ message: "This email could not be added. It may already be on the list." }, 400);
    }
    return json({ message: "Unable to subscribe right now. Please try again later." }, 502);
  } catch {
    return json({ message: "Unable to subscribe right now. Please try again later." }, 502);
  }
}
