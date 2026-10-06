#!/usr/bin/env python3
"""Dibuja marcadores numerados con círculo sobre una captura (①②③...).

Ninguna herramienta de anotación conocida trae numeración circulada de
serie (ver CREDITS.md) — se dibuja el círculo y el número en vez de confiar
en el glyph unicode ①②③, que además no existe más allá de ⑳ y no todas las
fuentes lo tienen. Nunca escribe sobre el original: la salida es siempre un
fichero distinto (o se exige --forzar si se pide explícitamente lo mismo).

Uso:
    python anotar-captura.py entrada.png salida.png --marca 120,80 --marca 300,200 --marca 450,60

Con --porcentaje, las coordenadas son 0-100 relativas al ancho/alto de la
imagen en vez de píxeles — sobreviven a un redimensionado posterior:

    python anotar-captura.py entrada.png salida.png --porcentaje --marca 20,15 --marca 60,40
"""
import argparse
import sys
from pathlib import Path

RUTAS_FUENTE = [
    r"C:\Windows\Fonts\arialbd.ttf",
    r"C:\Windows\Fonts\arial.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
]


def cargar_fuente(tam: int):
    from PIL import ImageFont

    for ruta in RUTAS_FUENTE:
        if Path(ruta).exists():
            try:
                return ImageFont.truetype(ruta, tam)
            except OSError:
                continue
    return ImageFont.load_default()


def parsear_marca(valor: str):
    try:
        x_str, y_str = valor.split(",")
        return float(x_str), float(y_str)
    except ValueError:
        raise argparse.ArgumentTypeError(f"'{valor}' no es 'x,y'")


def dibujar_marcadores(imagen_path: Path, salida_path: Path, marcas: list, porcentaje: bool,
                        radio: int, color: str, color_texto: str):
    from PIL import Image, ImageDraw

    img = Image.open(imagen_path).convert("RGB")
    ancho, alto = img.size
    draw = ImageDraw.Draw(img)
    fuente = cargar_fuente(int(radio * 1.2))

    for i, (x, y) in enumerate(marcas, 1):
        if porcentaje:
            x = x / 100 * ancho
            y = y / 100 * alto
        caja = (x - radio, y - radio, x + radio, y + radio)
        draw.ellipse(caja, fill=color, outline=color_texto, width=2)
        texto = str(i)
        bbox = draw.textbbox((0, 0), texto, font=fuente)
        tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
        draw.text((x - tw / 2 - bbox[0], y - th / 2 - bbox[1]), texto, fill=color_texto, font=fuente)

    salida_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(salida_path)


def main() -> int:
    # La ayuda y los mensajes llevan ①②③: en una consola de Windows (cp1252) no se pueden
    # mostrar y el script se caía al imprimirlos. Se sustituyen en vez de fallar.
    for flujo in (sys.stdout, sys.stderr):
        if hasattr(flujo, "reconfigure"):
            flujo.reconfigure(errors="replace")
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("entrada", help="Imagen original (no se toca)")
    parser.add_argument("salida", help="Fichero de salida, distinto de la entrada")
    parser.add_argument("--marca", action="append", type=parsear_marca, required=True,
                         help="Coordenada 'x,y' de un marcador. Repite en el orden en que el texto los menciona: el primero es ①")
    parser.add_argument("--porcentaje", action="store_true", help="Las coordenadas son 0-100 relativas al tamaño de la imagen, no píxeles")
    parser.add_argument("--radio", type=int, default=18, help="Radio del círculo en píxeles (por defecto 18)")
    parser.add_argument("--color", default="#E63946", help="Color de relleno del círculo (por defecto un rojo legible)")
    parser.add_argument("--color-texto", default="white", help="Color del número y del borde del círculo")
    parser.add_argument("--forzar", action="store_true", help="Permite que entrada y salida sean el mismo fichero (no recomendado)")
    args = parser.parse_args()

    entrada = Path(args.entrada)
    salida = Path(args.salida)

    if not entrada.exists():
        print(f"No encuentro la imagen: {entrada}", file=sys.stderr)
        return 1
    if entrada.resolve() == salida.resolve() and not args.forzar:
        print("Entrada y salida son el mismo fichero. Usa un nombre distinto o --forzar.", file=sys.stderr)
        print("Anotar sobre el original impide rehacerlo si el recorte no vale, y con --forzar", file=sys.stderr)
        print("repetido las anotaciones se van acumulando unas sobre otras.", file=sys.stderr)
        return 1

    try:
        from PIL import Image  # noqa: F401
    except ImportError:
        print("Falta Pillow. Instala con: pip install pillow", file=sys.stderr)
        return 1

    dibujar_marcadores(entrada, salida, args.marca, args.porcentaje, args.radio, args.color, args.color_texto)
    print(f"{len(args.marca)} marcador(es) dibujados: {salida}")
    print("Referencia cada uno en el texto del paso por su número, en el mismo orden.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
