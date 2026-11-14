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
  { to: "/categories/kitchen-bath", label: "Kitchen & Bath" },
  { to: "/categories/laundry-fabric", label: "Laundry" },
  { to: "/categories/home-floors", label: "Home" },
  { to: "/categories/packaging", label: "Packaging" },
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
    slug: "kitchen-bath",
    name: "Kitchen & Bath",
    blurb: "Aerators, drains, dishwasher racks and the small kitchen and bathroom parts that keep failing: fit, fixes and what to buy.",
  },
  {
    slug: "laundry-fabric",
    name: "Laundry & Fabric Care",
    blurb: "Washing, drying and repairing wool, cashmere, bedding and upholstery without shrinking or stretching them.",
  },
  {
    slug: "home-floors",
    name: "Home & Floors",
    blurb: "Chair pads, rug grippers, door sweeps and screens: measure once and stop things sliding, peeling or popping out.",
  },
  {
    slug: "cleaning-pets",
    name: "Cleaning & Pets",
    blurb: "Pet hair, lint and everyday cleanup: tools that actually work and how to use them without damage.",
  },
  {
    slug: "garden",
    name: "Garden & Irrigation",
    blurb: "Drip irrigation and fertigation troubleshooting: clogged emitters, pressure regulators and stock tanks.",
  },
  {
    slug: "packaging",
    name: "Small-Batch Packaging",
    blurb: "Shrink bands, induction seals, labels, cappers and fillers for small makers: sizes, fit and what to test first.",
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