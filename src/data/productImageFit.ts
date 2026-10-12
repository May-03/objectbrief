/**
 * Product photos shot on a plain white studio background.
 *
 * The product card shows the photo in a full-height side panel. Cropping a
 * photo to fill that panel (`object-cover`) reads well for supplier photos
 * taken in a real workspace, but for these white-background studio shots it
 * zooms into the product and turns it into an abstract close-up. They keep
 * `object-contain` instead so the whole product stays visible.
 *
 * Classified by sampling the outer 10% ring of each image: at least 90% of
 * those pixels are near-white. 45 of the 111 images qualify.
 */
export const WHITE_BACKGROUND_PRODUCT_IMAGES = new Set<string>([
  '/images/products/ali-11000022646016.jpg',
  '/images/products/ali-11000032825427.jpg',
  '/images/products/ali-1600065064889.jpg',
  '/images/products/ali-1600187466754.jpg',
  '/images/products/ali-1600366918160.jpg',
  '/images/products/ali-1600555060434.jpg',
  '/images/products/ali-1600626061135.jpg',
  '/images/products/ali-1600695519353.jpg',
  '/images/products/ali-1600845080603.jpg',
  '/images/products/ali-1600918437511.jpg',
  '/images/products/ali-1600945930330.jpg',
  '/images/products/ali-1600953840059.jpg',
  '/images/products/ali-1600994360911.jpg',
  '/images/products/ali-1601023347467.jpg',
  '/images/products/ali-1601039041500.jpg',
  '/images/products/ali-1601044403799.jpg',
  '/images/products/ali-1601101205412.jpg',
  '/images/products/ali-1601105440740.jpg',
  '/images/products/ali-1601137890552.jpg',
  '/images/products/ali-1601172936278.jpg',
  '/images/products/ali-1601199378967.jpg',
  '/images/products/ali-1601213326262.jpg',
  '/images/products/ali-1601293514594.jpg',
  '/images/products/ali-1601338264801.jpg',
  '/images/products/ali-1601350675794.jpg',
  '/images/products/ali-1601357963518.jpg',
  '/images/products/ali-1601378754716.jpg',
  '/images/products/ali-1601382713645.jpg',
  '/images/products/ali-1601386168083.jpg',
  '/images/products/ali-1601408529901.jpg',
  '/images/products/ali-1601451840509.jpg',
  '/images/products/ali-1601606535494.jpg',
  '/images/products/ali-1601608301425.jpg',
  '/images/products/ali-1601618959875.jpg',
  '/images/products/ali-1601639497754.jpg',
  '/images/products/ali-1601666979128.jpg',
  '/images/products/ali-1601680277376.jpg',
  '/images/products/ali-1601897779853.jpg',
  '/images/products/ali-2006528454.jpg',
  '/images/products/ali-60132511158.jpg',
  '/images/products/ali-62050284799.jpg',
  '/images/products/ali-62072448659.jpg',
  '/images/products/ali-62091804763.jpg',
  '/images/products/ali-62498146139.jpg',
  '/images/products/eucalan-no-rinse-delicate-wash.jpg',
]);
