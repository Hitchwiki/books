const { test, expect } = require("@playwright/test");

test.beforeEach(async ({ page }) => {
  await page.goto("/hitchhikers-guide/");
});

test("part jumps keep the destination visible instead of moving the page to the TOC", async ({ page }) => {
  await page.locator(".toc-parts a", { hasText: "Part III" }).click();

  await expect(page).toHaveURL(/#.*part-iii-resources-and-the-road-ahead$/);
  const heading = page.getByRole("heading", {
    level: 1,
    name: "Part III — Resources and the road ahead",
  });
  await expect(heading).toBeInViewport();
  await expect(page.getByRole("heading", { level: 1, name: "Appearance" })).not.toBeInViewport();
});

test("Part I exposes chapters in practical groups and reading order", async ({ page }) => {
  const groups = page.locator("#toc-part-01-practice > details.toc-subsection > summary");
  await expect(groups).toHaveText([
    /Getting started/,
    /Planning the journey/,
    /Roads and places to stand/,
    /Different travellers and rides/,
    /Community and culture/,
    /Reference/,
  ]);

  const firstGroup = page.locator("#toc-part-01-practice > details.toc-subsection").first();
  await expect(firstGroup.locator("summary a")).toHaveText("Getting started");
  await expect(firstGroup.locator("li a").first()).toHaveText("The Pros and Cons of Hitch Hiking");
  await expect(page.locator(".book-body a.wikilink")).toHaveCount(0);
});

test("chapter search filters and restores the TOC", async ({ page }) => {
  const search = page.getByPlaceholder("Find a chapter…");
  await search.fill("wheelchair");

  await expect(page.locator("#TOC li:not([hidden]) a", { hasText: "Hitchhiking in a wheelchair" })).toBeVisible();
  await expect(page.locator("#toc-part-02-countries")).toBeHidden();

  await search.clear();
  await expect(page.locator("#toc-part-02-countries")).toBeVisible();
});

test("chapter sources are compact, unbulleted, and alphabetical", async ({ page }) => {
  const sources = page.locator(".chapter-sources");
  await expect(sources).toHaveCount(1);
  await expect(sources.locator("ul, ol")).toHaveCount(0);

  const labels = await sources
    .locator('a:not([href*="action=history"])')
    .allTextContents();
  const fold = (value) =>
    value
      .trim()
      .toLocaleLowerCase()
      .normalize("NFKD")
      .replace(/\p{M}/gu, "")
      .replace(/[^\p{L}\p{N}]/gu, "");
  const sorted = [...labels].sort((a, b) => {
    const left = fold(a);
    const right = fold(b);
    return left < right ? -1 : left > right ? 1 : 0;
  });
  expect(labels).toEqual(sorted);
});

test("desktop reader gives the text column more room than the TOC", async ({ page }) => {
  await page.setViewportSize({ width: 1440, height: 900 });

  const widths = await page.locator(".book-layout").evaluate((layout) => {
    const toc = layout.querySelector("#TOC").getBoundingClientRect();
    const body = layout.querySelector(".book-body").getBoundingClientRect();
    return { toc: toc.width, body: body.width };
  });

  expect(widths.body).toBeGreaterThanOrEqual(700);
  expect(widths.body).toBeGreaterThan(widths.toc * 1.8);
});

test("Dumpsterdam presents a thematic core, grouped archive, and English appendix", async ({ page }) => {
  await page.goto("/dumpsterdam/");

  await expect(page.locator(".toc-parts a")).toHaveText([
    "Deel I — Waarom Dumpsterdam",
    "Deel II — Zelf dumpsterdiven",
    "Deel III — Van vondst naar maaltijd",
    "Deel IV — Delen en organiseren",
    "Deel V — Van actie naar verandering",
    "Archief",
    "Engelse selectie",
    "Naamsvermelding",
  ]);

  const archive = page.locator("#toc-part-archief");
  await expect(archive.locator(":scope > details.toc-subsection > summary")).toHaveText([
    /Verhalen en portretten/,
    /Media/,
    /Evenementen en projecten/,
    /Nieuws en internationale voorbeelden/,
  ]);
  await expect(page.locator("#toc-part-archief + #toc-part-engelse-selectie")).toHaveCount(1);

  const headings = await page.locator(".book-body h1").allTextContents();
  expect(headings).toHaveLength(new Set(headings).size);
  await expect(
    page.getByRole("heading", { level: 1, name: "Bestemming onbekend Dumpster diven" }),
  ).toHaveCount(1);
  expect(await page.locator('.chapter-source a[href*="dumpsterdam.nl"]').count()).toBeGreaterThan(0);
});

test("catalog masthead uses the cropped wordmark without clipping", async ({ page }) => {
  await page.goto("/");
  await page.setViewportSize({ width: 1440, height: 900 });

  const wordmark = page.locator(".masthead-logo img");
  await expect(wordmark).toHaveAttribute("src", /hitchwiki-wordmark\.png/);
  await expect(wordmark).toHaveAttribute("alt", "Hitchwiki");
  await expect(page.locator(".masthead-title")).toHaveText("BOOKS");
  await expect(page.locator(".masthead-version")).toHaveText("0.1");

  const desktop = await page.locator("h1").evaluate((heading) => {
    const logo = heading.querySelector(".masthead-logo img").getBoundingClientRect();
    const title = heading.querySelector(".masthead-title").getBoundingClientRect();
    return {
      separated: logo.right <= title.left,
      visible: logo.top >= 0 && logo.bottom <= window.innerHeight,
      noHorizontalScroll: document.documentElement.scrollWidth <= window.innerWidth,
    };
  });
  expect(desktop).toEqual({ separated: true, visible: true, noHorizontalScroll: true });

  await page.setViewportSize({ width: 390, height: 844 });
  const mobile = await page.locator("h1").evaluate((heading) => {
    const logo = heading.querySelector(".masthead-logo img").getBoundingClientRect();
    const title = heading.querySelector(".masthead-title").getBoundingClientRect();
    return {
      separated: logo.right <= title.left,
      noHorizontalScroll: document.documentElement.scrollWidth <= window.innerWidth,
    };
  });
  expect(mobile).toEqual({ separated: true, noHorizontalScroll: true });
});

test("Hospitality Exchange prioritizes practice and groups its geography", async ({ page }) => {
  await page.goto("/hospitality-exchange/");

  const practiceLinks = page.locator("#toc-part-part-i-practice li a");
  await expect(practiceLinks.first()).toHaveText("How to write a hosting request");
  await expect(practiceLinks.nth(1)).toHaveText("How to write a request");
  await expect(practiceLinks.nth(2)).toHaveText("Searching and requesting a couch");

  await page.locator('.toc-parts a[data-part="part-iii-places"]').click();
  const places = page.locator("#toc-part-part-iii-places");
  await expect(places).toBeVisible();
  await expect(places.locator("summary", { hasText: "Europe — Regional indexes" })).toBeVisible();
  await expect(places.locator("summary", { hasText: "Europe — Belarus" })).toBeVisible();
  await expect(places.locator("summary", { hasText: "Europe — Bulgaria" })).toBeVisible();
  await expect(places.locator("summary", { hasText: "Europe — France" })).toBeVisible();
  await expect(places.locator("summary", { hasText: "Oceania — Australia" })).toBeVisible();
  await expect(places.locator("summary", { hasText: "Rural hospitality" })).toBeVisible();
});

test("Hospitality Exchange removes wiki noise but keeps useful references", async ({ page }) => {
  await page.goto("/hospitality-exchange/");

  await expect(page.locator(".book-body a.wikilink")).toHaveCount(0);
  await expect(page.locator('.chapter-sources a[href*="wiki.trustroots.org"]')).not.toHaveCount(0);
  await expect(page.locator('.chapter-edit[href*="action=edit"]')).not.toHaveCount(0);
  await expect(page.locator('a[href="https://www.trustroots.org/support"]')).not.toHaveCount(0);
  await expect(page.locator('.book-banner-downloads a[href$=".epub"]')).toHaveCount(1);
  await expect(page.locator('.book-banner-downloads a[href$=".pdf"]')).toHaveCount(1);
});
