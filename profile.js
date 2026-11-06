const data=window.UMI_PROFILE;
const embedded=window.UMI_ASSETS||{};
if(data){
 const stats={repos:data.public_repos,stars:data.stars,languages:data.languages.length,contributions:data.contribution_total,activeDays:data.active_days,recent:data.recent_contributions,bestDay:data.best_day};
 document.querySelectorAll('[data-stat]').forEach(node=>node.textContent=stats[node.dataset.stat].toLocaleString('en-US'));
 document.getElementById('snapshot-date').textContent='Public GitHub data · '+data.date_label;
 const colors=['#3f7346','#506e85','#8c682b','#82687d','#52746d','#9c6b42'];
 const rows=Object.entries(data.language_counts).sort((a,b)=>b[1]-a[1]);
 const max=Math.max(...rows.map(x=>x[1]));
 document.getElementById('language-bars').replaceChildren(...rows.map(([name,count],i)=>{
  const row=document.createElement('div');row.className='language-row';
  const label=document.createElement('span');label.textContent=name;
  const track=document.createElement('i');track.setAttribute('aria-hidden','true');
  const bar=document.createElement('span');bar.style.setProperty('--bar-width',(count/max*100)+'%');bar.style.setProperty('--bar-color',colors[i%colors.length]);track.append(bar);
  const value=document.createElement('b');value.textContent=count;value.setAttribute('aria-label',count+' public repositories');row.append(label,track,value);return row;
 }));
}
const calendar=document.querySelector('.activity-scroll');
function alignCalendar(){calendar.scrollLeft=calendar.scrollWidth;document.querySelector('.calendar-cue').hidden=calendar.scrollWidth<=calendar.clientWidth+1;}
const calendarImage=document.querySelector('.activity-image');
const motionImages=[...document.querySelectorAll('[data-gif],[data-animated-sprite]')];
const inView=new Map(motionImages.map(img=>[img,true]));
const toggle=document.querySelector('.motion-toggle');
const reduce=window.matchMedia('(prefers-reduced-motion: reduce)');
let userPaused=false,calendarVisible=true;
function setMotionImage(img,stop){const path=stop?img.dataset.stillSrc:img.dataset.liveSrc;const next=embedded[path]||path;if(img.getAttribute('src')!==next)img.src=next;}
function updateMotion(){
 const paused=userPaused||reduce.matches||document.hidden;
 document.body.dataset.motion=paused?'paused':'running';
 motionImages.forEach(img=>{const stop=paused||!inView.get(img);setMotionImage(img,stop);(img.closest('.sprite')||img).classList.toggle('motion-offscreen',stop);});
 setMotionImage(calendarImage,paused||!calendarVisible);
 toggle.disabled=reduce.matches;toggle.setAttribute('aria-pressed',String(userPaused||reduce.matches));
 toggle.setAttribute('aria-label',reduce.matches?'Animations reduced by your system setting':userPaused?'Resume animations':'Pause animations');
 toggle.querySelector('span').textContent=reduce.matches?'Reduced motion':userPaused?'Resume motion':'Pause motion';
 toggle.querySelector('use').setAttribute('href',userPaused||reduce.matches?'#play':'#pause');
}
 toggle.addEventListener('click',()=>{if(!reduce.matches){userPaused=!userPaused;updateMotion();}});
 reduce.addEventListener('change',updateMotion);document.addEventListener('visibilitychange',updateMotion);
 if('IntersectionObserver'in window){const observer=new IntersectionObserver(entries=>{entries.forEach(entry=>{if(inView.has(entry.target))inView.set(entry.target,entry.isIntersecting);if(entry.target===calendar)calendarVisible=entry.isIntersecting;});updateMotion();},{threshold:.02});[calendar,...motionImages].forEach(node=>observer.observe(node));}
 window.addEventListener('resize',alignCalendar,{passive:true});alignCalendar();updateMotion();
