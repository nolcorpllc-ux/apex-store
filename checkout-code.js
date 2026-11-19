(function () {
  var CODES = {
    DALLAS10: 10,
    TEAM15: 15,
    CLUB10: 10,
    DOUBLES10: 10,
    DADBOD10: 10,
    COACHSU10: 10
  };

  function stored() {
    var code = "";
    try {
      code = String(sessionStorage.getItem("apx_promo_code") || "").trim().toUpperCase();
    } catch (e) {}
    return CODES[code] ? code : "";
  }

  function withPromo(url) {
    var code = stored();
    if (!code || !url || /[?&]promo=/.test(url) || /[?&]discount=/.test(url)) return url;
    return url + (url.indexOf("?") === -1 ? "?" : "&") + "promo=" + encodeURIComponent(code);
  }

  function note(msg) {
    var el = document.createElement("div");
    el.setAttribute("role", "status");
    el.textContent = msg;
    el.style.cssText = "position:fixed;left:12px;right:12px;bottom:72px;z-index:300;background:#0f172a;color:#fff;padding:12px 14px;border-radius:8px;font:700 14px system-ui,sans-serif;text-align:center";
    document.body.appendChild(el);
  }

  function finish(checkoutId, leave) {
    var dest = "https://apex-hybrid-co-shop.fourthwall.com/checkout/" + encodeURIComponent(checkoutId);
    var code = stored();
    if (!code) {
      leave(dest);
      return;
    }
    fetch("https://apex-hybrid-co-shop.fourthwall.com/api/v2/checkout/" + encodeURIComponent(checkoutId) + "/code", {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ code: code })
    }).then(function (res) {
      if (!res.ok) {
        note("Fourthwall did not accept code " + code + ". Checkout will open without that discount.");
        setTimeout(function () { leave(dest); }, 1600);
      } else {
        leave(dest + "?promo=" + encodeURIComponent(code));
      }
    }).catch(function () {
      note("Fourthwall did not accept code " + code + ". Checkout will open without that discount.");
      setTimeout(function () { leave(dest); }, 1600);
    });
  }

  window.apexStoredCode = stored;
  window.apexPromoUrl = withPromo;
  window.apexFinishCheckout = finish;

  document.addEventListener("click", function (ev) {
    var link = ev.target && ev.target.closest && ev.target.closest('a[href*="fourthwall.com"]');
    if (!link) return;
    var href = link.getAttribute("href") || "";
    var next = withPromo(href);
    if (next !== href) link.setAttribute("href", next);
  }, true);
})();
