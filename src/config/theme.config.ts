const siteUrl = (
  import.meta.env.SITE_URL ||
  import.meta.env.PUBLIC_SITE_URL ||
  "https://objectbrief.com"
).replace(/\/$/, "");

export const SITE = {
  name: "Object Brief",
  description:
    "Buyer's guides for equipment and the small parts that keep it running: fit checks, specifications, MOQs and supplier questions, written for people who place the order.",
  tagline: "Equipment and parts buying guides",
  url: siteUrl,
  locale: "en-US",
  language: "en",
  repositoryUrl: "https://github.com/andreialba/quietpages",
};

export const NAVIGATION = [
  { to: "/", label: "Home" },
  { to: "/categories/equipment", label: "Equipment" },
  { to: "/categories/parts", label: "Parts" },
  { to: "/categories/comparisons", label: "Comparisons" },
  { to: "/blog", label: "Archive" },
  { to: "/about", label: "About" },
  { to: "/contact", label: "Contact" },
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
    slug: "equipment",
    name: "Equipment",
    description:
      "Machines and instruments for small-batch production and packaging: sealers, cappers, labelers, fillers, checkweighers, coders and test equipment. Each guide covers what to verify before you buy.",
  },
  {
    slug: "parts",
    name: "Parts & Consumables",
    description:
      "The small components that decide whether equipment works: induction liners, shrink bands, closures, sprayers and similar parts. Size, fit and specification checks before a bulk order.",
  },
  {
    slug: "comparisons",
    name: "Comparisons",
    description:
      "Side-by-side decisions between equipment types, materials and formats, with the specifications that separate them.",
  },
  {
    slug: "household",
    name: "Household Parts & Care",
    description:
      "Replacement parts and care guides for common household items: fit checks, sizing and what to try before buying.",
  },
];

// Categories shown in the homepage feed and chosen for the featured slot.
// Posts in other categories stay published and reachable through the archive.
export const FEED_EXCLUDED_CATEGORIES = ["household"];

// Hand-picked entry points for the homepage "Start here" list and the sidebar.
export const START_HERE = [
  "how-to-choose-a-handheld-induction-sealer-for-small-batch-bottles",
  "manual-vs-semi-automatic-round-bottle-labelers",
  "how-to-choose-a-handheld-or-benchtop-screw-capper-for-small-batch-bottles",
  "induction-seal-liner-size-guide",
  "shrink-band-size-guide",
  "28-400-vs-28-410-trigger-sprayers",
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