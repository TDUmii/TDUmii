const data=window.UMI_PROFILE;
const embedded=window.UMI_ASSETS||{};
const colors=['#b8efaa','#99c7dd','#efc780','#cfb4e7','#a1c2bc','#dcad89'];
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
function alignCalendar(){calendar.scrollLeft=calendar.scrollWidth;document.querySelector('.calendar-cue').hidden=calendar.scrollWidth<=calendar.clientWidth+1;}
const calendarImage=document.querySelector('.activity-image');
const gifs=[...document.querySelectorAll('[data-gif]')];
const inView=new Map(gifs.map(img=>[img,true]));
const scene=document.querySelector('.night-scene');
const toggle=document.querySelector('.motion-toggle');
const reduce=window.matchMedia('(prefers-reduced-motion: reduce)');
let userPaused=false,sceneVisible=true,calendarVisible=true;
let frameId=0,lastFrame=0,running=false;
const canvas=document.getElementById('starfield');
const ctx=canvas.getContext('2d');
const stars=Array.from({length:36},(_,i)=>({x:((i*67+11)%101)/100,y:((i*29+9)%97)/100,size:i%7===0?2:1,speed:.002+(i%4)*.001}));
function draw(delta){const w=canvas.clientWidth,h=canvas.clientHeight;ctx.clearRect(0,0,w,h);stars.forEach((star,i)=>{star.x=(star.x-star.speed*delta+1)%1;ctx.fillStyle=i%7===0?'#b8efaa':'#7291b1';ctx.globalAlpha=star.size===2?.6:.38;ctx.fillRect(Math.round(star.x*w),Math.round(star.y*h),star.size,star.size);});ctx.globalAlpha=1;}
function sizeCanvas(){const box=scene.getBoundingClientRect();const ratio=Math.min(devicePixelRatio||1,2);canvas.width=box.width*ratio;canvas.height=box.height*ratio;ctx.setTransform(ratio,0,0,ratio,0,0);draw(0);}
function tick(t){if(!running)return;if(t-lastFrame>1000/20){draw(lastFrame?Math.min((t-lastFrame)/1000,.1):0);lastFrame=t;}frameId=requestAnimationFrame(tick);}
function setMotionImage(img,stop){const path=stop?img.dataset.stillSrc:img.dataset.liveSrc;const next=embedded[path]||path;if(img.getAttribute('src')!==next)img.src=next;}
function updateMotion(){
 const paused=userPaused||reduce.matches||document.hidden;
 document.body.dataset.motion=paused?'paused':'running';
 gifs.forEach(img=>{const stop=paused||!inView.get(img);setMotionImage(img,stop);img.closest('.sprite').classList.toggle('motion-offscreen',stop);});
 setMotionImage(calendarImage,paused||!calendarVisible);
 toggle.disabled=reduce.matches;
 toggle.setAttribute('aria-pressed',String(userPaused||reduce.matches));
 toggle.setAttribute('aria-label',reduce.matches?'Animations reduced by your system setting':userPaused?'Resume animations':'Pause animations');
 toggle.querySelector('span').textContent=reduce.matches?'Reduced motion':userPaused?'Resume motion':'Pause motion';
 toggle.querySelector('use').setAttribute('href',userPaused||reduce.matches?'#play':'#pause');
 const shouldRun=!paused&&sceneVisible;
 if(shouldRun&&!running){running=true;lastFrame=0;frameId=requestAnimationFrame(tick);}
 else if(!shouldRun){running=false;cancelAnimationFrame(frameId);draw(0);}
}
toggle.addEventListener('click',()=>{if(!reduce.matches){userPaused=!userPaused;updateMotion();}});
reduce.addEventListener('change',updateMotion);document.addEventListener('visibilitychange',updateMotion);
if('IntersectionObserver'in window){
 const observer=new IntersectionObserver(entries=>{entries.forEach(entry=>{if(inView.has(entry.target))inView.set(entry.target,entry.isIntersecting);if(entry.target===scene)sceneVisible=entry.isIntersecting;if(entry.target===calendar)calendarVisible=entry.isIntersecting;});updateMotion();},{threshold:.02});
 [scene,calendar,...gifs].forEach(node=>observer.observe(node));
}
window.addEventListener('resize',()=>{sizeCanvas();alignCalendar();},{passive:true});
sizeCanvas();alignCalendar();updateMotion();
