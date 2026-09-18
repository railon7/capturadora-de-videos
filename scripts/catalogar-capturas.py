#!/usr/bin/env python3
"""Genera el catálogo de contenido de las capturas de un vídeo.

Cada imagen que sale del vídeo (fotogramas, hojas de contacto, capturas
puntuales) tiene que quedar descrita en un .md — no basta con el nombre por
marca de tiempo para saber qué hay dentro sin abrir la imagen. Este script
deja el esqueleto listo con el texto OCR de cada imagen; la columna "Qué se
ve" se completa a mano o pidiéndole a un LLM que mire las imágenes y la
rellene — el OCR lee texto, no interpreta la pantalla.

Requiere para el texto OCR (opcional, sin él el catálogo sale igual con esa
columna vacía): pip install pytesseract pillow
y el binario de Tesseract-OCR: winget install --id UB-Mannheim.TesseractOCR

Uso:
    python catalogar-capturas.py "Capturas/Rejilla" --salida "Analisis/Catalogo de capturas.md"
    python catalogar-capturas.py "Capturas/Seleccionadas"
"""
import argparse
import re
import shutil
import sys
from pathlib import Path

RE_HORA = re.compile(r"[te]_(\d{2})(\d{2})(\d{2})")

# Rutas donde el instalador oficial / winget dejan tesseract.exe en Windows
# cuando su carpeta no está en el PATH — mismo enfoque que ya usa
# extraer-capturas.ps1 para localizar ffmpeg sin depender del PATH.
RUTAS_TESSERACT_WINDOWS = [
    r"C:\Program Files\Tesseract-OCR\tesseract.exe",
    r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
]


def localizar_tesseract(cmd_manual: str = None) -> str:
    """Ruta al ejecutable de tesseract, o None si no se encuentra."""
    if cmd_manual:
        return cmd_manual if Path(cmd_manual).exists() else None
    en_path = shutil.which("tesseract")
    if en_path:
        return en_path
    for candidato in RUTAS_TESSERACT_WINDOWS:
        if Path(candidato).exists():
            return candidato
    return None


def hora_desde_nombre(nombre: str) -> str:
    m = RE_HORA.search(nombre)
    if not m:
        return ""
    h, mnt, s = m.groups()
    return f"{h}:{mnt}:{s}"


def leer_ocr(imagen: Path, ocr_disponible: bool) -> str:
    if not ocr_disponible:
        return ""
    try:
        import pytesseract
        from PIL import Image
        texto = pytesseract.image_to_string(Image.open(imagen), lang="spa+eng")
    except Exception:
        return ""
    texto = " ".join(texto.split())  # colapsa saltos de línea y espacios repetidos
    return texto[:200]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("carpeta", help="Carpeta con las imágenes a catalogar (p. ej. Capturas/Rejilla)")
    parser.add_argument("--salida", default=None, help="Fichero .md de salida (por defecto: Analisis/Catalogo de capturas.md junto a la carpeta de trabajo)")
    parser.add_argument("--sin-ocr", action="store_true", help="No intentes leer texto de las imágenes, deja la columna vacía para rellenar a mano")
    parser.add_argument("--tesseract-cmd", default=None, help="Ruta al ejecutable de tesseract, si no está en el PATH ni en su ubicación habitual")
    args = parser.parse_args()

    carpeta = Path(args.carpeta)
    if not carpeta.is_dir():
        print(f"No encuentro la carpeta: {carpeta}", file=sys.stderr)
        return 1

    ocr_disponible = not args.__dict__["sin_ocr"]
    if ocr_disponible:
        try:
            import pytesseract
            from PIL import Image  # noqa: F401
        except ImportError:
            print("Aviso: falta pytesseract/pillow, el catálogo sale sin texto OCR.", file=sys.stderr)
            print("Instala con: pip install pytesseract pillow", file=sys.stderr)
            ocr_disponible = False

    if ocr_disponible:
        ruta_tesseract = localizar_tesseract(args.tesseract_cmd)
        if not ruta_tesseract:
            print("Aviso: pytesseract está instalado pero no encuentro el binario de tesseract.", file=sys.stderr)
            print("Instálalo con: winget install --id UB-Mannheim.TesseractOCR", file=sys.stderr)
            print("o indica la ruta con --tesseract-cmd \"C:\\ruta\\a\\tesseract.exe\"", file=sys.stderr)
            ocr_disponible = False
        else:
            pytesseract.pytesseract.tesseract_cmd = ruta_tesseract

    imagenes = sorted(
        [p for p in carpeta.iterdir() if p.suffix.lower() in (".jpg", ".jpeg", ".png")],
        key=lambda p: p.name,
    )
    if not imagenes:
        print(f"No hay imágenes en {carpeta}", file=sys.stderr)
        return 1

    if args.salida:
        salida = Path(args.salida)
    else:
        # busca una carpeta "Analisis" hermana de la carpeta dada; si no, la crea junto a ella
        candidatos = [p for p in carpeta.parents if (p / "Analisis").is_dir()]
        base = candidatos[0] / "Analisis" if candidatos else carpeta.parent / "Analisis"
        salida = base / "Catalogo de capturas.md"
    salida.parent.mkdir(parents=True, exist_ok=True)

    print(f"Catalogando {len(imagenes)} imágenes de {carpeta}{' (con OCR)' if ocr_disponible else ' (sin OCR)'}...")

    filas = []
    for i, imagen in enumerate(imagenes, 1):
        hora = hora_desde_nombre(imagen.name)
        texto = leer_ocr(imagen, ocr_disponible)
        texto_md = texto.replace("|", "\\|") if texto else ""
        filas.append(f"| {imagen.name} | {hora} | {texto_md} | |")
        if i % 25 == 0:
            print(f"  ... {i}/{len(imagenes)}")

    with salida.open("w", encoding="utf-8") as f:
        f.write(f"# Catálogo de capturas — {carpeta.name}\n\n")
        f.write(
            "Qué hay en cada imagen capturada, para poder entender el contenido "
            "sin abrirlas una por una. La columna \"Texto detectado\" es OCR "
            "automático (lee texto, no interpreta la pantalla); la columna "
            "\"Qué se ve\" se completa a mano o revisando las imágenes con un LLM.\n\n"
        )
        f.write("| Fichero | Hora | Texto detectado (OCR) | Qué se ve |\n")
        f.write("|---|---|---|---|\n")
        f.write("\n".join(filas))
        f.write("\n")

    print(f"\nListo: {salida}")
    if not ocr_disponible:
        print("Sin OCR: rellena \"Texto detectado\" y \"Qué se ve\" a mano, o revisando las imágenes con un LLM.")
    else:
        print("Revisa y completa la columna \"Qué se ve\" — el OCR ayuda pero no sustituye mirar la imagen.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
