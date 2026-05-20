"""Static JS for youplot — all chart interactivity."""

# CDN fallback (used only if vendored assets unavailable)
UPLOT_CDN = "https://cdn.jsdelivr.net/npm/uplot@1.6.31/dist/uPlot.iife.min.js"
UPLOT_CSS = "https://cdn.jsdelivr.net/npm/uplot@1.6.31/dist/uPlot.min.css"

JS = r"""
function hexAlpha(hex, alpha) {
  if (!hex) return 'rgba(0,0,0,'+alpha+')';
  if (hex.startsWith('rgba')||hex.startsWith('rgb')) return hex;
  var h=hex.replace('#','');
  if(h.length===3)h=h[0]+h[0]+h[1]+h[1]+h[2]+h[2];
  var r=parseInt(h.slice(0,2),16),g=parseInt(h.slice(2,4),16),b=parseInt(h.slice(4,6),16);
  return 'rgba('+r+','+g+','+b+','+alpha+')';
}

// ── Fill plugin ───────────────────────────────────────────────────────────────
function makeFillPlugin(seriesConfigs) {
  return {hooks:{draw:[function(u){
    seriesConfigs.forEach(function(cfg,si){
      if(!cfg._fill)return;
      var s=u.series[si+1];
      if(!s||s.show===false)return;
      var ctx=u.ctx,sk=s.scale,data=u.data[si+1],b=u.bbox;
      ctx.save();
      ctx.beginPath();ctx.rect(b.left,b.top,b.width,b.height);ctx.clip();
      var grad=ctx.createLinearGradient(0,b.top,0,b.top+b.height);
      var fc=cfg._fillColor||cfg.stroke;
      grad.addColorStop(0,hexAlpha(fc,cfg._fillOpacity||0.15));
      grad.addColorStop(1,hexAlpha(fc,0));
      ctx.fillStyle=grad;ctx.beginPath();
      var first=true,lastX=null;
      for(var i=0;i<data.length;i++){
        var yv=data[i];
        if(yv==null||isNaN(yv)){first=true;continue;}
        var px=u.valToPos(u.data[0][i],'x',true);
        var py=u.valToPos(yv,sk,true);
        if(first){ctx.moveTo(px,b.top+b.height);ctx.lineTo(px,py);first=false;}
        else ctx.lineTo(px,py);
        lastX=px;
      }
      if(lastX!==null)ctx.lineTo(lastX,b.top+b.height);
      ctx.closePath();ctx.fill();ctx.restore();
    });
  }]}};
}

// ── Threshold bands plugin ────────────────────────────────────────────────────
function makeThresholdPlugin(bands) {
  if (!bands || bands.length === 0) return {hooks:{}};
  return {hooks:{draw:[function(u){
    var ctx=u.ctx, b=u.bbox;
    ctx.save();
    ctx.beginPath();ctx.rect(b.left,b.top,b.width,b.height);ctx.clip();
    bands.forEach(function(band){
      var sk  = (band.scale && u.scales[band.scale]) ? band.scale : 'y';
      var y0  = u.valToPos(band.y_lo, sk, true);
      var y1  = u.valToPos(band.y_hi, sk, true);
      var top    = Math.min(y0, y1);
      var height = Math.abs(y1 - y0);
      ctx.fillStyle = hexAlpha(band.color, band.opacity || 0.12);
      ctx.fillRect(b.left, top, b.width, height);
      // draw border lines
      [y0, y1].forEach(function(y){
        ctx.strokeStyle = hexAlpha(band.color, 0.45);
        ctx.lineWidth   = 1;
        ctx.setLineDash([4, 4]);
        ctx.beginPath();
        ctx.moveTo(b.left, y); ctx.lineTo(b.left + b.width, y);
        ctx.stroke();
        ctx.setLineDash([]);
      });
      if (band.label) {
        ctx.fillStyle = hexAlpha(band.color, 0.9);
        ctx.font      = '600 10px sans-serif';
        ctx.fillText(band.label, b.left + 6, Math.min(y0,y1) + 12);
      }
    });
    ctx.restore();
  }]}};
}

// ── Annotation (regions/vlines/hlines) plugin ─────────────────────────────────
function makeAnnotationPlugin(vlines,hlines,regions,isTimeseries){
  return {hooks:{draw:[function(u){
    var ctx=u.ctx,b=u.bbox;
    ctx.save();ctx.beginPath();ctx.rect(b.left,b.top,b.width,b.height);ctx.clip();
    regions.forEach(function(r){
      var x0=u.valToPos(isTimeseries?r.x_start/1000:r.x_start,'x',true);
      var x1=u.valToPos(isTimeseries?r.x_end/1000:r.x_end,'x',true);
      var left = Math.min(x0,x1), width = Math.abs(x1-x0);
      ctx.fillStyle=hexAlpha(r.color,r.opacity);
      ctx.fillRect(left,b.top,width,b.height);
      if (r._tagId && r.label) {
          var hh = 18;
          ctx.fillStyle=hexAlpha(r.color, 1.0);
          ctx.fillRect(left, b.top, width, hh);
          ctx.save();
          ctx.fillStyle="#000";
          ctx.font='600 10px sans-serif';
          ctx.textAlign='center';ctx.textBaseline='middle';
          ctx.beginPath();ctx.rect(left,b.top,width,hh);ctx.clip();
          ctx.fillText(r.label, left+width/2, b.top+hh/2);
          ctx.restore();
      }
    });
    // Measurements
    var measuresToDraw = UP_MEASUREMENTS.slice();
    if(measureAnchorIdx !== null && window._up_currentMeasureIdx !== null) {
        measuresToDraw.push({startX:u.data[0][measureAnchorIdx],endX:u.data[0][window._up_currentMeasureIdx]});
    }
    measuresToDraw.forEach(function(m){
        var x0=u.valToPos(m.startX,'x',true), x1=u.valToPos(m.endX,'x',true);
        var left=Math.min(x0,x1), width=Math.abs(x1-x0);
        ctx.fillStyle="rgba(0,0,0,0.05)"; ctx.fillRect(left,b.top,width,b.height);
        var fh=18;
        ctx.fillStyle="rgba(0,0,0,0.85)"; ctx.fillRect(left,b.top+b.height-fh,width,fh);
        ctx.strokeStyle="rgba(0,0,0,0.6)"; ctx.lineWidth=1; ctx.setLineDash([4,4]);
        ctx.beginPath();
        ctx.moveTo(x0,b.top);ctx.lineTo(x0,b.top+b.height);
        ctx.moveTo(x1,b.top);ctx.lineTo(x1,b.top+b.height);
        ctx.stroke();ctx.setLineDash([]);
    });
    vlines.forEach(function(v){
      var x=u.valToPos(isTimeseries?v.x/1000:v.x,'x',true);
      ctx.strokeStyle=v.color;ctx.lineWidth=v.width;
      ctx.setLineDash(v.dash?[5,4]:[]);
      ctx.beginPath();ctx.moveTo(x,b.top);ctx.lineTo(x,b.top+b.height);ctx.stroke();
      ctx.setLineDash([]);
      if(v.label){ctx.save();ctx.fillStyle=v.color;ctx.font='600 10px sans-serif';ctx.fillText(v.label,x+4,b.top+14);ctx.restore();}
    });
    hlines.forEach(function(h){
      var sk=(h.scale&&u.scales[h.scale])?h.scale:'y';
      var y=u.valToPos(h.y,sk,true);
      ctx.strokeStyle=h.color;ctx.lineWidth=h.width;
      ctx.setLineDash(h.dash?[5,4]:[]);
      ctx.beginPath();ctx.moveTo(b.left,y);ctx.lineTo(b.left+b.width,y);ctx.stroke();
      ctx.setLineDash([]);
      if(h.label){ctx.save();ctx.fillStyle=h.color;ctx.font='600 10px sans-serif';ctx.fillText(h.label,b.left+6,y-5);ctx.restore();}
    });
    ctx.restore();
  }]}};
}

// ── Helpers ───────────────────────────────────────────────────────────────────
function round2(v){return Math.round(v*100)/100;}
function formatVal(v,fmt){
  if(!fmt)return round2(v);
  var m=fmt.match(/\.(\d+)f/);
  return m?v.toFixed(parseInt(m[1])):round2(v);
}
function formatTagDateTime(unixSec, isTimeseries) {
  if (!isTimeseries) return round2(unixSec);
  var d=new Date(unixSec*1000), pad=function(n){return String(n).padStart(2,'0');};
  var months=['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
  return d.getDate()+' '+months[d.getMonth()]+' '+d.getFullYear()+', '+pad(d.getHours())+':'+pad(d.getMinutes())+':'+pad(d.getSeconds());
}

// ── Crosshair sync ────────────────────────────────────────────────────────────
// Global registry: [{u, showTooltipFn, hideTooltipFn}]
if (!window._UP_SYNC_REGISTRY) window._UP_SYNC_REGISTRY = [];

function registerForSync(u, showFn, hideFn) {
  window._UP_SYNC_REGISTRY.push({u: u, show: showFn, hide: hideFn});
}

function syncCrosshair(sourceU, idx, sourceClientX, sourceClientY) {
  var xVal = sourceU.data[0][idx];
  window._UP_SYNC_REGISTRY.forEach(function(entry) {
    if (entry.u === sourceU) return;
    try {
      var u = entry.u;
      var left = u.valToPos(xVal, 'x');
      var midY = (u.over.offsetHeight || 100) / 2;
      u.setCursor({left: left, top: midY});
      // Show tooltip on synced chart using its own renderer
      if (entry.show) entry.show(idx, xVal, sourceClientX, sourceClientY);
    } catch(e){}
  });
}

function clearSyncCrosshair(sourceU) {
  window._UP_SYNC_REGISTRY.forEach(function(entry) {
    if (entry.u === sourceU) return;
    try {
      entry.u.setCursor({left: -10, top: -10});
      if (entry.hide) entry.hide();
    } catch(e){}
  });
}

// ── State ─────────────────────────────────────────────────────────────────────
var uplotInst=null;
var seriesVisible=[];
var legendEls=[];
var lastClickTime=0,lastClickIdx=-1,DBLCLICK_MS=300;
var tooltipEl=null;
var initialScales=null;

// Tool state
var currentTool = 'zoom';
var activeTagRegion = null;
var tagColors = ['#FF00FF','#00FFFF','#00FF00','#FFFF00','#FF00AA','#00FF88','#FF8800','#8800FF'];
var tagColorIdx = 0;

// Measure state (line only)
var measureAnchorIdx = null;
var UP_MEASUREMENTS = [];
window._up_currentMeasureIdx = null;

// Annotation pins state
var UP_PINS = [];   // {id, x, y_px_frac, label, color}
var pinDragId = null;

var scatterVisible = {};

// ── Legend ────────────────────────────────────────────────────────────────────
function scatterLegendClick(el, scIdx){
  var now=Date.now(), isDbl=(now-lastClickTime<DBLCLICK_MS)&&(lastClickIdx==='sc'+scIdx);
  lastClickTime=now;lastClickIdx='sc'+scIdx;
  if(isDbl){
    var allHidden=true;
    UP_SCATTER_CFG.forEach(function(s){if(s._scatterIdx!==scIdx&&s.visible!==false)allHidden=false;});
    UP_SCATTER_CFG.forEach(function(s){s.visible=allHidden?true:(s._scatterIdx===scIdx);});
    var lc=document.getElementById(UP_CONTAINER_ID).closest('.up-card');
    if(lc)lc.querySelectorAll('.up-leg-item[data-kind="scatter"]').forEach(function(e){
      var idx=parseInt(e.dataset.si.replace('sc-',''));
      var cfg=UP_SCATTER_CFG.find(function(s){return s._scatterIdx===idx;});
      e.classList.toggle('up-leg-off',cfg&&cfg.visible===false);
    });
  } else {
    var scfg=UP_SCATTER_CFG.find(function(s){return s._scatterIdx===scIdx;});
    if(scfg)scfg.visible=(scfg.visible===false)?true:false;
    el.classList.toggle('up-leg-off',scfg&&scfg.visible===false);
  }
  if(uplotInst)uplotInst.redraw();
}

function legendClick(el,si){
  var now=Date.now(), isDbl=(now-lastClickTime<DBLCLICK_MS)&&(lastClickIdx===si);
  lastClickTime=now;lastClickIdx=si;
  if(isDbl){
    var anyOther=false;
    for(var i=1;i<seriesVisible.length;i++){if(i!==si&&seriesVisible[i]){anyOther=true;break;}}
    for(var i=1;i<seriesVisible.length;i++){
      var show=anyOther?(i===si):true;
      seriesVisible[i]=show;
      uplotInst.setSeries(i,{show:show});
      legendEls[i]&&legendEls[i].classList.toggle('up-leg-off',!show);
    }
  } else {
    seriesVisible[si]=!seriesVisible[si];
    uplotInst.setSeries(si,{show:seriesVisible[si]});
    el.classList.toggle('up-leg-off',!seriesVisible[si]);
  }
}

// ── Tooltip ───────────────────────────────────────────────────────────────────
function buildTooltipHtml(u, idx) {
  var tsVal = u.data[0][idx];
  var timeStr = UP_IS_TIMESERIES
    ? (new Date(tsVal*1000)).toLocaleString('en-IN',{timeZone:'Asia/Kolkata',hour12:false,day:'2-digit',month:'short',hour:'2-digit',minute:'2-digit',second:'2-digit'})+' IST'
    : String(round2(tsVal));
  var html = '<div class="up-tooltip-time">'+timeStr+'</div>';
  var xVal = UP_IS_TIMESERIES ? tsVal*1000 : tsVal;
  UP_REGIONS.forEach(function(r){
    if(r._tagId&&r.label&&xVal>=Math.min(r.x_start,r.x_end)&&xVal<=Math.max(r.x_start,r.x_end)){
      html += '<div class="up-tooltip-row" style="background:'+hexAlpha(r.color,0.15)+';border-radius:4px;padding:3px 6px;margin-bottom:6px;border:1px solid '+hexAlpha(r.color,0.3)+';">'
        +'<span class="up-tooltip-dot" style="background:'+r.color+'"></span>'
        +'<span class="up-tooltip-name" style="font-weight:600;color:'+r.color+';">Tag: '+r.label+'</span></div>';
    }
  });
  var hasVal = false;
  UP_SERIES_CFG.slice(1).forEach(function(cfg,i){
    var si=i+1;
    if(!seriesVisible[si])return;
    var val=u.data[si]?u.data[si][idx]:null;
    if(val==null||isNaN(val))return;
    hasVal=true;
    var display=cfg._hoverFormat?formatVal(val,cfg._hoverFormat):round2(val);
    html+='<div class="up-tooltip-row"><span class="up-tooltip-dot" style="background:'+cfg.stroke+'"></span>'
      +'<span class="up-tooltip-name">'+(cfg.label||'')+'</span>'
      +'<span class="up-tooltip-val" style="color:'+cfg.stroke+'">'+display+(cfg._hoverUnit||'')+'</span></div>';
  });
  return hasVal ? html : null;
}

function showTooltipAt(html, clientX, clientY) {
  if(!tooltipEl)return;
  tooltipEl.innerHTML = html;
  tooltipEl.style.display = 'block';
  var tw = tooltipEl.offsetWidth||200;
  var left = clientX+18;
  if(left+tw>window.innerWidth-12) left=clientX-tw-18;
  var top = clientY-10;
  if(top+130>window.innerHeight) top=clientY-130;
  tooltipEl.style.left=left+'px'; tooltipEl.style.top=top+'px';
}

function attachLineTooltip(u){
  // Capture THIS chart's tooltip element in a local variable — never reassign it.
  // (tooltipEl is the IIFE-scoped var used elsewhere; myTip is this chart's own)
  var myTip = document.getElementById(UP_TOOLTIP_ID);
  tooltipEl = myTip;  // keep the shared var pointing here too for non-sync use
  if(!myTip) return;

  function showForIdx(idx, xValOverride, clientX, clientY) {
    // Render THIS chart's series data into THIS chart's tooltip element
    var html = buildTooltipHtml(u, idx);
    if(!html){ myTip.style.display='none'; return; }
    // Position near the mouse that triggered the sync
    myTip.innerHTML = html;
    myTip.style.display = 'block';
    var tw = myTip.offsetWidth || 200;
    // Place tooltip just below the other chart's cursor, near top of this chart
    var rect = u.over.getBoundingClientRect();
    var left = rect.left + u.valToPos(u.data[0][idx], 'x') + 18;
    if(left + tw > window.innerWidth - 12) left = left - tw - 36;
    var top = rect.top + 8;
    myTip.style.left = left + 'px';
    myTip.style.top  = top  + 'px';
  }

  registerForSync(u, showForIdx, function(){ myTip.style.display='none'; });

  u.over.addEventListener('mousemove',function(e){
    if(UP_HAS_SCATTER)return;
    var rect=u.over.getBoundingClientRect();
    var cx=e.clientX-rect.left;
    var idx=u.posToIdx(cx);
    if(idx==null||idx<0||idx>=u.data[0].length){ myTip.style.display='none'; return; }
    syncCrosshair(u, idx, e.clientX, e.clientY);
    var html = buildTooltipHtml(u, idx);
    if(!html){ myTip.style.display='none'; return; }
    myTip.innerHTML = html;
    myTip.style.display = 'block';
    var tw = myTip.offsetWidth||200;
    var left = e.clientX+18;
    if(left+tw>window.innerWidth-12) left=e.clientX-tw-18;
    var top = e.clientY-10;
    if(top+130>window.innerHeight) top=e.clientY-130;
    myTip.style.left=left+'px'; myTip.style.top=top+'px';
  });
  u.over.addEventListener('mouseleave',function(){
    myTip.style.display='none';
    clearSyncCrosshair(u);
  });
}

function attachMixedTooltip(u){
  tooltipEl=document.getElementById(UP_TOOLTIP_ID);
  if(!tooltipEl)return;
  registerForSync(u, null, function(){ if(tooltipEl)tooltipEl.style.display='none'; });
  u.over.addEventListener('mousemove',function(e){
    var rect=u.over.getBoundingClientRect();
    var idx=u.posToIdx(e.clientX-rect.left);
    if(idx!=null&&idx>=0) syncCrosshair(u, idx, e.clientX, e.clientY);
  });
  u.over.addEventListener('mouseleave',function(){
    if(tooltipEl)tooltipEl.style.display='none';
    clearSyncCrosshair(u);
  });
}
// ── Tag bubble list ───────────────────────────────────────────────────────────
function renderTagBubbles(tagsList) {
  if (!tagsList) return;
  // Remove only tag bubbles — preserve annotation (up-ann-item) rows
  var existing = tagsList.querySelector('.up-tag-bubbles');
  if (existing) existing.remove();
  var existingLabel = tagsList.querySelector('.up-list-section-label.for-tags');
  if (existingLabel) existingLabel.remove();

  var bubbleWrap=document.createElement('div');
  bubbleWrap.className='up-tag-bubbles';
  UP_REGIONS.forEach(function(r){
    if(!r._tagId) return;
    var bubble=document.createElement('span');
    bubble.className='up-tag-bubble';
    bubble.style.background=hexAlpha(r.color,0.18);
    bubble.style.borderColor=hexAlpha(r.color,0.5);
    bubble.style.color=r.color;
    var s0=UP_IS_TIMESERIES?r.x_start/1000:r.x_start;
    var s1=UP_IS_TIMESERIES?r.x_end/1000:r.x_end;
    bubble.title=formatTagDateTime(s0,UP_IS_TIMESERIES)+' → '+formatTagDateTime(s1,UP_IS_TIMESERIES);
    var nameSpan=document.createElement('span');
    nameSpan.className='up-tag-bubble-name';nameSpan.textContent=r.label;
    bubble.appendChild(nameSpan);
    bubble.addEventListener('click',function(ev){
      if(ev.target.classList.contains('up-tag-bubble-del'))return;
      var pad=(s1-s0)*0.15;
      uplotInst.setScale('x',{min:s0-pad,max:s1+pad});
    });
    if(r._removable!==false){
      var delBtn=document.createElement('button');
      delBtn.className='up-tag-bubble-del';delBtn.title='Remove';delBtn.innerHTML='&times;';
      delBtn.addEventListener('click',function(ev){
        ev.stopPropagation();
        var idx=UP_REGIONS.indexOf(r);
        if(idx!==-1)UP_REGIONS.splice(idx,1);
        if(uplotInst)uplotInst.redraw();
        renderTagBubbles(tagsList);
      });
      bubble.appendChild(delBtn);
    }
    bubbleWrap.appendChild(bubble);
  });
  if(bubbleWrap.children.length>0){
    // Insert tags section before any annotation items
    var firstAnn = tagsList.querySelector('.up-ann-section');
    if (firstAnn) {
      tagsList.insertBefore(bubbleWrap, firstAnn);
    } else {
      tagsList.insertBefore(bubbleWrap, tagsList.firstChild);
    }
  }
}

// ── Annotation pins (Figma-style) ─────────────────────────────────────────────
function positionPinEl(u, pinEl, pin) {
  var b   = u.bbox;
  var dpr = window.devicePixelRatio || 1;
  var xSec = UP_IS_TIMESERIES ? pin.x / 1000 : pin.x;
  // Hide pin when x is outside the visible scale range
  var sc = u.scales.x;
  if (sc && (xSec < sc.min || xSec > sc.max)) {
    pinEl.style.display = 'none';
    return;
  }
  pinEl.style.display = '';
  var xPos = u.valToPos(xSec, 'x', true);
  xPos = Math.max(b.left, Math.min(b.left + b.width, xPos));

  var yPos;
  if (pin.y != null) {
    var sk = 'y';
    if (pin.scale === 'left') sk = 'y';
    else if (pin.scale === 'right') sk = 'y2';
    else if (pin.scale && u.scales[pin.scale]) sk = pin.scale;
    yPos = u.valToPos(pin.y, sk, true);
  } else {
    var frac = (pin.y_frac != null) ? pin.y_frac : 0.2;
    yPos = b.top + frac * b.height;
  }
  yPos = Math.max(b.top, Math.min(b.top + b.height, yPos));

  // pins layer is offset to (b.left/dpr, b.top/dpr) — subtract origin, convert to CSS px
  pinEl.style.left = ((xPos - b.left) / dpr - 10) + 'px';
  pinEl.style.top  = ((yPos - b.top)  / dpr - 10) + 'px';
}

var pinColors = [
  '#f59e0b', // amber
  '#10b981', // emerald
  '#6366f1', // indigo
  '#f43f5e', // rose
  '#06b6d4', // cyan
  '#8b5cf6', // violet
  '#f97316', // orange
  '#84cc16', // lime
  '#ec4899', // pink
  '#14b8a6', // teal
];
if (typeof window._UP_PIN_COLOR_IDX === 'undefined') window._UP_PIN_COLOR_IDX = 0;
var pinColorIdx = 0; // local alias, reads/writes window._UP_PIN_COLOR_IDX

function buildPinEl(u, pin, pinsLayer, tagsList) {
  // Assign a color if not set
  if (!pin.color) {
    pin.color = pinColors[window._UP_PIN_COLOR_IDX % pinColors.length];
    window._UP_PIN_COLOR_IDX++;
  }

  // ── Marker on canvas ──────────────────────────────────────────────────────
  var el = document.createElement('div');
  el.className = 'up-pin';
  el.id = 'pin-' + pin.id;

  var icon = document.createElement('div');
  icon.className = 'up-pin-icon';
  icon.style.background = pin.color;
  icon.textContent = pin.label ? pin.label[0].toUpperCase() : '✎';
  el.appendChild(icon);

  var popup = document.createElement('div');
  popup.className = 'up-pin-popup';
  popup.innerHTML = '<div class="up-pin-popup-label">'+escapeHtml(pin.label)+'</div>'
    +'<div class="up-pin-popup-time">'+formatTagDateTime(UP_IS_TIMESERIES?pin.x/1000:pin.x, UP_IS_TIMESERIES)+'</div>';
  el.appendChild(popup);

  var delMarker = document.createElement('button');
  delMarker.className = 'up-pin-del';
  delMarker.innerHTML = '&times;';
  delMarker.title = 'Delete annotation';
  el.appendChild(delMarker);

  positionPinEl(u, el, pin);
  pinsLayer.appendChild(el);

  // ── Entry in the notes list below ────────────────────────────────────────
  var listItem = null;
  if (tagsList) {
    // Ensure annotations section container exists
    var annSection = tagsList.querySelector('.up-ann-section');
    if (!annSection) {
      annSection = document.createElement('div');
      annSection.className = 'up-ann-section';
      var sectionLabel = document.createElement('div');
      sectionLabel.className = 'up-list-section-label';
      sectionLabel.textContent = 'Annotations';
      annSection.appendChild(sectionLabel);
      // Wrap for flex-row sticky notes layout
      var notesWrap = document.createElement('div');
      notesWrap.className = 'up-ann-notes-wrap';
      annSection.appendChild(notesWrap);
      tagsList.appendChild(annSection);
    }
    var notesWrap = annSection.querySelector('.up-ann-notes-wrap');

    listItem = document.createElement('div');
    listItem.className = 'up-ann-item';
    listItem.id = 'ann-item-' + pin.id;

    // Sticky note background + folded corner tinted with pin color
    var cornerColor = hexAlpha(pin.color, 0.45);
    listItem.style.backgroundImage = 'linear-gradient(135deg, '+cornerColor+' 0px, '+cornerColor+' 12px, transparent 12px)';
    listItem.style.backgroundColor = hexAlpha(pin.color, 0.28);

    // Slight alternating tilt for the "scattered notes" feel
    var noteCount = notesWrap.children.length;
    var tilt = (noteCount % 2 === 0) ? 'rotate(-1.5deg)' : 'rotate(1deg)';
    listItem.style.transform = tilt;

    // Text block
    var body = document.createElement('div');
    body.className = 'up-ann-item-body';

    var labelEl = document.createElement('div');
    labelEl.className = 'up-ann-item-label';
    labelEl.textContent = pin.label;

    var timeEl = document.createElement('div');
    timeEl.className = 'up-ann-item-time';
    timeEl.textContent = formatTagDateTime(UP_IS_TIMESERIES?pin.x/1000:pin.x, UP_IS_TIMESERIES);

    body.appendChild(labelEl);
    body.appendChild(timeEl);

    var delList = document.createElement('button');
    delList.className = 'up-tag-del';
    delList.innerHTML = '&times;';
    delList.title = 'Delete annotation';

    // Invisible dot (kept for delete logic compat)
    var dot = document.createElement('span');
    dot.className = 'up-ann-item-dot';

    listItem.appendChild(dot);
    listItem.appendChild(body);
    listItem.appendChild(delList);

    // Navigate to pin on click
    listItem.addEventListener('click', function(ev) {
      if(ev.target === delList) return;
      var pad = (u.scales.x.max - u.scales.x.min) * 0.05;
      var xSec = UP_IS_TIMESERIES ? pin.x/1000 : pin.x;
      u.setScale('x', {min: xSec - pad, max: xSec + pad});
    });

    notesWrap.appendChild(listItem);
  }

  // Shared delete logic
  function doDelete(e) {
    e.stopPropagation();
    UP_PINS = UP_PINS.filter(function(p){return p.id !== pin.id;});
    el.remove();
    if(listItem) {
      listItem.remove();
      // Remove the annotations section if no more notes remain
      if(tagsList) {
        var sec = tagsList.querySelector('.up-ann-section');
        var wrap = sec ? sec.querySelector('.up-ann-notes-wrap') : null;
        if(wrap && wrap.children.length === 0) sec.remove();
      }
    }
  }
  delMarker.addEventListener('click', doDelete);
  if(listItem) listItem.querySelector('.up-tag-del').addEventListener('click', doDelete);

  return el;
}

function escapeHtml(s) {
  return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}

// ── HTML Export ───────────────────────────────────────────────────────────────
function exportAsHtml() {
  // Clone the entire document so we never touch the live DOM.
  var docClone = document.documentElement.cloneNode(true);

  // Clear uPlot-rendered DOM from chart containers in the CLONE only.
  // (Leaving them populated causes double-chart when JS re-runs on open.)
  docClone.querySelectorAll('[id^="up-chart-"]').forEach(function(el) {
    el.innerHTML = '';
  });
  // Clear pins layer in clone (pins are re-created by JS on load)
  docClone.querySelectorAll('.up-pins-layer').forEach(function(el) {
    el.innerHTML = '';
  });
  // Clear tags list in clone (bubbles + sticky notes are re-created by JS on load)
  docClone.querySelectorAll('.up-tags-list').forEach(function(el) {
    el.innerHTML = '';
  });
  // Hide tooltip in clone (it may have stale position/content)
  docClone.querySelectorAll('.up-tooltip').forEach(function(el) {
    el.style.display = 'none';
  });

  var html = '<!DOCTYPE html>\n' + docClone.outerHTML;

  // Persist runtime state: UP_REGIONS (tags) and interactive-only pins.
  // Code pins (UP_CODE_PINS) are already in the JS source — don't duplicate them.
  var codePinIds = {};
  if (typeof UP_CODE_PINS !== 'undefined') {
    UP_CODE_PINS.forEach(function(p) { codePinIds[p.id] = true; });
  }
  var interactivePins = UP_PINS.filter(function(p) { return !codePinIds[p.id]; });

  var regionsPatch = '<script id="up-state-patch">'
    + 'window._UP_REGIONS_PATCH=window._UP_REGIONS_PATCH||{};'
    + 'window._UP_REGIONS_PATCH["' + UP_CONTAINER_ID + '"]='
    + JSON.stringify(UP_REGIONS) + ';'
    + 'window._UP_PINS_PATCH=window._UP_PINS_PATCH||{};'
    + 'window._UP_PINS_PATCH["' + UP_CONTAINER_ID + '"]='
    + JSON.stringify(interactivePins) + ';'
    + '<\/script>';

  // Fix up-page padding
  html = html.replace(/\.up-page\{[^}]*\}/g, '.up-page{max-width:100%;padding:0}');

  // Move any <style> tags inside <body> into <head>
  var headEndIdx = html.indexOf('</head>');
  if (headEndIdx !== -1) {
    var head = html.slice(0, headEndIdx);
    var rest = html.slice(headEndIdx);
    var bodyStyles = [];
    var cleanRest = rest.replace(/<style[\s\S]*?<\/style>/gi, function(s) {
      bodyStyles.push(s);
      return '';
    });
    html = head + '\n' + bodyStyles.join('\n') + '\n' + regionsPatch + '\n' + cleanRest;
  }

  var blob = new Blob([html], {type:'text/html'});
  var a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  var now = new Date();
  a.download = 'chart-' + now.toISOString().slice(0,19).replace(/[:.]/g,'-') + '.html';
  a.click();
  URL.revokeObjectURL(a.href);
}

// ── Show measure bar ──────────────────────────────────────────────────────────
function buildShowMeasureBar(mBar, mDetails) {
  return function showMeasureBar(timeStr, yDeltas, mId) {
    if(!mBar) return;
    var html='<div class="up-m-stat">ΔX: <span class="up-m-val">'+timeStr+'</span></div>';
    yDeltas.forEach(function(d){
      var sign=d.diff>0?'+':'';
      html+='<div class="up-m-stat"><span class="up-tooltip-dot" style="background:'+d.color+'"></span>'+d.label+': <span class="up-m-val" style="color:'+d.color+'">'+sign+formatVal(d.diff,d.fmt)+'</span></div>';
    });
    mDetails.innerHTML=html;
    mBar.style.display='flex';
    if(mId)mBar.dataset.mid=mId; else mBar.dataset.mid='';
  };
}

// ── Build chart ───────────────────────────────────────────────────────────────
function buildChart(){
  var container=document.getElementById(UP_CONTAINER_ID);

  // Restore any state that was captured at export time
  if (window._UP_REGIONS_PATCH && window._UP_REGIONS_PATCH[UP_CONTAINER_ID]) {
    UP_REGIONS = window._UP_REGIONS_PATCH[UP_CONTAINER_ID];
    delete window._UP_REGIONS_PATCH[UP_CONTAINER_ID];
  }
  if (window._UP_PINS_PATCH && window._UP_PINS_PATCH[UP_CONTAINER_ID]) {
    UP_PINS = window._UP_PINS_PATCH[UP_CONTAINER_ID];
    delete window._UP_PINS_PATCH[UP_CONTAINER_ID];
  }

  var card=container.closest('.up-card');
  var W=container.offsetWidth||window.innerWidth;
  var allData=[UP_X_DATA].concat(UP_Y_DATA);
  var isScatterOnly = UP_HAS_SCATTER && UP_SERIES_CFG.filter(function(s,i){return i>0&&s.stroke!=='rgba(0,0,0,0)';}).length===0;

  // Tool buttons
  var toolBtns=card?card.querySelectorAll('.up-tool-btn'):[];
  toolBtns.forEach(function(btn){
    // Hide tag + measure for scatter charts
    if (isScatterOnly && (btn.dataset.tool==='tag'||btn.dataset.tool==='measure'||btn.dataset.tool==='annotate')) {
      btn.style.display='none'; return;
    }
    btn.addEventListener('click',function(e){
      e.preventDefault();
      toolBtns.forEach(function(b){b.classList.remove('active');});
      btn.classList.add('active');
      currentTool=btn.dataset.tool;
      if(currentTool==='measure'){
        container.classList.add('up-measure-mode');
      } else {
        container.classList.remove('up-measure-mode');
        measureAnchorIdx=null;
        var bar=document.getElementById('up-measure-bar-'+UP_CONTAINER_ID.replace('up-chart-',''));
        if(bar)bar.style.display='none';
        if(uplotInst)uplotInst.redraw();
      }
    });
  });

  // Prompt
  var tagPrompt=card?card.querySelector('.up-tag-prompt'):null;
  var tagInput=card?card.querySelector('.up-tag-input'):null;
  var btnCancel=card?card.querySelector('[id^="up-tag-cancel-"]'):null;
  var btnSave=card?card.querySelector('[id^="up-tag-save-"]'):null;
  var tagsList=card?card.querySelector('.up-tags-list'):null;

  // Pins layer (overlay on uPlot canvas area)
  var pinsLayer=card?card.querySelector('.up-pins-layer'):null;

  // Annotation prompt (for pins)
  var annPrompt=card?card.querySelector('.up-ann-prompt'):null;
  var annInput=card?card.querySelector('.up-ann-input'):null;
  var annCancel=card?card.querySelector('[id^="up-ann-cancel-"]'):null;
  var annSave=card?card.querySelector('[id^="up-ann-save-"]'):null;
  var pendingPinPos=null;

  if(tagPrompt && btnCancel && btnSave && tagInput){
    btnCancel.addEventListener('click',function(e){e.preventDefault();tagPrompt.style.display='none';activeTagRegion=null;});
    btnSave.addEventListener('click',function(e){
      e.preventDefault();
      var name=tagInput.value.trim()||'Untitled';
      tagPrompt.style.display='none';
      if(activeTagRegion){
        var tagId='tag_'+Date.now(), color=tagColors[tagColorIdx%tagColors.length]; tagColorIdx++;
        UP_REGIONS.push({x_start:activeTagRegion.min*(UP_IS_TIMESERIES?1000:1),x_end:activeTagRegion.max*(UP_IS_TIMESERIES?1000:1),color:color,opacity:0.05,label:name,_tagId:tagId,_removable:true});
        if(uplotInst)uplotInst.redraw();
        renderTagBubbles(tagsList);
        activeTagRegion=null;
      } else if(window._activeMeasureRegion){
        var mId='m_'+Date.now();
        var mn=Math.min(window._activeMeasureRegion.min,window._activeMeasureRegion.max);
        var mx=Math.max(window._activeMeasureRegion.min,window._activeMeasureRegion.max);
        UP_MEASUREMENTS.push({id:mId,startIdx:uplotInst.valToIdx(mn),endIdx:uplotInst.valToIdx(mx),startX:mn,endX:mx,label:name});
        if(uplotInst)uplotInst.redraw();
        window._activeMeasureRegion=null;
      }
    });
    tagInput.addEventListener('keydown',function(e){if(e.key==='Enter'){e.preventDefault();btnSave.click();}else if(e.key==='Escape'){e.preventDefault();btnCancel.click();}});
  }

  if(annPrompt && annSave && annCancel && annInput) {
    annCancel.addEventListener('click',function(e){e.preventDefault();annPrompt.style.display='none';pendingPinPos=null;});
    annSave.addEventListener('click',function(e){
      e.preventDefault();
      var name=annInput.value.trim()||'Note';
      annPrompt.style.display='none';
      if(pendingPinPos && uplotInst){
        var pin={id:'pin_'+Date.now(),x:pendingPinPos.x,y_frac:pendingPinPos.y_frac,y:pendingPinPos.y,label:name,color:null};
        UP_PINS.push(pin);
        buildPinEl(uplotInst, pin, pinsLayer, tagsList);
        pendingPinPos=null;
      }
    });
    annInput.addEventListener('keydown',function(e){if(e.key==='Enter'){e.preventDefault();annSave.click();}else if(e.key==='Escape'){e.preventDefault();annCancel.click();}});
  }

  var fillPlugin=makeFillPlugin(UP_SERIES_CFG.slice(1));
  var threshPlugin=makeThresholdPlugin(UP_BANDS||[]);
  var annPlugin=makeAnnotationPlugin(UP_VLINES,UP_HLINES,UP_REGIONS,UP_IS_TIMESERIES);
  var scatterPlugin=UP_HAS_SCATTER?window._makeScatterPlugin(UP_SCATTER_CFG,UP_TOOLTIP_ID,UP_REGIONS,UP_IS_TIMESERIES):null;
  var plugins=UP_HAS_SCATTER?[fillPlugin,threshPlugin,annPlugin,scatterPlugin]:[fillPlugin,threshPlugin,annPlugin];

  var mBar=card?card.querySelector('.up-measure-bar'):null;
  var mDetails=card?card.querySelector('.up-measure-details'):null;
  var showMeasureBar=buildShowMeasureBar(mBar,mDetails);

  // Y-drag zoom state
  var yDragStart=null;

  var opts={
    width:W, height:UP_HEIGHT,
    plugins:plugins,
    select:{show:true},
    cursor:{
      drag:{x:true,y:false,uni:20},  // we handle Y manually
      bind:{
        dblclick:function(u,targ,handler){
          return function(e){e.preventDefault();upResetZoom();return null;};
        }
      },
      points:{
        size:function(u,si){return 8;},
        fill:function(u,si){return u.series[si].stroke||'#fff';},
        stroke:function(u,si){return u.series[si].stroke||'#000';},
        width:2,
      },
    },
    legend:{show:false},
    scales:UP_SCALES,
    axes:UP_AXES,
    series:UP_SERIES_CFG,
    hooks:{
      ready:[function(u){
        initialScales={};
        Object.keys(u.scales).forEach(function(k){
          var sc=u.scales[k];
          initialScales[k]={min:sc.min,max:sc.max};
        });
        registerForSync(u);
        if(UP_HAS_SCATTER)attachMixedTooltip(u); else attachLineTooltip(u);
        renderTagBubbles(tagsList);

        // Position pins layer over plot
        if(pinsLayer){
          pinsLayer.style.position='absolute';
          var b=u.bbox,dpr=window.devicePixelRatio||1;
          pinsLayer.style.left=(b.left/dpr)+'px';
          pinsLayer.style.top=(b.top/dpr)+'px';
          pinsLayer.style.width=(b.width/dpr)+'px';
          pinsLayer.style.height=(b.height/dpr)+'px';
        }

        // ── Mouse events ──────────────────────────────────────────────────
        u.over.addEventListener('mousemove',function(e){
          var rect=u.over.getBoundingClientRect();
          var cx=e.clientX-rect.left, cy=e.clientY-rect.top;
          var idx=u.posToIdx(cx);
          if(idx==null||idx<0)return;

          // Y-axis drag zoom: detect vertical drag (more Y movement than X)
          if(yDragStart!==null&&currentTool==='zoom'){
            var dx=Math.abs(cx-yDragStart.cx), dy=cy-yDragStart.cy, dyAbs=Math.abs(dy);
            // Once committed to vertical drag, keep going; commit when dy>dx and dy>8px
            if(yDragStart.dragging||(dyAbs>8&&dyAbs>dx*1.5)){
              yDragStart.dragging=true;
              if(dyAbs>1){
                var sks=Object.keys(u.scales).filter(function(k){return k!=='x';});
                sks.forEach(function(sk){
                  var sc=u.scales[sk]; if(!sc)return;
                  var range=sc.max-sc.min;
                  // drag down = zoom out (expand), drag up = zoom in (contract)
                  var factor=dy/300;
                  var newMin=sc.min+range*factor*0.5;
                  var newMax=sc.max-range*factor*0.5;
                  if(newMax-newMin>1e-9)u.setScale(sk,{min:newMin,max:newMax});
                });
                yDragStart.cy=cy;
              }
              return; // prevent uPlot's own x-drag selection while doing y-drag
            }
          }

          if(currentTool==='measure'&&measureAnchorIdx!==null){
            window._up_currentMeasureIdx=idx;
            var yDeltas=[];
            UP_SERIES_CFG.slice(1).forEach(function(cfg,i){
              var si=i+1; if(!seriesVisible[si])return;
              var y1=u.data[si][measureAnchorIdx],y2=u.data[si][idx];
              if(y1!=null&&y2!=null)yDeltas.push({label:cfg.label||'Series '+si,color:cfg.stroke,diff:y2-y1,fmt:cfg._hoverFormat});
            });
            var t1=u.data[0][measureAnchorIdx],t2=u.data[0][idx],tDiff=Math.abs(t2-t1);
            var tStr=UP_IS_TIMESERIES?(tDiff<60?round2(tDiff)+'s':tDiff<3600?Math.floor(tDiff/60)+'m '+round2(tDiff%60)+'s':Math.floor(tDiff/3600)+'h '+Math.floor((tDiff%3600)/60)+'m'):round2(tDiff);
            showMeasureBar(tStr,yDeltas,null);
            u.redraw();
          } else {
            window._up_currentMeasureIdx=null;
            var tsVal=u.data[0][idx], hoveredId=null;
            for(var j=0;j<UP_MEASUREMENTS.length;j++){
              var m=UP_MEASUREMENTS[j];
              var mMin=Math.min(m.startX,m.endX),mMax=Math.max(m.startX,m.endX);
              if(tsVal>=mMin&&tsVal<=mMax){
                hoveredId=m.id;
                var yDeltas=[];
                UP_SERIES_CFG.slice(1).forEach(function(cfg,i){
                  var si=i+1;if(!seriesVisible[si])return;
                  var y1=u.data[si][m.startIdx],y2=u.data[si][m.endIdx];
                  if(y1!=null&&y2!=null)yDeltas.push({label:cfg.label||'Series '+si,color:cfg.stroke,diff:y2-y1,fmt:cfg._hoverFormat});
                });
                var tDiff=Math.abs(m.endX-m.startX);
                var tStr=UP_IS_TIMESERIES?(tDiff<60?round2(tDiff)+'s':tDiff<3600?Math.floor(tDiff/60)+'m '+round2(tDiff%60)+'s':Math.floor(tDiff/3600)+'h '+Math.floor((tDiff%3600)/60)+'m'):round2(tDiff);
                showMeasureBar(tStr,yDeltas,m.id);
                break;
              }
            }
            if(!hoveredId){if(mBar)mBar.style.display='none';if(currentTool==='measure')u.redraw();}
          }
        });

        u.over.addEventListener('mousedown',function(e){
          var rect=u.over.getBoundingClientRect();
          var cx=e.clientX-rect.left, cy=e.clientY-rect.top;
          var idx=u.posToIdx(cx);
          if(idx==null)return;

          // Start Y-drag tracking on left-button (we detect vertical vs horizontal later)
          if(e.button===0&&currentTool==='zoom'){
            yDragStart={cx:cx, cy:cy, dragging:false};
          }

          // Bottom measure bar click-to-delete
          if(cy>=u.bbox.height-18&&cy<=u.bbox.height){
            var tsVal=u.data[0][idx];
            for(var j=0;j<UP_MEASUREMENTS.length;j++){
              var m=UP_MEASUREMENTS[j];
              if(tsVal>=Math.min(m.startX,m.endX)&&tsVal<=Math.max(m.startX,m.endX)){
                UP_MEASUREMENTS.splice(j,1);
                if(mBar)mBar.style.display='none';
                u.redraw();e.stopPropagation();return;
              }
            }
          }

          if(currentTool==='measure'){
            if(e.button===2){
              if(measureAnchorIdx!==null){
                window._activeMeasureRegion={min:u.data[0][measureAnchorIdx],max:u.data[0][idx]};
                if(tagPrompt){tagPrompt.style.display='flex';tagInput.value='';setTimeout(function(){tagInput.focus();},10);}
                measureAnchorIdx=null;window._up_currentMeasureIdx=null;u.redraw();
              }
            } else if(e.button===0){
              measureAnchorIdx=measureAnchorIdx===null?idx:null;
              if(measureAnchorIdx===null){window._up_currentMeasureIdx=null;if(mBar)mBar.style.display='none';}
              u.redraw();
            }
          }

          // Annotate mode: left click drops a pin
          if(currentTool==='annotate'&&e.button===0){
            var b=u.bbox, dpr=window.devicePixelRatio||1;
            var xVal=u.posToVal(cx,'x');
            // cx/cy are CSS px from getBoundingClientRect.
            // b.top is canvas (physical) px — divide by dpr to get CSS px offset.
            var plotH = u.over.offsetHeight || b.height / (window.devicePixelRatio||1);
            var y_frac = Math.max(0, Math.min(1, cy / plotH));
            var y_val = u.posToVal(cy, 'y');
            pendingPinPos={
              x: UP_IS_TIMESERIES?xVal*1000:xVal,
              y_frac: y_frac,
              y: y_val
            };
            if(annPrompt && annInput){
              annPrompt.style.display='flex';
              annInput.value='';
              setTimeout(function(){annInput.focus();},10);
            }
          }
        });

        u.over.addEventListener('mouseup',function(e){
          yDragStart=null;
        });

        u.root.addEventListener('contextmenu',function(e){
          if(currentTool==='measure')e.preventDefault();
        });
        u.over.addEventListener('mouseleave',function(){
          if(measureAnchorIdx===null&&mBar)mBar.style.display='none';
          yDragStart=null;
        });
      }],
      setSelect:[function(u){
        if(tooltipEl)tooltipEl.style.display='none';
        // In annotate mode clicks should not trigger a selection
        if(currentTool==='annotate'){u.setSelect({left:0,top:0,width:0,height:0},false);return;}
        if(u.select.width>10){
          var min=u.posToVal(u.select.left,'x');
          var max=u.posToVal(u.select.left+u.select.width,'x');
          if(currentTool==='zoom'){
            u.setScale('x',{min:min,max:max});
            u.setSelect({left:0,top:0,width:0,height:0},false);
            u.redraw();
          } else if(currentTool==='tag'){
            activeTagRegion={min:min,max:max};
            u.setSelect({left:0,top:0,width:0,height:0},false);
            if(tagPrompt){tagPrompt.style.display='flex';tagInput.value='';setTimeout(function(){tagInput.focus();},10);}
          } else {
            u.setSelect({left:0,top:0,width:0,height:0},false);
          }
        }
      }],
      draw:[function(u){
        // Re-position pins on every redraw (zoom/pan)
        if(pinsLayer){
          var b=u.bbox,dpr=window.devicePixelRatio||1;
          pinsLayer.style.left=(b.left/dpr)+'px';
          pinsLayer.style.top=(b.top/dpr)+'px';
          pinsLayer.style.width=(b.width/dpr)+'px';
          pinsLayer.style.height=(b.height/dpr)+'px';
          UP_PINS.forEach(function(pin){
            var el=pinsLayer.querySelector('#pin-'+pin.id);
            if(el)positionPinEl(u,el,pin);
          });
        }
      }],
    }
  };

  uplotInst=new uPlot(opts,allData,container);

  // Track which pin IDs have been built — prevents double-build across patch + code pins
  var builtPinIds = {};

  if (UP_PINS && UP_PINS.length > 0) {
    UP_PINS.forEach(function(pin) {
      builtPinIds[pin.id] = true;
      buildPinEl(uplotInst, pin, pinsLayer, tagsList);
    });
  }

  // Build code-defined pins (from fig.pin() API) — skip any already built via patch
  if (typeof UP_CODE_PINS !== 'undefined' && UP_CODE_PINS.length > 0) {
    UP_CODE_PINS.forEach(function(pin) {
      if (builtPinIds[pin.id]) return; // already restored via patch — skip
      var pinCopy = {id: pin.id, x: pin.x, label: pin.label, y_frac: pin.y_frac, color: pin.color || null};
      UP_PINS.push(pinCopy);
      builtPinIds[pin.id] = true;
      buildPinEl(uplotInst, pinCopy, pinsLayer, tagsList);
    });
  }
  seriesVisible=[null];
  for(var i=1;i<UP_SERIES_CFG.length;i++)seriesVisible.push(true);
  legendEls=[null];
  var legContainer=container.closest('.up-card');
  var legEls=legContainer?legContainer.querySelectorAll('.up-leg-item[data-si]'):document.querySelectorAll('.up-leg-item[data-si]');
  legEls.forEach(function(el){
    var kind=el.dataset.kind,siRaw=el.dataset.si;
    if(kind==='line'){
      var si=parseInt(siRaw); if(isNaN(si))return;
      legendEls[si]=el;
      el.addEventListener('click',(function(e,s){return function(ev){ev.preventDefault();legendClick(e,s);};})(el,si));
    } else if(kind==='scatter'){
      var scIdx=parseInt(siRaw.replace('sc-','')); if(isNaN(scIdx))return;
      el.addEventListener('click',(function(e,idx){return function(ev){ev.preventDefault();scatterLegendClick(e,idx);};})(el,scIdx));
    }
  });

  // Export button
  var exportBtn=card?card.querySelector('.up-export-btn'):null;
  if(exportBtn)exportBtn.addEventListener('click',function(){exportAsHtml();});
}

// ── Reset zoom ────────────────────────────────────────────────────────────────
function upResetZoom(){
  if(!uplotInst)return;
  var xRange=(UP_INITIAL_RANGES&&UP_INITIAL_RANGES.x)?UP_INITIAL_RANGES.x:(initialScales&&initialScales.x?[initialScales.x.min,initialScales.x.max]:null);
  if(xRange)uplotInst.setScale('x',{min:xRange[0],max:xRange[1]});
  // Also reset unlocked Y scales
  Object.keys(initialScales||{}).forEach(function(k){
    if(k!=='x'&&initialScales[k]){
      uplotInst.setScale(k,{min:initialScales[k].min,max:initialScales[k].max});
    }
  });
}
window[UP_RESET_FN]=upResetZoom;

window.addEventListener('load',function(){
  if (typeof uPlot === 'undefined') {
    var el = document.getElementById(UP_CONTAINER_ID);
    if (el) el.innerHTML = '<div style="padding:24px;color:#f43f5e;font-size:13px;">⚠ uPlot failed to load. Open this file via a local web server or use the bundled version.</div>';
    return;
  }
  buildChart();
  window.addEventListener('resize',function(){
    if(!uplotInst)return;
    uplotInst.setSize({width:document.getElementById(UP_CONTAINER_ID).offsetWidth,height:UP_HEIGHT});
  });
});
"""
