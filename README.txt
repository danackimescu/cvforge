╔══════════════════════════════════════════════════════╗
║                     CVForge                         ║
║         Generator de CV  •  RO / EN                 ║
╚══════════════════════════════════════════════════════╝

 ► Romana  (pag. 1)
 ► English (page 2)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                        ROMANA
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

INSTALARE
─────────
1. Instaleaza Python de la https://python.org
   (bifeaza "Add Python to PATH" la instalare)

2. Deschide un terminal in acest folder si ruleaza:
      pip install jinja2

3. Copiaza datele exemplu:
      copy cv_example.json cv.json

4. Deschide cv.json cu orice editor de text (Notepad, VS Code)
   si completeaza cu datele tale.
   Fisierul are doua sectiuni: "ro" si "en" — completeaza ambele.


PORNIRE PREVIEW
───────────────
      python preview_server.py

Deschide browserul la:  http://localhost:8765

In browser poti:
  • Alege template-ul:  classic / minimal / modern
  • Alege limba:        RO / EN
  • Previzualizeaza si tiparesti / salvezi PDF
  • Trimiti CV-ul prin email (necesita configurare SMTP)

ACCES DE PE TELEFON (acelasi WiFi)
────────────────────────────────────
Dupa ce pornesti serverul pe PC, deschide pe telefon:
      http://<IP-ul PC-ului tau>:8765

Exemplu:  http://192.168.1.10:8765

Poti previzualiza si descarca PDF-ul direct de pe telefon.
Nota: aplicatia NU se instaleaza pe telefon, ruleaza pe PC.


GENERARE PDF DIN TERMINAL
──────────────────────────
      python generate.py --template modern --lang ro
      python generate.py --template classic --lang en --output cv_meu.pdf

Optiuni:
  --template    classic / minimal / modern
  --lang        ro / en  (default: ro)
  --output      numele fisierului PDF generat


TRIMITERE EMAIL (optional)
───────────────────────────
1. Copiaza: copy email_config.example.json email_config.json
2. Completeaza cu datele tale SMTP (Gmail, Outlook etc.)
   * Gmail: Google Account → Security → App Passwords


STRUCTURA FISIERE
──────────────────
  cv.json                 ← datele tale (RO + EN)
  cv_example.json         ← exemplu de referinta
  generate.py             ← generare PDF din terminal
  preview_server.py       ← server preview in browser
  templates/
    classic.html          ← template clasic (serif)
    minimal.html          ← template minimalist
    modern.html           ← template modern (doua coloane)


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                        ENGLISH
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

INSTALLATION
────────────
1. Install Python from https://python.org
   (check "Add Python to PATH" during setup)

2. Open a terminal in this folder and run:
      pip install jinja2

3. Copy the example data:
      copy cv_example.json cv.json

4. Open cv.json in any text editor (Notepad, VS Code)
   and fill in your details.
   The file has two sections: "ro" and "en" — fill in both.


STARTING THE PREVIEW
─────────────────────
      python preview_server.py

Open your browser at:  http://localhost:8765

In the browser you can:
  • Choose a template:  classic / minimal / modern
  • Choose a language:  RO / EN
  • Preview and print / save as PDF
  • Send your CV by email (requires SMTP configuration)

ACCESS FROM A MOBILE PHONE (same WiFi)
────────────────────────────────────────
After starting the server on your PC, open on your phone:
      http://<your PC's IP address>:8765

Example:  http://192.168.1.10:8765

You can preview and download the PDF directly from your phone.
Note: the app does NOT install on your phone — it runs on the PC.


GENERATE PDF FROM TERMINAL
────────────────────────────
      python generate.py --template modern --lang en
      python generate.py --template classic --lang ro --output my_cv.pdf

Options:
  --template    classic / minimal / modern
  --lang        ro / en  (default: ro)
  --output      output PDF filename


SEND BY EMAIL (optional)
─────────────────────────
1. Copy: copy email_config.example.json email_config.json
2. Fill in your SMTP credentials (Gmail, Outlook, etc.)
   * Gmail: Google Account → Security → App Passwords


FILE STRUCTURE
───────────────
  cv.json                 ← your CV data (RO + EN)
  cv_example.json         ← reference example
  generate.py             ← PDF generator (terminal)
  preview_server.py       ← browser preview server
  templates/
    classic.html          ← classic serif template
    minimal.html          ← minimalist template
    modern.html           ← modern two-column template


──────────────────────────────────────────────────────
Requires: Python 3.10+  |  pip install jinja2
PDF generated with: Microsoft Edge (built into Windows)
──────────────────────────────────────────────────────
