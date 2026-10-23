() => {
  const rgba = s => (s.match(/[\d.]+/g) || []).map(Number);
  const blend = (a,b) => {const opacity=a[3]??1;return [...a.slice(0,3).map((v,i)=>v*opacity+b[i]*(1-opacity)),1]};
  const background = el => {let colors=[];for(let e=el;e;e=e.parentElement) colors.push(rgba(getComputedStyle(e).backgroundColor));return colors.reverse().reduce((b,a)=>blend(a,b),[255,255,255,1])};
  const luminance = c => c.slice(0,3).map(v=>v/255).map(v=>v<=.04045?v/12.92:((v+.055)/1.055)**2.4).reduce((a,v,i)=>a+v*[.2126,.7152,.0722][i],0);
  const failures=[], pairs=new Map();
  for (const el of document.querySelectorAll('body *')) {
    const s=getComputedStyle(el), rect=el.getBoundingClientRect();
    if (!rect.width||!rect.height||s.visibility==='hidden'||!Array.from(el.childNodes).some(n=>n.nodeType===3&&n.textContent.trim())) continue;
    const bg=background(el), fg=blend(rgba(s.color),bg), a=luminance(fg),b=luminance(bg), ratio=(Math.max(a,b)+.05)/(Math.min(a,b)+.05);
    const threshold=parseFloat(s.fontSize)>=24||(parseFloat(s.fontSize)>=18.66&&parseInt(s.fontWeight)>=700)?3:4.5;
    const item={selector:el.tagName.toLowerCase()+'.'+el.className,text:el.textContent.trim().slice(0,80),foreground:s.color,background:bg,ratio:Math.round(ratio*100)/100,threshold};
    pairs.set(s.color+'|'+bg.join()+'|'+threshold,item);
    if(ratio<threshold) failures.push(item);
  }
  for (const el of document.querySelectorAll('.track-problem,.track-did,.track-outcome')) {
    const s=getComputedStyle(el,'::before');
    if (s.content==='none'||s.display==='none') continue;
    const bg=background(el),fg=blend(rgba(s.color),bg),a=luminance(fg),b=luminance(bg),ratio=(Math.max(a,b)+.05)/(Math.min(a,b)+.05);
    const item={selector:el.className+'::before',text:s.content,foreground:s.color,background:bg,ratio:Math.round(ratio*100)/100,threshold:4.5};
    pairs.set(s.color+'|'+bg.join()+'|4.5',item);
    if(ratio<4.5)failures.push(item);
  }
  return {failures,pairs:[...pairs.values()]};
}
