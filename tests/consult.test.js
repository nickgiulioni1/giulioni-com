const { test } = require('node:test');
const assert = require('node:assert/strict');
const { Readable } = require('node:stream');
const { createHandler } = require('../api/consult.js');
const fields = { name: 'Sample Visitor', email: 'visitor@example.test', phone: '202-555-0147', intent: 'Buy', consent: 'yes', source: 'contact', company_website: '' };
const env = Object.fromEntries(['RESEND_API_KEY', 'NOTIFY_EMAIL_TO', 'NOTIFY_EMAIL_FROM', 'QUO_API_KEY', 'QUO_FROM_NUMBER', 'NOTIFY_SMS_TO'].map(k => [k, 'test-value']));
async function submit(handler, values = {}, options = {}) {
  const req = Readable.from([new URLSearchParams({ ...fields, ...values }).toString()]);
  req.method = options.method || 'POST';
  req.headers = { 'content-type': 'application/x-www-form-urlencoded', ...options.headers };
  if ('body' in options) req.body = options.body;
  const headers = {};
  const res = { setHeader: (k,v) => { headers[k] = v; }, end() {} };
  await handler(req, res);
  assert.equal(res.statusCode, 303);
  assert.equal(headers['Cache-Control'], 'no-store');
  return headers.Location;
}
function setup(extra = {}) {
  const calls = [], logs = [];
  const handler = createHandler({ env, log: (...v) => logs.push(v), fetcher: async (url, request) => { calls.push({ url, ...JSON.parse(request.body) }); return { ok: true }; }, ...extra });
  return { handler, calls, logs };
}
test('honeypot accepts silently without notifications', async () => { const { handler, calls } = setup(); assert.equal(await submit(handler, { company_website: 'filled' }), '/contact/thanks/'); assert.equal(calls.length, 0); });
test('required consent fails closed', async () => { const { handler, calls } = setup(); assert.equal(await submit(handler, { consent: '' }), '/contact/error/'); assert.equal(calls.length, 0); });
test('valid input sends email and text with reply address and source', async () => { const { handler, calls, logs } = setup(); assert.equal(await submit(handler), '/contact/thanks/'); assert.equal(calls.length, 2); assert.equal(calls[1].url, 'https://api.quo.com/v1/messages'); assert.equal(calls[0].reply_to, fields.email); assert.match(calls[0].text, /Source: contact/); assert.match(calls[1].content, /Sample Visitor: Buy, contact/); assert.equal(logs.length, 1); assert.equal(logs[0][1], 'sent'); });
test('missing configuration sends nothing', async () => { const { handler, calls, logs } = setup({ env: {} }); assert.equal(await submit(handler), '/contact/error/'); assert.equal(calls.length, 0); assert.equal(logs[0][1], 'notifications not configured'); });
test('email failure is an error and skips text', async () => { let n=0; const { handler } = setup({ fetcher: async () => { n++; return { ok: false }; } }); assert.equal(await submit(handler), '/contact/error/'); assert.equal(n, 1); });
test('text failure preserves successful email', async () => { let n=0; const { handler } = setup({ fetcher: async () => { if (++n === 2) throw Error('offline'); return { ok: true }; } }); assert.equal(await submit(handler), '/contact/thanks/'); });
test('body size, fields and content type are enforced', async () => { const { handler, calls } = setup(); for (const input of [{ name:'' }, { email:'invalid' }, { phone:'123' }, { message:'x'.repeat(2001) }, { source:'unknown' }, { source:'sell-or-rent-home', intent:'Sell or rent review' }]) assert.equal(await submit(handler,input), '/contact/error/'); assert.equal(await submit(handler, {}, { headers: { 'content-type':'application/json' } }), '/contact/error/'); assert.equal(await submit(handler, {message:'x'.repeat(11000)}), '/contact/error/'); assert.equal(await submit(handler, {}, {method:'GET'}), '/contact/error/'); assert.equal(calls.length,0); });
test('parsed Vercel bodies work and arrays are rejected', async () => { const {handler}=setup(); assert.equal(await submit(handler,{}, {body:fields}),'/contact/thanks/'); assert.equal(await submit(handler,{}, {body:{...fields,intent:['Buy','Sell']}}),'/contact/error/'); });
test('rate limit resets after window', async () => { let time=0; const {handler,calls}=setup({now:()=>time}); for(let i=0;i<5;i++) assert.equal(await submit(handler),'/contact/thanks/'); assert.equal(await submit(handler),'/contact/error/'); time=600001; assert.equal(await submit(handler),'/contact/thanks/'); assert.equal(calls.length,12); });

test('unconfigured requests never consume the configured limit', async () => {
  const config = {};
  const { handler, calls, logs } = setup({ env: config });
  for (let i = 0; i < 8; i++) assert.equal(await submit(handler), '/contact/error/');
  assert.equal(calls.length, 0);
  assert.ok(logs.every(entry => entry[1] === 'notifications not configured'));
  Object.assign(config, env);
  assert.equal(await submit(handler), '/contact/thanks/');
});
