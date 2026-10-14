# Ahmed Imran Kabir — Noir Academic Portfolio

Static portfolio with daily Google Scholar synchronization via GitHub Actions and SerpApi. Original portrait and design are retained.

## Publish

1. Create a **public GitHub repository** and upload the **contents** of this folder to the repository root (including `.github/workflows`).
2. In repository **Settings → Secrets and variables → Actions**, create a repository secret named `SERPAPI_KEY` with your own [SerpApi](https://serpapi.com/) API key. A subscription or credits may be needed for daily requests and pagination.
3. In **Actions**, enable workflows if prompted. Open **Sync Google Scholar** → **Run workflow** to perform the first synchronization.
4. In **Settings → Pages**, choose **Deploy from a branch**, branch `main`, folder `/ (root)`, then save. If your default branch is not `main`, select its actual name.
5. Visit the GitHub Pages URL after deployment. Updates occur at approximately 03:17 UTC daily (GitHub may delay scheduled workflows).

## How it works

- `scripts/sync_scholar.py` fetches Google Scholar author profile `1OWW__EAAAAJ` using SerpApi's `google_scholar_author` endpoint, paginating publication results.
- `.github/workflows/sync-scholar.yml` runs daily and on demand, committing refreshed `data/scholar.json` only when valid data was returned.
- `index.html` reads that JSON in the browser. If unavailable, résumé metrics and bibliography remain visible.
- `data/publications.json` preserves the original manually compiled résumé bibliography and its DOI/publisher links. Scholar discoveries are appended rather than replacing those links.
- Metrics are Google Scholar metrics, **not** Scopus metrics. Publication matching is title-based and should be reviewed for variants or duplicates.

## Notes

Google Scholar has **no official public API**. SerpApi is a third-party provider, may have charges/rate limits, and can change its response format. GitHub Pages itself is static; the scheduled GitHub Action performs the refresh. Do **not** put your API key in HTML or commit it to the repository. New Scholar papers appear only after Scholar indexes them and the next successful sync. The 2027 book chapter in the résumé remains in the manual bibliography regardless of Scholar indexing.

To run locally: `python -m http.server 8000` from this directory, then open http://localhost:8000. To trigger an update locally: set `SERPAPI_KEY` in your environment and run `python scripts/sync_scholar.py`.
