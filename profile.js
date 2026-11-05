const data=window.UMI_PROFILE;
const embedded=window.UMI_ASSETS||{};
const asset=path=>embedded[path]||path;
const calendar=document.querySelector('.activity-scroll');
function alignCalendar(){calendar.scrollLeft=innerWidth<=620?calendar.scrollWidth:0;}
requestAnimationFrame(alignCalendar);window.addEventListener('resize',alignCalendar,{passive:true});
if(data){
 const stats={repos:data.public_repos,stars:data.stars,languages:data.languages.length,contributions:data.contribution_total};
 document.querySelectorAll('[data-stat]').forEach(node=>node.textContent=stats[node.dataset.stat].toLocaleString('en-US'));
 const list=document.getElementById('languages');list.replaceChildren(...data.languages.map(name=>{const item=document.createElement('span');item.textContent=name;return item;}));
 document.getElementById('snapshot-date').textContent='Public GitHub data · '+data.date_label;
}
const image=document.getElementById('nyan-cat');
const stage=document.querySelector('.cat-stage');
const toggle=document.querySelector('.motion-toggle');
const reduce=window.matchMedia('(prefers-reduced-motion: reduce)');
let userPaused=false,visible=true;
function updateMotion(){
 const paused=userPaused||reduce.matches||document.hidden||!visible;
 document.body.dataset.motion=paused?'paused':'running';
 const next=asset(paused?'assets/nyan-cat-still.png':'assets/nyan-cat.gif');
 if(image.getAttribute('src')!==next)image.src=next;
 toggle.disabled=reduce.matches;
 toggle.setAttribute('aria-pressed',String(userPaused||reduce.matches));
 toggle.setAttribute('aria-label',reduce.matches?'Animations reduced by your system setting':userPaused?'Resume animations':'Pause animations');
 toggle.querySelector('span').textContent=reduce.matches?'Reduced motion':userPaused?'Resume motion':'Pause motion';
 toggle.querySelector('use').setAttribute('href',userPaused||reduce.matches?'#play':'#pause');
}
toggle.addEventListener('click',()=>{if(reduce.matches)return;userPaused=!userPaused;updateMotion();});
reduce.addEventListener('change',updateMotion);document.addEventListener('visibilitychange',updateMotion);
if('IntersectionObserver'in window)new IntersectionObserver(entries=>{visible=entries[0].isIntersecting;updateMotion();},{threshold:.05}).observe(stage);
updateMotion();
