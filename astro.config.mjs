import { defineConfig } from "astro/config";
import mdx from "@astrojs/mdx";
import vercel from "@astrojs/vercel";

// Cloudflare Pages sets CF_PAGES=1 during builds. There the site is exported
// as fully static HTML (no adapter); Vercel keeps the server build.
const onCloudflare = !!process.env.CF_PAGES;
import tailwindcss from "@tailwindcss/vite";

const site =
  process.env.SITE_URL || process.env.PUBLIC_SITE_URL || "https://objectbrief.com";

// Rehype plugin: give affiliate/CPS links in rendered article bodies the same
// attributes the .astro affiliate components already carry. Without this,
// markdown table links render bare (no rel="sponsored", no target="_blank").
// Zero dependencies: a small recursive walk over the hast tree.
function rehypeAffiliateLinks() {
  const affiliateHosts = ["offer.alibaba.com"];

  const walk = (node) => {
    if (node && Array.isArray(node.children)) {
      for (const child of node.children) walk(child);
    }
    if (!node || node.tagName !== "a" || !node.properties || !node.properties.href) {
      return;
    }
    let url;
    try {
      url = new URL(String(node.properties.href), "https://example.com");
    } catch {
      return;
    }
    if (!affiliateHosts.includes(url.hostname)) return;

    const rel = new Set(
      String(node.properties.rel ?? "")
        .split(/\s+/)
        .filter(Boolean),
    );
    rel.add("sponsored");
    rel.add("noopener");
    rel.add("noreferrer");
    node.properties.rel = [...rel].join(" ");
    node.properties.target = "_blank";
    node.properties.dataPlacement = "article-inline";
  };

  return (tree) => {
    walk(tree);
  };
}

export default defineConfig({
  site,
  integrations: [
    mdx(),
    // Static export on Cloudflare: the newsletter API route needs a server,
    // so it is prerendered (dropped) there; functions/api/subscribe.js serves it.
    ...(onCloudflare
      ? [{
          name: "cf-static-routes",
          hooks: {
            "astro:route:setup": ({ route }) => {
              if (route.component.endsWith("api/subscribe.ts")) route.prerender = true;
            },
          },
        }]
      : []),
  ],
  markdown: {
    rehypePlugins: [rehypeAffiliateLinks],
  },
  image: {
    dangerouslyProcessSVG: true,
  },
  vite: {
    plugins: [tailwindcss()],
  },
  ...(onCloudflare ? { output: "static" } : { output: "server", adapter: vercel() }),
});
