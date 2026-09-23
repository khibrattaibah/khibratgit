"""Build the bilingual A4 brochure. Requires PyMuPDF."""
from pathlib import Path
import fitz

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'docs' / 'Research_to_Impact_AR_EN_Profile.pdf'
FONT = Path('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf')
ARCHIVE = fitz.Archive(str(FONT.parent))
CSS = '''
@font-face { font-family: dv; src: url(DejaVuSans.ttf); }
* { font-family: dv; box-sizing: border-box; }
body { color: #183344; font-size: 11pt; line-height: 1.48; }
h1 { font-size: 29pt; line-height: 1.28; margin: 0 0 16pt; color: #12384a; }
h2 { font-size: 17pt; color: #12384a; margin: 0 0 11pt; }
h3 { font-size: 12.5pt; color: #007f79; margin: 0 0 5pt; }
p { margin: 0 0 10pt; }
ul { margin: 0 0 9pt; padding-left: 20pt; }
li { margin: 0 0 6pt; }
.ar { direction: rtl; text-align: right; }
.en { direction: ltr; text-align: left; }
.eyebrow { color: #008b81; font-size: 10pt; font-weight: bold; letter-spacing: 1px; }
.lead { font-size: 15pt; line-height: 1.55; color: #274e59; }
.small { font-size: 9.5pt; color: #526b71; }
.card { background: #eff6f4; padding: 14pt; border-radius: 9pt; margin: 10pt 0; }
.card2 { background: #f4f2ec; padding: 14pt; border-radius: 9pt; margin: 10pt 0; }
.step { color: #007f79; font-weight: bold; }
'''

def box(page, rect, html, css=CSS):
    spare, scale = page.insert_htmlbox(fitz.Rect(*rect), html, css=css, archive=ARCHIVE, scale_low=0.86)
    if spare < 0:
        raise RuntimeError(f'HTML did not fit page {page.number + 1}: {scale}')

def base(doc, number, section):
    p = doc.new_page(width=595, height=842)
    p.draw_rect(fitz.Rect(0, 0, 595, 12), color=None, fill=(0.0, .49, .47))
    p.draw_rect(fitz.Rect(0, 806, 595, 842), color=None, fill=(.07, .22, .29))
    p.insert_text((42, 826), section, fontsize=8, color=(1, 1, 1))
    p.insert_text((519, 826), f'{number:02d} / 04', fontsize=8, color=(1, 1, 1))
    return p

doc = fitz.open()
# 1: cover
p = base(doc, 1, 'KHIBRAT TAIBAH  |  OPEN SOURCE')
p.draw_circle((528, 118), 93, color=None, fill=(.88, .94, .91))
p.draw_circle((528, 118), 62, color=None, fill=(.75, .88, .84))
p.draw_circle((528, 118), 33, color=None, fill=(.0, .49, .47))
box(p, (42, 78, 471, 298), '''<div class="ar"><p class="eyebrow">أداة مفتوحة المصدر · الإصدار التجريبي 0.1.0</p><h1>من الفكرة<br>إلى الأثر</h1><p class="lead">عدة عربية تساعد الفرق الصغيرة على تحديد المشكلة، وتوثيق الدليل، وبناء شريحة نافعة قابلة للاختبار.</p></div>''')
p.draw_line((42, 330), (553, 330), color=(0, .49, .47), width=1.5)
box(p, (42, 361, 552, 568), '''<div class="en"><p class="eyebrow">OPEN-SOURCE PRESET FOR GITHUB SPEC KIT</p><h1>Research to Impact</h1><p class="lead">A practical Arabic workflow for small research, education, and community teams: define the need, trace the evidence, review the content, and test a useful first release.</p></div>''')
p.draw_rect(fitz.Rect(42, 555, 204, 601), color=None, fill=(.90, .95, .93))
p.draw_rect(fitz.Rect(214, 555, 380, 601), color=None, fill=(.93, .95, .91))
p.draw_rect(fitz.Rect(390, 555, 553, 601), color=None, fill=(.90, .95, .93))
box(p, (53, 565, 200, 596), '<div class="en" style="font-size:10pt;color:#007f79">EVIDENCE</div>')
box(p, (225, 565, 376, 596), '<div class="en" style="font-size:10pt;color:#007f79">REVIEW</div>')
box(p, (401, 565, 548, 596), '<div class="en" style="font-size:10pt;color:#007f79">DELIVERY</div>')
box(p, (42, 636, 552, 779), '''<div class="card ar"><h3>ثلاث وثائق عملية</h3><p>دستور المشروع ← مواصفة الميزة ← خطة التنفيذ</p><p class="small">تصدر الأداة عن مبادرة مكتب خبرات طيبة للبحوث والدراسات بالمدينة المنورة. وهي مستقلة عن مشروع GitHub Spec Kit الرسمي.</p></div>''')
# 2 Arabic
p = base(doc, 2, 'METHOD & PRINCIPLES  |  ARABIC')
box(p, (42, 55, 553, 182), '''<div class="ar"><p class="eyebrow">01  /  المشكلة والحل</p><h2>كيف تتحول الفكرة إلى عمل يمكن مراجعته؟</h2><p>كثير من المبادرات تبدأ بمنصة أو وعود واسعة قبل تحديد المستفيد، والتحقق من الحقوق، أو وضع معيار لما يُعد نجاحًا. ترتب الأداة الأسئلة والقرارات في ملفات واضحة قبل توسيع البرمجة والإنفاق.</p></div>''')
box(p, (42, 188, 553, 390), '''<div class="ar"><div class="card"><h3>دستور المشروع</h3><p>المصادر، والأمانة العلمية، والحقوق، والخصوصية، وأدوار المراجعة والتصحيح.</p></div><div class="card2"><h3>مواصفة الميزة</h3><p>المستفيد والمشكلة، وسيناريوهات الاستخدام، ومعايير القبول، وسجل المصادر والحالات الناقصة.</p></div></div>''')
box(p, (42, 402, 553, 522), '''<div class="ar"><div class="card"><h3>خطة التنفيذ</h3><p>الشريحة الأولى، والمسؤوليات، والتبعيات، وتكلفة الوقت والمال، والمخاطر ونقطة قرار الاستمرار.</p></div></div>''')
box(p, (42, 550, 553, 763), '''<div class="ar"><p class="eyebrow">02  /  الضابط العلمي</p><h2>من المصدر إلى تصحيح الخطأ</h2><p>المصدر الأصلي ← حق الاستخدام ← التحويل أو التلخيص ← مراجعة بشرية ← نشر بإصدار معلوم ← بلاغ وتصحيح.</p><p>لا تُنسب نتيجة مولدة آليًا إلى مصدر لم يقلها، ولا تُوصف مادة مشتقة بأنها «محكّمة» لمجرد أن بحثها الأصلي محكّم. تقيس التجربة استخدام المنتج وجودته ضمن عيّنتها؛ ولا تدّعي إثبات أثر مجتمعي طويل المدى دون متابعة مناسبة.</p></div>''')
# 3 English
p = base(doc, 3, 'METHOD & SCOPE  |  ENGLISH')
box(p, (42, 55, 553, 208), '''<div class="en"><p class="eyebrow">01  /  THE PRACTICAL WORKFLOW</p><h2>Turn an idea into a reviewable first release</h2><p>The kit is a preset for GitHub Spec Kit. It adapts three templates while leaving Spec Kit's planning, task generation, implementation, and convergence workflow in place. It runs on Markdown and Git; no paid API or new platform is required.</p></div>''')
box(p, (42, 212, 553, 530), '''<div class="en"><div class="card"><h3>Project constitution</h3><p>Establishes evidence, licensing, privacy, expert review, correction, and change control from the first commit.</p></div><div class="card2"><h3>Feature specification</h3><p>States the user's job, a testable scenario, acceptance criteria, out-of-scope items, and a source-and-rights ledger.</p></div><div class="card"><h3>Implementation plan</h3><p>Defines the smallest useful slice, owners, dependencies, cost assumptions, risks, rollback, and a stop-or-expand decision.</p></div></div>''')
box(p, (42, 555, 553, 765), '''<div class="en"><p class="eyebrow">02  /  WHO CAN USE IT</p><h2>Research, education, and civic projects</h2><p>A project lead and one developer can start; specialist reviewers join only where the subject requires them. The repository includes a sample Tadabbur Index feature, showing how a small searchable corpus would be gated on text accuracy and reuse rights.</p><p class="small">The sample is illustrative. It does not verify the rights or accuracy of any specific journal material.</p></div>''')
# 4 quickstart
p = base(doc, 4, 'START & GOVERNANCE  |  AR / EN')
box(p, (42, 55, 553, 315), '''<div class="ar"><p class="eyebrow">03  /  ابدأ بتجربة صغيرة</p><h2>مسار الاستخدام</h2><p><span class="step">1.</span> ثبّت Spec Kit رسميًا وأنشئ مشروعًا بتكامل وكيلك.</p><p><span class="step">2.</span> ثبّت هذا الـPreset محليًا، ثم راجع واعتمد الدستور.</p><p><span class="step">3.</span> اكتب مواصفة لميزة واحدة، وخطة، ومهامًا مرتبة؛ نفّذها واختبر قبولها.</p><p><span class="step">4.</span> سجّل نتائج الاستخدام والأخطاء والتكلفة، ثم قرر التوسع أو التعديل أو التوقف.</p></div>''')
p.draw_line((42, 344), (553, 344), color=(.72, .83, .81), width=1)
box(p, (42, 370, 553, 616), '''<div class="en"><p class="eyebrow">QUICK START</p><h2>One small feature at a time</h2><p>Install Spec Kit, initialize a project, and add the preset from its local directory. Review the constitution before accepting contributions. Use the supplied Tadabbur Index example to rehearse the workflow; replace it with your own project's evidence and permissions.</p><p><b>Release gate:</b> verify preset installation on the intended Spec Kit version, inspect the templates in a real project, then publish a tagged GitHub release.</p></div>''')
p.draw_rect(fitz.Rect(42, 615, 553, 773), color=None, fill=(.94, .96, .94))
box(p, (56, 632, 539, 763), '''<div class="ar"><h3>المسؤولية والملكية</h3><p>المكتب يصدر العدة العامة؛ كل فريق مسؤول عن مادته وحقوقها وصحة مخرجاته. استخدام مجلة تدبر مثالًا لا يغيّر استقلال قرارها العلمي والتحريري.</p><p class="small">الترخيص: MIT · الحالة: نسخة تجريبية · 23 سبتمبر 2026</p></div>''')
OUT.parent.mkdir(parents=True, exist_ok=True)
doc.set_metadata({'title':'من الفكرة إلى الأثر | Research to Impact','author':'Khibrat Taibah for Research and Studies','subject':'Bilingual open-source Spec Kit preset profile'})
doc.save(OUT, garbage=4, deflate=True)
print(OUT)
