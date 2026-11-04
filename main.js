/* ===== Kamobo site interactions ===== */
(function () {
  "use strict";

  var reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  // Year
  var yearEl = document.getElementById("year");
  if (yearEl) yearEl.textContent = String(new Date().getFullYear());

  // Header scrolled state
  var header = document.querySelector(".site-header");
  function onScroll() {
    if (header) header.classList.toggle("scrolled", window.scrollY > 12);
  }
  onScroll();
  window.addEventListener("scroll", onScroll, { passive: true });

  // Mobile menu
  var toggle = document.querySelector(".nav-toggle");
  if (toggle && header) {
    toggle.addEventListener("click", function () {
      var open = header.classList.toggle("menu-open");
      toggle.setAttribute("aria-expanded", open ? "true" : "false");
    });
    header.querySelectorAll(".nav a").forEach(function (a) {
      a.addEventListener("click", function () {
        header.classList.remove("menu-open");
        toggle.setAttribute("aria-expanded", "false");
      });
    });
  }

  // Reveal on scroll.
  // Threshold 0, not 0.12: a tall section that is only ever partly on screen must
  // still reveal. And anything already at or above the fold on load is shown
  // immediately, otherwise an anchor link such as /#proof jumps past earlier
  // sections and leaves them invisible for the rest of the visit.
  var revealEls = Array.prototype.slice.call(document.querySelectorAll(".reveal"));

  function showAllAbove() {
    var limit = window.innerHeight + 80;
    revealEls.forEach(function (el) {
      if (el.classList.contains("in")) return;
      if (el.getBoundingClientRect().top < limit) el.classList.add("in");
    });
  }

  function showEverything() {
    revealEls.forEach(function (el) { el.classList.add("in"); });
  }

  // A deep link such as /#retainers scrolls the page before the observer has
  // seen anything, so the sections it skipped would stay invisible. Anyone
  // arriving on an anchor just gets the whole page.
  if (reduceMotion || !("IntersectionObserver" in window) || window.location.hash) {
    showEverything();
  } else {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (e.isIntersecting) { e.target.classList.add("in"); io.unobserve(e.target); }
      });
    }, { threshold: 0, rootMargin: "0px 0px -40px 0px" });
    revealEls.forEach(function (el) { io.observe(el); });

    showAllAbove();
    window.addEventListener("scroll", showAllAbove, { passive: true });
    window.addEventListener("hashchange", function () { setTimeout(showAllAbove, 50); });
    window.addEventListener("load", showAllAbove);
    // Last resort: nothing on a marketing page should ever stay invisible.
    setTimeout(showEverything, 6000);
  }
})();
