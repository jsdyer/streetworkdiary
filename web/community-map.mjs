import {streetMap} from './streets.mjs';

const colour = count => count > 20 ? '#164d51' : count > 5 ? '#378981' : '#a6cfb5';
export function communityMap(geometry, selectCommunity) {
  const map = L.map('community-map', {scrollWheelZoom:false, minZoom:6, maxZoom:18})
    .setView([44.68,-63.56],10);
  streetMap(map).addTo(map);
  L.control.scale({imperial:false}).addTo(map);
  const outlines = L.featureGroup().addTo(map);
  return function render(grouped) {
    map.invalidateSize({pan:false});
    outlines.clearLayers();
    let mapped = 0, communities = 0, total = 0;
    for (const [name, requests] of grouped) {
      const count = requests.length;
      total += count;
      if (!geometry[name]) continue;
      const text = document.createElement('span');
      text.textContent = name + ' · ' + count + (count === 1 ? ' request' : ' requests');
      L.geoJSON(geometry[name], {style:{color:'#154f52', weight:1.6, fillColor:colour(count), fillOpacity:.68}})
        .bindTooltip(text).on('click', () => selectCommunity(name)).addTo(outlines);
      communities++;
      mapped += count;
    }
    const bounds = outlines.getBounds();
    if (bounds.isValid()) map.fitBounds(bounds, {padding:[14,14], maxZoom:13, animate:false});
    else map.setView([44.68,-63.56],10,{animate:false});
    const status = document.getElementById('map-summary');
    status.textContent = mapped + ' of ' + total + ' selected requests mapped across ' + communities +
      (communities === 1 ? ' community.' : ' communities.') +
      (total > mapped ? ' ' + (total-mapped) + ' lack a matching named boundary.' : '');
  };
}
