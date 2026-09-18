#!/usr/bin/env python3
"""Genera un borrador del mapa del vídeo cruzando transcripción y catálogo.

No sustituye el criterio humano de trocear en bloques y actos (eso lo pide
metodologia/de-video-a-guion-y-patrones.md §2) — hace el trabajo mecánico
que sí se puede automatizar: coger cada segmento de la transcripción con su
marca de tiempo (ya viene de Whisper) y sugerir, mirando el catálogo de
capturas, qué pantalla hay más o menos en ese momento. El resultado es un
BORRADOR: hay que fundir filas en bloques con sentido, agruparlas en actos,
y corregir la pantalla sugerida cuando la más cercana en el tiempo no sea
la correcta.

Requiere: Analisis/transcripcion.tsv (de transcribir.py) y, si existe,
Analisis/Catalogo de capturas.md (de catalogar-capturas.py) — sin este
segundo fichero el borrador sale igual, solo que sin sugerencia de pantalla.

Uso:
    python generar-borrador-guion.py "Analisis/transcripcion.tsv" --catalogo "Analisis/Catalogo de capturas.md"
"""
import argparse
import re
import sys
from pathlib import Path

RE_FILA_CATALOGO = re.compile(
    r"^\|\s*(?P<fichero>[^|]+?)\s*\|\s*(?P<hora>[^|]*?)\s*\|\s*(?P<ocr>[^|]*?)\s*\|\s*(?P<ve>[^|]*?)\s*\|\s*$"
)


def hora_a_segundos(hora: str):
    partes = hora.strip().split(":")
    if len(partes) != 3:
        return None
    try:
        h, m, s = (int(p) for p in partes)
    except ValueError:
        return None
    return h * 3600 + m * 60 + s


def segundos_a_hora(segundos: float) -> str:
    segundos = int(round(segundos))
    h, resto = divmod(segundos, 3600)
    m, s = divmod(resto, 60)
    return f"{h:02d}:{m:02d}:{s:02d}"


def leer_catalogo(ruta: Path):
    """Devuelve una lista de (segundos, fichero, descripcion) ordenada por tiempo."""
    if not ruta or not ruta.exists():
        return []
    filas = []
    for linea in ruta.read_text(encoding="utf-8").splitlines():
        m = RE_FILA_CATALOGO.match(linea)
        if not m or m.group("fichero") in ("Fichero", "---"):
            continue
        seg = hora_a_segundos(m.group("hora"))
        if seg is None:
            continue
        descripcion = m.group("ve").strip() or m.group("ocr").strip()
        filas.append((seg, m.group("fichero").strip(), descripcion))
    filas.sort(key=lambda t: t[0])
    return filas


def pantalla_mas_cercana(segundos: float, catalogo: list, tolerancia: float):
    """La entrada del catálogo más cercana en el tiempo, dentro de la tolerancia."""
    mejor = None
    mejor_dist = None
    for seg, fichero, desc in catalogo:
        dist = abs(seg - segundos)
        if mejor_dist is None or dist < mejor_dist:
            mejor_dist = dist
            mejor = (fichero, desc, dist)
    if mejor and mejor[2] <= tolerancia:
        return mejor[0], mejor[1]
    return None, None


def leer_transcripcion(ruta: Path):
    """Lee el TSV de transcribir.py: inicio_seg, fin_seg, hora, texto."""
    segmentos = []
    lineas = ruta.read_text(encoding="utf-8").splitlines()
    for linea in lineas[1:]:  # salta la cabecera
        partes = linea.split("\t")
        if len(partes) < 4:
            continue
        try:
            inicio = float(partes[0])
        except ValueError:
            continue
        texto = partes[3].strip()
        if texto:
            segmentos.append((inicio, texto))
    return segmentos


def fusionar_segmentos(segmentos: list, pausa_min: float):
    """Junta segmentos consecutivos si están más cerca que pausa_min segundos,
    para no sacar una fila por cada frase suelta de una transcripción con VAD."""
    if not segmentos:
        return []
    fusionados = [list(segmentos[0])]
    for inicio, texto in segmentos[1:]:
        anterior_inicio, anterior_texto = fusionados[-1]
        # Aproxima el fin del anterior asumiendo que el siguiente empieza poco después
        if inicio - anterior_inicio < pausa_min:
            fusionados[-1][1] = f"{anterior_texto} {texto}"
        else:
            fusionados.append([inicio, texto])
    return [(i, t) for i, t in fusionados]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("transcripcion", help="Fichero transcripcion.tsv de transcribir.py")
    parser.add_argument("--catalogo", default=None, help="Catalogo de capturas.md, para sugerir pantalla por cercanía de tiempo")
    parser.add_argument("--salida", default=None, help="Fichero .md de salida (por defecto: junto a la transcripción)")
    parser.add_argument("--tolerancia", type=float, default=30, help="Segundos máximos de distancia para sugerir una pantalla del catálogo (por defecto 30)")
    parser.add_argument("--pausa-min", type=float, default=1.5, help="Segundos de separación mínima entre segmentos para no fusionarlos en un bloque (por defecto 1.5)")
    args = parser.parse_args()

    ruta_transcripcion = Path(args.transcripcion)
    if not ruta_transcripcion.exists():
        print(f"No encuentro la transcripción: {ruta_transcripcion}", file=sys.stderr)
        return 1

    segmentos = leer_transcripcion(ruta_transcripcion)
    if not segmentos:
        print("La transcripción no tiene segmentos con texto.", file=sys.stderr)
        return 1
    bloques = fusionar_segmentos(segmentos, args.pausa_min)

    catalogo = leer_catalogo(Path(args.catalogo)) if args.catalogo else []

    salida = Path(args.salida) if args.salida else ruta_transcripcion.parent / "Mapa del video (borrador).md"

    filas = []
    for n, (inicio, texto) in enumerate(bloques, 1):
        hora = segundos_a_hora(inicio)
        fichero, desc = pantalla_mas_cercana(inicio, catalogo, args.tolerancia) if catalogo else (None, None)
        pantalla = f"`{fichero}`" if fichero else "¿?"
        if desc:
            pantalla += f" — {desc}"
        cita = texto.replace("|", "\\|").strip()
        filas.append(f"| {n} | *(revisar bloque/acto)* | \"{cita}\" | {pantalla} | | {hora} |")

    with salida.open("w", encoding="utf-8") as f:
        f.write(f"# Mapa del vídeo — borrador ({ruta_transcripcion.parent.name})\n\n")
        f.write(
            "**Esto es un borrador, no el guion final.** Cada fila es un segmento de\n"
            "la transcripción, no un bloque con sentido propio — hay que fundir filas\n"
            "consecutivas del mismo tema, agruparlas en actos (columna aparte, mira\n"
            "`plantillas/plantilla-mapa-de-video.md`), y corregir la pantalla sugerida:\n"
            "es la más cercana en el tiempo dentro del catálogo, no necesariamente la\n"
            "correcta — revísala contra la hoja de contacto si hay duda.\n\n"
        )
        f.write("| # | Acto | Cita (revisar bloque) | Pantalla sugerida | Destino | t |\n")
        f.write("|---|---|---|---|---|---|\n")
        f.write("\n".join(filas))
        f.write("\n")

    print(f"Borrador con {len(filas)} bloques candidatos: {salida}")
    if not catalogo:
        print("Aviso: sin --catalogo no hay sugerencia de pantalla — pásalo si ya existe Catalogo de capturas.md")
    print("Revísalo: funde filas en bloques, agrúpalos en actos, y guárdalo como el mapa definitivo.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
