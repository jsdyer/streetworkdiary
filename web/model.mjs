export function median(values){const s=values.filter(Number.isFinite).sort((a,b)=>a-b);return s.length?(s[Math.floor((s.length-1)/2)]+s[Math.floor(s.length/2)])/2:null}
export function counts(rows){
  const closed=rows.filter(r=>r[4]==='CLOSED');return {total:rows.length,closed:closed.length,detail:rows.filter(r=>r[7].length).length,resolution:rows.filter(r=>r[6]).length,elapsed:median(closed.map(r=>r[5]))};
}
