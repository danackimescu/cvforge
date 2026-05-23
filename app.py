"""CVForge — Flask server for production deployment (gunicorn-compatible)."""
__author__  = "Dan Achimescu"
__app__     = "CVForge"
__version__ = "1.0.0"

import json
import os
import smtplib
import subprocess
import tempfile
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

from flask import Flask, request, jsonify, Response
from jinja2 import Environment, FileSystemLoader

app = Flask(__name__)

TEMPLATES_DIR = Path(__file__).parent / "templates"
DATA_FILE     = Path(__file__).parent / "cv_example.json"
EMAIL_CONFIG_FILE = Path(__file__).parent / "email_config.json"

LANGS = ["ro", "en"]

LABELS = {
    "ro": {
        "contact":    "Contact",
        "profile":    "Profil",
        "experience": "Experienta",
        "education":  "Educatie",
        "skills":     "Competente",
        "languages":  "Limbi",
        "projects":   "Proiecte",
    },
    "en": {
        "contact":    "Contact",
        "profile":    "Profile",
        "experience": "Experience",
        "education":  "Education",
        "skills":     "Skills",
        "languages":  "Languages",
        "projects":   "Projects",
    },
}

EDGE_PATHS = [
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    "/usr/bin/google-chrome",
    "/usr/bin/chromium-browser",
    "/usr/bin/chromium",
]


def get_templates():
    return sorted(f.stem for f in TEMPLATES_DIR.glob("*.html"))


def load_cv_data(lang: str) -> dict:
    with open(DATA_FILE, encoding="utf-8") as f:
        raw = json.load(f)
    if "ro" in raw or "en" in raw:
        return raw.get(lang) or raw.get(LANGS[0]) or {}
    return raw


def render_cv(template_name: str, lang: str = "ro") -> str:
    data = load_cv_data(lang)
    env = Environment(loader=FileSystemLoader(str(TEMPLATES_DIR)))
    return env.get_template(f"{template_name}.html").render(
        **data, labels=LABELS.get(lang, LABELS["ro"])
    )


def html_to_pdf_bytes(html: str) -> bytes:
    browser = next((p for p in EDGE_PATHS if Path(p).exists()), None)
    if not browser:
        raise RuntimeError("Edge/Chrome not found for PDF generation.")
    with tempfile.NamedTemporaryFile(suffix=".html", delete=False,
                                     mode="w", encoding="utf-8") as fh:
        fh.write(html)
        tmp_html = fh.name
    tmp_pdf = tmp_html.replace(".html", ".pdf")
    subprocess.run(
        [browser, "--headless=new", "--disable-gpu", "--no-sandbox",
         "--run-all-compositor-stages-before-draw",
         f"--print-to-pdf={tmp_pdf}", "--no-pdf-header-footer",
         f"file:///{tmp_html}"],
        capture_output=True, timeout=30, check=True,
    )
    pdf_bytes = Path(tmp_pdf).read_bytes()
    Path(tmp_html).unlink(missing_ok=True)
    Path(tmp_pdf).unlink(missing_ok=True)
    return pdf_bytes


def do_send_email(to: str, subject: str, body: str, template: str, lang: str = "ro"):
    if not EMAIL_CONFIG_FILE.exists():
        raise RuntimeError("email_config.json not found.")
    cfg = json.loads(EMAIL_CONFIG_FILE.read_text(encoding="utf-8"))
    pdf_bytes = html_to_pdf_bytes(render_cv(template, lang))
    with open(DATA_FILE, encoding="utf-8") as f:
        raw = json.load(f)
    data = raw.get(lang) or raw.get(LANGS[0]) or raw
    name = data.get("personal", {}).get("name", "CV")
    filename = f"CV_{name.replace(' ', '_')}_{template}.pdf"
    msg = MIMEMultipart()
    msg["From"] = f"{cfg.get('from_name', cfg['username'])} <{cfg['username']}>"
    msg["To"] = to
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain", "utf-8"))
    msg.attach(MIMEApplication(pdf_bytes, Name=filename, _subtype="pdf"))
    with smtplib.SMTP(cfg["smtp_host"], int(cfg["smtp_port"])) as srv:
        srv.ehlo(); srv.starttls()
        srv.login(cfg["username"], cfg["password"])
        srv.sendmail(cfg["username"], to, msg.as_string())


INJECTED_UI = """
<style>
@media print {
  #cv-nav, #cv-nav-spacer, #cv-print-modal, #cv-email-modal { display:none!important; }
  body { margin:0!important; }
}
.cv-modal {
  display:none; position:fixed; inset:0; z-index:10000;
  background:rgba(0,0,0,.55); font-family:Segoe UI,sans-serif;
}
.cv-modal.open { display:flex; flex-direction:column; align-items:center; }
.cv-modal-bar {
  width:100%; background:#1b3a5c; color:white;
  display:flex; align-items:center; justify-content:space-between;
  padding:0 24px; height:52px; flex-shrink:0;
}
.cv-modal-bar span { font-size:14px; font-weight:600; letter-spacing:.3px; }
.cv-modal-actions { display:flex; gap:10px; }
.cv-modal-actions button {
  padding:7px 20px; border:none; border-radius:4px;
  font-size:13px; font-weight:600; cursor:pointer;
}
.btn-primary { background:white; color:#1b3a5c; }
.btn-secondary { background:rgba(255,255,255,.15); color:white; }
.btn-secondary:disabled { opacity:.5; cursor:not-allowed; }
#cv-print-modal-body {
  flex:1; overflow-y:auto; padding:24px 0;
  display:flex; justify-content:center; width:100%;
}
#cv-print-frame {
  border:none; width:210mm; height:297mm;
  box-shadow:0 4px 32px rgba(0,0,0,.35);
  background:white; flex-shrink:0;
}
#cv-email-modal-body {
  background:white; margin-top:48px; border-radius:8px;
  padding:28px 32px; width:480px; box-shadow:0 8px 40px rgba(0,0,0,.25);
}
#cv-email-modal-body h3 { margin:0 0 20px; font-size:15px; color:#1b3a5c; }
.cv-field { margin-bottom:14px; }
.cv-field label {
  display:block; font-size:11px; font-weight:700;
  text-transform:uppercase; letter-spacing:.8px; color:#888; margin-bottom:5px;
}
.cv-field input, .cv-field textarea {
  width:100%; padding:8px 10px; border:1px solid #ddd; border-radius:4px;
  font-size:13px; font-family:inherit; box-sizing:border-box;
}
.cv-field textarea { resize:vertical; min-height:80px; }
#email-status {
  margin-top:12px; font-size:12px; min-height:18px;
  padding:6px 10px; border-radius:4px; display:none;
}
#email-status.ok  { display:block; background:#e8f5e9; color:#2e7d32; }
#email-status.err { display:block; background:#fdecea; color:#c62828; }
#email-status.loading { display:block; background:#e3f2fd; color:#1565c0; }
</style>
<div id="cv-print-modal" class="cv-modal">
  <div class="cv-modal-bar">
    <span>&#128438; Previzualizare inainte de tiparire</span>
    <div class="cv-modal-actions">
      <button class="btn-primary" onclick="doPrint()">Tipareste / PDF</button>
      <button class="btn-secondary" onclick="closeModal('cv-print-modal')">&#x2715; Inchide</button>
    </div>
  </div>
  <div id="cv-print-modal-body"><iframe id="cv-print-frame"></iframe></div>
</div>
<div id="cv-email-modal" class="cv-modal">
  <div class="cv-modal-bar">
    <span>&#9993; Trimite CV prin email</span>
    <div class="cv-modal-actions">
      <button id="btn-send-email" class="btn-primary" onclick="doSendEmail()">Trimite</button>
      <button class="btn-secondary" onclick="closeModal('cv-email-modal')">&#x2715; Inchide</button>
    </div>
  </div>
  <div id="cv-email-modal-body">
    <h3>Trimite CV-ul ca atasament PDF</h3>
    <div class="cv-field"><label>Catre (To)</label><input id="email-to" type="email" placeholder="destinatar@email.com"></div>
    <div class="cv-field"><label>Subiect</label><input id="email-subject" type="text"></div>
    <div class="cv-field"><label>Mesaj</label><textarea id="email-body"></textarea></div>
    <div id="email-status"></div>
  </div>
</div>
<script>
function currentTemplate(){return new URLSearchParams(window.location.search).get('t')||'';}
function currentLang(){return new URLSearchParams(window.location.search).get('lang')||'ro';}
function openPreview(){var t=currentTemplate(),lang=currentLang();document.getElementById('cv-print-frame').src='/raw?t='+t+'&lang='+lang;openModal('cv-print-modal');}
function doPrint(){document.getElementById('cv-print-frame').contentWindow.print();}
function openEmail(){var tmpl=currentTemplate(),lang=currentLang(),isEn=lang==='en';document.getElementById('email-subject').value=isEn?'CV - '+(tmpl?tmpl.charAt(0).toUpperCase()+tmpl.slice(1):'Application'):'CV - '+(tmpl?tmpl.charAt(0).toUpperCase()+tmpl.slice(1):'Candidatura');document.getElementById('email-body').value=isEn?'Dear Sir/Madam,\\n\\nPlease find my CV attached.\\n\\nBest regards,':'Buna ziua,\\n\\nVa trimit CV-ul meu in atasament.\\n\\nCu stima,';setStatus('','');openModal('cv-email-modal');}
function doSendEmail(){var to=document.getElementById('email-to').value.trim(),subject=document.getElementById('email-subject').value.trim(),body=document.getElementById('email-body').value,tmpl=currentTemplate(),lang=currentLang(),isEn=lang==='en';if(!to){setStatus(isEn?'Enter an email address.':'Introdu adresa de email.','err');return;}var btn=document.getElementById('btn-send-email');btn.disabled=true;setStatus(isEn?'Sending...':'Se trimite...','loading');fetch('/send-email',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({to,subject,body,template:tmpl,lang})}).then(r=>r.json()).then(d=>{var isEn=currentLang()==='en';if(d.ok){setStatus((isEn?'Email sent to ':'Email trimis catre ')+to+' !','ok');}else{setStatus((isEn?'Error: ':'Eroare: ')+d.error,'err');}btn.disabled=false;}).catch(e=>{var isEn=currentLang()==='en';setStatus((isEn?'Network error: ':'Eroare retea: ')+e,'err');btn.disabled=false;});}
function setStatus(msg,cls){var el=document.getElementById('email-status');el.textContent=msg;el.className=cls;}
function openModal(id){document.getElementById(id).classList.add('open');document.body.style.overflow='hidden';}
function closeModal(id){document.getElementById(id).classList.remove('open');if(id==='cv-print-modal')document.getElementById('cv-print-frame').src='';if(!document.querySelector('.cv-modal.open'))document.body.style.overflow='';}
document.addEventListener('keydown',function(e){if(e.key==='Escape')document.querySelectorAll('.cv-modal.open').forEach(m=>closeModal(m.id));});
</script>
"""


def wrap_with_nav(cv_html: str, templates: list, active_t: str, active_lang: str) -> str:
    tabs = "".join(
        f'<a href="/?t={t}&lang={active_lang}" style="padding:8px 14px;text-decoration:none;'
        f'font-weight:{"700" if t == active_t else "400"};'
        f'color:{"#1b3a5c" if t == active_t else "#888"};'
        f'border-bottom:{"3px solid #1b3a5c" if t == active_t else "3px solid transparent"};'
        f'font-size:13px">{t}</a>'
        for t in templates
    )
    lang_switcher = "".join(
        f'<a href="/?t={active_t}&lang={lg}" style="padding:4px 9px;text-decoration:none;'
        f'font-size:11px;font-weight:700;border-radius:3px;'
        f'background:{"#1b3a5c" if lg == active_lang else "transparent"};'
        f'color:{"white" if lg == active_lang else "#aaa"};'
        f'border:1px solid {"#1b3a5c" if lg == active_lang else "#ddd"}">'
        f'{lg.upper()}</a>'
        for lg in LANGS
    )
    buttons = (
        '<div style="margin-left:auto;display:flex;align-items:center;gap:8px">'
        f'<div style="display:flex;gap:3px;margin-right:4px">{lang_switcher}</div>'
        '<button onclick="openPreview()" style="padding:6px 14px;background:#1b3a5c;color:white;border:none;border-radius:4px;font-size:12px;font-weight:600;cursor:pointer">&#128438; Previzualizeaza / Print</button>'
        '<button onclick="openEmail()" style="padding:6px 14px;background:#2e7d32;color:white;border:none;border-radius:4px;font-size:12px;font-weight:600;cursor:pointer">&#9993; Trimite email</button>'
        '</div>'
    )
    nav = (
        f'<div id="cv-nav" style="position:fixed;top:0;left:0;right:0;background:white;'
        f'border-bottom:1px solid #eee;display:flex;align-items:center;'
        f'gap:4px;padding:0 20px;z-index:9999;height:44px;'
        f'font-family:Segoe UI,sans-serif;box-shadow:0 1px 4px rgba(0,0,0,.06)">'
        f'<span style="font-size:13px;font-weight:700;color:#1b3a5c;margin-right:16px;letter-spacing:-.3px">CV<span style="color:#e05c1a">Forge</span></span>'
        f'<span style="font-size:11px;color:#aaa;margin-right:8px">Template:</span>'
        f'{tabs}{buttons}</div>'
        f'<div id="cv-nav-spacer" style="height:44px"></div>'
    )
    injection = INJECTED_UI + nav
    if "<body>" in cv_html:
        return cv_html.replace("<body>", f"<body>{injection}", 1)
    return injection + cv_html


@app.route("/")
def index():
    templates = get_templates()
    active_t = request.args.get("t", templates[0])
    if active_t not in templates:
        active_t = templates[0]
    active_lang = request.args.get("lang", LANGS[0])
    if active_lang not in LANGS:
        active_lang = LANGS[0]
    html = wrap_with_nav(render_cv(active_t, active_lang), templates, active_t, active_lang)
    return Response(html, mimetype="text/html; charset=utf-8")


@app.route("/raw")
def raw():
    templates = get_templates()
    active_t = request.args.get("t", templates[0])
    if active_t not in templates:
        active_t = templates[0]
    active_lang = request.args.get("lang", LANGS[0])
    if active_lang not in LANGS:
        active_lang = LANGS[0]
    html = render_cv(active_t, active_lang)
    return Response(html, mimetype="text/html; charset=utf-8")


@app.route("/send-email", methods=["POST"])
def send_email_route():
    templates = get_templates()
    payload = request.get_json(force=True)
    try:
        do_send_email(
            to=payload["to"],
            subject=payload.get("subject", "CV"),
            body=payload.get("body", ""),
            template=payload.get("template") or templates[0],
            lang=payload.get("lang", LANGS[0]),
        )
        return jsonify({"ok": True})
    except Exception as exc:
        return jsonify({"ok": False, "error": str(exc)})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8765))
    app.run(host="0.0.0.0", port=port, debug=False)
