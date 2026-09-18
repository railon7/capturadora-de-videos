#!/usr/bin/env python3
"""Aviso heurístico de datos identificables antes de entregar capturas o guiones.

Es un aviso, no una garantía: revisa siempre a ojo antes de mandar nada a
cliente. Dos modos, combinables:

  --textos CARPETA   Busca email / teléfono / DNI-NIE-CIF / tarjeta en
                      ficheros de texto (.md, .txt, .tsv) — la transcripción,
                      el mapa del vídeo, etc. Rápido, sin dependencias.

  --ocr CARPETA       Igual, pero pasando antes cada imagen (.jpg/.png) por
                      OCR para leer el texto que aparece EN la captura de
                      pantalla. Requiere: pip install pytesseract pillow
                      y tener instalado el binario de Tesseract-OCR
                      (winget install --id UB-Mannheim.TesseractOCR).
                      Cuenta con que tarda varios segundos por imagen: no lo
                      lances sobre cientos de capturas sin querer.

DNI, NIE, CIF, tarjeta, email y teléfono se detectan solos porque tienen un
patrón verificable (dígito de control o formato fijo). **Los nombres propios
y de empresa NO** — no hay forma fiable de reconocerlos solo con regex/OCR.
Para esos, pásale `--nombres fichero.txt` con un nombre por línea (los
nombres reales del vídeo o proyecto, que alguien tiene que conocer y
escribir — un LLM que haya leído la transcripción puede generar esa lista).

El informe enmascara los hallazgos (solo dos caracteres a cada lado) para
que el propio informe no se convierta en la fuga.

Para tapar los datos EN la imagen, no solo avisar de que están, usa
scripts/redactar-captura.py.

Uso:
    python auditar-privacidad.py --textos "Analisis"
    python auditar-privacidad.py --ocr "Capturas/Seleccionadas"
    python auditar-privacidad.py --textos "Analisis" --ocr "Capturas/Editadas" --nombres "nombres-a-tapar.txt"
"""
import argparse
import re
import shutil
import sys
from pathlib import Path

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


PATRONES_SIMPLES = {
    "email": re.compile(r"\b[\w.+-]+@[\w-]+\.[\w.-]+\b"),
    "telefono_es": re.compile(r"\b(?:\+34|0034)?[6789]\d{8}\b"),
}

RE_TARJETA = re.compile(r"\b(?:\d[ -]?){13,19}\b")
RE_DNI = re.compile(r"\b(\d{8})([A-Za-z])\b")
RE_NIE = re.compile(r"\b([XYZxyz])(\d{7})([A-Za-z])\b")
RE_CIF = re.compile(r"\b([ABCDEFGHJKLMNPQRSUVWabcdefghjklmnpqrsuvw])(\d{7})([0-9A-Ja-j])\b")

LETRAS_DNI = "TRWAGMYFPDXBNJZSQVHLCKE"
LETRAS_CIF_CONTROL = "JABCDEFGHI"


def luhn_valido(numero: str) -> bool:
    digitos = [int(c) for c in numero if c.isdigit()]
    if len(digitos) < 13:
        return False
    suma = 0
    for i, d in enumerate(reversed(digitos)):
        if i % 2 == 1:
            d *= 2
            if d > 9:
                d -= 9
        suma += d
    return suma % 10 == 0


def dni_valido(numero: str, letra: str) -> bool:
    return LETRAS_DNI[int(numero) % 23] == letra.upper()


def nie_valido(prefijo: str, numero: str, letra: str) -> bool:
    mapa = {"X": "0", "Y": "1", "Z": "2"}
    numero_completo = mapa[prefijo.upper()] + numero
    return dni_valido(numero_completo, letra)


def cif_valido(letra_inicial: str, digitos: str, control: str) -> bool:
    """CIF español: letra de tipo de entidad + 7 dígitos + dígito o letra de control."""
    letra_inicial, control = letra_inicial.upper(), control.upper()
    suma_par = sum(int(d) for d in digitos[1::2])
    suma_impar = 0
    for d in digitos[0::2]:
        doble = int(d) * 2
        suma_impar += doble // 10 + doble % 10
    digito_control = (10 - (suma_par + suma_impar) % 10) % 10
    if letra_inicial in "ABEH":
        return control == str(digito_control)
    if letra_inicial in "KPQS":
        return control == LETRAS_CIF_CONTROL[digito_control]
    if letra_inicial in "CDFGJLMNRUVW":
        return control == str(digito_control) or control == LETRAS_CIF_CONTROL[digito_control]
    return False


def enmascarar(texto: str) -> str:
    if len(texto) <= 4:
        return "*" * len(texto)
    return texto[:2] + "*" * (len(texto) - 4) + texto[-2:]


def buscar_en_texto(texto: str, origen: str) -> list[str]:
    hallazgos = []
    for tipo, patron in PATRONES_SIMPLES.items():
        for m in patron.finditer(texto):
            hallazgos.append(f"- **{tipo}** en `{origen}`: `{enmascarar(m.group())}`")

    for m in RE_TARJETA.finditer(texto):
        if luhn_valido(m.group()):
            hallazgos.append(f"- **tarjeta (Luhn ok)** en `{origen}`: `{enmascarar(m.group())}`")

    for m in RE_DNI.finditer(texto):
        numero, letra = m.groups()
        if dni_valido(numero, letra):
            hallazgos.append(f"- **DNI (checksum ok)** en `{origen}`: `{enmascarar(m.group())}`")

    for m in RE_NIE.finditer(texto):
        prefijo, numero, letra = m.groups()
        if nie_valido(prefijo, numero, letra):
            hallazgos.append(f"- **NIE (checksum ok)** en `{origen}`: `{enmascarar(m.group())}`")

    for m in RE_CIF.finditer(texto):
        letra_inicial, digitos, control = m.groups()
        if cif_valido(letra_inicial, digitos, control):
            hallazgos.append(f"- **CIF (checksum ok)** en `{origen}`: `{enmascarar(m.group())}`")

    return hallazgos


def buscar_nombres(texto: str, origen: str, nombres: list) -> list[str]:
    """Coincidencia literal (sin distinguir mayúsculas) contra una lista de
    nombres propios o de empresa. No hay forma fiable de detectar esto solo
    con regex — depende de que la lista la rellene quien conoce los nombres
    reales del vídeo o del proyecto."""
    hallazgos = []
    texto_bajo = texto.lower()
    for nombre in nombres:
        nombre = nombre.strip()
        if nombre and nombre.lower() in texto_bajo:
            hallazgos.append(f"- **nombre de la lista** en `{origen}`: `{enmascarar(nombre)}`")
    return hallazgos


def leer_lista_nombres(ruta: str) -> list:
    if not ruta:
        return []
    return [
        linea.strip()
        for linea in Path(ruta).read_text(encoding="utf-8").splitlines()
        if linea.strip() and not linea.strip().startswith("#")
    ]


def escanear_textos(carpeta: Path, nombres: list = None) -> list[str]:
    hallazgos = []
    for ext in ("*.md", "*.txt", "*.tsv"):
        for fichero in carpeta.rglob(ext):
            try:
                texto = fichero.read_text(encoding="utf-8", errors="ignore")
            except OSError:
                continue
            hallazgos.extend(buscar_en_texto(texto, str(fichero)))
            if nombres:
                hallazgos.extend(buscar_nombres(texto, str(fichero), nombres))
    return hallazgos


def escanear_ocr(carpeta: Path, tesseract_cmd: str = None, nombres: list = None) -> list[str]:
    try:
        import pytesseract
        from PIL import Image
    except ImportError:
        print("Falta pytesseract y/o pillow. Instala con: pip install pytesseract pillow", file=sys.stderr)
        print("Y el binario de Tesseract-OCR: winget install --id UB-Mannheim.TesseractOCR", file=sys.stderr)
        return []

    ruta_tesseract = localizar_tesseract(tesseract_cmd)
    if not ruta_tesseract:
        print("pytesseract está instalado pero no encuentro el binario de tesseract.", file=sys.stderr)
        print("Instálalo con: winget install --id UB-Mannheim.TesseractOCR", file=sys.stderr)
        print("o indica la ruta con --tesseract-cmd \"C:\\ruta\\a\\tesseract.exe\"", file=sys.stderr)
        return []
    pytesseract.pytesseract.tesseract_cmd = ruta_tesseract

    hallazgos = []
    imagenes = list(carpeta.rglob("*.jpg")) + list(carpeta.rglob("*.jpeg")) + list(carpeta.rglob("*.png"))
    print(f"OCR sobre {len(imagenes)} imagenes (varios segundos cada una)...")
    for i, imagen in enumerate(imagenes, 1):
        try:
            texto = pytesseract.image_to_string(Image.open(imagen), lang="spa+eng")
        except Exception as e:
            print(f"  aviso: no se pudo leer {imagen.name}: {e}", file=sys.stderr)
            continue
        hallazgos.extend(buscar_en_texto(texto, str(imagen)))
        if nombres:
            hallazgos.extend(buscar_nombres(texto, str(imagen), nombres))
        if i % 10 == 0:
            print(f"  ... {i}/{len(imagenes)}")
    return hallazgos


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--textos", help="Carpeta con .md/.txt/.tsv a escanear por patrón, sin OCR")
    parser.add_argument("--ocr", help="Carpeta con imágenes a pasar por OCR antes de escanear")
    parser.add_argument("--salida", default=None, help="Fichero de informe (por defecto: aviso-privacidad.md en la primera carpeta dada)")
    parser.add_argument("--tesseract-cmd", default=None, help="Ruta al ejecutable de tesseract, si no está en el PATH ni en su ubicación habitual")
    parser.add_argument("--nombres", default=None, help="Fichero de texto, un nombre propio o de empresa por línea, a buscar literalmente (esto NO se detecta solo con regex)")
    args = parser.parse_args()

    if not args.textos and not args.ocr:
        parser.error("indica --textos, --ocr, o los dos")

    nombres = leer_lista_nombres(args.nombres)
    hallazgos = []
    if args.textos:
        hallazgos.extend(escanear_textos(Path(args.textos), nombres))
    if args.ocr:
        hallazgos.extend(escanear_ocr(Path(args.ocr), args.tesseract_cmd, nombres))

    salida = Path(args.salida) if args.salida else Path(args.textos or args.ocr) / "aviso-privacidad.md"
    salida.parent.mkdir(parents=True, exist_ok=True)

    with salida.open("w", encoding="utf-8") as f:
        f.write("# Aviso de privacidad — revisión heurística\n\n")
        f.write("Esto es un aviso automático, no una garantía. Revisa cada hallazgo a\n")
        f.write("ojo antes de entregar nada a cliente; puede haber falsos positivos y,\n")
        f.write("sobre todo, falsos negativos: direcciones o importes sin formato\n")
        f.write("reconocible no se detectan, y los nombres propios o de empresa solo\n")
        if nombres:
            f.write(f"se han buscado contra la lista dada ({len(nombres)} términos) — si falta\n")
            f.write("alguno en la lista, no se detecta.\n\n")
        else:
            f.write("se detectan si se pasa `--nombres fichero.txt`; no se ha usado en esta pasada.\n\n")
        if hallazgos:
            f.write(f"## {len(hallazgos)} hallazgos\n\n")
            f.write("\n".join(hallazgos))
            f.write("\n")
        else:
            f.write("Sin hallazgos con los patrones actuales.\n")

    print(f"\n{len(hallazgos)} hallazgos. Informe: {salida}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
