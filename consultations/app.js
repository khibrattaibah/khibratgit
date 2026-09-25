const areas=["البحث العلمي وتطوير الباحثين","النشر العلمي واختيار المجلات","إدارة وتطوير المجلات العلمية","التحكيم والنزاهة وأخلاقيات النشر","الفهرسة الدولية وقواعد البيانات","Crossref وDOI والبيانات الوصفية","OJS وإدارة منصات المجلات","الذكاء الاصطناعي في البحث العلمي","التحول الرقمي والأتمتة","المواقع والمنصات العلمية","تطوير المناهج والبرامج التعليمية","المشروعات والمبادرات العلمية","تطوير المؤسسات البحثية والتعليمية","قياس الأثر والمؤشرات","أخرى"];
document.querySelector("#areas").innerHTML=areas.map(x=>'<div class="card"><b>'+x+'</b></div>').join("");
document.querySelector("#areaSelect").innerHTML+=areas.map(x=>'<option>'+x+'</option>').join("");
const ch=document.querySelector('[name="challenge"]');
ch.addEventListener("input",()=>document.querySelector("#challengeCount").textContent=ch.value.length);

const cfg=window.KHIBRAT_CONFIG||{};
const ready=cfg.SUPABASE_URL&&!cfg.SUPABASE_URL.includes("YOUR_")&&cfg.SUPABASE_ANON_KEY&&!cfg.SUPABASE_ANON_KEY.includes("YOUR_");
const sb=ready?supabase.createClient(cfg.SUPABASE_URL,cfg.SUPABASE_ANON_KEY):null;

document.querySelector("#consultationForm").addEventListener("submit",async(e)=>{
  e.preventDefault();
  const msg=document.querySelector("#formMsg");
  msg.hidden=false;
  msg.className="msg";
  if(!sb){
    msg.classList.add("error");
    msg.textContent="النموذج جاهز تقنيًا، لكن لم يتم ربط قاعدة البيانات بعد. أضف بيانات Supabase في config.js.";
    return;
  }
  const button=e.target.querySelector('button[type="submit"]');
  button.disabled=true;
  button.textContent="جارٍ الإرسال...";
  const fd=new FormData(e.target);
  const payload=Object.fromEntries(fd.entries());
  payload.scope_consent=fd.get("scope_consent")==="on";
  payload.privacy_consent=fd.get("privacy_consent")==="on";
  const {data,error}=await sb.rpc("submit_consultation",{payload});
  button.disabled=false;
  button.textContent="إرسال طلب الاستشارة";
  if(error){
    console.error(error);
    msg.classList.add("error");
    msg.textContent="تعذر إرسال الطلب الآن. حاول مرة أخرى.";
    return;
  }
  location.href="./success.html?id="+encodeURIComponent(data);
});