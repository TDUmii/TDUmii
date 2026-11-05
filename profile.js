const data=window.UMI_PROFILE;
const embedded=window.UMI_ASSETS||{};
const asset=path=>embedded[path]||path;
const colors=['#b8efaa','#8cbdd1','#efc780','#cfb4e7','#a1c2bc','#dcad89'];
if(data){
 const stats={repos:data.public_repos,stars:data.stars,languages:data.languages.length,contributions:data.contribution_total,activeDays:data.active_days,recent:data.recent_contributions,bestDay:data.best_day};
 document.querySelectorAll('[data-stat]').forEach(node=>node.textContent=stats[node.dataset.stat].toLocaleString('en-US'));
 document.getElementById('snapshot-date').textContent='Public GitHub data · '+data.date_label;
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
function alignCalendar(){calendar.scrollLeft=calendar.scrollWidth;const cue=document.querySelector('.calendar-cue');if(cue)cue.hidden=calendar.scrollWidth<=calendar.clientWidth+1;}
requestAnimationFrame(alignCalendar);window.addEventListener('resize',alignCalendar,{passive:true});
const calendarImage=document.querySelector('.activity-image');
const calendarLive=calendarImage.dataset.liveSrc||asset('assets/calendar.svg');
const calendarStill=calendarImage.dataset.stillSrc||asset('assets/calendar-static.svg');
let calendarVisible=true;
function updateCalendarMotion(){const stop=userPaused||reduce.matches||document.hidden||!calendarVisible;const next=stop?calendarStill:calendarLive;if(calendarImage.getAttribute('src')!==next)calendarImage.src=next;}
const image=document.getElementById('nyan-cat');
const stage=document.querySelector('.cat-stage');
const toggle=document.querySelector('.motion-toggle');
const reduce=window.matchMedia('(prefers-reduced-motion: reduce)');
let userPaused=false,visible=true;
let canvasRunning=false,lastFrame=0,frameId=0;
const canvas=document.getElementById('starfield');
const ctx=canvas.getContext('2d');
const stars=Array.from({length:27},(_,i)=>({x:((i*67+11)%101)/100,y:((i*29+9)%97)/100,s:i%5===0?2:1,speed:.012+(i%4)*.005}));
function sizeCanvas(){document.querySelectorAll('.timeline-track').forEach(track=>track.style.setProperty('--track-distance',track.clientWidth+'px'));const box=stage.getBoundingClientRect();const ratio=Math.min(devicePixelRatio||1,2);canvas.width=box.width*ratio;canvas.height=box.height*ratio;ctx.setTransform(ratio,0,0,ratio,0,0);draw(0);}
function draw(delta){const w=canvas.clientWidth,h=canvas.clientHeight;ctx.clearRect(0,0,w,h);stars.forEach(star=>{star.x=(star.x-star.speed*delta+1)%1;ctx.fillStyle=star.s===2?'#b8efaa':'#7893a5';ctx.globalAlpha=star.s===2?.65:.55;ctx.fillRect(Math.round(star.x*w),Math.round(star.y*h),star.s,star.s);});ctx.globalAlpha=1;}
function tick(t){if(!canvasRunning)return;if(t-lastFrame>1000/24){draw(lastFrame?Math.min((t-lastFrame)/1000,.1):0);lastFrame=t;}frameId=requestAnimationFrame(tick);}
function updateMotion(){
 const paused=userPaused||reduce.matches||document.hidden;
 document.body.dataset.motion=paused?'paused':'running';
 const stopGif=paused||!visible;
 const next=asset(stopGif?'assets/nyan-cat-still.png':'assets/nyan-cat.gif');
 if(image.getAttribute('src')!==next)image.src=next;
 toggle.disabled=reduce.matches;
 toggle.setAttribute('aria-pressed',String(userPaused||reduce.matches));
 toggle.setAttribute('aria-label',reduce.matches?'Animations reduced by your system setting':userPaused?'Resume animations':'Pause animations');
 toggle.querySelector('span').textContent=reduce.matches?'Reduced motion':userPaused?'Resume motion':'Pause motion';
 toggle.querySelector('use').setAttribute('href',userPaused||reduce.matches?'#play':'#pause');
 const shouldRun=!stopGif;
 if(shouldRun&&!canvasRunning){canvasRunning=true;lastFrame=0;frameId=requestAnimationFrame(tick);}
 else if(!shouldRun){canvasRunning=false;cancelAnimationFrame(frameId);draw(0);}
 document.querySelectorAll('.flight-path svg').forEach(svg=>{if(stopGif)svg.pauseAnimations();else svg.unpauseAnimations();});
 updateCalendarMotion();
}
toggle.addEventListener('click',()=>{if(reduce.matches)return;userPaused=!userPaused;updateMotion();});
reduce.addEventListener('change',updateMotion);document.addEventListener('visibilitychange',updateMotion);
if('IntersectionObserver'in window){
 const observer=new IntersectionObserver(entries=>entries.forEach(entry=>{entry.target.classList.toggle('motion-offscreen',!entry.isIntersecting);if(entry.target===stage){visible=entry.isIntersecting;updateMotion();}if(entry.target===calendar){calendarVisible=entry.isIntersecting;updateCalendarMotion();}}),{threshold:.03});
 [stage,calendar,...document.querySelectorAll('.bridge-visual,.display-diagram,.timeline-diagram')].forEach(node=>observer.observe(node));
}
window.addEventListener('resize',sizeCanvas,{passive:true});sizeCanvas();updateMotion();
