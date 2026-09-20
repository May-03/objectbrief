# Article Upload Policy (objectbrief.com)

Every new article upload (by Hermes, Codex, or any other AI agent) MUST pass:

```bash
./scripts/check-article-policy.sh src/content/blog/<slug>/index.mdx
```

Full rules and canonical wording live in `ARTICLE_CHECKLIST.md` (read it first).
Two hard rules enforced by the script:

1. The affiliate-disclosure paragraph matches the canonical template byte-for-byte
   (heat-gun/equipment articles use the documented heat-gun variant).
2. No `Product <digits>` IDs in visible text — IDs are allowed only inside
   `offer.alibaba.com` URLs.

If the script fails: fix the article, do not push. If `pnpm build` fails: fix, do not push.
