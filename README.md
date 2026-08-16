# Above & Beyond Fitness — website

Single self-contained page. `index.html` includes all styles, scripts, and photos inline (~1.3 MB); no build step.

## Deploy to GitHub Pages

1. Create a new **public** repo, e.g. `elliebfit-site`.
2. Upload `index.html` and `CNAME` to the repo root (drag-and-drop works: **Add file → Upload files**).
3. **Settings → Pages** → Source: *Deploy from a branch* → Branch: `main`, folder `/ (root)` → Save.
4. Wait ~1 minute, then check `https://<username>.github.io/elliebfit-site/` — the site should load.

## Point elliebfit.com at it

The domain is currently pointed at Google Sites, so DNS records must be changed at the domain registrar (likely Google Domains → now Squarespace Domains, or wherever the domain is managed).

1. **Settings → Pages → Custom domain**: enter `www.elliebfit.com`, Save. (The `CNAME` file already declares this.)
2. At the registrar, edit DNS:
   - Delete the existing Google Sites records (a `CNAME` for `www` pointing to `ghs.googlehosted.com`, and any `A` records for the apex used by Sites).
   - Add `CNAME` — host `www` → value `<username>.github.io`
   - For the bare domain `elliebfit.com`, add four `A` records to:
     `185.199.108.153`, `185.199.109.153`, `185.199.110.153`, `185.199.111.153`
     (and optionally the AAAA equivalents `2606:50c0:8000::153`, `…8001::153`, `…8002::153`, `…8003::153`)
3. Back in **Settings → Pages**, wait for the DNS check to pass, then tick **Enforce HTTPS** (certificate issuance can take up to an hour).
4. In Google Sites, **unpublish** the old site so it can't be served or indexed.

DNS propagation is usually minutes but can take up to 24 hours.

## Updating

Re-export the design and replace `index.html` in the repo — Pages redeploys automatically.
