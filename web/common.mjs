
export const by=id=>document.getElementById(id);
export function el(tag,text){const node=document.createElement(tag);if(text!=null)node.textContent=text;return node}
export function choices(id,items,selected){const s=by(id);s.replaceChildren(...items.map(([v,t])=>new Option(t,v)));if(items.some(x=>x[0]===selected))s.value=selected}
export function cards(items){by('stats').replaceChildren(...items.map(([label,value,detail])=>{const n=el('div');n.className='card';n.append(el('span',label),el('strong',value),el('small',detail));return n}))}
export function row(values,heading=false){const n=el('tr');for(const v of values)n.append(el(heading?'th':'td',v));return n}
export function csv(filename,rows){const escape=v=>'"'+String(v??'').replaceAll('"','""')+'"';const url=URL.createObjectURL(new Blob([rows.map(r=>r.map(escape).join(',')).join('\r\n')],{type:'text/csv;charset=utf-8'}));const a=el('a');a.href=url;a.download=filename;a.click();setTimeout(()=>URL.revokeObjectURL(url),1000)}
