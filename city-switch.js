(function(){
  var root = (location.pathname.indexOf("/collections/")>=0 || location.pathname.indexOf("/products/")>=0) ? "../" : "";
  function money(n){ return "$"+Number(n); }
  function mount(box, items){
    if(!items || !items.length) return;
    box.innerHTML = '<div class="Pin__grid"><div class="Pin__img"><a class="Pin__hero" data-role="page" href="#"><img data-role="photo" alt="" width="800" height="1000" decoding="async" /></a><div class="Pin__chips" data-role="chips" role="group"></div></div><div><p class="Pin__eyebrow" data-role="label"></p><h2 data-role="title">Race Day Windbreaker</h2><p class="Pin__price" data-role="price"></p><div class="Pin__cta"><a class="Btn Btn--cobalt" data-role="buy" href="#">Buy</a></div></div></div>';
    var chips=box.querySelector("[data-role=chips]");
    function select(item, btn){
      var all=chips.querySelectorAll("button");
      for(var i=0;i<all.length;i++) all[i].setAttribute("aria-pressed", all[i]===btn ? "true" : "false");
      box.querySelector("[data-role=photo]").setAttribute("src", root+item.photo);
      box.querySelector("[data-role=photo]").setAttribute("srcset", root+item.photo+" 2x");
      box.querySelector("[data-role=photo]").setAttribute("alt", item.title);
      box.querySelector("[data-role=page]").setAttribute("href", root+item.page);
      box.querySelector("[data-role=label]").textContent=item.label;
      box.querySelector("[data-role=title]").textContent=item.title;
      box.querySelector("[data-role=price]").textContent="From $"+Number(item.price)+" · Black · Free US shipping";
      var buy=box.querySelector("[data-role=buy]");
      buy.setAttribute("href", item.fourthwall);
      buy.textContent="Buy "+item.city;
    }
    items.forEach(function(item, idx){
      var b=document.createElement("button");
      b.type="button";
      b.textContent=item.city;
      b.setAttribute("aria-pressed", idx===0 ? "true" : "false");
      b.addEventListener("click", function(){ select(item, b); });
      chips.appendChild(b);
      if(idx===0) select(item, b);
    });
  }
  fetch(root+"race-day-switcher.json?v=20261119b").then(function(r){return r.json();}).then(function(data){
    document.querySelectorAll(".CitySwitch").forEach(function(box){
      mount(box, data[box.getAttribute("data-switch")]||[]);
    });
  }).catch(function(){});
})();
