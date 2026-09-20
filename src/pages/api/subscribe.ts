import type { APIRoute } from 'astro';

export const prerender = false;

const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

function json(body: Record<string, unknown>, status = 200) {
	return new Response(JSON.stringify(body), {
		status,
		headers: { 'Content-Type': 'application/json', 'Cache-Control': 'no-store' },
	});
}

export const POST: APIRoute = async ({ request }) => {
		let body: Record<string, unknown> = {};
		try {
			const contentType = request.headers.get('content-type') || '';
			body = contentType.includes('application/json')
				? await request.json()
				: Object.fromEntries(await request.formData());
		} catch {
			return json({ message: 'Please enter a valid email address.' }, 400);
		}

		// Quietly discard obvious bot submissions without revealing the honeypot.
		if (typeof body.company === 'string' && body.company.trim()) return json({ ok: true });

		const email = typeof body.email === 'string' ? body.email.trim().toLowerCase() : '';
		if (!emailPattern.test(email)) return json({ message: 'Please enter a valid email address.' }, 400);

		const apiKey = import.meta.env.BENCHMARK_API_KEY;
		const apiBaseUrl = import.meta.env.BENCHMARK_API_BASE_URL?.replace(/\/$/, '');
		const listId = import.meta.env.BENCHMARK_LIST_ID;
		if (!apiKey || !apiBaseUrl || !listId) {
			console.error('Benchmark Email environment variables are not fully configured.');
			return json({ message: 'Newsletter signup is being configured. Please try again soon.' }, 503);
		}

		try {
			const response = await fetch(`${apiBaseUrl}/api/contact`, {
				method: 'POST',
				headers: {
					'X-API-Key': apiKey,
					'Content-Type': 'application/json',
				},
				body: JSON.stringify({
					key: email,
					contactStructureId: '6aabad92bcc5301fb756f6f5',
					lists: [{ _id: listId, action: 'add' }],
				}),
			});

			if (response.ok) {
				return json({ ok: true, message: 'Thanks — you’re on the list.' });
			}

			const providerError = await response.json().catch(() => ({}));
			console.error('Benchmark Email contact creation failed:', response.status, providerError);
			if (response.status === 400 || response.status === 409 || response.status === 422) {
				return json({ message: 'This email could not be added. It may already be on the list.' }, 400);
			}
			return json({ message: 'Unable to subscribe right now. Please try again later.' }, 502);
		} catch (error) {
			console.error('Benchmark Email request failed:', error);
			return json({ message: 'Unable to subscribe right now. Please try again later.' }, 502);
		}
};
