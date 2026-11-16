/* ================= 2. Helpers ================= */
const $=id=>document.getElementById(id);
const esc=s=>String(s??"").replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
const norm=s=>String(s||"").replace(/[‘’]/g,"'").replace(/[“”]/g,'"').replace(/\s+/g," ").trim().toLowerCase();
const money=v=>v==null?"—":"$"+Number(v).toLocaleString("en-US");
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
function hash(s){let h=2166136261;for(const c of s){h^=c.charCodeAt(0);h=Math.imul(h,16777619)}return("0000000"+(h>>>0).toString(16)).slice(-8)}
const uid=(()=>{let n=0;return p=>p+"-"+(++n).toString(36)})();
function wordingIn(text){return Object.keys(WORDING).filter(k=>WORDING[k].test(text||""))}

