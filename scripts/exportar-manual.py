#!/usr/bin/env python3
"""Empaqueta un protocolo Markdown + sus imágenes en un único entregable.

El manual vive como Markdown + imágenes sueltas mientras se escribe (así se
edita mejor), pero para mandarlo a cliente hace falta un fichero único que
no dependa de rutas relativas. Este script convierte el Markdown a HTML e
incrusta cada imagen referenciada como base64 dentro del propio HTML: un
solo fichero, que se abre en cualquier navegador y se imprime a PDF desde
ahí (Ctrl+P → Guardar como PDF) sin depender de ninguna herramienta más.

Requiere: pip install markdown

Uso:
    python exportar-manual.py "08-Formacion/P-01 · Entrada de factura.md" --salida "P-01.html"

Con --pdf intenta además generar un .pdf llamando a pandoc, si está
instalado (necesita también un motor de PDF instalado aparte — wkhtmltopdf
o una distribución LaTeX). Si no lo encuentra o falla, no es un error: el
HTML es el entregable fiable, el PDF es un extra.
"""
import argparse
import base64
import glob
import re
import shutil
import subprocess
import sys
from pathlib import Path
from urllib.parse import unquote

# ![alt](ruta) con la ruta tal cual (puede llevar espacios, como las deja
# Obsidian), entre <...> o con %20, y un título opcional: ![alt](ruta "título")
RE_IMAGEN_MD = re.compile(r'(!\[[^\]]*\]\()\s*(<[^>\n]+>|[^)\n]+?)(\s+"[^"\n]*")?\s*(\))')
# Incrustación de Obsidian: ![[imagen.png]] o ![[imagen.png|300]]
RE_IMAGEN_OBSIDIAN = re.compile(r"!\[\[([^\]|\n]+)(?:\|[^\]\n]*)?\]\]")

TIPOS_MIME = {
    ".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg",
    ".gif": "image/gif", ".svg": "image/svg+xml", ".webp": "image/webp",
}

PLANTILLA_HTML = """<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="utf-8">
<title>{titulo}</title>
<style>
  body {{ font-family: -apple-system, Segoe UI, Arial, sans-serif; max-width: 820px;
         margin: 2rem auto; padding: 0 1.5rem; line-height: 1.5; color: #1a1a1a; }}
  img {{ max-width: 100%; display: block; margin: 1rem 0; page-break-inside: avoid; }}
  table {{ border-collapse: collapse; width: 100%; margin: 1rem 0; }}
  th, td {{ border: 1px solid #ccc; padding: 0.4rem 0.6rem; text-align: left; }}
  blockquote {{ border-left: 3px solid #ccc; margin: 1rem 0; padding: 0.2rem 1rem; color: #444; }}
  h1, h2, h3 {{ page-break-after: avoid; }}
  code {{ background: #f2f2f2; padding: 0.1rem 0.3rem; border-radius: 3px; }}
</style>
</head>
<body>
{cuerpo}
</body>
</html>
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


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("manual", help="Fichero Markdown del protocolo")
    parser.add_argument("--salida", default=None, help="Fichero .html de salida (por defecto: mismo nombre, extensión .html)")
    parser.add_argument("--pdf", action="store_true", help="Intenta además generar un .pdf con pandoc, si está disponible")
    args = parser.parse_args()

    ruta_manual = Path(args.manual)
    if not ruta_manual.exists():
        print(f"No encuentro el fichero: {ruta_manual}", file=sys.stderr)
        return 1

    try:
        import markdown
    except ImportError:
        print("Falta el paquete markdown. Instala con: pip install markdown", file=sys.stderr)
        return 1

    md_texto = ruta_manual.read_text(encoding="utf-8")
    md_texto = incrustar_imagenes(md_texto, ruta_manual.parent)
    cuerpo_html = markdown.markdown(md_texto, extensions=["tables", "fenced_code"])

    titulo = ruta_manual.stem
    primera_linea = md_texto.lstrip().splitlines()[0] if md_texto.strip() else ""
    if primera_linea.startswith("# "):
        titulo = primera_linea[2:].strip()

    html_completo = PLANTILLA_HTML.format(titulo=titulo, cuerpo=cuerpo_html)

    salida = Path(args.salida) if args.salida else ruta_manual.with_suffix(".html")
    salida.parent.mkdir(parents=True, exist_ok=True)
    salida.write_text(html_completo, encoding="utf-8")
    print(f"HTML autocontenido: {salida}")
    print("Ábrelo en el navegador; Ctrl+P -> Guardar como PDF si hace falta un .pdf.")

    if args.pdf:
        pandoc = shutil.which("pandoc")
        if not pandoc:
            print("Aviso: --pdf pedido pero no encuentro pandoc en el PATH. El HTML sigue siendo válido.", file=sys.stderr)
            return 0
        ruta_pdf = salida.with_suffix(".pdf")
        try:
            subprocess.run([pandoc, str(salida), "-o", str(ruta_pdf)], check=True, capture_output=True, text=True)
            print(f"PDF generado: {ruta_pdf}")
        except subprocess.CalledProcessError as e:
            print("Aviso: pandoc no ha podido generar el PDF (¿falta un motor de PDF como wkhtmltopdf?).", file=sys.stderr)
            print(e.stderr, file=sys.stderr)
            print("El HTML sigue siendo un entregable válido por sí solo.", file=sys.stderr)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
