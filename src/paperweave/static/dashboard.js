(() => {
'use strict';
const data=JSON.parse(document.getElementById('paper-data').textContent);
const $=id=>document.getElementById(id);
const kinds={question:'核心问题',method:'研究方法',argument:'论证路径',contribution:'关键贡献',result:'实验与结论',limitation:'局限',boundary:'应用边界',concept:'关键概念',background:'研究背景'};
const statuses={anchored:'原文摘录匹配 · 语义待核对',inference:'分析者推断 · 请核对依据',unmatched:'原文摘录未匹配'};
const index=new Map(data.nodes.map(n=>[n.id,n]));
let mode='mindmap',selected=data.nodes[0]?.id,collapsed=new Set(),query='',critical=false,theme='light',renderSerial=0;
let scale=1,tx=0,ty=0,pointer=null,pdfURL=null,currentPage=1,currentQuote='';
const make=(tag,text,cls)=>{const e=document.createElement(tag);if(text!==undefined)e.textContent=text;if(cls)e.className=cls;return e;};
function toast(message){$('toast').textContent=message;$('toast').hidden=false;setTimeout(()=>$('toast').hidden=true,4200);}
function download(name,text,type){const url=URL.createObjectURL(new Blob([text],{type}));const a=make('a');a.href=url;a.download=name;a.click();setTimeout(()=>URL.revokeObjectURL(url),30000);}
function label(text){return text.replace(/[^\p{L}\p{N}_\s.,，。:：;%％+−=/\-]/gu,' ').replace(/\s+/g,' ').trim().slice(0,70)||'节点';}
function matching(n){const q=query.toLowerCase();return (!critical||['limitation','boundary'].includes(n.kind))&&(!q||[n.label,n.detail,n.explanation,...n.evidence.map(e=>e.quote)].join(' ').toLowerCase().includes(q));}
function renderOutline(){
 const focusedId=document.activeElement?.dataset.nodeId;const target=$('outline');target.replaceChildren();let found=0;
 function branch(n,container){
   if(index.has(n.id)){const node=index.get(n.id);if(!matching(node))return false;found++;const b=make('button',node.label,'node-button'+(selected===node.id?' selected':''));b.dataset.nodeId=node.id;const pages=[...new Set(node.evidence.filter(e=>e.page).map(e=>e.page))];b.append(make('small',`${kinds[node.kind]||node.kind} · ${pages.length?'p. '+pages.join(', '):'来源未匹配'}`));b.onclick=()=>select(node.id);container.append(b);return true;}
   const details=make('details');details.open=true;const summary=make('summary',n.label);details.append(summary);const children=make('div',undefined,'outline-children');let any=false;for(const child of n.children||[])any=branch(child,children)||any;if(any){details.append(children);container.append(details);}return any;
 }
 for(const n of data.tree.children)branch(n,target);
 if(!found)target.append(make('p','没有匹配内容。可尝试搜索原文术语。','empty'));
 $('search-count').textContent=`${found} 项`;if(focusedId){const restore=target.querySelector('[data-node-id="'+focusedId+'"]');if(restore)restore.focus({preventScroll:true});}
}
function select(id){selected=id;const n=index.get(id);if(!n)return;renderOutline();const box=$('detail-content');box.replaceChildren();box.append(make('div',kinds[n.kind]||n.kind,'kind-label'),make('h2',n.label),make('span',statuses[n.status]||n.status,'node-status '+n.status));
 const section=(title,text,cls)=>{const e=make('section',undefined,'detail-section'+(cls?' '+cls:''));e.append(make('h3',title),make('p',text||'未提供'));box.append(e);};
 section('论文分析',n.detail);section('换个方式理解',n.explanation,'plain-explain');const evidence=make('section',undefined,'detail-section');evidence.append(make('h3',`来源证据 / ${n.evidence.length}`));
 for(const ref of n.evidence){const card=make('div',undefined,'evidence-card'),head=make('div',undefined,'evidence-top'),page=make('button',ref.page?'PDF 第 '+ref.page+' 页':'无有效页码','page-link');page.disabled=!ref.page;page.onclick=()=>openSource(ref.page,ref.quote);head.append(page,make('span',ref.matched?'摘录匹配':'未匹配',ref.matched?'':'mismatch'));card.append(head,make('div',ref.section,'trace-note'),make('blockquote',ref.quote));evidence.append(card);}
 evidence.append(make('p','匹配检查仅确认摘录能在提取文本中找到。请结合上下文核对结论、推断和实验数值。','trace-note'));box.append(evidence,make('div',`节点 ${n.id} · ${data.model_info.source==='fixture'?'确定性教学示例':'模型 '+data.model_info.model}`,'node-footer'));highlight();
}
function highlight(){document.querySelectorAll('#diagram [data-paper-id]').forEach(e=>{e.dataset.selected=String(e.dataset.paperId===selected);e.style.opacity=(!query&&!critical)||!index.has(e.dataset.paperId)||matching(index.get(e.dataset.paperId))?'1':'.25';});}
function wireSVG(){
 const svg=$('diagram').querySelector('svg');if(!svg)return;const vb=svg.viewBox.baseVal;svg.style.width=(vb.width||1200)+'px';svg.style.height=(vb.height||800)+'px';svg.removeAttribute('height');
 const nodes=[{id:'root',label:data.title},...data.nodes];
 function all(n){if(!index.has(n.id)&&n.id!=='root')nodes.push(n);for(const c of n.children||[])all(c);}all(data.tree);
 const labels=new Map(nodes.map(n=>[label(n.label),n.id]));
 const candidates=svg.querySelectorAll('g.node, g.mindmap-node, g.section-root, g[class*="node"]');
 candidates.forEach(g=>{const t=(g.querySelector('foreignObject')?.textContent||g.querySelector('text')?.textContent||g.textContent).trim();let id=nodes.find(n=>g.id===n.id||g.id.startsWith('flowchart-'+n.id+'-'))?.id||labels.get(t);
 if(id){g.dataset.paperId=id;g.setAttribute('role','button');g.setAttribute('tabindex','0');g.setAttribute('aria-label',nodes.find(n=>n.id===id)?.label||t);g.onkeydown=event=>{if(event.key==='Enter'||event.key===' '){event.preventDefault();event.stopPropagation();g.dispatchEvent(new MouseEvent('click',{bubbles:true}));}};g.style.cursor='pointer';g.onclick=event=>{event.stopPropagation();if(index.has(id))select(id);else{collapsed.has(id)?collapsed.delete(id):collapsed.add(id);redraw();}};}});highlight();
}
function transform(){$('diagram').style.transform=`translate(${tx}px,${ty}px) scale(${scale})`;}
function fit(){const svg=$('diagram').querySelector('svg');if(!svg)return;const vb=svg.viewBox.baseVal;const w=vb.width||1200,h=vb.height||800,cw=$('canvas').clientWidth,ch=$('canvas').clientHeight;scale=Math.min((cw-36)/w,(ch-36)/h,1.2);tx=(cw-w*scale)/2;ty=(ch-h*scale)/2;transform();}
function changeZoom(factor,cx=$('canvas').clientWidth/2,cy=$('canvas').clientHeight/2){const next=Math.max(.06,Math.min(6,scale*factor)),ratio=next/scale;tx=cx-(cx-tx)*ratio;ty=cy-(cy-ty)*ratio;scale=next;transform();}
function visible(n){return {...n,children:collapsed.has(n.id)?[]:(n.children||[]).map(visible)};}
function codeFor(tree,view){const lines=[view==='mindmap'?'mindmap':'flowchart LR'];function walk(n,d=1){if(view==='mindmap'){lines.push('    '.repeat(d)+n.id+(d===1?'(("'+label(n.label)+'"))':'["'+label(n.label)+'"]'));}else lines.push(`${n.id}["${label(n.label)}"]`);for(const c of n.children||[]){walk(c,d+1);if(view!=='mindmap')lines.push(`${n.id} --> ${c.id}`);}}walk(tree);return lines.join('\n');}
function initMermaid(){
 const dark=theme==='dark';
 const palette=dark?['#344460','#2d3b52','#263347','#304058','#28384f','#35435b']:['#e8edfd','#edf1f7','#f0f2f6','#f5f6f8','#e8edf5','#eff2f7'];
 const variables={fontFamily:'Cambria, Noto Serif SC, SimSun, serif',fontSize:'15px',primaryColor:dark?'#2d3b52':'#eef2fe',primaryTextColor:dark?'#edf1f7':'#13233f',primaryBorderColor:dark?'#687d9c':'#b4c1dc',lineColor:dark?'#7f91ac':'#9ba6b9',secondaryColor:dark?'#263347':'#f0f2f6',tertiaryColor:dark?'#1a273a':'#f6f7f9'};
 for(let i=0;i<12;i++){variables['cScale'+i]=palette[i%palette.length];variables['cScaleLabel'+i]=dark?'#edf1f7':'#13233f';}
 PaperMermaid.initialize({startOnLoad:false,securityLevel:'strict',theme:'base',maxTextSize:2000000,maxEdges:20000,themeVariables:variables});
}

async function redraw(){const serial=++renderSerial;$('render-state').textContent='正在渲染…';try{initMermaid();const code=codeFor(visible(data.tree),mode);await PaperMermaid.parse(code);const result=await PaperMermaid.render('paper-map-'+serial,code);if(serial!==renderSerial)return;$('diagram').innerHTML=result.svg;wireSVG();fit();$('render-state').textContent='Mermaid 已校验';}catch(e){if(serial===renderSerial){$('render-state').textContent='渲染失败';toast('导图渲染失败。请导出 Mermaid 源码核对；节点与原文仍可查看。');console.error(e);}}}
function openSource(page=1,quote=''){currentPage=page;currentQuote=quote;$('source-dialog').showModal();showText();}
function showText(){const body=$('source-body');body.replaceChildren();$('source-page').textContent='PDF 第 '+currentPage+' 页';for(const p of data.pages){const section=make('section',undefined,'source-page-block');section.id='source-p-'+p.page;section.append(make('h3','PDF 第 '+p.page+' 页'));const text=make('div');const pos=p.page===currentPage&&currentQuote?p.text.indexOf(currentQuote):-1;if(pos>=0){text.append(document.createTextNode(p.text.slice(0,pos)),make('mark',currentQuote),document.createTextNode(p.text.slice(pos+currentQuote.length)));}else text.textContent=p.text;section.append(text);body.append(section);}setTimeout(()=>$('source-p-'+currentPage)?.scrollIntoView({block:'start'}),30);}
function showPDF(){if(!data.pdf_base64){toast('此看板未内嵌原 PDF，仍可按页查看提取原文。');return;}try{if(!pdfURL){const bytes=Uint8Array.from(atob(data.pdf_base64),c=>c.charCodeAt(0));pdfURL=URL.createObjectURL(new Blob([bytes],{type:'application/pdf'}));}const frame=make('iframe');frame.title='原始 PDF';frame.src=pdfURL+'#page='+currentPage;$('source-body').replaceChildren(frame);$('source-page').textContent='PDF 第 '+currentPage+' 页（页码跳转取决于浏览器 PDF 阅读器）';}catch(e){toast('浏览器未能打开内嵌 PDF，请使用提取文本视图。');}}
$('paper-title').textContent=data.title;document.title=data.title+' · 研脉';$('paper-meta').textContent=`${data.filename} · ${data.model_info.source==='fixture'?'教学示例':data.model_info.model} · ${new Date(data.created_at).toLocaleString('zh-CN')} · Mermaid 离线渲染`;
$('page-count').textContent=data.coverage.pages_total;$('node-count').textContent=data.nodes.length;$('chunk-count').textContent=data.coverage.chunks_analyzed+'/'+data.coverage.chunks_total;
const notices=[...(data.model_info.source==='fixture'?['教学演示：分析内容来自本地确定性测试响应，并非真实模型 API 输出。']:[]),...data.warnings];if(notices.length){$('notice').hidden=false;$('notice').textContent=notices.join('；');}
$('search').oninput=e=>{query=e.target.value;renderOutline();highlight();};$('all-filter').onclick=()=>{critical=false;$('all-filter').classList.add('active');$('critical-filter').classList.remove('active');$('all-filter').setAttribute('aria-pressed','true');$('critical-filter').setAttribute('aria-pressed','false');renderOutline();highlight();};$('critical-filter').onclick=()=>{critical=true;$('critical-filter').classList.add('active');$('all-filter').classList.remove('active');$('critical-filter').setAttribute('aria-pressed','true');$('all-filter').setAttribute('aria-pressed','false');renderOutline();highlight();};
for(const view of ['mindmap','flowchart'])$('mode-'+view).onclick=()=>{mode=view;for(const m of ['mindmap','flowchart']){$('mode-'+m).classList.toggle('active',m===mode);$('mode-'+m).setAttribute('aria-pressed',String(m===mode));}redraw();};
$('expand').onclick=()=>{collapsed.clear();redraw();};$('collapse').onclick=()=>{collapsed=new Set(data.tree.children.filter(n=>n.children?.length).map(n=>n.id));redraw();};
$('theme').onclick=()=>{theme=theme==='light'?'dark':'light';document.body.dataset.theme=theme;$('theme').textContent=theme==='light'?'切换深色':'切换浅色';redraw();};
$('zoom-in').onclick=()=>changeZoom(1.25);$('zoom-out').onclick=()=>changeZoom(.8);$('fit').onclick=fit;
$('canvas').addEventListener('keydown',event=>{if(event.target!==$('canvas'))return;const moves={ArrowLeft:[32,0],ArrowRight:[-32,0],ArrowUp:[0,32],ArrowDown:[0,-32]};if(moves[event.key]){event.preventDefault();tx+=moves[event.key][0];ty+=moves[event.key][1];transform();}else if(['+','=','-','0'].includes(event.key)){event.preventDefault();if(event.key==='0')fit();else changeZoom(event.key==='-'?.8:1.25);}});
$('canvas').addEventListener('wheel',event=>{event.preventDefault();const r=$('canvas').getBoundingClientRect();changeZoom(event.deltaY>0?.9:1.1,event.clientX-r.left,event.clientY-r.top);},{passive:false});
$('canvas').addEventListener('pointerdown',event=>{if(event.button!==0)return;pointer={x:event.clientX,y:event.clientY,tx,ty};});window.addEventListener('pointermove',event=>{if(!pointer)return;tx=pointer.tx+event.clientX-pointer.x;ty=pointer.ty+event.clientY-pointer.y;transform();});window.addEventListener('pointerup',()=>pointer=null);window.addEventListener('resize',fit);
$('export-mmd').onclick=()=>download(mode+'.mmd',data.mermaid[mode],'text/plain;charset=utf-8');$('export-json').onclick=()=>download('analysis.json',JSON.stringify(data,null,2),'application/json');$('export-svg').onclick=()=>{const svg=$('diagram').querySelector('svg');if(svg)download('paper-'+mode+'.svg',new XMLSerializer().serializeToString(svg),'image/svg+xml');};$('download-html').onclick=()=>download('paperweave.html','<!DOCTYPE html>\n'+document.documentElement.outerHTML,'text/html;charset=utf-8');$('show-source').onclick=()=>openSource();$('close-source').onclick=()=>$('source-dialog').close();$('source-text').onclick=showText;$('source-pdf').onclick=showPDF;
initMermaid();wireSVG();renderOutline();if(selected)select(selected);requestAnimationFrame(fit);
})();
