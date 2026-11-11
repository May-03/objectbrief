import { SITE, authors, categories, sortedPosts, usedTags, MIN_INDEXABLE_POSTS } from "../lib/blog-data.js";

const BASE_URL = SITE.url || "";

export async function GET() {
  const posts = await sortedPosts();
  const newest = posts[0]?.updated || posts[0]?.date;
  const indexableCategories = categories.filter(
    (category) => posts.filter((post) => post.category === category.slug).length >= MIN_INDEXABLE_POSTS,
  );
  const indexableTags = (await usedTags()).filter((tag) => tag.count >= MIN_INDEXABLE_POSTS);
  const entries = [
    { path: "/", lastmod: newest },
    { path: "/blog", lastmod: newest },
    { path: "/about" },
    { path: "/contact" },
    { path: "/affiliate-disclosure" },
    { path: "/privacy" },
    ...posts.map((post) => ({
      path: `/blog/${post.slug}`,
      lastmod: post.updated || post.date,
    })),
    ...indexableCategories.map((category) => ({ path: `/categories/${category.slug}`, lastmod: newest })),
    ...indexableTags.map((tag) => ({ path: `/tags/${tag.slug}`, lastmod: newest })),
    ...authors.map((author) => ({ path: `/authors/${author.slug}` })),
  ];

  const urls = entries.map((entry) =>
    [
      "  <url>",
      `    <loc>${BASE_URL}${entry.path}</loc>`,
      entry.lastmod ? `    <lastmod>${entry.lastmod}</lastmod>` : null,
      "  </url>",
    ]
      .filter(Boolean)
      .join("\n"),
  );

  const xml = [
    '<?xml version="1.0" encoding="UTF-8"?>',
    '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
    ...urls,
    "</urlset>",
  ].join("\n");

  return new Response(xml, {
    headers: {
      "Content-Type": "application/xml",
      "Cache-Control": "public, max-age=3600",
    },
  });
}
