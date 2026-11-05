# LinkedIn research, November 2026

What the checklist in [README.md](README.md) rests on, and how strong each source is. Most
"LinkedIn best practice" is vendor opinion without a published method; this file marks which is which.

## From LinkedIn itself

- The 2026 feed retrieves and ranks with LLM-based models and filters engagement bait and
  repetitive, click-driven posts:
  [Social Media Today](https://www.socialmediatoday.com/news/linkedin-updates-its-feed-algorithm/814638/),
  [ppc.land](https://ppc.land/linkedin-rebuilds-its-feed-from-scratch-with-llms-and-gpu-powered-ranking/),
  [ZenML summary of the engineering post](https://www.zenml.io/llmops-database/next-generation-feed-ranking-with-llms-and-sequential-transformers).
- Collaborative posts (up to 5 collaborators, invite and accept, public posts only, the creator keeps control):
  [LinkedIn announcement](https://news.linkedin.com/2026/introducing-collaborative-posts-now-available-to-members-and-company-pages-on-linkedin),
  [Buffer](https://buffer.com/resources/linkedin-collab-posts/),
  [ppc.land](https://ppc.land/linkedin-caps-collaborative-posts-at-five-and-blocks-page-engagement-metrics/).

## Vendor and practitioner studies (directional)

- Links in the body cost reach (estimates 30 to 60%); some say the penalty softened in late 2025, and
  others warn that "link in first comment" is throttled too:
  [Agility PR](https://www.agilitypr.com/pr-news/social-media-influencer-marketing/the-linkedin-link-tax-why-sharing-your-blog-is-costing-you-60-percent-of-your-audience/),
  [SocialPilot](https://www.socialpilot.co/?p=694640),
  [viralbrain](https://www.viralbrain.ai/blog/linkedin-growth-hacks-2026-tactics-that-work?page=7).
  Disputed; AJ chose the first comment.
- Comments, dwell time and saves count more than likes; carousels and multi-image posts hold attention:
  [Webtures](https://www.webtures.com/insights/linkedin-algorithm-2026/), SocialPilot.
- Hook, length (about 1,300 to 1,800 characters), short paragraphs, 0 to 3 hashtags; the studies
  conflict on exact numbers and publish no method:
  [stan.store six-month study](https://stan.store/blog/linkedin-engagement/),
  [dev.to 50,000-post analysis](https://dev.to/olams/i-analyzed-50000-linkedin-posts-heres-what-actually-gets-engagement-56l9),
  [ligosocial hooks](https://ligosocial.com/en/blog/linkedin-post-hooks-30-first-line-formulas).

## Gemini (agy) sweep, 2026-11-05

A 12-topic sweep run on Gemini through agy. Treat it as a lead: its checklist agrees with the
sources above on hook, length, bait, hashtags, alt text and old posts, and adds square images,
timing and the first hour. Its source labels are its own and were not all checked.

## Concise Checklist: Do / Don't Guide for Researchers

| Practice | Recommendation | Operational Rule | Primary Source |
| :--- | :---: | :--- | :--- |
| **The Hook** | **DO** | Keep the core technical punchline within **140 characters**; avoid blank line breaks before the mobile fold. | [AuthoredUp](https://authoredup.com) `[Empirical]` |
| **Boilerplate** | **DON'T** | Never open with *"I am thrilled/humbled to announce..."*. | [Entrepreneur / Dan Roth](https://www.entrepreneur.com/growing-a-business/linkedin-feed-algorithm-dan-roth/454516) `[Official]` |
| **Post Length** | **DO** | Aim for **1,200 to 1,800 characters** (~200 words) with clear spacing and bullet points. | [Buffer](https://buffer.com/resources/linkedin-algorithm/) `[Empirical]` |
| **Outbound Links** | **DO** | Place links at the bottom of the body text and **manually dismiss the link preview card**. | [AuthoredUp](https://authoredup.com) `[Empirical]` |
| **Link Hacks** | **DON'T** | Do not use "Link in comment #1" or edit the post 15 mins later to slip in a link (triggers reach throttling). | [Just Connecting](https://justconnecting.nl) `[Empirical]` |
| **Visual Media** | **DO** | Use **6–10 slide PDF Carousels** (Visual Abstracts) for maximum dwell time and saves. | [Just Connecting](https://justconnecting.nl) `[Empirical]` |
| **Multi-Images** | **DO** | Format all images as **1:1 square (1200x1200px)**; Image #1 dictates the entire collage crop. | [Reachly](https://reachly.co) `[Empirical]` |
| **Tagging People** | **DON'T** | Never tag >5 people; avoid tagging anyone who won't engage (non-engagement incurs a 20–50% penalty). | [Just Connecting](https://justconnecting.nl) `[Empirical]` |
| **Tagging Orgs** | **DO** | Tag lab pages, university departments, funding agencies, and conferences (no non-engagement drag). | [LinkedIn Policy](https://www.linkedin.com) `[Official]` |
| **Hashtags** | **DON'T** | Do not use >3 hashtags or inline hashtags (feeds are deprecated; LLM reads body text). | [LinkedIn Product](https://www.linkedin.com) `[Official UI]` |
| **Closing Prompt** | **DO** | Ask a specific, technical question that invites long-form peer discussion (>15 words). | [Just Connecting](https://justconnecting.nl) `[Empirical]` |
| **Engagement Bait** | **DON'T** | Never use *"Agree?"*, *"Thoughts?"*, or reaction polls (*"Like for X, Clap for Y"*). | [LinkedIn Newsroom](https://www.linkedin.com/pulse/how-linkedin-improving-feed-show-more-relevant-authentic-content) `[Official]` |
| **Timing** | **DO** | Post **Tuesday–Thursday between 8:00 AM – 9:00 AM ET** for optimal global academic reach. | [Sprout Social](https://sproutsocial.com/insights/best-times-to-post-on-social-media/) `[Empirical]` |
| **The Golden Hour** | **DO** | Monitor the post for the first 60 minutes; reply to early comments with substantive thoughts. | [LinkedIn Engineering](https://arxiv.org/abs/2404.03848) `[Official Paper]` |
| **Accessibility** | **DO** | Add descriptive Alt Text (120–300 chars) explaining charts and transcribing text in graphics. | [LinkedIn Help](https://www.linkedin.com/help/linkedin/answer/a549977) `[Official]` |
| **Old Posts** | **DON'T** | Do not edit old posts expecting revived impressions (it does not bump the post). | [LinkedIn Preview](https://linkedinpreview.com) `[Empirical]` |
| **Past Errata** | **DO** | Edit past posts only to fix broken URLs, correct scientific inaccuracies, or add formal update notes. | Professional Integrity Standard |
