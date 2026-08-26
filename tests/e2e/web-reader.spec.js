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
