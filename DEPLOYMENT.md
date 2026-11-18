# Deployment

Repository: `nickgiulioni1/giulioni-com`. Existing Vercel project: `giulioni-com`, in `nick-giulionis-projects`, project ID `prj_v6dRhb9H3UQQ5CGzQLM8nblLIuib`.

Do not merge or deploy without Nick's yes. This rebuild is approved for a preview only. Do not alter production domains, project settings, or environment variables. Vercel Git deployments are disabled in `vercel.json`. Build locally on Omarchy with `vercel build`, then publish the preview with `vercel deploy --prebuilt` (never use the production flag). After any `vercel pull`, remove `.vercel` when the work is finished. Do not commit local deployment files.

## Notification configuration, left unset

No Resend or Quo accounts or API keys are created by this change. Before live notifications can work, Nick must authorize configuration of:

| Variable | Requirement |
| --- | --- |
| `RESEND_API_KEY` | Resend account and email-sending API key |
| `NOTIFY_EMAIL_TO` | Nick’s public email, nick@giulioni.com |
| `NOTIFY_EMAIL_FROM` | A sender on giulioni.com verified in Resend |
| `QUO_API_KEY` | Quo account with API access and text messaging configured |
| `QUO_FROM_NUMBER` | The business line, +14632239952 |
| `NOTIFY_SMS_TO` | Nick’s destination number, entered only by Nick in Vercel |

No secret values belong in the repository. Until all six variables exist, submissions redirect to `/contact/error/` and record only a request ID and `notifications not configured`. Honeypot submissions silently redirect to thanks without notifications. Successful email delivery redirects to thanks even if text delivery fails. Live delivery testing needs Nick’s go-ahead and is not performed with unset credentials.

API references: [Resend email API](https://resend.com/docs/api-reference/emails/send-email) and [Quo text API](https://www.quo.com/docs/mdx/api-reference/messages/send-a-text-message).

## Required dashboard action before live form use

Nick or Site DRI must turn on a Vercel Firewall rate-limit rule in the dashboard for POST requests to `/api/consult`: limit by client IP, five requests per ten minutes, blocking further requests. Check plan availability before activating; no paid feature is authorized here. The function’s in-memory limit is best effort per running instance and does not replace this rule. This PR does not change dashboard settings.

## Future embedded review

The sell-or-rent wrapper currently contains only the native fallback form. A separately approved change can replace it with a Lifecycle iframe and change only CSP `frame-src` to the approved embed origin. That service must allow `https://giulioni.com` in its own `frame-ancestors` policy. Our pages retain `frame-ancestors 'none'`; www redirects to the apex.
