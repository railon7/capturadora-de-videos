#!/usr/bin/env python3
"""Empaqueta un documento Markdown + sus imágenes en un único entregable.

El documento vive como Markdown + imágenes sueltas mientras se escribe (así se
edita mejor), pero para mandarlo a cliente hace falta un fichero único que
no dependa de rutas relativas. Este script convierte el Markdown a HTML e
incrusta cada imagen referenciada como base64 dentro del propio HTML: un
solo fichero, que se abre en cualquier navegador.

Si el documento es de la biblioteca (tiene frontmatter YAML):
  - el frontmatter no se vuelca al HTML; de él salen el título, el idioma de
    la página, la línea ID · versión · estado y el pie de cada página;
  - un documento en borrador, en revisión u obsoleto sale con una marca de agua
    (BORRADOR / DRAFT...). --sin-marca-agua la quita, solo para uso interno;
  - los comentarios <!-- GUÍA: ... --> de la plantilla no pasan al HTML.
  - si junto al documento hay una carpeta entregables/, la salida va ahí.

Con --pdf genera además un .pdf con Chrome o Edge en modo headless (con la marca
Tazuke); si no los encuentra, prueba con pandoc. Un PDF que no sale no es un
error: el HTML es el entregable fiable.

Requiere: pip install markdown

Uso:
    python exportar-manual.py "ClienteX/Biblioteca/SOP-HOLD-003_emitir-factura.es.md" --pdf
    python exportar-manual.py "08-Formacion/P-01 · Entrada de factura.md" --salida "P-01.html"
"""
import argparse
import base64
import glob
import html
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from urllib.parse import unquote

sys.path.insert(0, str(Path(__file__).resolve().parent))
import biblioteca as bib  # noqa: E402

# ![alt](ruta) con la ruta tal cual (puede llevar espacios, como las deja
# Obsidian), entre <...> o con %20, y un título opcional: ![alt](ruta "título")
RE_IMAGEN_MD = re.compile(r'(!\[[^\]]*\]\()\s*(<[^>\n]+>|[^)\n]+?)(\s+"[^"\n]*")?\s*(\))')
# Incrustación de Obsidian: ![[imagen.png]] o ![[imagen.png|300]]
RE_IMAGEN_OBSIDIAN = re.compile(r"!\[\[([^\]|\n]+)(?:\|[^\]\n]*)?\]\]")
RE_COMENTARIO_HTML = re.compile(r"<!--.*?-->\n?", re.DOTALL)
RE_BLOQUE_CODIGO = re.compile(r"(```.*?```)", re.DOTALL)

TIPOS_MIME = {
    ".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg",
    ".gif": "image/gif", ".svg": "image/svg+xml", ".webp": "image/webp",
}

# Textos de la cabecera y la marca de agua, por idioma de la página
ETIQUETAS = {
    "es": {"version": "Versión", "revisado": "Revisado",
           "estado": {"borrador": "Borrador", "revision": "En revisión", "aprobado": "Aprobado", "obsoleto": "Obsoleto"},
           "marca": {"borrador": "BORRADOR", "revision": "EN REVISIÓN", "obsoleto": "OBSOLETO"}},
    "en": {"version": "Version", "revisado": "Reviewed",
           "estado": {"borrador": "Draft", "revision": "In review", "aprobado": "Approved", "obsoleto": "Obsolete"},
           "marca": {"borrador": "DRAFT", "revision": "IN REVIEW", "obsoleto": "OBSOLETE"}},
}

CSS = """
@page { size: A4; margin: 20mm 18mm 20mm 18mm; @bottom-center { content: "@@PIE@@"; font-size: 8pt; color: #9E9E9E; } }
:root { --amber:#F6B420; --lemon-soft:#FFF4C2; --amber-dark:#D89A0F; --carbon:#1A1A1A; --gris:#4A4A4A;
        --gris-claro:#9E9E9E; --offwhite:#FAFAFA; --divisor:#E5E5E5; }
* { box-sizing: border-box; }
body { font-family: "Open Sans", "Segoe UI", Calibri, Arial, sans-serif; max-width: 820px; margin: 2rem auto;
       padding: 0 1.5rem; line-height: 1.5; color: var(--gris); font-size: 10.5pt;
       -webkit-print-color-adjust: exact; print-color-adjust: exact; }
h1, h2, h3, h4 { font-family: "Montserrat", "Segoe UI", Calibri, Arial, sans-serif; color: var(--carbon); page-break-after: avoid; }
h1 { font-size: 20pt; font-weight: 800; margin: 0 0 .3rem 0; }
h2 { font-size: 14pt; font-weight: 700; margin: 1.8rem 0 .8rem 0; padding-bottom: .3rem; border-bottom: 2px solid var(--amber); }
h3 { font-size: 11.5pt; font-weight: 700; margin: 1.4rem 0 .5rem 0; }
.doc-meta { font-size: 9pt; color: var(--gris-claro); margin: 0 0 1.4rem 0; letter-spacing: .02em; }
img { max-width: 100%; display: block; margin: 1rem 0; page-break-inside: avoid; border: 1px solid var(--divisor); }
table { border-collapse: collapse; width: 100%; margin: 1rem 0; font-size: 9.5pt; }
thead th { background: var(--carbon); color: #fff; text-align: left; padding: .45rem .7rem; }
th, td { border: 1px solid var(--divisor); padding: .4rem .7rem; text-align: left; vertical-align: top; }
tr { page-break-inside: avoid; }
blockquote { border-left: 3px solid var(--amber); background: var(--lemon-soft); margin: 1rem 0; padding: .4rem 1rem; color: var(--carbon);
             page-break-inside: avoid; }
code { background: #f2f2f2; padding: .1rem .3rem; border-radius: 3px; }
a { color: var(--amber-dark); }
.marca-agua { position: fixed; top: 42%; left: 0; right: 0; text-align: center; font-family: "Montserrat", Arial, sans-serif;
              font-size: 90pt; font-weight: 800; color: rgba(246, 180, 32, .18); transform: rotate(-30deg);
              pointer-events: none; z-index: 1000; }
"""


def a_data_uri(ruta_img: Path) -> str:
    mime = TIPOS_MIME.get(ruta_img.suffix.lower(), "application/octet-stream")
    return f"data:{mime};base64,{base64.b64encode(ruta_img.read_bytes()).decode('ascii')}"


def incrustar_imagenes(md_texto: str, base_dir: Path) -> str:
    def reemplazar(m):
        prefijo, ruta_rel, titulo, cierre = m.groups()
        if ruta_rel.startswith("<") and ruta_rel.endswith(">"):
            ruta_rel = ruta_rel[1:-1]
        if ruta_rel.startswith(("http://", "https://", "data:")):
            return m.group(0)
        ruta_img = (base_dir / unquote(ruta_rel)).resolve()
        if not ruta_img.exists():
            print(f"Aviso: no encuentro la imagen {ruta_img}, se deja el enlace tal cual", file=sys.stderr)
            return m.group(0)
        return f"{prefijo}{a_data_uri(ruta_img)}{titulo or ''}{cierre}"

    def reemplazar_obsidian(m):
        nombre = m.group(1).strip()
        ruta_img = (base_dir / nombre).resolve()
        if not ruta_img.exists():
            # Obsidian también resuelve por nombre de fichero en cualquier subcarpeta
            ruta_img = next(base_dir.rglob(glob.escape(Path(nombre).name)), None)
        if ruta_img is None or not ruta_img.exists():
            print(f"Aviso: no encuentro la imagen {nombre}, se deja la incrustación tal cual", file=sys.stderr)
            return m.group(0)
        return f"![{Path(nombre).stem}]({a_data_uri(ruta_img)})"

    md_texto = RE_IMAGEN_MD.sub(reemplazar, md_texto)
    return RE_IMAGEN_OBSIDIAN.sub(reemplazar_obsidian, md_texto)


# --------------------------------------------------------- documento de biblioteca
def separar_frontmatter(md_texto: str):
    """(meta, cuerpo). Un frontmatter roto avisa y se trata como si no hubiera."""
    try:
        return bib.parsear_frontmatter(md_texto)
    except bib.ErrorFrontmatter as e:
        print(f"Aviso: frontmatter ilegible ({e}); se exporta el fichero tal cual.", file=sys.stderr)
        return {}, md_texto


def quitar_comentarios(md_texto: str) -> str:
    """Quita los comentarios HTML (la guía de las plantillas), sin tocar los bloques de código."""
    partes = RE_BLOQUE_CODIGO.split(md_texto)
    return "".join(p if i % 2 else RE_COMENTARIO_HTML.sub("", p) for i, p in enumerate(partes))


def idioma_de(meta: dict) -> str:
    return meta.get("idioma") if meta.get("idioma") in bib.IDIOMAS else "es"


def linea_meta(meta: dict) -> str:
    """'SOP-HOLD-003 · Versión 1.0 · Aprobado · Revisado 2026-10-06', o vacío si no hay metadatos."""
    if not meta.get("id") and not meta.get("estado"):
        return ""
    et = ETIQUETAS[idioma_de(meta)]
    partes = [meta.get("id", "")]
    if meta.get("version"):
        partes.append(f"{et['version']} {meta['version']}")
    if meta.get("estado"):
        partes.append(et["estado"].get(meta["estado"], meta["estado"]))
    if meta.get("revisado"):
        partes.append(f"{et['revisado']} {meta['revisado']}")
    return " · ".join(p for p in partes if p)


def texto_marca_agua(meta: dict) -> str:
    return ETIQUETAS[idioma_de(meta)]["marca"].get(meta.get("estado", ""), "")


def titulo_documento(meta: dict, cuerpo_md: str, ruta: Path) -> str:
    if meta.get("titulo"):
        return meta["titulo"]
    primera = cuerpo_md.lstrip().splitlines()[0] if cuerpo_md.strip() else ""
    return primera[2:].strip() if primera.startswith("# ") else ruta.stem


def convertir_a_html(md_texto: str, base_dir: Path, ruta: Path = Path("documento.md"), marca_agua: bool = True) -> str:
    """Markdown (con o sin frontmatter) -> HTML autocontenido. Necesita el paquete markdown."""
    import markdown

    meta, cuerpo = separar_frontmatter(md_texto)
    cuerpo = incrustar_imagenes(quitar_comentarios(cuerpo), base_dir)
    cuerpo_html = markdown.markdown(cuerpo, extensions=["tables", "fenced_code"])
    titulo = titulo_documento(meta, cuerpo, ruta)

    cabecera = linea_meta(meta)
    if cabecera:
        bloque = f'<p class="doc-meta">{html.escape(cabecera)}</p>'
        if "</h1>" in cuerpo_html:
            cuerpo_html = cuerpo_html.replace("</h1>", "</h1>\n" + bloque, 1)
        else:
            cuerpo_html = f"<h1>{html.escape(titulo)}</h1>\n{bloque}\n{cuerpo_html}"

    marca = texto_marca_agua(meta) if marca_agua else ""
    if marca:
        cuerpo_html = f'<div class="marca-agua">{html.escape(marca)}</div>\n{cuerpo_html}'

    pie = cabecera.replace('"', "'") or html.escape(titulo).replace('"', "'")
    css = CSS.replace("@@PIE@@", pie)
    return (f'<!DOCTYPE html>\n<html lang="{idioma_de(meta)}">\n<head>\n<meta charset="utf-8">\n'
            f"<title>{html.escape(titulo)}</title>\n<style>{css}</style>\n</head>\n<body>\n{cuerpo_html}\n</body>\n</html>\n")


def salida_por_defecto(ruta_md: Path, meta: dict) -> Path:
    """Junto al .md, o en entregables/ si es un documento de biblioteca y la carpeta existe."""
    entregables = ruta_md.parent / "entregables"
    if meta.get("id") and entregables.is_dir():
        return entregables / (ruta_md.stem + ".html")
    return ruta_md.with_suffix(".html")


# ----------------------------------------------------------------------- PDF
NAVEGADORES = [
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
]


def buscar_navegador(candidatos=None):
    """Ruta de Chrome o Edge, o None. Mira las rutas habituales de Windows y el PATH."""
    for ruta in (NAVEGADORES if candidatos is None else candidatos):
        if os.path.exists(ruta):
            return ruta
    for nombre in ("chrome", "msedge", "google-chrome", "chromium"):
        encontrado = shutil.which(nombre)
        if encontrado:
            return encontrado
    return None


def comando_pdf(navegador: str, html_ruta: Path, pdf_ruta: Path, perfil: str) -> list:
    return [navegador, "--headless=new", "--disable-gpu", "--no-pdf-header-footer", "--print-to-pdf-no-header",
            f"--user-data-dir={perfil}", "--run-all-compositor-stages-before-draw", "--virtual-time-budget=8000",
            f"--print-to-pdf={pdf_ruta}", Path(html_ruta).resolve().as_uri()]


def generar_pdf(html_ruta: Path, pdf_ruta: Path) -> bool:
    """PDF con Chrome/Edge; si no hay, con pandoc. Devuelve True si el PDF existe al final."""
    navegador = buscar_navegador()
    if navegador:
        with tempfile.TemporaryDirectory() as perfil:
            try:
                subprocess.run(comando_pdf(navegador, html_ruta, pdf_ruta, perfil), capture_output=True, timeout=180)
            except (OSError, subprocess.SubprocessError) as e:
                print(f"Aviso: {Path(navegador).name} no ha podido generar el PDF ({e}).", file=sys.stderr)
        if pdf_ruta.exists() and pdf_ruta.stat().st_size > 2000:
            return True
        print("Aviso: el navegador no ha generado el PDF; pruebo con pandoc.", file=sys.stderr)
    else:
        print("Aviso: no encuentro Chrome ni Edge; pruebo con pandoc.", file=sys.stderr)

    pandoc = shutil.which("pandoc")
    if not pandoc:
        print("Aviso: tampoco hay pandoc. El HTML sigue siendo válido: ábrelo y Ctrl+P -> Guardar como PDF.", file=sys.stderr)
        return False
    try:
        subprocess.run([pandoc, str(html_ruta), "-o", str(pdf_ruta)], check=True, capture_output=True, text=True)
        return True
    except subprocess.CalledProcessError as e:
        print("Aviso: pandoc no ha podido generar el PDF (¿falta un motor de PDF como wkhtmltopdf?).", file=sys.stderr)
        print(e.stderr, file=sys.stderr)
        return False


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("manual", help="Fichero Markdown del documento")
    parser.add_argument("--salida", default=None,
                        help="Fichero .html de salida (por defecto: junto al .md, o en entregables/ si es de la biblioteca)")
    parser.add_argument("--pdf", action="store_true", help="Genera además un .pdf con Chrome o Edge (o pandoc si no hay)")
    parser.add_argument("--sin-marca-agua", action="store_true",
                        help="No pone BORRADOR / EN REVISIÓN / OBSOLETO en un documento que no está aprobado (solo uso interno)")
    args = parser.parse_args()

    ruta_manual = Path(args.manual)
    if not ruta_manual.exists():
        print(f"No encuentro el fichero: {ruta_manual}", file=sys.stderr)
        return 1

    try:
        import markdown  # noqa: F401
    except ImportError:
        print("Falta el paquete markdown. Instala con: pip install markdown", file=sys.stderr)
        return 1

    md_texto = ruta_manual.read_text(encoding="utf-8")
    meta, _ = separar_frontmatter(md_texto)
    estado = meta.get("estado", "")
    if estado and estado != "aprobado":
        if args.sin_marca_agua:
            print(f"Aviso: el documento está en estado '{estado}' y se exporta SIN marca de agua.", file=sys.stderr)
        else:
            print(f"Aviso: el documento está en estado '{estado}': sale con marca de agua. Apruébalo antes de entregarlo.", file=sys.stderr)

    html_completo = convertir_a_html(md_texto, ruta_manual.parent, ruta_manual, marca_agua=not args.sin_marca_agua)

    salida = Path(args.salida) if args.salida else salida_por_defecto(ruta_manual, meta)
    salida.parent.mkdir(parents=True, exist_ok=True)
    salida.write_text(html_completo, encoding="utf-8")
    print(f"HTML autocontenido: {salida}")

    if args.pdf:
        ruta_pdf = salida.with_suffix(".pdf")
        if generar_pdf(salida, ruta_pdf):
            print(f"PDF generado: {ruta_pdf}")
    else:
        print("Ábrelo en el navegador; Ctrl+P -> Guardar como PDF, o vuelve a lanzarlo con --pdf.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
