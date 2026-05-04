# Deployment Costs

## Hosting Options
| Platform | Free Tier | Paid |
|----------|-----------|------|
| **Railway** | ❌ | $5/mo (Hobby) |
| **Render** | ✅ (sleeps after 15min) | $7/mo |
| **Fly.io** | ✅ ($5 credit) | ~$2-5/mo |

## AI Chatbot (Groq)
| Tier | Cost | Limits |
|------|------|--------|
| **Free** | $0 | 30 req/min, 14.4K req/day |
| **Paid** | $0.05-0.08/1M tokens | Unlimited |

---

## Monthly Cost Scenarios

### 🆓 All Free (~100 users/day)
| Service | Cost |
|---------|------|
| Render (free) | $0 |
| Groq (free tier) | $0 |
| **Total** | **$0** |

*Drawback: 30s cold start on Render*

---

### ⚡ Fast Hosting + Free AI (~100 users/day)
| Service | Cost |
|---------|------|
| Railway (Hobby) | $5 |
| Groq (free tier) | $0 |
| **Total** | **$5/mo** |

*Best value - no cold starts, free AI*

---

### 🚀 All Paid (~1,000 users/day)
| Service | Cost |
|---------|------|
| Railway (Hobby) | $5 |
| Groq (paid) | ~$1.75 |
| **Total** | **~$7/mo** |

---

### 💰 High Traffic (~10,000 users/day)
| Service | Cost |
|---------|------|
| Railway (Hobby) | $5 |
| Groq (paid) | ~$17.50 |
| **Total** | **~$23/mo** |

---

## Recommendation
Start with **Railway ($5) + Groq Free** — upgrade Groq only if you hit rate limits.

---

## Railway Setup

### 1. Deploy
1. Go to [railway.app](https://railway.app)
2. **New Project** → **Deploy from GitHub repo**
3. Select `beauvilerobed/calc-tutor-bot` → branch `production-ready`

### 2. Add Environment Variables
Click your service → **Variables** → **Add**:
```
SECRET_KEY=<generate with: python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())">
DEBUG=False
ALLOWED_HOSTS=.up.railway.app
GROQ_API_KEY=gsk_your_key_here
```

### 3. Get Domain
1. Click service → **Settings** → **Networking**
2. Click **Generate Domain**
3. (Optional) Click domain to customize subdomain name

### 4. Update ALLOWED_HOSTS
After customizing domain, update variable:
```
ALLOWED_HOSTS=yourname.up.railway.app
```

**Done!** App live in ~2-3 minutes.
