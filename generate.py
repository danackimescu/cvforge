import argparse
import json
import sys
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

TEMPLATES_DIR = Path(__file__).parent / "templates"


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


def load_data(path: str, lang: str = "ro") -> dict:
    with open(path, encoding="utf-8") as f:
        raw = json.load(f)
    if "ro" in raw or "en" in raw:
        return raw.get(lang) or raw.get(LANGS[0]) or {}
    return raw


def list_templates() -> list:
    return sorted(f.stem for f in TEMPLATES_DIR.glob("*.html"))


def render_html(data: dict, template_name: str, lang: str = "ro") -> str:
    env = Environment(loader=FileSystemLoader(str(TEMPLATES_DIR)))
    template = env.get_template(f"{template_name}.html")
    return template.render(**data, labels=LABELS.get(lang, LABELS["ro"]))


EDGE_PATHS = [
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
]


def _find_browser() -> str | None:
    for p in EDGE_PATHS:
        if Path(p).exists():
            return p
    return None


def generate_pdf(html: str, output_path: str):
    # Try WeasyPrint first
    try:
        from weasyprint import HTML
        HTML(string=html, base_url=str(TEMPLATES_DIR)).write_pdf(output_path)
        print(f"CV generat: {output_path}")
        return
    except Exception:
        pass

    # Fallback: Edge / Chrome headless
    browser = _find_browser()
    if not browser:
        _save_html_fallback(html, output_path)
        return

    import subprocess
    import tempfile

    with tempfile.NamedTemporaryFile(suffix=".html", delete=False, mode="w", encoding="utf-8") as f:
        f.write(html)
        tmp_html = f.name

    abs_output = str(Path(output_path).resolve())
    result = subprocess.run(
        [
            browser,
            "--headless=new",
            "--disable-gpu",
            "--no-sandbox",
            "--run-all-compositor-stages-before-draw",
            f"--print-to-pdf={abs_output}",
            "--no-pdf-header-footer",
            "--print-to-pdf-no-header",
            f"file:///{tmp_html}",
        ],
        capture_output=True,
        timeout=30,
    )
    Path(tmp_html).unlink(missing_ok=True)

    if result.returncode == 0 and Path(abs_output).exists():
        print(f"CV generat: {output_path}")
    else:
        _save_html_fallback(html, output_path)


def _save_html_fallback(html: str, pdf_path: str):
    html_path = Path(pdf_path).with_suffix(".html")
    html_path.write_text(html, encoding="utf-8")
    print(f"PDF generation failed. HTML salvat: {html_path}")
    print("Deschide fisierul in browser si foloseste Ctrl+P → 'Save as PDF'.")


def pick_template_interactive(templates: list) -> str:
    print("\nTemplate-uri disponibile:")
    for i, t in enumerate(templates, 1):
        print(f"  {i}. {t}")
    choice = input("\nAlege template (nume sau numar): ").strip()
    if choice.isdigit():
        idx = int(choice) - 1
        if 0 <= idx < len(templates):
            return templates[idx]
        print("Numar invalid.")
        sys.exit(1)
    if choice in templates:
        return choice
    print(f"Template '{choice}' nu exista.")
    sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="CVForge — generator CV din JSON → PDF",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemple:
  python generate.py                              # mod interactiv
  python generate.py --template modern
  python generate.py --data cv.json --template classic --output cv_dan.pdf
  python generate.py --list-templates
""",
    )
    parser.add_argument("--data", default="cv.json",
                        help="Fisier JSON cu datele CV-ului (default: cv.json)")
    parser.add_argument("--template", "-t",
                        help="Numele template-ului (modern / classic / minimal)")
    parser.add_argument("--output", "-o",
                        help="Fisier PDF de output (default: cv_<template>.pdf)")
    parser.add_argument("--lang", default="ro", choices=LANGS,
                        help="Limba CV-ului: ro (default) sau en")
    parser.add_argument("--list-templates", "-l", action="store_true",
                        help="Afiseaza template-urile disponibile")
    args = parser.parse_args()

    templates = list_templates()

    if args.list_templates:
        print("Template-uri disponibile:")
        for t in templates:
            print(f"  - {t}")
        return

    if not templates:
        print("Niciun template gasit in folderul 'templates/'.")
        sys.exit(1)

    template_name = args.template or pick_template_interactive(templates)

    if template_name not in templates:
        print(f"Template '{template_name}' nu exista. Disponibile: {', '.join(templates)}")
        sys.exit(1)

    data_path = args.data
    if not Path(data_path).exists():
        print(f"Fisierul '{data_path}' nu exista.")
        print("Copiaza cv_example.json ca punct de pornire:  copy cv_example.json cv.json")
        sys.exit(1)

    output_path = args.output or f"cv_{template_name}.pdf"

    print(f"Template : {template_name}")
    print(f"Limba    : {args.lang}")
    print(f"Date     : {data_path}")
    print(f"Output   : {output_path}")

    data = load_data(data_path, args.lang)
    html = render_html(data, template_name, args.lang)
    generate_pdf(html, output_path)


if __name__ == "__main__":
    main()
