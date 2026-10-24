const [action, value, cursor] = process.argv.slice(2);
const base = process.env.SOCAI_API_BASE_URL?.replace(/\/$/, '');
const key = process.env.SOCAI_API_KEY;
if (!base || !key || !value) throw new Error('Set SOCAI_API_BASE_URL and SOCAI_API_KEY; use create/get/records/cancel and a value.');
const headers: Record<string, string> = { Authorization: `Bearer ${key}`, 'Content-Type': 'application/json' };
let path = '/responses', method = 'GET', body: string | undefined;
if (action === 'create') {
  if (!process.env.SOCAI_IDEMPOTENCY_KEY) throw new Error('Set a stable SOCAI_IDEMPOTENCY_KEY for creation.');
  headers['Idempotency-Key'] = process.env.SOCAI_IDEMPOTENCY_KEY;
  method = 'POST'; body = JSON.stringify({ model: 'socai-research', background: true, input: value });
} else {
  if (!/^resp_[A-Za-z0-9_-]+$/.test(value)) throw new Error('Use a Response ID returned by create.');
  path += `/${value}`;
  if (action === 'records') {
    const query = new URLSearchParams({ limit: '20' });
    if (cursor) query.set('cursor', cursor);
    path += `/records?${query}`;
  } else if (action === 'cancel') { method = 'POST'; path += '/cancel'; }
  else if (action !== 'get') throw new Error('Use create, get, records or cancel.');
}
try {
  const response = await fetch(base + path, { method, headers, body, redirect: 'error', signal: AbortSignal.timeout(30000) });
  if (!response.ok) throw new Error(`HTTP ${response.status}; request ID: ${response.headers.get('X-Request-ID') ?? 'unavailable'}`);
  console.log(await response.text());
} catch (error) {
  console.error(String(error instanceof Error ? error.message : error).replaceAll(key, '[redacted]')); process.exitCode = 1;
}
