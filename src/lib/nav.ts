import { NAVIGATION, categories } from "../config/theme.config.ts";

export type NavLink = { to: string; label: string };
export type NavItem = NavLink | { label: string; children: NavLink[] };

/** Category links used by the "Topics" menu (kept in sync with `categories`). */
export const topicLinks: NavLink[] = categories.map((c) => ({
  to: `/categories/${c.slug}`,
  label: c.name,
}));

/** Categories shown in the header "Topics" menu (largest sections first);
    the rest stay reachable from the footer and the archive. */
const HEADER_TOPICS = ["packaging", "kitchen-bath", "laundry-fabric", "home-floors"];
const SHORT_LABELS: Record<string, string> = {
  packaging: "Packaging",
  "laundry-fabric": "Laundry & Fabric",
};
const headerTopicLinks: NavLink[] = [
  ...HEADER_TOPICS.map((slug) => {
    const c = categories.find((x) => x.slug === slug)!;
    return { to: `/categories/${slug}`, label: SHORT_LABELS[slug] ?? c.name };
  }),
];

/** Top-level nav with menu placeholders resolved to their child links. */
const resolve = (children: NavLink[]): NavItem[] =>
  NAVIGATION.map((item) =>
    "menu" in item && item.menu === "categories"
      ? { label: item.label, children }
      : (item as NavLink),
  );

export const navItems: NavItem[] = resolve(headerTopicLinks);

/** Flat list of every nav destination (used by the footer). */
export const flatNavLinks: NavLink[] = resolve(topicLinks).flatMap((item) =>
  "children" in item ? item.children : [item],
);
