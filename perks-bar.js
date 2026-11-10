(function () {
  var bar = document.getElementById("apexStickyPromoBar");
  if (!bar) return;

  function clearPad() {
    document.body.classList.add("perks-closed");
    document.body.style.paddingBottom = "0px";
  }

  try {
    if (sessionStorage.getItem("apx_perks_closed") === "1") {
      bar.remove();
      clearPad();
      return;
    }
  } catch (e) {}

  function syncPad() {
    if (!document.body.contains(bar)) return;
    if (document.body.classList.contains("perks-closed") || document.body.classList.contains("is-locked") || document.body.classList.contains("nav-open")) return;
    var h = bar.offsetHeight || 64;
    document.body.style.paddingBottom = (h + 16) + "px";
  }

  var btn = document.createElement("button");
  btn.type = "button";
  btn.className = "PerksDismiss";
  btn.setAttribute("aria-label", "Dismiss race-week perks");
  btn.textContent = "Close";
  btn.addEventListener("click", function () {
    try { sessionStorage.setItem("apx_perks_closed", "1"); } catch (e) {}
    bar.remove();
    clearPad();
  });
  var row = bar.querySelector("div");
  if (row) row.appendChild(btn);
  else bar.appendChild(btn);
  syncPad();
  window.addEventListener("resize", syncPad);
})();
