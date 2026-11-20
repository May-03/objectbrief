import { NAVIGATION, categories } from "../config/theme.config.ts";

export type NavLink = { to: string; label: string };
export type NavItem = NavLink | { label: string; children: NavLink[] };

/** Category links used by the "Topics" menu (kept in sync with `categories`). */
export const topicLinks: NavLink[] = categories.map((c) => ({
  to: `/categories/${c.slug}`,
  label: c.name,
}));

/** Top-level nav with menu placeholders resolved to their child links. */
export const navItems: NavItem[] = NAVIGATION.map((item) =>
  "menu" in item && item.menu === "categories"
    ? { label: item.label, children: topicLinks }
    : (item as NavLink),
);

/** Flat list of every nav destination (used by the footer). */
export const flatNavLinks: NavLink[] = navItems.flatMap((item) =>
  "children" in item ? item.children : [item],
);
