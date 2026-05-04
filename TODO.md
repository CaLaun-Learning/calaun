# TODO

## Wire up the Sponsor button

The footer "❤️ Sponsor" link (in `templates/index.html`) and the **Sponsors** section in `README.md` both point to `https://github.com/sponsors/beauvilerobed`. As of 2026-05-04 that URL 302-redirects to the GitHub profile because GitHub Sponsors enrollment isn't set up yet.

Pick one path:

### Option A — GitHub Sponsors (no code change once approved)
1. Go to https://github.com/sponsors → **Set up GitHub Sponsors**.
2. Choose Personal or Organization, complete identity verification + Stripe payout setup, define tiers.
3. Submit for review — approval typically takes a few business days.
4. Once approved, the existing URL just works. Done.

### Option B — PayPal (live within minutes)
Pick a format and swap it into both places:
- **PayPal.Me** — claim a handle at https://paypal.me (~30 s) → URL is `https://paypal.me/<handle>`.
- **PayPal Donate button** — generate at https://www.paypal.com/donate/buttons (~5 min, needs a PayPal account) → URL is `https://www.paypal.com/donate?hosted_button_id=XXXXXXXXXX`.

Then update:
- `templates/index.html` — the `<li><a href="...">❤️ Sponsor</a></li>` near the bottom of the footer.
- `README.md` — the "Sponsors" section link.

### Other alternatives considered
Open Collective (good for non-profits w/ fiscal host), Ko-fi, Buy Me A Coffee, Stripe Payment Link.
