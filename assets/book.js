(function () {
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
    var part = a && a.closest("details");
    if (part) part.open = true;
    if (a) a.classList.add("is-current");
  }
  openHash();
  window.addEventListener("hashchange", openHash);

  if (filter) {
    filter.addEventListener("input", function () {
      var q = fold(filter.value.trim());
      toc.classList.toggle("is-filtering", !!q);
      var hits = 0;
      toc.querySelectorAll("details.toc-part").forEach(function (d) {
        var summaryHit = !!q && fold(d.querySelector("summary").textContent).indexOf(q) !== -1;
        var any = false;
        Array.prototype.forEach.call(d.querySelectorAll("li"), function (li) {
          var a = li.querySelector("a");
          var hit = !q || summaryHit || fold(a && a.textContent).indexOf(q) !== -1;
          li.hidden = !hit;
          if (hit) {
            any = true;
            hits += 1;
          }
        });
        d.hidden = !!q && !any && !summaryHit;
        if (q && (any || summaryHit)) d.open = true;
        if (!q) d.open = !d.getAttribute("data-collapse");
        var az = d.querySelector(".toc-az");
        if (az) az.hidden = !!q;
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

  toc.querySelectorAll(".toc-az a").forEach(function (a) {
    a.addEventListener("click", function (e) {
      var id = (a.getAttribute("href") || "").replace(/^#/, "");
      var el = id && document.getElementById(id);
      if (!el) return;
      e.preventDefault();
      el.scrollIntoView({ block: "start" });
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
        var part = a.closest("details");
        if (part && !toc.classList.contains("is-filtering")) part.open = true;
        if (!toc.classList.contains("is-filtering")) {
          a.scrollIntoView({ block: "nearest" });
        }
      });
    },
    { rootMargin: "-15% 0px -70% 0px", threshold: 0 }
  );
  headings.forEach(function (h) {
    obs.observe(h);
  });
})();
