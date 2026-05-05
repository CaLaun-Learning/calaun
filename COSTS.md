# CaLaun Costs

Last updated: 2026-05-04. Production reality, not theoretical pricing.

## What it currently costs to run

**Operational: $0/month.** Everything in production runs on free tiers.

| Service | What it does | Tier | Cost |
|---------|--------------|------|------|
| **Render** Web Service | Django app hosting | Free (sleeps 15min idle) | $0 |
| **Neon** Postgres | Database (DATABASE_URL) | Free (0.5 GB, 100 CU-hr/mo) | $0 |
| **Groq** API | LLM inference for chatbot | Free (~30 req/min) | $0 |
| **Render TLS** | HTTPS for *.onrender.com + custom domain | Free (Let's Encrypt + Google Trust Services) | $0 |
| **Cloudflare** CDN | Edge caching (via Render) | Free (passthrough) | $0 |

**Cold-start trade-off:** the free Render instance sleeps after 15 min of no traffic. First request after sleep takes ~30 s. To remove cold starts, upgrade to Render Starter ($7/mo).

---

## Annual fixed costs (already paid or recurring)

| Item | Provider | Cost | Notes |
|------|----------|------|-------|
| `calaun.org` domain | Namecheap | ~$12/yr | Year-1 paid |
| `rbeauvile@calaun.org` private email | Namecheap Private Email | ~$15/yr ($1.24/mo) | Real send + receive inbox |
| **Annual recurring total** | | **~$27/yr** | |

---

## Scaling estimates

| Daily users | Stack | Monthly cost |
|-------------|-------|--------------|
| 100 | Render free + Neon free + Groq free | **$0** |
| 1,000 | Render Starter ($7) + Neon free + Groq free | **$7** |
| 5,000 | Render Starter ($7) + Neon Launch ($19) + Groq free | **$26** |
| 10,000+ | Render Starter ($7) + Neon Launch ($19) + Groq paid (~$10–20) | **$36–46** |

Scaling triggers:
- **Render Starter ($7/mo)** removes cold starts. Worth it once you have any school partnership or grant.
- **Neon Launch ($19/mo)** at >0.5 GB storage or >100 CU-hr/mo of compute.
- **Groq paid** at >14.4K chatbot requests/day. Token-priced; even at high volume usually <$20/mo.

---

## Non-profit formation costs (one-time, year 1)

This is the path you're starting on — incorporate as a PA non-profit, file IRS Form 1023-EZ for 501(c)(3) status.

| Item | Cost | Notes |
|------|------|-------|
| PA Articles of Incorporation (DSCB:15-5306) | $125 | Pennsylvania Department of State |
| PA newspaper publication notice (15 Pa.C.S. § 1307) | $50–$300 | One general-circulation paper + one legal journal in your county |
| PA charitable solicitation registration (BCO-10) | $15–$250 | Likely $15 in year 1 (revenue-tiered) |
| Registered agent service | $50–$150/yr | E.g., Northwest Registered Agent |
| IRS Form 1023-EZ filing fee | $275 | Approval typically 3–6 weeks |
| EIN | $0 | Free, online, ~10 min |
| Bylaws / COI policy / IP assignment templates | $0 | Free templates from councilofnonprofits.org |
| **D&O insurance** (optional year 1) | $400–$800/yr | Highly recommended |
| **Total year 1, no insurance** | **~$515–$990** | |
| **Total year 1, with insurance** | **~$915–$1,790** | |

---

## Recurring obligations after 501(c)(3) approval

| Item | Cost | Frequency |
|------|------|-----------|
| IRS Form 990-N (e-postcard) | $0 | Annually by May 15 — **3 missed years = automatic loss of 501(c)(3)** |
| PA Annual Report (under PA's 2025 Annual Report Act) | ~$7 | Annually |
| PA charitable solicitation renewal | $15–$250 | Annually |
| Domain renewal | ~$12 | Annually |
| Private Email renewal | ~$15 | Annually |
| Registered agent renewal | $50–$150 | Annually |
| D&O insurance renewal | $400–$800 | Annually |
| **Recurring total** (with insurance) | **~$500–$1,250** | per year |

---

## Donations & grants — operating capital expectations

After 501(c)(3) approval:
- Tax-deductible donations via Stripe non-profit pricing (2.2% + $0.30/transaction)
- Grant targets — see TODO.html § Phase 6 for the priority list and deadlines
- Realistic year-2 funding goal: $5K–$25K from a mix of small individual donors + 1–3 small grants (state DOE, MAA Tensor-SUMMA, local family foundations)

---

## Recommended path

1. **Now (free)**: keep operational stack as-is. $0/mo runs the live site.
2. **Once 501(c)(3) approves**: upgrade Render to Starter ($7/mo) for no cold starts — schools and funders see a snappy site.
3. **As traffic grows**: add Neon Launch ($19/mo) only when you actually hit storage or compute limits. Don't pre-pay.

Total realistic year-1 budget: **~$1,000–$2,000** (formation + ~6 months of paid Render Starter).
