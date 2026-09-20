# New Article Upload Checklist — objectbrief.com

> This file is a hard gate for ANYONE (Hermes, Codex, or other AI agents) uploading a new
> article to this repo. Run the check script before every commit/push. Do not skip it.
> 文档同时供人与 AI 使用；脚本失败则禁止 push。

## 1. Affiliate disclosure（必须逐字统一）

Every article containing Alibaba affiliate tables MUST include, before the first
recommendation table, exactly this line (one paragraph, no leading/trailing variants):

```markdown
**Affiliate disclosure:** the links below are Alibaba affiliate links. Object Brief may earn a commission if a purchase is completed through them. They are organized by sourcing role, not by commission rate or supplier ranking. Confirm dimensions, film, perforation, MOQ, and current availability in the quote and physical sample before production.
```

Exceptions to the role clause (keep article-specific role wording ONLY if the article is
organized by something other than sourcing role — e.g. "production stage" for the
heat-gun/equipment comparison). The FIRST TWO sentences and the final "Confirm
dimensions, film, perforation, MOQ..." sentence are NEVER altered.

Forbidden variants (these existed and were removed — never reintroduce):
- "Alibaba listing data changes — confirm …"
- "Marketplace data changes — confirm …"
- "Marketplace terms change, so confirm …"
- "These are organized by production stage — not by …"（用逗号，不用破折号）

## 2. No internal product IDs in visible text（产品编号禁止出现在正文）

Never write `Product 1600874115983` / `Product 62498146139` etc. in article body text or
recommendation tables. The numeric ID may exist ONLY inside the
`https://offer.alibaba.com/cps/…&productId=…` URL (that is how the redirect works).

Instead of the ID, describe the listing by role: "perforated neck-band listing
previously screened for small-batch testing…".

## 3. How to verify mechanically（每篇上传前必跑）

```bash
./scripts/check-article-policy.sh <path/to/index.mdx>
```

Checks performed:
- disclosure line matches the canonical template byte-for-byte (or documented variant)
- zero `Product ` followed by 6+ digits outside of `offer.alibaba.com` URLs
- (build check is separate: run `pnpm build` before pushing)

Exit code 0 = pass; nonzero = fix the article, do NOT push.

## 4. Existing reference implementation

See any current article for the disclosure placement pattern, e.g.
`src/content/blog/perforated-vs-non-perforated-shrink-bands/index.mdx` line ~119
(disclosure paragraph immediately above the recommendation table).

## 5. Historical fix record

- 2026-09-20: unified all 7 articles' disclosure to the template (heat-gun article keeps
  its hair-dryer caveat with standardized framing sentences).
- 2026-09-20: removed all 18 visible `Product <ID>` mentions across 6 articles.
