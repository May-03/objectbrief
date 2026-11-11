const siteUrl = (
  import.meta.env.SITE_URL ||
  import.meta.env.PUBLIC_SITE_URL ||
  "https://objectbrief.com"
).replace(/\/$/, "");

export const SITE = {
  name: "Object Brief",
  tagline: "Plain-spoken guides to everyday goods and small-batch supplies",
  description:
    "Plain-spoken guides to everyday goods and small-batch supplies: what fits, what to buy, and how to fix the small things that go wrong, with product picks you can check yourself.",
  url: siteUrl,
  locale: "en-US",
  /* Path under public/ used for social previews when a page has no image. */
  defaultOgImage: "/og-default.png",
  language: "en",
};

export const NAVIGATION = [
  { to: "/categories/packaging", label: "Packaging" },
  { to: "/categories/guides", label: "Guides" },
  { to: "/categories/comparisons", label: "Comparisons" },
  { to: "/blog", label: "Archive" },
  { to: "/about", label: "About" },
];

/* Hand-picked evergreen articles for the home page "Start here" block.
   Slugs must exist in src/content/blog; unknown slugs are skipped. */
export const STARTER_GUIDES = [
  "shrink-band-size-guide",
  "induction-seal-liner-size-guide",
  "how-to-choose-a-handheld-induction-sealer-for-small-batch-bottles",
  "why-labels-wrinkle-skew-or-bubble-on-round-bottles",
  "why-bath-rugs-slide-on-tile",
  "how-to-wash-a-wool-sweater-without-shrinking",
];

export const CONTACT = {
  email: "hello@objectbrief.com",
  socialHandle: "@objectbrief",
  socialUrl: "https://x.com/objectbrief",
};

export const FORMS = {
  contact: {
    action: "",
    method: "post",
    enctype: "application/x-www-form-urlencoded",
  },
  newsletter: {
    action: "",
    method: "post",
    enctype: "application/x-www-form-urlencoded",
  },
};

export const SOCIAL_LINKS = [  { href: `mailto:${CONTACT.email}`, label: "Email", icon: "mail" },
];

export const authors = [
  {
    slug: "david-okoro",
    name: "David Okoro",
    bio: "Sourcing analyst writing about suppliers, MOQs, and procurement for small businesses.",
    longBio:
      "David spent eight years in procurement for a mid-size packaging distributor before starting Object Brief. He writes the guides and sourcing deep-dives — the kind of advice he wishes someone had given him before his first container order.",
    avatar: "/avatars/david-okoro.svg",
  },
  {
    slug: "lena-schmidt",
    name: "Lena Schmidt",
    bio: "Editor covering product categories, comparisons, and packaging materials.",
    longBio:
      "Lena worked as a packaging engineer and, more recently, a freelance product researcher. At Object Brief she tests the products we write about, stresses the comparisons, and keeps the numbers honest.",
    avatar: "/avatars/lena-schmidt.svg",
  },
];

export const categories = [
  {
    slug: "packaging",
    name: "Packaging",
    blurb: "Bottles, seals, labels and small-batch equipment: sizes, fit and what to test first.",
  },
  {
    slug: "guides",
    name: "Guides",
    blurb: "Fixes and fit guides for the small things around the home that keep going wrong.",
  },
  {
    slug: "comparisons",
    name: "Comparisons",
    blurb: "Side-by-side picks with the numbers that matter, so you can choose once.",
  },
];

export const tags = [
  { slug: "alibaba", name: "Alibaba" },
  { slug: "moq", name: "MOQ" },
  { slug: "packaging", name: "Packaging" },
  { slug: "materials", name: "Materials" },
  { slug: "comparisons", name: "Comparisons" },
  { slug: "certification", name: "Certification" },
  { slug: "suppliers", name: "Suppliers" },
  { slug: "customization", name: "Customization" },
  { slug: "shipping", name: "Shipping" },
  { slug: "troubleshooting", name: "Troubleshooting" },
  { slug: "quality", name: "Quality" },
];