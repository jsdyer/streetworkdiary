import {by,choices,cards,row,csv} from './common.mjs';
import {counts} from './model.mjs';
let data;
function period(){return data.periods.find(p=>p.start===by('week').value)}
function setTypes(){
  const types=[...new Set(period().rows.map(r=>r[1]))].sort();
  choices('type',[['','All request types'],...types.map(v=>[v,v])],by('type').options.length ? by('type').value : 'Street Surface Maintenance');setAreas();
}
function matching(){return period().rows.filter(r=>!by('type').value||r[1]===by('type').value)}
function setAreas(){
  const areas=[...new Set(matching().map(r=>r[2]))].sort();
  choices('area',[['','All communities'],...areas.map(v=>[v,v])],by('area').value);render();
}
function render(){
  const selected=matching().filter(r=>!by('area').value||r[2]===by('area').value),c=counts(selected);
  const pc=n=>c.total?Math.round(100*n/c.total)+'%':'—';
  cards([['Requests',String(c.total),'Unique Cityworks IDs'],['Marked closed',String(c.closed),pc(c.closed)+' of this selection'],['Custom detail',String(c.detail),pc(c.detail)+' have a matching detail row'],['Median time to closure',c.elapsed===null?'Unavailable':c.elapsed.toLocaleString('en-CA',{maximumFractionDigits:2})+' days','Closed requests with valid dates']]);
  by('coverage').textContent=c.resolution+' of '+c.total+' requests include a resolution entry. '+c.detail+' have at least one custom detail row. Closure is an administrative status.';
  const grouped=new Map();for(const r of selected){if(!grouped.has(r[2]))grouped.set(r[2],[]);grouped.get(r[2]).push(r)}
  by('summary').replaceChildren(...[...grouped].sort((a,b)=>b[1].length-a[1].length||a[0].localeCompare(b[0])).map(([name,records])=>{const g=counts(records);return row([name,g.total,g.closed,g.resolution,g.detail])}));
  by('rows').replaceChildren(...selected.map(r=>row([r[0],r[3],r[2],r[1],r[4]||'Unreported',r[7].join(', ')||'No matching row'])));
  by('csv').onclick=()=>csv('streetwork-'+period().start+'.csv',[['request_id','category','community','received_utc','status','days_to_close','resolution_present','custom_fields','work_order_flag','retrieved'],...selected.map(r=>[...r.slice(0,7),r[7].join(' / '),r[8],data.retrieved])]);
}
try{
  const res=await fetch('./data/requests.json');if(!res.ok)throw Error();data=await res.json();
  by('meta').textContent=data.count+' requests in '+data.periods.length+' selected weeks · Retrieved '+data.retrieved+' UTC · Newest source intake '+data.sourceThrough;
  choices('week',data.periods.map(p=>[p.start,p.start+' to '+p.end]),data.periods[0].start);
  by('week').onchange=setTypes;by('type').onchange=setAreas;by('area').onchange=render;setTypes();by('work').hidden=false;
}catch{by('meta').textContent='The request snapshot could not load. Open the source below or reload.'}
