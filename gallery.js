/* Product gallery thumbs. Inline onclick only assigns img.src, and a leftover
   srcset (or a <picture><source>) keeps the lead on screen. This runs for
   every product page that includes it. */
(function () {
  function applyMain(img, src, srcset) {
    if (!img || !src) return;
    var picture = img.closest ? img.closest("picture") : null;
    img.src = src;
    if (srcset) img.setAttribute("srcset", srcset);
    else img.removeAttribute("srcset");
    img.removeAttribute("sizes");
    if (!picture) return;
    var sources = picture.querySelectorAll("source");
    for (var i = 0; i < sources.length; i++) {
      if (srcset) sources[i].setAttribute("srcset", srcset);
      else sources[i].removeAttribute("srcset");
      sources[i].removeAttribute("sizes");
    }
  }

  function chosen(node) {
    if (!node || !node.closest) return null;
    var el = node.closest("button, a, [onclick]");
    if (!el) return null;
    var code = el.getAttribute("onclick") || "";
    var direct = code.match(/staticMainProdImg['"]\)\.src\s*=\s*['"]([^'"]+)['"]/);
    var color = code.match(/selectStaticColor\(\s*['"][^'"]*['"]\s*,\s*['"]([^'"]+)['"]/);
    var src = (direct && direct[1]) || (color && color[1]) || "";
    if (!src) return null;
    var nested = el.querySelector ? el.querySelector("img") : null;
    var srcset = "";
    if (nested && (nested.getAttribute("src") || "").split("?")[0] === src.split("?")[0]) {
      srcset = nested.getAttribute("srcset") || "";
    }
    if (!srcset) srcset = src + " 2x";
    return { src: src, srcset: srcset };
  }

  document.addEventListener("click", function (event) {
    var img = document.getElementById("staticMainProdImg");
    if (!img) return;
    var pick = chosen(event.target);
    if (!pick) return;
    applyMain(img, pick.src, pick.srcset);
  }, true);

  window.setStaticMainImage = function (src, srcset) {
    applyMain(document.getElementById("staticMainProdImg"), src, srcset || (src ? src + " 2x" : ""));
  };
})();
