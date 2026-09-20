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

exit $fail
