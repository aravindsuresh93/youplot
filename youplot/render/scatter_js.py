"""Scatter plot JS."""

SCATTER_JS = r"""
(function() {

function hexAlpha(hex,alpha){
  if(!hex)return'rgba(128,128,128,'+alpha+')';
  if(hex.startsWith('rgba')||hex.startsWith('rgb'))return hex;
  var h=hex.replace('#','');
  if(h.length===3)h=h[0]+h[0]+h[1]+h[1]+h[2]+h[2];
  var r=parseInt(h.slice(0,2),16),g=parseInt(h.slice(2,4),16),b=parseInt(h.slice(4,6),16);
  return'rgba('+r+','+g+','+b+','+alpha+')';
}
function lerpColor(hex1,hex2,t){
  var h1=hex1.replace('#',''),h2=hex2.replace('#','');
  if(h1.length===3)h1=h1[0]+h1[0]+h1[1]+h1[1]+h1[2]+h1[2];
  if(h2.length===3)h2=h2[0]+h2[0]+h2[1]+h2[1]+h2[2]+h2[2];
  var r=Math.round(parseInt(h1.slice(0,2),16)*(1-t)+parseInt(h2.slice(0,2),16)*t);
  var g=Math.round(parseInt(h1.slice(2,4),16)*(1-t)+parseInt(h2.slice(2,4),16)*t);
  var b=Math.round(parseInt(h1.slice(4,6),16)*(1-t)+parseInt(h2.slice(4,6),16)*t);
  return'rgb('+r+','+g+','+b+')';
}
function drawShape(ctx,shape,cx,cy,r){
  ctx.beginPath();
  switch(shape){
    case'square':ctx.rect(cx-r,cy-r,r*2,r*2);break;
    case'triangle':ctx.moveTo(cx,cy-r);ctx.lineTo(cx+r*0.866,cy+r*0.5);ctx.lineTo(cx-r*0.866,cy+r*0.5);ctx.closePath();break;
    case'diamond':ctx.moveTo(cx,cy-r);ctx.lineTo(cx+r,cy);ctx.lineTo(cx,cy+r);ctx.lineTo(cx-r,cy);ctx.closePath();break;
    case'cross':var t=r*0.32;ctx.rect(cx-r,cy-t,r*2,t*2);ctx.rect(cx-t,cy-r,t*2,r*2);break;
    case'star':for(var i=0;i<10;i++){var a=(i*Math.PI/5)-Math.PI/2,rad=i%2===0?r:r*0.45;if(i===0)ctx.moveTo(cx+rad*Math.cos(a),cy+rad*Math.sin(a));else ctx.lineTo(cx+rad*Math.cos(a),cy+rad*Math.sin(a));}ctx.closePath();break;
    default:ctx.arc(cx,cy,r,0,Math.PI*2);
  }
}
function linearRegression(xs,ys){
  var n=xs.length,sx=0,sy=0,sxy=0,sxx=0;
  for(var i=0;i<n;i++){sx+=xs[i];sy+=ys[i];sxy+=xs[i]*ys[i];sxx+=xs[i]*xs[i];}
  var slope=(n*sxy-sx*sy)/(n*sxx-sx*sx);
  return{slope:slope,intercept:(sy-slope*sx)/n};
}
function rSquared(xs,ys,slope,intercept){
  var ym=ys.reduce(function(a,b){return a+b;},0)/ys.length,ssTot=0,ssRes=0;
  for(var i=0;i<xs.length;i++){ssTot+=Math.pow(ys[i]-ym,2);ssRes+=Math.pow(ys[i]-(slope*xs[i]+intercept),2);}
  return ssTot===0?1:1-ssRes/ssTot;
}
function round2(v){return Math.round(v*100)/100;}
function fmtVal(v,fmt){if(!fmt)return round2(v);var m=fmt.match(/\.(\d+)f/);return m?v.toFixed(parseInt(m[1])):round2(v);}

function makeScatterPlugin(scatterConfigs, tooltipId, upRegions, isTimeseries) {
  var hitMap = [];

  return {
    hooks: {
      ready: [function(u) {
        var el = document.getElementById(tooltipId);
        if (!el) return;

        // Identical pattern to line chart:
        // mousemove on u.over → compute position → find hit → show/hide
        u.over.addEventListener('mousemove', function(e) {
          // mouse position relative to the plot area (same space as hitMap hx/hy)
          var rect = u.over.getBoundingClientRect();
          var mx = e.clientX - rect.left;
          var my = e.clientY - rect.top;

          // Find point whose drawn radius contains the mouse
          var best = null;
          var bestDist = Infinity;
          for (var k = 0; k < hitMap.length; k++) {
            var h = hitMap[k];
            if (h.cfg.visible === false) continue;
            var d = Math.sqrt(Math.pow(mx - h.hx, 2) + Math.pow(my - h.hy, 2));
            // Only trigger if mouse is within the drawn point radius (+2px grace)
            if (d <= h.r + 2 && d < bestDist) {
              bestDist = d;
              best = h;
            }
          }

          if (!best) { el.style.display = 'none'; return; }

          var cfg = best.cfg, unit = cfg.hoverUnit||'';
          var html = '<div class="up-tooltip-time">'+(cfg.label||'')+'</div>';
          
          if (upRegions) {
            var tsVal = best.xv;
            var xVal = isTimeseries ? tsVal * 1000 : tsVal;
            upRegions.forEach(function(r){
              if (r._tagId && r.label && xVal >= Math.min(r.x_start, r.x_end) && xVal <= Math.max(r.x_start, r.x_end)) {
                html += '<div class="up-tooltip-row" style="background:'+hexAlpha(r.color, 0.15)+'; border-radius:4px; padding:3px 6px; margin-bottom:6px; border:1px solid '+hexAlpha(r.color,0.3)+';">'
                  + '<span class="up-tooltip-dot" style="background:'+r.color+'"></span>'
                  + '<span class="up-tooltip-name" style="font-weight:600; color:'+r.color+'; text-shadow:0 0 1px #000;">Tag: '+r.label+'</span>'
                  + '</div>';
              }
            });
          }

          html += '<div class="up-tooltip-row">'
            +'<span class="up-tooltip-dot" style="background:'+best.fillColor+'"></span>'
            +'<span class="up-tooltip-name">'+(cfg.hoverXLabel||'x')+'</span>'
            +'<span class="up-tooltip-val" style="color:'+best.fillColor+'">'+fmtVal(best.xv,cfg.hoverFormat)+unit+'</span>'
            +'</div>'
            +'<div class="up-tooltip-row">'
            +'<span class="up-tooltip-dot" style="background:'+best.fillColor+'"></span>'
            +'<span class="up-tooltip-name">'+(cfg.hoverYLabel||'y')+'</span>'
            +'<span class="up-tooltip-val" style="color:'+best.fillColor+'">'+fmtVal(best.yv,cfg.hoverFormat)+unit+'</span>'
            +'</div>';
          if(cfg._sizeData&&cfg._sizeData[best.i]!=null)
            html+='<div class="up-tooltip-row"><span class="up-tooltip-name">size</span><span class="up-tooltip-val">'+round2(cfg._sizeData[best.i])+'</span></div>';
          if(cfg._colorData&&cfg._colorData[best.i]!=null)
            html+='<div class="up-tooltip-row"><span class="up-tooltip-name">value</span><span class="up-tooltip-val">'+round2(cfg._colorData[best.i])+'</span></div>';

          el.innerHTML = html;
          el.style.display = 'block';

          // Position using e.clientX/Y — exactly like line chart
          var tw = el.offsetWidth || 200;
          var left = e.clientX + 18;
          if (left + tw > window.innerWidth - 12) left = e.clientX - tw - 18;
          var top = e.clientY - 10;
          if (top + 140 > window.innerHeight) top = e.clientY - 140;
          el.style.left = left + 'px';
          el.style.top  = top  + 'px';
        });

        u.over.addEventListener('mouseleave', function() {
          el.style.display = 'none';
        });
      }],

      draw: [function(u) {
        var ctx=u.ctx, b=u.bbox;
        ctx.save();
        ctx.beginPath();ctx.rect(b.left,b.top,b.width,b.height);ctx.clip();
        hitMap = [];

        scatterConfigs.forEach(function(scfg){
          if(scfg.visible===false)return;
          var xData=scfg._xData,yData=scfg._yData,sizeData=scfg._sizeData,colorData=scfg._colorData,labelData=scfg._labelData;
          var scaleKey=scfg.scale||'y';
          var sMin=Infinity,sMax=-Infinity;
          if(sizeData){for(var i=0;i<sizeData.length;i++){if(sizeData[i]!=null&&!isNaN(sizeData[i])){sMin=Math.min(sMin,sizeData[i]);sMax=Math.max(sMax,sizeData[i]);}}}
          var cMin=Infinity,cMax=-Infinity;
          if(colorData){for(var i=0;i<colorData.length;i++){if(colorData[i]!=null&&!isNaN(colorData[i])){cMin=Math.min(cMin,colorData[i]);cMax=Math.max(cMax,colorData[i]);}}}

          var validX=[],validY=[];
          for(var i=0;i<xData.length;i++){
            var xv=xData[i],yv=yData[i];
            if(xv==null||isNaN(xv)||yv==null||isNaN(yv))continue;
            // canvas-absolute coords
            var cx=u.valToPos(xv,'x',true);
            var cy=u.valToPos(yv,scaleKey,true);
            var r=scfg.size;
            if(sizeData&&sizeData[i]!=null&&!isNaN(sizeData[i])&&sMax>sMin){var st=(sizeData[i]-sMin)/(sMax-sMin);r=scfg.sizeRange[0]+st*(scfg.sizeRange[1]-scfg.sizeRange[0]);}
            var fillColor=scfg.color;
            if(colorData&&colorData[i]!=null&&!isNaN(colorData[i])&&cMax>cMin){var ct=(colorData[i]-cMin)/(cMax-cMin);fillColor=lerpColor(scfg.colorScale[0],scfg.colorScale[1],ct);}

            ctx.globalAlpha=scfg.opacity;ctx.fillStyle=fillColor;
            drawShape(ctx,scfg.shape,cx,cy,r);ctx.fill();
            if(scfg.strokeWidth>0){ctx.globalAlpha=Math.min(1,scfg.opacity+0.15);ctx.strokeStyle=scfg.stroke||fillColor;ctx.lineWidth=scfg.strokeWidth;drawShape(ctx,scfg.shape,cx,cy,r);ctx.stroke();}
            ctx.globalAlpha=1;
            if(labelData&&labelData[i]!=null){ctx.fillStyle=hexAlpha(scfg.labelColor||scfg.color,0.9);ctx.font=scfg.labelFontSize+'px -apple-system,sans-serif';ctx.textAlign='left';ctx.fillText(String(labelData[i]),cx+r+3,cy+4);}

            // hitMap stores plot-area-relative coords (matching mx/my from mousemove)
            // mx = e.clientX - over.rect.left  (over covers exactly the plot area in CSS pixels)
            // hx = (cx - b.left) / pr          (convert canvas-abs to CSS plot-area-relative)
            var pr = window.devicePixelRatio || 1;
            hitMap.push({si:scfg._scatterIdx,i:i,hx:(cx-b.left)/pr,hy:(cy-b.top)/pr,r:r,xv:xv,yv:yv,fillColor:fillColor,cfg:scfg});
            validX.push(xv);validY.push(yv);
          }

          if(scfg.trendline&&validX.length>=2){
            var reg=linearRegression(validX,validY);
            var r2=rSquared(validX,validY,reg.slope,reg.intercept);
            var xMin=Math.min.apply(null,validX),xMax=Math.max.apply(null,validX);
            var px0=u.valToPos(xMin,'x',true),px1=u.valToPos(xMax,'x',true);
            var py0=u.valToPos(reg.slope*xMin+reg.intercept,scaleKey,true);
            var py1=u.valToPos(reg.slope*xMax+reg.intercept,scaleKey,true);
            ctx.strokeStyle=scfg.trendlineColor||scfg.color;ctx.lineWidth=scfg.trendlineWidth;
            ctx.setLineDash(scfg.trendlineDash?[6,4]:[]);ctx.globalAlpha=0.75;
            ctx.beginPath();ctx.moveTo(px0,py0);ctx.lineTo(px1,py1);ctx.stroke();
            ctx.setLineDash([]);ctx.globalAlpha=1;
            ctx.font='600 10px -apple-system,sans-serif';ctx.fillStyle=scfg.trendlineColor||scfg.color;ctx.globalAlpha=0.8;
            ctx.fillText('R\u00b2='+r2.toFixed(3),px1-58,py1-6);ctx.globalAlpha=1;
          }
        });
        ctx.restore();
      }]
    }
  };
}

window._makeScatterPlugin = makeScatterPlugin;

})();
"""
