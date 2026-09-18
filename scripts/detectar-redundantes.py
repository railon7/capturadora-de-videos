#!/usr/bin/env python3
"""Aviso de fotogramas borrosos o casi duplicados, antes de revisarlos a mano.

Dos comprobaciones, sin más dependencia que Pillow (ya la usan otros
scripts de este repo):

  - Borrosos: aproxima nitidez por la desviación típica de los bordes
    detectados (PIL ImageFilter.FIND_EDGES). Una imagen nítida tiene bordes
    marcados y por tanto más dispersión de valores; una borrosa, bordes
    débiles y valores más planos. El umbral es relativo al propio lote de
    imágenes (percentil), no un número fijo — varía mucho entre vídeos.

  - Casi duplicados: hash perceptivo simple (aHash de 64 bits: reduce a
    8x8 en escala de grises y compara cada píxel con la media) entre
    fotogramas CONSECUTIVOS por nombre de fichero. Distancia de Hamming
    baja = casi idénticos.

Es un aviso, no una garantía, y no borra nada: deja un informe para que
decidas qué ignorar.

Uso:
    python detectar-redundantes.py "Capturas/Rejilla"
    python detectar-redundantes.py "Capturas/Rejilla" --umbral-duplicado 4 --percentil-borroso 25
"""
import argparse
import sys
from pathlib import Path


def hash_perceptivo(imagen) -> int:
    pequena = imagen.convert("L").resize((8, 8))
    pixeles = list(pequena.tobytes())  # un byte 0-255 por píxel en modo "L"
    media = sum(pixeles) / len(pixeles)
    bits = 0
    for p in pixeles:
        bits = (bits << 1) | (1 if p >= media else 0)
    return bits


def distancia_hamming(a: int, b: int) -> int:
    return bin(a ^ b).count("1")


def puntuacion_nitidez(imagen) -> float:
    from PIL import ImageFilter, ImageStat

    bordes = imagen.convert("L").filter(ImageFilter.FIND_EDGES)
    return ImageStat.Stat(bordes).stddev[0]


def percentil(valores: list, p: float) -> float:
    if not valores:
        return 0.0
    ordenados = sorted(valores)
    k = (len(ordenados) - 1) * (p / 100)
    f, c = int(k), min(int(k) + 1, len(ordenados) - 1)
    if f == c:
        return ordenados[f]
    return ordenados[f] + (ordenados[c] - ordenados[f]) * (k - f)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("carpeta", help="Carpeta con las imágenes a revisar (p. ej. Capturas/Rejilla)")
    parser.add_argument("--salida", default=None, help="Fichero .md de salida (por defecto: Analisis/Fotogramas a revisar.md)")
    parser.add_argument("--umbral-duplicado", type=int, default=4, help="Distancia de Hamming máxima (de 64) para considerar dos fotogramas consecutivos casi duplicados (por defecto 4)")
    parser.add_argument("--percentil-borroso", type=float, default=20, help="Se marcan como borrosos los fotogramas por debajo de este percentil de nitidez del propio lote (por defecto 20)")
    args = parser.parse_args()

    try:
        from PIL import Image
    except ImportError:
        print("Falta Pillow. Instala con: pip install pillow", file=sys.stderr)
        return 1

    carpeta = Path(args.carpeta)
    if not carpeta.is_dir():
        print(f"No encuentro la carpeta: {carpeta}", file=sys.stderr)
        return 1

    imagenes = sorted(
        [p for p in carpeta.iterdir() if p.suffix.lower() in (".jpg", ".jpeg", ".png")],
        key=lambda p: p.name,
    )
    if len(imagenes) < 2:
        print("Hacen falta al menos 2 imágenes para comparar.", file=sys.stderr)
        return 1

    print(f"Analizando {len(imagenes)} imágenes...")
    datos = []
    for i, ruta in enumerate(imagenes, 1):
        img = Image.open(ruta)
        datos.append({
            "ruta": ruta,
            "hash": hash_perceptivo(img),
            "nitidez": puntuacion_nitidez(img),
        })
        if i % 25 == 0:
            print(f"  ... {i}/{len(imagenes)}")

    umbral_nitidez = percentil([d["nitidez"] for d in datos], args.percentil_borroso)

    borrosos = [d for d in datos if d["nitidez"] <= umbral_nitidez]

    duplicados = []
    for anterior, actual in zip(datos, datos[1:]):
        dist = distancia_hamming(anterior["hash"], actual["hash"])
        if dist <= args.umbral_duplicado:
            duplicados.append((anterior["ruta"].name, actual["ruta"].name, dist))

    if args.salida:
        salida = Path(args.salida)
    else:
        candidatos = [p for p in carpeta.parents if (p / "Analisis").is_dir()]
        base = candidatos[0] / "Analisis" if candidatos else carpeta.parent / "Analisis"
        salida = base / "Fotogramas a revisar.md"
    salida.parent.mkdir(parents=True, exist_ok=True)

    with salida.open("w", encoding="utf-8") as f:
        f.write(f"# Fotogramas a revisar — {carpeta.name}\n\n")
        f.write(
            "Aviso automático, no una garantía: revisa antes de descartar nada, "
            "esto no borra ni mueve ficheros.\n\n"
        )
        f.write(f"## Posiblemente borrosos ({len(borrosos)} de {len(datos)}, percentil {args.percentil_borroso})\n\n")
        if borrosos:
            for d in sorted(borrosos, key=lambda d: d["nitidez"]):
                f.write(f"- `{d['ruta'].name}` (nitidez {d['nitidez']:.1f}, umbral {umbral_nitidez:.1f})\n")
        else:
            f.write("Ninguno.\n")
        f.write(f"\n## Posibles duplicados consecutivos (distancia ≤ {args.umbral_duplicado})\n\n")
        if duplicados:
            for a, b, dist in duplicados:
                f.write(f"- `{a}` ≈ `{b}` (distancia {dist})\n")
        else:
            f.write("Ninguno.\n")

    print(f"\n{len(borrosos)} posibles borrosos, {len(duplicados)} posibles duplicados.")
    print(f"Informe: {salida}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
