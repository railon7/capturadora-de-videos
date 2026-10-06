#!/usr/bin/env python3
"""Recorta la pantalla compartida de una grabación de videollamada (Teams, Zoom, Meet...).

En la grabación de un webinar o una reunión, lo que se comparte ocupa solo un
rectángulo en el centro: alrededor quedan el fondo oscuro de la aplicación, sus
barras de botones y la miniatura de la cámara del ponente. Este script deja
solo ese rectángulo, sin más dependencia que Pillow:

  - Detección: la pantalla compartida es la zona clara y ancha sobre el fondo
    oscuro. Se mira, por columnas y luego por filas, qué parte de la imagen no
    es fondo (gris > --umbral) y se toma el tramo continuo más largo. La
    miniatura de cámara y las barras son más estrechas y quedan fuera.

  - Consenso (por defecto, al procesar una carpeta): la disposición de la
    llamada dura minutos, así que las cajas que se repiten en al menos 3
    fotogramas son "disposiciones estables". Un fotograma cuya detección no
    coincide con ninguna (contenido muy oscuro dentro de la pantalla, una
    portada con degradado) toma la del fotograma estable más cercano.

  - --forzar-caja: para los tramos en que ni la detección ni el consenso
    aciertan (típico: la sala de espera antes de empezar, con la cámara
    apagada y una portada oscura), se fija la caja a mano por patrón de nombre.

  - Pestaña de la cámara: Teams monta una pestaña oscura (un "═") sobre el
    borde superior de la pantalla compartida. Se tapa copiando el fondo de su
    izquierda, sin tocar las letras de los menús (--sin-pestana para no hacerlo).

Nunca pisa los originales: la salida tiene que ser otra carpeta u otro fichero.

Uso:
    python recortar-pantalla.py "Capturas/Rejilla"
    python recortar-pantalla.py "Capturas/Rejilla" "Capturas/Rejilla-pantalla"
    python recortar-pantalla.py "Capturas/Rejilla" --forzar-caja "t_0000*.jpg=232,37,1373,680"
    python recortar-pantalla.py "Capturas/Seleccionadas/P01-03.png" "Capturas/Editadas/P01-03.png"

Salida: por defecto, una carpeta "<carpeta>-pantalla" junto a la de entrada,
con las imágenes recortadas y el mismo nombre. Al terminar lista los tamaños
de recorte: deberían salir pocos (uno por disposición de la llamada); si sale
uno raro, revisa esas imágenes y fija su caja con --forzar-caja.
"""
import argparse
import fnmatch
import sys
from pathlib import Path

EXTENSIONES = (".jpg", ".jpeg", ".png")


def tramo_mas_largo(valores, umbral):
    """(inicio, fin) del tramo contiguo más largo con valores > umbral; fin excluido. None si no hay."""
    mejor = None
    inicio = None
    for i, v in enumerate(list(valores) + [float("-inf")]):
        if v > umbral:
            if inicio is None:
                inicio = i
        elif inicio is not None:
            if mejor is None or i - inicio > mejor[1] - mejor[0]:
                mejor = (inicio, i)
            inicio = None
    return mejor


def _fracciones(mascara, eje):
    """Fracción de píxeles blancos de una máscara 0/255, por columna (eje=0) o por fila (eje=1)."""
    from PIL import Image

    w, h = mascara.size
    destino = (w, 1) if eje == 0 else (1, h)
    return [v / 255 for v in mascara.resize(destino, Image.BOX).tobytes()]  # un byte por píxel en modo "L"


def detectar_pantalla(img, umbral=60):
    """Caja (x0, y0, x1, y1) de la pantalla compartida, o None si no se encuentra."""
    gris = img.convert("L")
    w, h = gris.size
    mascara = gris.point(lambda v: 255 if v > umbral else 0)
    # Columnas: en la franja central de filas, para no contar barras de arriba y abajo
    cols = tramo_mas_largo(_fracciones(mascara.crop((0, int(h * .05), w, int(h * .95))), 0), 0.45)
    if not cols:
        return None
    x0, x1 = cols
    # Filas: dentro de esas columnas, la pantalla ocupa casi todo el ancho;
    # la miniatura de cámara y las barras de la aplicación, no.
    filas = tramo_mas_largo(_fracciones(mascara.crop((x0, 0, x1, h)), 1), 0.5)
    if not filas:
        return None
    y0, y1 = filas
    if (x1 - x0) < w * .3 or (y1 - y0) < h * .3:
        return None
    return x0, y0, x1, y1


def parecida(a, b, tol=4):
    return a is not None and b is not None and all(abs(x - y) <= tol for x, y in zip(a, b))


def consenso(cajas, min_fotogramas=3, tol=4):
    """Ajusta cada caja a una disposición estable de la llamada.

    Estable = caja que se repite (con tolerancia `tol` píxeles) en al menos
    `min_fotogramas` imágenes. Una imagen que no encaja en ninguna toma la del
    fotograma estable más cercano en la lista (que va en orden de tiempo).
    Si no hay ninguna estable, devuelve las cajas tal cual.
    """
    grupos = []  # [caja representativa, cuenta]
    for c in cajas:
        if c is None:
            continue
        for g in grupos:
            if parecida(c, g[0], tol):
                g[1] += 1
                break
        else:
            grupos.append([c, 1])
    estables = [g[0] for g in grupos if g[1] >= min_fotogramas]
    if not estables:
        return list(cajas)
    asignadas = [next((e for e in estables if parecida(c, e, tol)), None) for c in cajas]
    resultado = []
    for i, a in enumerate(asignadas):
        if a is None:
            vecinos = [(abs(j - i), b) for j, b in enumerate(asignadas) if b is not None]
            a = min(vecinos, key=lambda x: x[0])[1]
        resultado.append(a)
    return resultado


def tapar_pestana(img, oscuro=90):
    """Tapa la pestaña oscura de la miniatura de cámara si asoma arriba, en el centro.

    La pestaña es un bloque oscuro compacto (2-12 % del ancho) en las primeras
    filas. En una fila de menú, los píxeles oscuros (las letras) se reparten a
    lo ancho y no cuentan. Devuelve la misma imagen si no hay pestaña.
    """
    gris = img.convert("L")
    w, h = gris.size
    c0, c1 = int(w * .35), int(w * .65)
    filas = []
    for y in range(max(8, int(h * .06))):
        fila = gris.crop((c0, y, c1, y + 1)).tobytes()
        d = [i for i, v in enumerate(fila) if v < oscuro]
        if len(d) >= w * .015 and d[-1] - d[0] <= w * .12:
            filas.append((y, d[0] + c0, d[-1] + c0))
        elif filas:
            break
    if len(filas) < 3:
        return img
    y0, y1 = max(0, filas[0][0] - 1), min(h, filas[-1][0] + 2)
    x0 = max(1, min(f[1] for f in filas) - 3)
    x1 = min(w, max(f[2] for f in filas) + 4)
    # Rellena estirando la columna limpia de su izquierda (el fondo de la cabecera)
    resultado = img.copy()
    columna = resultado.crop((x0 - 1, y0, x0, y1)).resize((x1 - x0, y1 - y0))
    resultado.paste(columna, (x0, y0))
    return resultado


def parsear_regla(texto):
    """'patron=x0,y0,x1,y1' -> (patron, (x0, y0, x1, y1))."""
    patron, sep, coords = texto.rpartition("=")
    numeros = coords.split(",")
    if not sep or not patron or len(numeros) != 4:
        raise ValueError(f"Regla no válida: {texto!r}. Formato: PATRON=X0,Y0,X1,Y1")
    caja = tuple(int(n) for n in numeros)
    if caja[2] <= caja[0] or caja[3] <= caja[1]:
        raise ValueError(f"Caja vacía en {texto!r}: X1 y Y1 deben ser mayores que X0 y Y0")
    return patron, caja


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("entrada", help="Imagen o carpeta de imágenes (p. ej. Capturas/Rejilla)")
    parser.add_argument("salida", nargs="?", default=None, help="Fichero o carpeta de salida (por defecto: <entrada>-pantalla)")
    parser.add_argument("--umbral", type=int, default=60, help="Gris (0-255) por debajo del cual un píxel cuenta como fondo (por defecto 60)")
    parser.add_argument("--sin-consenso", action="store_true", help="Usa la detección de cada imagen tal cual, sin ajustarla a las disposiciones estables")
    parser.add_argument("--sin-pestana", action="store_true", help="No tapa la pestaña de la miniatura de cámara")
    parser.add_argument("--forzar-caja", action="append", default=[], metavar="PATRON=X0,Y0,X1,Y1",
                        help="Caja fija para los ficheros cuyo nombre encaje con el patrón, p. ej. 't_0000*.jpg=232,37,1373,680'. Se puede repetir")
    args = parser.parse_args()

    try:
        from PIL import Image
    except ImportError:
        print("Falta Pillow. Instala con: pip install pillow", file=sys.stderr)
        return 1

    entrada = Path(args.entrada)
    if not entrada.exists():
        print(f"No encuentro: {entrada}", file=sys.stderr)
        return 1
    if args.salida:
        salida = Path(args.salida)
    elif entrada.is_dir():
        salida = entrada.parent / f"{entrada.name}-pantalla"
    else:
        salida = entrada.with_name(f"{entrada.stem}-pantalla{entrada.suffix}")
    if salida.resolve() == entrada.resolve():
        print("La salida tiene que ser distinta de la entrada: este script no pisa los originales.", file=sys.stderr)
        return 1

    try:
        reglas = [parsear_regla(r) for r in args.forzar_caja]
    except ValueError as e:
        print(e, file=sys.stderr)
        return 1

    if entrada.is_dir():
        ficheros = sorted((p for p in entrada.iterdir() if p.suffix.lower() in EXTENSIONES), key=lambda p: p.name)
        destinos = [salida / p.name for p in ficheros]
        salida.mkdir(parents=True, exist_ok=True)
    else:
        ficheros, destinos = [entrada], [salida]
        salida.parent.mkdir(parents=True, exist_ok=True)
    if not ficheros:
        print(f"No hay imágenes en {entrada}", file=sys.stderr)
        return 1

    print(f"Detectando la pantalla compartida en {len(ficheros)} imágenes...")
    cajas = []
    for i, ruta in enumerate(ficheros, 1):
        with Image.open(ruta) as img:
            cajas.append(detectar_pantalla(img, args.umbral))
        if i % 50 == 0:
            print(f"  ... {i}/{len(ficheros)}")
    if not args.sin_consenso and len(ficheros) > 1:
        cajas = consenso(cajas)
    for i, ruta in enumerate(ficheros):
        for patron, caja in reglas:
            if fnmatch.fnmatch(ruta.name, patron):
                cajas[i] = caja

    tamanos = {}
    sin_recortar = []
    for ruta, destino, caja in zip(ficheros, destinos, cajas):
        with Image.open(ruta) as img:
            if caja is None:
                sin_recortar.append(ruta.name)
                recorte = img.copy()
            else:
                recorte = img.crop(caja)
                tam = f"{caja[2] - caja[0]}x{caja[3] - caja[1]}"
                tamanos[tam] = tamanos.get(tam, 0) + 1
            if not args.sin_pestana:
                recorte = tapar_pestana(recorte)
            if destino.suffix.lower() in (".jpg", ".jpeg"):
                recorte.convert("RGB").save(destino, quality=92)
            else:
                recorte.save(destino)

    print(f"\nListo: {len(ficheros)} imágenes -> {salida}")
    print("Tamaños de recorte (uno por disposición de la llamada; uno raro = revisar):")
    for tam, n in sorted(tamanos.items(), key=lambda x: -x[1]):
        print(f"  {tam}: {n}")
    if sin_recortar:
        print(f"\nSin pantalla clara, copiadas sin recortar ({len(sin_recortar)}): {', '.join(sin_recortar[:10])}"
              + (" ..." if len(sin_recortar) > 10 else ""))
        print("Si deberían recortarse, fija su caja con --forzar-caja.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
