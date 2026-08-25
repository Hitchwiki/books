(function () {
  var banner = document.querySelector(".book-banner");
  function syncBanner() {
    var h = banner ? Math.ceil(banner.getBoundingClientRect().height) : 0;
    document.body.style.setProperty("--banner", h + "px");
  }
  syncBanner();
  window.addEventListener("resize", syncBanner);

  var toc = document.getElementById("TOC");
  if (!toc) return;

  var filter = toc.querySelector(".toc-filter");
  var empty = toc.querySelector(".toc-empty");
  var chapterLinks = Array.prototype.slice.call(toc.querySelectorAll("li a[href^='#']"));

  toc.querySelectorAll("details[data-collapse='true']").forEach(function (d) {
    d.open = false;
  });

  function fold(s) {
    return (s || "")
      .toLowerCase()
      .normalize("NFD")
      .replace(/[\u0300-\u036f]/g, "");
  }

  function openHash() {
    var hash = location.hash;
    if (!hash) return;
    var a = toc.querySelector('a[href="' + hash.replace(/"/g, "") + '"]');
    var node = a && a.closest("details");
    while (node) {
      node.open = true;
      node = node.parentElement && node.parentElement.closest("details");
    }
    if (a) a.classList.add("is-current");
  }

  function revealInToc(node) {
    if (!node) return;
    var top = node.offsetTop;
    var bottom = top + node.offsetHeight;
    if (top < toc.scrollTop) toc.scrollTop = top;
    else if (bottom > toc.scrollTop + toc.clientHeight) {
      toc.scrollTop = bottom - toc.clientHeight;
    }
  }
  openHash();
  window.addEventListener("hashchange", openHash);

  if (filter) {
    filter.addEventListener("input", function () {
      var q = fold(filter.value.trim());
      toc.classList.toggle("is-filtering", !!q);
      var hits = 0;
      function walkLi(li) {
        var label = li.querySelector(":scope > a, :scope > .toc-orphan");
        var own = !q || fold(label && label.textContent).indexOf(q) !== -1;
        var childHit = false;
        Array.prototype.forEach.call(li.querySelectorAll(":scope > ul > li"), function (child) {
          if (walkLi(child)) childHit = true;
        });
        var hit = own || childHit;
        li.hidden = !!q && !hit;
        if (hit) hits += 1;
        return hit;
      }
      toc.querySelectorAll("details.toc-part").forEach(function (d) {
        var summaryHit = !!q && fold(d.querySelector("summary").textContent).indexOf(q) !== -1;
        var any = false;
        Array.prototype.forEach.call(d.querySelectorAll(":scope > ul > li, :scope > details.toc-region, :scope > details.toc-subsection"), function (node) {
          if (node.tagName === "DETAILS") {
            var rSummaryHit = !!q && fold(node.querySelector("summary").textContent).indexOf(q) !== -1;
            var rAny = false;
            Array.prototype.forEach.call(node.querySelectorAll(":scope > ul > li"), function (li) {
              if (walkLi(li)) rAny = true;
            });
            node.hidden = !!q && !rAny && !rSummaryHit && !summaryHit;
            if (q && (rAny || rSummaryHit || summaryHit)) node.open = true;
            if (!q) node.open = !node.getAttribute("data-collapse");
            if (rAny || rSummaryHit) any = true;
            return;
          }
          if (walkLi(node)) any = true;
        });
        d.hidden = !!q && !any && !summaryHit;
        if (q && (any || summaryHit)) d.open = true;
        if (!q) d.open = !d.getAttribute("data-collapse");
        var jumps = d.querySelector(".toc-az, .toc-regions");
        if (jumps) jumps.hidden = !!q;
      });
      toc.querySelectorAll(".toc-solo").forEach(function (p) {
        var hit = !q || fold(p.textContent).indexOf(q) !== -1;
        p.hidden = !hit;
        if (hit) hits += 1;
      });
      if (empty) empty.hidden = hits > 0;
    });
  }

  toc.querySelectorAll("summary a").forEach(function (a) {
    a.addEventListener("click", function (e) {
      e.stopPropagation();
    });
  });

  toc.querySelectorAll(".toc-az a, .toc-regions a").forEach(function (a) {
    a.addEventListener("click", function (e) {
      var id = (a.getAttribute("href") || "").replace(/^#/, "");
      var el = id && document.getElementById(id);
      if (!el) return;
      e.preventDefault();
      el.scrollIntoView({ block: "start" });
    });
  });

  toc.querySelectorAll(".toc-parts a").forEach(function (a) {
    a.addEventListener("click", function () {
      var part = a.getAttribute("data-part");
      var d = part && toc.querySelector('details.toc-part[data-part="' + part + '"]');
      if (d) {
        d.open = true;
        revealInToc(d);
      }
    });
  });

  var map = {};
  chapterLinks.forEach(function (a) {
    var id = (a.getAttribute("href") || "").replace(/^#/, "");
    if (id) map[id] = a;
  });
  toc.querySelectorAll("summary a[href^='#'], .toc-solo a[href^='#']").forEach(function (a) {
    var id = (a.getAttribute("href") || "").replace(/^#/, "");
    if (id && !map[id]) map[id] = a;
  });
  var headings = document.querySelectorAll(".book-body h1[id]");
  if (!("IntersectionObserver" in window) || !headings.length) return;
  var current = null;
  var obs = new IntersectionObserver(
    function (entries) {
      entries.forEach(function (entry) {
        if (!entry.isIntersecting) return;
        var a = map[entry.target.id];
        if (!a || a === current) return;
        if (current) current.classList.remove("is-current");
        current = a;
        a.classList.add("is-current");
        var node = a.closest("details");
        while (node && !toc.classList.contains("is-filtering")) {
          node.open = true;
          node = node.parentElement && node.parentElement.closest("details");
        }
        if (!toc.classList.contains("is-filtering")) {
          revealInToc(a);
        }
      });
    },
    { rootMargin: "-15% 0px -70% 0px", threshold: 0 }
  );
  headings.forEach(function (h) {
    obs.observe(h);
  });
})();
