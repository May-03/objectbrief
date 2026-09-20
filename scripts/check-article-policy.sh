#!/usr/bin/env bash
# Article policy check for objectbrief.com — run before committing/pushing new articles.
# Usage: ./scripts/check-article-policy.sh src/content/blog/<slug>/index.mdx
set -euo pipefail

SP="$(pwd)/$(dirname "$0")"
f="${1:?usage: check-article-policy.sh <index.mdx>}"
f="$(cd "$(dirname "$f")" && pwd)/$(basename "$f")"
fail=0

STD="**Affiliate disclosure:** the links below are Alibaba affiliate links. Object Brief may earn a commission if a purchase is completed through them. They are organized by sourcing role, not by commission rate or supplier ranking. Confirm dimensions, film, perforation, MOQ, and current availability in the quote and physical sample before production."

HEATGUN="**Affiliate disclosure:** the links below are Alibaba affiliate links. Object Brief may earn a commission if a purchase is completed through them. They are organized by production stage, not by commission rate or supplier ranking. Hair dryers are intentionally not listed as a purchasing recommendation: use one only when the shrink-band supplier permits it and the actual package passes validation. Confirm dimensions, film, perforation, MOQ, voltage, control specifications, and current availability in the quote and physical sample before production."

disc="$(grep -m1 '^\*\*Affiliate disclosure' "$f" || true)"
if [ -z "$disc" ]; then
  # article has no affiliate table → nothing to check for disclosure
  echo "OK  (no affiliate disclosure — no affiliate table expected)"
else
  exp="$STD"
  case "$f" in *heat-gun*) exp="$HEATGUN";; esac
  if [ "$disc" = "$exp" ]; then
    echo "OK  disclosure matches canonical template"
  else
    echo "FAIL disclosure does not match canonical template."
    echo "  expected: $exp"
    echo "  found   : $disc"
    fail=1
  fi
fi

# product IDs outside alibaba URLs: strip URLs first, then search
stripped="$(sed -E 's#https?://[^ )|]+#URL#g' "$f")"
ids="$(grep -oE '\bProduct [0-9]{6,}\b' <<<"$stripped" || true)"
if [ -z "$ids" ]; then
  echo "OK  no visible Product IDs"
else
  echo "FAIL visible product IDs found (move them into offer.alibaba.com URLs or remove):"
  echo "$ids"
  fail=1
fi

# affiliate links must carry a productId pinned to the target product
# strip URLs first: every offer.alibaba.com link checked separately
alinks="$(grep -oE 'https://offer\.alibaba\.com/[^ )|"]+' "$f" | sed 's/&amp;/\&/g' | sort -u || true)"
bad=0
if [ -n "$alinks" ]; then
  while IFS= read -r link; do
    if ! echo "$link" | grep -q 'productId=[0-9]\{5,\}'; then
      echo "FAIL affiliate link missing productId (dead-PLA risk): $link"
      fail=1
    fi
  done <<< "$alinks"
  [ $fail -eq 0 ] && echo "OK  all affiliate links are productId-pinned"
else
  echo "OK  (no affiliate links)"
fi

# built-output gate: rendered HTML must give every CPS link rel="sponsored",
# target="_blank", and noopener. Run against dist/client/blog/<slug>/index.html
# after `pnpm build` (or pnpm dlx vercel build). Usage: pass a second arg
# pointing at the dist root, e.g. ./scripts/check-article-policy.sh src/.../index.mdx dist/client
dist_root="${2:-}"
if [ -n "$dist_root" ]; then
  slug="$(basename "$(dirname "$f")")"
  h="$dist_root/blog/$slug/index.html"
  if [ -f "$h" ]; then
    total="$(grep -o 'href="https://offer\.alibaba\.com/cps/' "$h" | wc -l | tr -d ' ')"
    if [ "$total" -gt 0 ]; then
      # per-tag check: every CPS anchor must carry sponsored/_blank/noopener.
      # (page-wide counting is wrong — share buttons also use target="_blank".)
      tags="$(grep -o '<a href="https://offer\.alibaba\.com/cps/[^>]*>' "$h")"
      badtags=0
      while IFS= read -r tag; do
        [ -z "$tag" ] && continue
        echo "$tag" | grep -q 'rel="[^"]*sponsored[^"]*"' || badtags=$((badtags+1))
        echo "$tag" | grep -q 'target="_blank"' || badtags=$((badtags+1))
        echo "$tag" | grep -q 'noopener' || badtags=$((badtags+1))
      done <<< "$tags"
      if [ "$badtags" -eq 0 ]; then
        echo "OK  dist: $total CPS link(s) all rel=sponsored + target=_blank + noopener"
      else
        echo "FAIL dist gate: $badtags attribute miss(es) across $total CPS tags in $h"
        fail=1
      fi
    else
      echo "OK  dist: no CPS links in built page"
    fi
  else
    echo "SKIP dist gate: $h not built"
  fi
fi

exit $fail
