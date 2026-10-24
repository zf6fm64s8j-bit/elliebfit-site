# Live search and AI ingestion audit — October 24, 2026

The live site has a sound technical foundation for discovery and accurate extraction. No material
crawl or metadata blockers were found after the three corrections below. This is technical readiness,
not evidence of indexing, citations, ranking or recommendations.

## Verified live

| Area | Evidence |
|---|---|
| Sitemap | All 16 canonical indexable URLs return 200; absolute HTTPS www URLs, no duplicates; last-modified dates match this release. Utility/noindex pages and drafts are excluded. |
| Canonical identity | All 16 canonical and Open Graph URLs match their published URLs. HTTP and bare-domain requests resolve to HTTPS www. |
| Crawl access | robots.txt permits crawling and names the sitemap. Googlebot, Bingbot, OAI-SearchBot, PerplexityBot and Claude-SearchBot user-agent probes received identical 200 homepage HTML. These are probes, not authenticated bot visits. |
| Readable content | Main business facts and substantial homepage copy are available without JavaScript; standalone pages expose normal HTML headings, text and links. |
| Business and trainer | Stable business, Ellen and website entity IDs connect services to Above & Beyond Fitness. Credentials, prices and Cave Creek / Scottsdale / Northeast Phoenix service wording agree with approved visible copy. Virtual availability is distinguished from in-home coverage. |
| Questions and answers | All 24 guide FAQ pairs match their visible answers and structured data. Medical boundaries and consultation qualifications remain visible. |
| Summaries and links | Titles, descriptions, Open Graph URLs, guide hub and internal navigation align with the current content. llms.txt links exactly the same 16 public canonical pages as the sitemap. |
| Publication boundary | All 66 served files match the production build. Nine missing/private-source probes return 404. No preview controls are present on the 16 indexable pages. |

## Corrections deployed

1. The business logo now references the actual 512px brand icon; the portrait remains the social image.
2. Older-adult guide schema and breadcrumb names now match its location-neutral heading.
3. The free-class service in the business offer catalog now links to its signup page.

Published revision: `1dd986d895b607680c80423b6b804c7df82fe3e2`.
[Successful deployment](https://github.com/zf6fm64s8j-bit/elliebfit-site/actions/runs/40141184289).
Fresh live file, page, redirect and exposure checks passed after deployment; rendered-browser checks
confirmed the business logo metadata and older-adult guide heading/schema identity.

Independent read-only reviewers Claude Opus and OpenRouter meta/muse-wonder both passed the audit.
Their findings were adjudicated locally; the optional catalog URL improvement was adopted.
Council receipt: `council-2026-10-24T23-03-05-543Z-55842-5f711c88.json` (local council audit store).
Detailed crawl receipts are in the machine-local dev-data/elliebfit-site/post-launch-audit folder.

## Interpretation and remaining work

Google says ordinary search fundamentals apply to AI features, with no special AI schema required;
it ignores llms.txt. Keep that file as a useful optional summary, rather than a ranking mechanism.
See [Google AI optimization guidance](https://developers.google.com/search/docs/fundamentals/ai-optimization-guide).

OpenAI distinguishes its search crawler from its training crawler. Search availability does not require
allowing training. Current site rules permit both; this audit did not change that policy.
See [OpenAI crawler documentation](https://developers.openai.com/api/docs/bots).
[Perplexity](https://docs.perplexity.ai/docs/resources/perplexity-crawlers) and
[Anthropic](https://support.claude.com/en/articles/8896518-does-anthropic-crawl-data-from-the-web-and-how-can-site-owners-block-the-crawler)
also document their search and user-request crawlers. User-agent probes alone do not prove real crawler access.

The highest-value next checks require evidence beyond public page fetching:

- Inspect existing Google Search Console and Bing Webmaster Tools properties: sitemap acceptance,
  URL indexing, crawl issues and relevant search/AI inclusion settings. No account status was verified.
- Confirm business-listing facts and service areas; confirm Ellen's exact active PWR directory URL
  before linking it. No listing changes or directory activation were performed.
- Establish a small repeatable buyer-question panel and measure actual citations, factual accuracy
  and qualified inquiries over time. No assistant recommendation or ranking guarantee is implied.

This audit does not establish Google rich-result eligibility, real-bot traffic, field performance data,
or form delivery. It does not add a private street address, inferred credentials or artificial reviews.
