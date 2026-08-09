/* Plotly dark theme — muted navy palette */
window.PD={paper_bgcolor:'#020617',plot_bgcolor:'#0b1220',font:{color:'#94a3b8',family:'"SF Pro Display","Inter",-apple-system,"PingFang SC",sans-serif'},margin:{l:55,r:20,t:15,b:45},legend:{orientation:'h',y:-0.18,x:0,font:{size:11,color:'#94a3b8'},bgcolor:'rgba(0,0,0,0)'},hoverlabel:{bgcolor:'#0b1220',bordercolor:'#1e293b',font:{color:'#e2e8f0',size:12}}};
window.PAx={color:'#94a3b8',gridcolor:'#1e293b',zerolinecolor:'#334155',linecolor:'#1e293b'};
/* Muted bluescale for heatmaps */
window.BlueSeq=[[0,'#070d1b'],[0.2,'#0f1d3a'],[0.4,'#1e3a6e'],[0.6,'#2563eb'],[0.8,'#3b82f6'],[1,'#93c5fd']];
window.BlueSeqMid=[[0,'#0f172a'],[0.25,'#1e3a6e'],[0.5,'#2563eb'],[0.75,'#3b82f6'],[1,'#93c5fd']];
function ml(o){const b=JSON.parse(JSON.stringify({paper_bgcolor:PD.paper_bgcolor,plot_bgcolor:PD.plot_bgcolor,font:PD.font,margin:PD.margin,legend:PD.legend,hoverlabel:PD.hoverlabel,xaxis:Object.assign({},PAx),yaxis:Object.assign({},PAx)}));(function d(t,s){for(const k in s){if(typeof s[k]==='object'&&s[k]&&!Array.isArray(s[k])){t[k]=t[k]||{};d(t[k],s[k]);}else t[k]=s[k];}})(b,o);return b;}
function pr(id,tr,ly,cfg){Plotly.newPlot(id,tr,ml(ly),Object.assign({responsive:true,displayModeBar:'hover',modeBarButtonsToRemove:['lasso2d','select2d']},cfg||{}));}
