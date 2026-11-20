const { randomUUID } = require('node:crypto');
const MAX_BODY = 10 * 1024;
const WINDOW = 10 * 60 * 1000;
const INTENTS = new Set(['Buy', 'Sell', 'Both', 'Sell or rent review', 'Not sure']);
const SOURCES = new Set(['contact', 'home', 'sell', 'buy', 'about', 'areas', 'area-carmel', 'area-westfield', 'area-fishers', 'sell-or-rent-home', 'sell-or-rent-sell']);
const ENV = ['RESEND_API_KEY', 'NOTIFY_EMAIL_TO', 'NOTIFY_EMAIL_FROM', 'QUO_API_KEY', 'QUO_FROM_NUMBER', 'NOTIFY_SMS_TO'];

function createHandler({ env = process.env, fetcher = globalThis.fetch, now = Date.now, log = console.log } = {}) {
  const limits = new Map();
  return async function consult(req, res) {
    const id = randomUUID();
    const finish = (success, status) => {
      log(id, status);
      res.setHeader('Cache-Control', 'no-store');
      res.setHeader('Location', success ? '/contact/thanks/' : '/contact/error/');
      res.statusCode = 303;
      res.end();
    };
    if (req.method !== 'POST' || !/^application\/x-www-form-urlencoded(?:\s*;.*)?$/i.test(req.headers['content-type'] || '')) return finish(false, 'invalid request');
    try {
      if (Number(req.headers['content-length']) > MAX_BODY) return finish(false, 'body too large');
      let raw = req.body;
      if (raw === undefined) {
        let size = 0;
        const chunks = [];
        for await (const chunk of req) {
          const bytes = Buffer.from(chunk);
          size += bytes.length;
          if (size > MAX_BODY) return finish(false, 'body too large');
          chunks.push(bytes);
        }
        raw = Buffer.concat(chunks);
      }
      if (Buffer.isBuffer(raw)) raw = raw.toString('utf8');
      if (typeof raw === 'object' && raw !== null) {
        if (Object.values(raw).some(value => typeof value !== 'string')) return finish(false, 'invalid fields');
        raw = new URLSearchParams(raw).toString();
      }
      if (typeof raw !== 'string' || Buffer.byteLength(raw) > MAX_BODY) return finish(false, 'invalid body');
      const params = new URLSearchParams(raw);
      if ([...new Set(params.keys())].some(key => params.getAll(key).length !== 1)) return finish(false, 'duplicate fields');
      if ((params.get('company_website') || '').trim()) return finish(true, 'ignored');
      const data = Object.fromEntries([...params].map(([key, value]) => [key, value.trim()]));
      const lengths = { name: 100, email: 254, phone: 40, location: 300, intent: 40, message: 2000, source: 50, consent: 3 };
      if (Object.entries(lengths).some(([key, max]) => (data[key] || '').length > max)) return finish(false, 'invalid fields');
      if (!data.name || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(data.email || '') || /[\r\n]/.test(data.name + data.email + data.phone) || !/^[+()\d\s.\-]+$/.test(data.phone || '') || !/^\d{10,11}$/.test((data.phone || '').replace(/\D/g, '')) || data.consent !== 'yes' || !INTENTS.has(data.intent) || !SOURCES.has(data.source)) return finish(false, 'invalid fields');
      if (data.source.startsWith('sell-or-rent-') && (!data.location || data.intent !== 'Sell or rent review')) return finish(false, 'address required');
      if (ENV.some(key => !env[key])) return finish(false, 'notifications not configured');
      const time = now();
      for (const [key, bucket] of limits) if (time - bucket.start >= WINDOW) limits.delete(key);
      const ip = req.headers['x-vercel-forwarded-for'] || req.headers['x-forwarded-for'] || req.socket?.remoteAddress || 'unknown';
      const bucket = limits.get(ip) || { start: time, count: 0 };
      if (bucket.count >= 5 || (!limits.has(ip) && limits.size >= 10000)) return finish(false, 'rate limited');
      bucket.count += 1;
      limits.set(ip, bucket);
      const received = new Intl.DateTimeFormat('en-US', { dateStyle: 'full', timeStyle: 'long', timeZone: 'America/Indianapolis' }).format(new Date(time));
      const text = ['Name: ' + data.name, 'Email: ' + data.email, 'Phone: ' + data.phone, 'City or address: ' + (data.location || ''), 'Intent: ' + data.intent, 'Message: ' + (data.message || ''), 'Consent: yes', 'Source: ' + data.source, 'Received: ' + received].join('\n');
      const email = await fetcher('https://api.resend.com/emails', { method: 'POST', signal: AbortSignal.timeout(8000), headers: { Authorization: 'Bearer ' + env.RESEND_API_KEY, 'Content-Type': 'application/json' }, body: JSON.stringify({ from: env.NOTIFY_EMAIL_FROM, to: [env.NOTIFY_EMAIL_TO], reply_to: data.email, subject: 'Consult request: ' + data.intent + ', ' + data.source, text }) });
      if (!email.ok) return finish(false, 'email failed');
      try {
        const sms = await fetcher('https://api.quo.com/v1/messages', { method: 'POST', signal: AbortSignal.timeout(5000), headers: { Authorization: env.QUO_API_KEY, 'Content-Type': 'application/json' }, body: JSON.stringify({ from: env.QUO_FROM_NUMBER, to: [env.NOTIFY_SMS_TO], content: `${data.name}: ${data.intent}, ${data.source}, ${data.phone}` }) });
        return finish(true, sms.ok ? 'sent' : 'email sent; text failed');
      } catch { return finish(true, 'email sent; text failed'); }
    } catch { return finish(false, 'request failed'); }
  };
}
module.exports = createHandler();
module.exports.createHandler = createHandler;
