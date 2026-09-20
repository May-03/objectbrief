const siteUrl = (
  import.meta.env.SITE_URL ||
  import.meta.env.PUBLIC_SITE_URL ||
  "https://objectbrief.com"
).replace(/\/$/, "");

export const SITE = {
  name: "Object Brief",
  description:
    "Practical sourcing intelligence for product buyers — supplier guides, product comparisons, MOQ breakdowns, and honest Alibaba sourcing advice, written for people who actually order.",
  url: siteUrl,
  locale: "en-US",
  language: "en",
  repositoryUrl: "https://github.com/andreialba/quietpages",
};

export const NAVIGATION = [
  { to: "/", label: "Home" },
  { to: "/blog", label: "Article" },
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

export const SOCIAL_LINKS = [
  { href: "/rss.xml", label: "RSS feed", icon: "rss" },
  { href: `mailto:${CONTACT.email}`, label: "Email", icon: "mail" },
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
  { slug: "guides", name: "Guides" },
  { slug: "products", name: "Products" },
  { slug: "comparisons", name: "Comparisons" },
  { slug: "sourcing", name: "Sourcing" },
  { slug: "packaging", name: "Packaging" },
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
];