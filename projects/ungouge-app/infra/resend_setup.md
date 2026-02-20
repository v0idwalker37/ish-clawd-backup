Resend SMTP / Deliverability Setup

Recommendation: Use Resend (https://resend.com) for quick API-based transactional email. It's fast to set up and developer-friendly.

Steps:
1. Create Resend account and copy API key (RESEND_API_KEY). Keep this secret.
2. In Resend dashboard, add your sending domain: ungouge.ai
3. Resend will provide DNS records (DKIM and CNAME/TXT) for domain verification. Add these to Cloudflare.

Typical DNS records you will see:
- TXT (SPF): v=spf1 include:spf.resend.com ~all
- TXT (DKIM selector): <selector>._domainkey.ungouge.ai  TXT  "v=DKIM1; k=rsa; p=..."
- CNAME (verification) or TXT for domain verification

Example test curl (send an email with Resend API):

curl https://api.resend.com/emails \
  -H "Authorization: Bearer $RESEND_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "from": "Hello <hello@ungouge.ai>",
    "to": ["jason@example.com"],
    "subject": "Resend test",
    "html": "<strong>It works!</strong>"
  }'

Deliverability notes
- Add SPF record in Cloudflare: (example above)
- Add DKIM keys provided by Resend; they ensure authenticity
- Add DMARC TXT policy if you want: v=DMARC1; p=none; rua=mailto:postmaster@ungouge.ai

If you want, I can generate the exact DNS records once you add ungouge.ai to Resend and paste the returned DKIM/verification strings here for me to write to Cloudflare.
