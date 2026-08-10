// 全站视频背景板。
// 自动探测 assets/media/bg.mp4 或 assets/media/bg.webm，
// 自动循环播放、静音、支持移动端 playsinline，叠加柔光磨砂蒙版。
(function(){
  var SRC = "assets/media/bg.mp4";
  var POSTER = "assets/media/bg.jpg";
  try { if (localStorage.getItem("wf_bg") === "off") return; } catch(e){}

  if (typeof fetch !== "function") return;
  fetch(SRC, { method: "HEAD" }).then(function(r){
    if(!r.ok) {
      // 备用探测 webm
      fetch("assets/media/bg.webm", { method: "HEAD" }).then(function(r2){
        if(r2.ok) inject("assets/media/bg.webm", POSTER);
      }).catch(function(){});
      return;
    }
    inject(SRC, POSTER);
  }).catch(function(){});

  function inject(src, poster){
    var wrap = document.createElement("div");
    wrap.className = "bg-video";
    var v = document.createElement("video");
    v.autoplay = true; v.muted = true; v.loop = true; v.playsInline = true;
    v.setAttribute("muted",""); v.setAttribute("playsinline","");
    v.setAttribute("autoplay",""); v.setAttribute("loop","");
    if(poster) v.poster = poster;
    v.src = src;
    wrap.appendChild(v);
    var mask = document.createElement("div");
    mask.className = "bg-video-mask";
    document.body.prepend(mask);
    document.body.prepend(wrap);
    document.body.classList.add("has-video");
    try{
      if(window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches){ v.pause(); }
    }catch(e){}
  }
})();
