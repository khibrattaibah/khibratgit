const cfg=window.KHIBRAT_CONFIG||{};
const ready=cfg.SUPABASE_URL&&!cfg.SUPABASE_URL.includes("YOUR_")&&cfg.SUPABASE_ANON_KEY&&!cfg.SUPABASE_ANON_KEY.includes("YOUR_");
const loginBox=document.querySelector("#loginBox");
const adminBox=document.querySelector("#adminBox");
let rows=[];

if(!ready){
  loginBox.innerHTML='<div class="msg error">لم يتم ربط Supabase بعد. أضف Project URL وAnon Key في config.js.</div>';
}else{
  const sb=supabase.createClient(cfg.SUPABASE_URL,cfg.SUPABASE_ANON_KEY);
  const labels={new:"جديد",reviewing:"قيد المراجعة",accepted:"مقبول",waitlist:"قائمة انتظار",declined:"معتذر",booked:"تم الحجز",completed:"مكتمل"};
  const criteria=[
    ["score_relevance","ارتباط الموضوع بتخصص المكتب"],
    ["score_clarity","وضوح المشكلة"],
    ["score_30min_value","إمكانية تقديم قيمة خلال 30 دقيقة"],
    ["score_impact","الأثر المحتمل"],
    ["score_readiness","جاهزية صاحب الطلب"]
  ];

  function esc(v){return String(v??"").replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#039;"}[c]));}
  function scoreOptions(v){return ["","0","1","2"].map(x=>'<option value="'+x+'" '+(String(v??"")===x?'selected':'')+'>'+ (x===""?"لم يقيّم":x) +'</option>').join("");}

  async function showAdmin(){
    const {data,error}=await sb.from("consultation_requests").select("*").order("created_at",{ascending:false});
    if(error){
      loginBox.hidden=false; adminBox.hidden=true;
      loginBox.innerHTML='<div class="msg error">الحساب مسجل، لكنه غير مخول للوصول إلى طلبات المبادرة. أضف المستخدم إلى admin_users.</div>';
      return;
    }
    rows=data||[]; loginBox.hidden=true; adminBox.hidden=false; render();
  }

  async function boot(){
    const {data}=await sb.auth.getSession();
    if(data.session) await showAdmin();
  }

  document.querySelector("#loginForm").addEventListener("submit",async(e)=>{
    e.preventDefault();
    const fd=new FormData(e.target),msg=document.querySelector("#loginMsg");
    const {error}=await sb.auth.signInWithPassword({email:String(fd.get("email")||""),password:String(fd.get("password")||"")});
    if(error){msg.hidden=false;msg.className="msg error";msg.textContent="بيانات الدخول غير صحيحة أو الحساب غير مفعّل.";return}
    await showAdmin();
  });

  function render(){
    const counts={new:0,reviewing:0,accepted:0,waitlist:0,declined:0,booked:0,completed:0};
    rows.forEach(r=>counts[r.status]=(counts[r.status]||0)+1);
    document.querySelector("#stats").innerHTML=
      '<div><b>'+rows.length+'</b><span>إجمالي الطلبات</span></div>'+
      ['new','reviewing','accepted'].map(k=>'<div><b>'+counts[k]+'</b><span>'+labels[k]+'</span></div>').join("");

    const q=document.querySelector("#search").value.trim().toLowerCase();
    const sf=document.querySelector("#statusFilter").value;
    const filtered=rows.filter(r=>{
      const bag=[r.full_name,r.email,r.organization,r.consultation_area,r.public_id].join(" ").toLowerCase();
      return (!sf||r.status===sf)&&(!q||bag.includes(q));
    });

    document.querySelector("#requests").innerHTML=filtered.map(r=>{
      const opts=Object.keys(labels).map(k=>'<option value="'+k+'" '+(k===r.status?'selected':'')+'>'+labels[k]+'</option>').join("");
      const criteriaHtml=criteria.map(([key,label])=>'<label>'+label+'<select data-field="'+key+'" class="criterion">'+scoreOptions(r[key])+'</select></label>').join("");
      return '<article class="card request-card" data-id="'+esc(r.id)+'">'+
        '<b>'+esc(r.public_id)+' · '+esc(r.full_name)+'</b>'+
        '<p>'+esc(r.consultation_area)+' · '+esc(r.email)+'</p>'+
        '<p><strong>التحدي:</strong> '+esc(r.challenge)+'</p>'+
        '<p><strong>ما جُرّب:</strong> '+esc(r.tried||"لم يذكر")+'</p>'+
        '<p><strong>النتيجة المطلوبة:</strong> '+esc(r.desired_outcome)+'</p>'+
        '<div class="grid2"><label>الحالة<select data-field="status">'+opts+'</select></label><label>المستشار<input data-field="assigned_consultant" value="'+esc(r.assigned_consultant)+'"></label></div>'+
        '<h3>التقييم الداخلي <span class="total-score">'+esc(r.score??0)+'</span>/10</h3>'+
        '<div class="grid2 criteria">'+criteriaHtml+'</div>'+
        '<label>رابط Luma للحالة المقبولة<input data-field="booking_url" type="url" value="'+esc(r.booking_url)+'"></label>'+
        '<label>ملاحظات المراجع<textarea data-field="reviewer_notes">'+esc(r.reviewer_notes)+'</textarea></label>'+
        '<div class="hero-actions"><button class="btn save" type="button">حفظ التعديلات</button><button class="btn ghost copy-email" type="button">نسخ البريد</button></div>'+
      '</article>';
    }).join("")||'<p>لا توجد نتائج.</p>';

    document.querySelectorAll(".request-card").forEach(card=>{
      const id=card.dataset.id;
      const recalc=()=>{let total=0;card.querySelectorAll(".criterion").forEach(el=>total+=Number(el.value||0));card.querySelector(".total-score").textContent=total;};
      card.querySelectorAll(".criterion").forEach(el=>el.addEventListener("change",recalc));
      card.querySelector(".save").addEventListener("click",async()=>{
        const payload={};
        card.querySelectorAll("[data-field]").forEach(el=>{
          const k=el.dataset.field;
          payload[k]=criteria.some(([key])=>key===k)?(el.value===""?null:Number(el.value)):el.value;
        });
        const {data,error}=await sb.from("consultation_requests").update(payload).eq("id",id).select("*").single();
        if(error){alert("تعذر حفظ التعديلات.");return}
        const idx=rows.findIndex(x=>x.id===id); if(idx>=0) rows[idx]=data;
        card.querySelector(".total-score").textContent=data.score??0;
        alert("تم الحفظ.");
      });
      card.querySelector(".copy-email").addEventListener("click",()=>{const row=rows.find(x=>x.id===id);if(row) navigator.clipboard.writeText(row.email);});
    });
  }

  document.querySelector("#search").addEventListener("input",render);
  document.querySelector("#statusFilter").addEventListener("change",render);
  boot();
}